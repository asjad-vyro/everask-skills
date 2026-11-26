#!/usr/bin/env python3
"""Apply an edit list to the sound of an audio or video file with ffmpeg.

Usage: python3 sound_edit.py edit.json
Prints one JSON object (ok, output, before, after, expected/actual duration,
change_list, cut_points, warnings). With no "ops" it only measures the input.

edit.json:
{"input": "in.mp3", "output": "out.mp3", "bitrate": "192k",
 "ops": [{"op": "denoise"}, {"op": "mute", "start": "0:12", "end": "0:14"},
         {"op": "cut", "ranges": [{"start": 5, "end": 8}], "crossfade": 0.05},
         {"op": "fade", "in": 1, "out": 2}, {"op": "normalize", "target_lufs": -16}]}
Ops run in list order; times refer to the timeline at that point.
"""
import json, os, re, shutil, subprocess, sys, tempfile

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
DURATION_OPS = {"trim", "cut", "speed", "join"}


class Fail(Exception):
    pass


def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise Fail("ffmpeg failed: " + " ".join(cmd[:6]) + " ... " + p.stderr[-600:])
    return p


def run_bytes(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise Fail("ffmpeg failed: " + p.stderr.decode()[-400:])
    return p.stdout


def tparse(v):
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().lower().rstrip("s").strip()
    if ":" in s:
        t = 0.0
        for part in s.split(":"):
            t = t * 60 + float(part)
        return t
    return float(s)


def fmt(t):
    t = max(0.0, t)
    return "%d:%05.2f" % (int(t // 60), t - 60 * int(t // 60))


def probe(path):
    p = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path])
    j = json.loads(p.stdout)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    v = next((s for s in j["streams"] if s["codec_type"] == "video" and
              s.get("disposition", {}).get("attached_pic", 0) == 0), None)
    d = float(j["format"].get("duration") or (a or {}).get("duration") or 0)
    return {"duration": round(d, 3), "has_audio": a is not None, "has_video": v is not None,
            "sample_rate": int(a["sample_rate"]) if a else None,
            "channels": a["channels"] if a else None,
            "audio_codec": a["codec_name"] if a else None,
            "audio_tracks": sum(1 for s in j["streams"] if s["codec_type"] == "audio"),
            "bit_rate": int(j["format"]["bit_rate"]) if j["format"].get("bit_rate") else None,
            "size_bytes": int(j["format"].get("size", 0))}


def measure(path, window=5.0):
    """Integrated loudness, loudness range, true peak and average momentary loudness per window."""
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "verbose", "-i", path, "-vn",
             "-af", "ebur128=peak=true:framelog=verbose", "-f", "null", "-"], check=False)
    err = p.stderr
    out = {}
    summ = err.rsplit("Summary:", 1)[-1]
    m = re.search(r"\n\s*I:\s+(-?[\d.]+|-inf)\s+LUFS", summ)
    out["integrated_lufs"] = float(m.group(1)) if m and m.group(1) != "-inf" else None
    m = re.search(r"LRA:\s+(-?[\d.]+)\s+LU", summ)
    out["loudness_range_lu"] = float(m.group(1)) if m else None
    m = re.search(r"True peak:\s*\n\s*Peak:\s+(-?[\d.]+|-inf)\s+dBFS", summ)
    out["true_peak_dbtp"] = float(m.group(1)) if m and m.group(1) != "-inf" else None
    blocks = {}
    for t, mm in re.findall(r"t:\s*([\d.]+)\s+TARGET:.*?M:\s*(-?[\d.]+|-inf|nan)\s", err):
        if mm in ("-inf", "nan"):
            continue
        v = float(mm)
        if v < -70:
            v = -70.0
        blocks.setdefault(int(float(t) // window), []).append(v)
    out["loudness_by_window"] = [
        {"from": round(k * window, 1), "to": round((k + 1) * window, 1),
         "avg_momentary_lufs": round(sum(v) / len(v), 1)} for k, v in sorted(blocks.items())]
    return out


def pcm_wav(src, dst, sr=None, ch=None, extra=None):
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + (extra or []) + ["-i", src, "-vn", "-map", "0:a:0"]
    if sr:
        cmd += ["-ar", str(sr)]
    if ch:
        cmd += ["-ac", str(ch)]
    run(cmd + ["-c:a", "pcm_f32le", dst])


def level_sections(src, dst, sr, ch, max_boost, max_cut, target_db=None):
    """Raise quiet parts and lower loud parts towards one level, smoothly. Needs numpy."""
    import numpy as np
    raw = run_bytes(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"])
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, ch).astype(np.float64)
    n = len(x)
    blk = max(1, int(0.2 * sr))
    nb = max(1, n // blk)
    pad = nb * blk
    xs = x[:pad] if pad else x
    rms = np.sqrt((xs.reshape(nb, blk, ch) ** 2).mean(axis=(1, 2)) + 1e-12)
    lvl = 20 * np.log10(rms + 1e-12)
    peak = 20 * np.log10(np.abs(xs.reshape(nb, blk, ch)).max(axis=(1, 2)) + 1e-12)
    live = lvl > -55.0
    if not live.any():
        raise Fail("the audio is silent; nothing to level")
    if target_db is not None:
        target = float(target_db)
    else:
        lo, hi = np.percentile(lvl[live], [10, 90])
        target = float((lo + hi) / 2.0)
    # a middle target between the quiet and loud parts, so neither is pushed too far
    gain = np.clip(target - lvl, -max_cut, max_boost)
    gain = np.minimum(gain, -peak - 0.5 + 0.0)  # keep peaks under about -0.5 dBFS before smoothing
    last = 0.0
    for i in range(nb):
        if live[i]:
            last = gain[i]
        else:
            gain[i] = last  # hold the previous gain through silence, do not boost the noise floor
    # keep the peaks of each block under the limit
    gain = np.minimum(gain, -peak - 0.5)
    # gain is constant inside a block. Between blocks it moves in a short linear ramp (in dB) placed on the side
    # of the LOWER gain: a drop ends exactly at the block edge, a rise starts at it. So the boost for a quiet part
    # never leaks into the loud part that follows it, and the loud part's cut never reaches the quiet part before it.
    g_db = np.empty(n)
    g_db[:pad] = np.repeat(gain, blk)
    g_db[pad:] = gain[-1]
    for i in range(1, nb):
        d = gain[i] - gain[i - 1]
        if abs(d) < 0.05:
            continue
        r = int(sr * (0.03 if abs(d) > 6 else 0.09))
        edge = i * blk
        if d < 0:
            s0, s1 = edge - r, edge
        else:
            s0, s1 = edge, edge + r
        g_db[s0:s1] = np.linspace(gain[i - 1], gain[i], r + 1)[1:]
    y = (x * (10 ** (g_db / 20.0))[:, None]).astype(np.float32)
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(sr), "-ac", str(ch),
                        "-i", "-", "-c:a", "pcm_f32le", dst], input=y.tobytes(), capture_output=True)
    if p.returncode != 0:
        raise Fail("ffmpeg failed while writing the levelled audio: " + p.stderr.decode()[-300:])


def atempo_chain(f):
    parts = []
    while f > 2.0:
        parts.append(2.0)
        f /= 2.0
    while f < 0.5:
        parts.append(0.5)
        f /= 0.5
    parts.append(f)
    return ",".join("atempo=%.6f" % x for x in parts)


def gain_expr(s, e, gain_db, ramp=0.05):
    g = 10 ** (gain_db / 20.0)
    if e is None:
        return "volume=%.6f" % g
    r = min(ramp, max(0.001, (e - s) / 2))
    # small frames, so the gain is re-evaluated every few milliseconds (the default frame is ~23 ms or more)
    return ("asetnsamples=n=64:p=0,volume='1+(%.6f-1)*(min(1,max(0,(t-%.4f)/%.4f))-min(1,max(0,(t-%.4f)/%.4f)))':eval=frame"
            % (g, s, r, e - r, r))


def main(spec):
    src = spec["input"]
    if not os.path.isfile(src):
        raise Fail("input file not found: " + src)
    ext_in = os.path.splitext(src)[1].lower()
    info = probe(src)
    if not info["has_audio"]:
        raise Fail("the file has no audio track")
    before = dict(info)
    before.update(measure(src))
    ops = spec.get("ops") or []
    if not ops:
        return {"ok": True, "mode": "measure_only", "input": src, "before": before}

    is_video = info["has_video"]
    out = spec.get("output") or os.path.splitext(src)[0] + "-fixed" + ext_in
    ext_out = os.path.splitext(out)[1].lower()
    warnings, changes, cuts = [], [], []
    work = tempfile.mkdtemp(prefix="soundfix-")
    n = [0]
    sr, ch = info["sample_rate"], info["channels"]

    def nxt():
        n[0] += 1
        return os.path.join(work, "s%d.wav" % n[0])

    def seg_dur(path):
        return probe(path)["duration"]

    try:
        cur = nxt()
        pcm_wav(src, cur)
        dur = seg_dur(cur)
        video_trim = None
        if is_video:
            bad = [o["op"] for o in ops if o["op"] in DURATION_OPS and o["op"] != "trim"]
            if bad or sum(1 for o in ops if o["op"] == "trim") > 1:
                raise Fail("on a video file only one 'trim' may change the length (not: %s); "
                           "fix the sound without changing the length, or cut the video first"
                           % ", ".join(bad or ["second trim"]))
        for o in ops:
            op = o["op"]
            nx = nxt()
            if op == "trim":
                s = tparse(o.get("start", 0))
                e = tparse(o["end"]) if "end" in o else (s + tparse(o["duration"]) if "duration" in o else dur)
                if e > dur + 0.01:
                    warnings.append("trim end %s is past the end of the audio (%s); used the end" % (fmt(e), fmt(dur)))
                    e = dur
                if e <= s:
                    raise Fail("trim end must be after start")
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-af",
                     "atrim=start=%.4f:end=%.4f,asetpts=PTS-STARTPTS" % (s, e), "-c:a", "pcm_f32le", nx])
                changes.append("Trim to %s - %s (length %s)" % (fmt(s), fmt(e), fmt(e - s)))
                cuts = [c - s for c in cuts if s < c < e]
                if is_video:
                    video_trim = (s, e - s)
                dur = e - s
            elif op == "cut":
                rng = sorted((tparse(r["start"]), tparse(r["end"])) for r in o["ranges"])
                xf = float(o.get("crossfade", 0.05))
                keep, pos = [], 0.0
                for s, e in rng:
                    if e > dur:
                        warnings.append("cut end %s is past the end; used the end" % fmt(e))
                        e = dur
                    if s >= e:
                        raise Fail("cut range %s - %s is empty" % (fmt(s), fmt(e)))
                    if s - pos > 0.001:
                        keep.append((pos, s))
                    pos = max(pos, e)
                if dur - pos > 0.001:
                    keep.append((pos, dur))
                if not keep:
                    raise Fail("the cut would remove everything")
                shortest = min(b - a for a, b in keep)
                if len(keep) > 1 and xf > shortest / 2:
                    xf = max(0.0, shortest / 2)
                    warnings.append("crossfade shortened to %.3f s because a kept piece is very short" % xf)
                parts = ["[0:a]atrim=start=%.4f:end=%.4f,asetpts=PTS-STARTPTS[k%d]" % (a, b, i)
                         for i, (a, b) in enumerate(keep)]
                if len(keep) == 1:
                    graph = ";".join(parts) + ";[k0]anull[o]"
                else:
                    last, graph_parts = "k0", parts
                    for i in range(1, len(keep)):
                        lab = "x%d" % i
                        if xf > 0:
                            graph_parts.append("[%s][k%d]acrossfade=d=%.4f:c1=qsin:c2=qsin[%s]" % (last, i, xf, lab))
                        else:
                            graph_parts.append("[%s][k%d]concat=n=2:v=0:a=1[%s]" % (last, i, lab))
                        last = lab
                    graph = ";".join(graph_parts) + ";[%s]anull[o]" % last
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-filter_complex", graph,
                     "-map", "[o]", "-c:a", "pcm_f32le", nx])
                # cut points in the new timeline
                newcuts, acc = [], 0.0
                for i, (a, b) in enumerate(keep[:-1]):
                    acc += (b - a) - (xf if i > 0 else 0)
                    newcuts.append(round(acc, 3))
                cuts = newcuts
                dur = sum(b - a for a, b in keep) - xf * (len(keep) - 1)
                changes.append("Cut out " + ", ".join("%s - %s" % (fmt(s), fmt(e)) for s, e in rng)
                               + " and joined the rest with a %.0f ms crossfade" % (xf * 1000))
            elif op in ("volume", "mute"):
                s = tparse(o["start"]) if "start" in o else 0.0
                e = tparse(o["end"]) if "end" in o else None
                if op == "mute":
                    g, desc = -200.0, "Mute"
                else:
                    g = float(o["gain_db"])
                    desc = "Volume %+g dB" % g
                if e is not None and e > dur:
                    e = dur
                if e is None and "start" in o:
                    e = dur
                rng_txt = "the whole file" if e is None else "%s - %s" % (fmt(s), fmt(e))
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-af", gain_expr(s, e, g),
                     "-c:a", "pcm_f32le", nx])
                changes.append("%s on %s" % (desc, rng_txt))
            elif op == "fade":
                fi, fo = float(o.get("in", 0)), float(o.get("out", 0))
                fl = []
                if fi > 0:
                    fl.append("afade=t=in:st=0:d=%.3f:curve=qsin" % fi)
                if fo > 0:
                    fl.append("afade=t=out:st=%.3f:d=%.3f:curve=qsin" % (max(0, dur - fo), fo))
                if not fl:
                    raise Fail("fade needs 'in' and/or 'out' seconds")
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-af", ",".join(fl), "-c:a", "pcm_f32le", nx])
                changes.append("Fade " + " and ".join(x for x in (
                    "in over %g s" % fi if fi > 0 else "", "out over the last %g s" % fo if fo > 0 else "") if x))
            elif op == "denoise":
                nr = float(o.get("reduction_db", 12))
                hp = float(o.get("highpass_hz", 80))
                fl = ["highpass=f=%g" % hp, "afftdn=nr=%g:nf=-40:tn=1" % nr]
                if o.get("lowpass_hz"):
                    fl.append("lowpass=f=%g" % float(o["lowpass_hz"]))
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-af", ",".join(fl), "-c:a", "pcm_f32le", nx])
                changes.append("Mild noise reduction (%g dB) and a %g Hz low cut" % (nr, hp))
                warnings.append("Noise reduction is mild: steady hiss and hum drop, but voices can sound slightly "
                                "watery, and it cannot remove echo, clipping or other voices.")
            elif op == "speed":
                f = float(o["factor"])
                if not 0.25 <= f <= 4:
                    raise Fail("speed factor must be between 0.25 and 4")
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-af", atempo_chain(f), "-c:a", "pcm_f32le", nx])
                dur /= f
                cuts = [c / f for c in cuts]
                changes.append("Speed x%g without changing pitch (length now %s)" % (f, fmt(dur)))
            elif op == "even_out":
                try:
                    import numpy  # noqa
                    ok_np = dur <= 1800
                except ImportError:
                    ok_np = False
                if ok_np:
                    mid = nxt()
                    level_sections(cur, mid, sr, ch, float(o.get("max_boost_db", 20)),
                                   float(o.get("max_cut_db", 12)), o.get("target_db"))
                    run(["ffmpeg", "-y", "-loglevel", "error", "-i", mid, "-af", "alimiter=limit=0.97",
                         "-c:a", "pcm_f32le", nx])
                    changes.append("Evened out loud and quiet parts (gain follows the level, silence is left alone)")
                else:
                    run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-af",
                         "dynaudnorm=f=150:g=5:p=0.9:m=60:s=0", "-c:a", "pcm_f32le", nx])
                    changes.append("Evened out loud and quiet parts (simple dynamic levelling)")
                    warnings.append("Used the simple levelling filter (numpy missing or file very long); "
                                    "very quiet parts may stay a little quieter.")
            elif op == "normalize":
                target = float(o.get("target_lufs", -16))
                tp = float(o.get("true_peak", -1.5))
                lra = float(o.get("lra", 11))
                p1 = run(["ffmpeg", "-hide_banner", "-nostats", "-i", cur, "-af",
                          "loudnorm=I=%g:TP=%g:LRA=%g:print_format=json" % (target, tp, lra), "-f", "null", "-"])
                js = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.S).group(0))
                if js["input_i"] in ("-inf", "inf"):
                    raise Fail("the audio is silent; nothing to normalise")
                # one constant gain (what linear loudnorm does), never loudnorm's dynamic mode, which makes bursts
                # at level steps; the gain is held back so the true peak stays under the limit
                gain_db = target - float(js["input_i"])
                room = tp - float(js["input_tp"])
                if gain_db > room:
                    gain_db = room
                run(["ffmpeg", "-hide_banner", "-nostats", "-i", cur, "-af", "volume=%.4fdB" % gain_db,
                     "-ar", str(sr), "-c:a", "pcm_f32le", nx])
                landed = float(js["input_i"]) + gain_db
                if abs(landed - target) > 1.0:
                    warnings.append("Loudness landed at %.1f LUFS, not %g: reaching the target would push the peaks "
                                    "over the %g dBTP limit or the recording is very uneven." % (
                                        landed, target, tp))
                changes.append("Normalise loudness to %g LUFS (true peak limit %g dBTP); was %.1f LUFS" % (
                    target, tp, float(js["input_i"])))
            elif op == "join":
                other = o["file"]
                tmp2 = nxt()
                pcm_wav(other, tmp2, sr=sr, ch=ch)
                xf = float(o.get("crossfade", 0))
                d2 = seg_dur(tmp2)
                if xf > min(dur, d2):
                    xf = min(dur, d2) / 2
                if xf > 0:
                    g = "[0:a][1:a]acrossfade=d=%.3f:c1=qsin:c2=qsin[o]" % xf
                else:
                    g = "[0:a][1:a]concat=n=2:v=0:a=1[o]"
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-i", tmp2, "-filter_complex", g,
                     "-map", "[o]", "-c:a", "pcm_f32le", nx])
                cuts.append(round(dur - xf, 3))
                dur = dur + d2 - xf
                changes.append("Join %s after it with a %g s crossfade" % (os.path.basename(other), xf))
            elif op == "duck":
                music = nxt()
                gain = float(o.get("music_gain_db", -10))
                pcm_wav(o["file"], music, sr=sr, ch=ch)
                bed = nxt()
                mf = "volume=%gdB,atrim=0:%.4f,afade=t=in:d=0.5,afade=t=out:st=%.3f:d=%.3f" % (
                    gain, dur, max(0, dur - 2), min(2, dur / 2))
                if not o.get("loop"):
                    mf = "apad,atrim=0:%.4f," % dur + mf
                run(["ffmpeg", "-y", "-loglevel", "error"] + (["-stream_loop", "-1"] if o.get("loop") else []) +
                    ["-i", music, "-af", mf, "-c:a", "pcm_f32le", bed])
                g = ("[0:a]asplit=2[vo][key];[1:a][key]sidechaincompress=threshold=0.02:ratio=12:attack=10:"
                     "release=500[d];[vo][d]amix=inputs=2:duration=first:normalize=0[o]")
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-i", bed, "-filter_complex", g,
                     "-map", "[o]", "-c:a", "pcm_f32le", nx])
                changes.append("Mix %s under the voice (%+g dB, lowered further while someone speaks)" % (
                    os.path.basename(o["file"]), gain))
            else:
                raise Fail("unknown op: " + op)
            cur = nx

        # encode
        codecs = {".wav": ["-c:a", "pcm_s24le" if info["audio_codec"] == "pcm_s24le" else "pcm_s16le"],
                  ".mp3": ["-c:a", "libmp3lame", "-b:a", spec.get("bitrate", "192k")],
                  ".m4a": ["-c:a", "aac", "-b:a", spec.get("bitrate", "192k")],
                  ".aac": ["-c:a", "aac", "-b:a", spec.get("bitrate", "192k")],
                  ".flac": ["-c:a", "flac"], ".ogg": ["-c:a", "libvorbis", "-b:a", spec.get("bitrate", "160k")],
                  ".opus": ["-c:a", "libopus", "-b:a", spec.get("bitrate", "128k")]}
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        if is_video:
            if info["audio_tracks"] > 1:
                warnings.append("The video has %d audio tracks; only the first was fixed and kept." % info["audio_tracks"])
            vc = ["-c:v", "copy"]
            vin = ["-i", src]
            if video_trim:
                vin = ["-ss", "%.4f" % video_trim[0], "-t", "%.4f" % video_trim[1], "-i", src]
                vc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
                warnings.append("The video was re-encoded (quality 18) because it was trimmed.")
            acodec = ["-c:a", "libopus", "-b:a", "160k"] if ext_out == ".webm" else ["-c:a", "aac", "-b:a", spec.get("bitrate", "192k")]
            run(["ffmpeg", "-y", "-loglevel", "error"] + vin + ["-i", cur, "-filter_complex", "[1:a]apad[a]",
                 "-map", "0:v:0", "-map", "[a]"] + vc + acodec + ["-t", "%.4f" % dur, "-movflags", "+faststart", out])
        else:
            if ext_out not in codecs:
                raise Fail("unsupported output format " + ext_out)
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", cur, "-vn"] + codecs[ext_out] + [out])
        after = probe(out)
        after.update(measure(out))
        if is_video:
            ov = probe(out)
            after["has_video"] = ov["has_video"]
        ok_dur = abs(after["duration"] - dur) <= 0.1
        if not ok_dur:
            warnings.append("Output length %.2f s differs from the expected %.2f s by more than 0.1 s" % (after["duration"], dur))
        return {"ok": True, "input": src, "output": out, "change_list": changes,
                "expected_duration": round(dur, 3), "actual_duration": after["duration"], "duration_ok": ok_dur,
                "cut_points_in_output_seconds": [round(c, 2) for c in cuts], "warnings": warnings,
                "before": before, "after": after}
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    try:
        with open(sys.argv[1]) as f:
            spec = json.load(f)
        print(json.dumps(main(spec), indent=1))
    except Fail as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=1))
        sys.exit(1)
    except Exception as e:  # noqa
        print(json.dumps({"ok": False, "error": "%s: %s" % (type(e).__name__, e)}, indent=1))
        sys.exit(1)
