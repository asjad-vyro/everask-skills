#!/usr/bin/env python3
"""Apply an edit list to a video with ffmpeg and check the result.

Usage: python3 video_edit.py edit.json     (prints one JSON object)

edit.json, action "edit" (default):
{"input": "in.mp4", "output": "out.mp4",
 "ops": [{"op": "remove", "ranges": [{"start": "0:10", "end": "0:15"}]},
         {"op": "resize", "aspect": "9:16", "mode": "blur"}]}
Other actions: "probe" (also the default when there are no ops),
 "frame" {"input","at","output"}, "gif" {"input","start","end","width","fps","output"}.

Ops run in order; times refer to the video as it is after the previous op.
Ops: keep, remove, trim, speed, freeze, join, resize, scale, overlay_image, text, cover, pip,
     image_segment, mute, volume, replace_audio.
Values between 0 and 1 for positions and sizes are fractions of the frame, larger values are pixels.
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile

Fail = type("Fail", (Exception,), {})
CRF_FINAL, CRF_MID = 18, 16


def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise Fail("ffmpeg failed: " + p.stderr[-700:])
    return p


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
    v = next((s for s in j["streams"] if s["codec_type"] == "video" and
              s.get("disposition", {}).get("attached_pic", 0) == 0), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        raise Fail("no video stream in " + path)
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    if abs(rot) % 180 == 90:
        w, h = h, w

    def rate(x):
        try:
            n, d = x.split("/")
            return float(n) / float(d) if float(d) else 0.0
        except Exception:
            return 0.0
    fr = rate(v.get("avg_frame_rate", "0/1")) or rate(v.get("r_frame_rate", "0/1")) or 25.0
    if fr > 120 or fr < 1:
        fr = 25.0
    dur = float(j["format"].get("duration") or v.get("duration") or 0)
    return {"duration": round(dur, 3), "width": w, "height": h, "fps": round(fr, 3),
            "has_audio": a is not None, "video_codec": v["codec_name"],
            "size_bytes": int(j["format"].get("size", 0)),
            "bit_rate": int(j["format"]["bit_rate"]) if j["format"].get("bit_rate") else None}


def num(v, total):
    v = float(v)
    return v * total if 0 < v <= 1 else v


def even(x):
    return max(2, int(round(x / 2.0)) * 2)


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


def enable(o, dur):
    s = tparse(o["start"]) if o.get("start") is not None else None
    e = tparse(o["end"]) if o.get("end") is not None else None
    if s is None and e is None:
        return "", None, None
    s = s or 0.0
    if e is None or e > dur:
        e = dur
    return ":enable='between(t,%.3f,%.3f)'" % (s, e), s, e


def place(pos, w, h, ow, oh, margin):
    """x, y pixel positions of an overlay of size ow x oh."""
    if isinstance(pos, dict):
        return int(num(pos["x"], w)), int(num(pos["y"], h))
    m = int(margin)
    xs = {"left": m, "center": (w - ow) // 2, "right": w - ow - m}
    ys = {"top": m, "center": (h - oh) // 2, "bottom": h - oh - m}
    pos = pos or "top-right"
    if pos == "center":
        return xs["center"], ys["center"]
    v, hh = pos.split("-")
    return xs[hh], ys[v]


def find_font(text, bold=True, custom=None):
    if custom and os.path.isfile(custom):
        return custom
    names = []
    if any("؀" <= c <= "ۿ" for c in text):
        names = ["NotoNaskhArabic-Bold.ttf", "NotoSansArabic-Bold.ttf", "NotoNaskhArabic-Regular.ttf"]
    elif any(c >= "⺀" for c in text):
        names = ["NotoSansCJK-Bold.ttc", "NotoSansCJKsc-Bold.otf", "NotoSansCJK-Regular.ttc"]
    names += (["NotoSans-Bold.ttf", "NotoSans-Regular.ttf"] if bold else ["NotoSans-Regular.ttf"])
    names += ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf",
              "Arial Unicode.ttf", "Arial.ttf"]
    roots = ["/usr/share/fonts", "/usr/local/share/fonts", "/System/Library/Fonts/Supplemental",
             "/Library/Fonts", os.path.expanduser("~/.fonts")]
    for n in names:
        for r in roots:
            hits = glob.glob(os.path.join(r, "**", n), recursive=True)
            if hits:
                return hits[0]
    return None


def render_text_png(o, vw, vh, path, warnings):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise Fail("Pillow is not available, so text cannot be drawn")
    text = str(o["text"])
    size = max(10, int(num(o.get("size", 0.07), min(vw, vh))))
    fpath = find_font(text, o.get("bold", True), o.get("font"))
    if fpath:
        font = ImageFont.truetype(fpath, size)
    else:
        font = ImageFont.load_default(size)
        warnings.append("No Noto or DejaVu font found; used the default font, accented letters may be missing.")
    probe_img = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    maxw = int(vw * 0.9)
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if cur and probe_img.textlength(t, font=font) > maxw - 2 * size * 0.4:
                lines.append(cur)
                cur = word
            else:
                cur = t
        lines.append(cur)
    lh = int(size * 1.25)
    tw = max(int(probe_img.textlength(l, font=font)) for l in lines)
    pad = int(size * 0.4) if o.get("box", True) else int(size * 0.15)
    W, H = tw + 2 * pad, lh * len(lines) + 2 * pad - int(size * 0.2)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if o.get("box", True):
        bc = o.get("box_color", "#000000")
        alpha = int(255 * float(o.get("box_opacity", 0.55)))
        c = Image.new("RGBA", (1, 1), bc)
        r, g, b = c.getpixel((0, 0))[:3]
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(size * 0.25), fill=(r, g, b, alpha))
    for i, l in enumerate(lines):
        d.text((pad, pad - int(size * 0.1) + i * lh), l, font=font, fill=o.get("color", "#FFFFFF"),
               stroke_width=0 if o.get("box", True) else max(1, size // 14), stroke_fill="#000000")
    img.save(path)
    return W, H


class Edit:
    def __init__(self, spec):
        self.spec = spec
        self.src = spec["input"]
        if not os.path.isfile(self.src):
            raise Fail("input file not found: " + self.src)
        self.work = tempfile.mkdtemp(prefix="videdit-")
        self.n = 0
        self.warnings, self.changes, self.points = [], [], []
        self.expect_size = None

    def tmp(self, ext):
        self.n += 1
        return os.path.join(self.work, "s%d%s" % (self.n, ext))

    # one encode stage: reads cur (input 0) plus extra inputs, graph makes [v] and optionally [a]
    def stage(self, cur, graph, extra, has_audio_out, final, v_copy=False, ext=".mp4"):
        out = self.tmp(ext)
        crf = CRF_FINAL if final else CRF_MID
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", cur] + extra
        if v_copy:
            cmd += ["-filter_complex", graph, "-map", "0:v:0"]
            vcodec = ["-c:v", "copy"]
        else:
            graph = graph + ";[v]scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1[vv]"
            cmd += ["-filter_complex", graph, "-map", "[vv]"]
            vcodec = ["-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p",
                      "-fps_mode", "cfr", "-r", str(self.fps)]
        if has_audio_out:
            cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
        cmd += vcodec + ["-movflags", "+faststart", out]
        run(cmd)
        return out

    def segments(self, st, segs):
        """segs: list of dict start, end, speed, freeze. Returns graph, new duration, time map."""
        parts, labels, total, tmap = [], "", 0.0, []
        n = len(segs)
        for i, g in enumerate(segs):
            s, e, sp, fz = g["start"], g["end"], g.get("speed", 1.0), g.get("freeze", 0.0)
            v = "[0:v]trim=start=%.4f:end=%.4f,setpts=(PTS-STARTPTS)/%.6f" % (s, e, sp)
            if fz:
                v += ",tpad=stop_mode=clone:stop_duration=%.4f" % fz
            parts.append(v + "[v%d]" % i)
            sd = (e - s) / sp
            if st["has_audio"]:
                a = "[0:a]atrim=start=%.4f:end=%.4f,asetpts=PTS-STARTPTS" % (s, e)
                if sp != 1.0:
                    a += "," + atempo_chain(sp)
                if n > 1 and i > 0:
                    a += ",afade=t=in:st=0:d=0.015"
                if n > 1 and i < n - 1 and sd > 0.05:
                    a += ",afade=t=out:st=%.4f:d=0.015" % max(0, sd - 0.015)
                if fz:
                    a += ",apad=pad_dur=%.4f" % fz
                parts.append(a + "[a%d]" % i)
                labels += "[v%d][a%d]" % (i, i)
            else:
                labels += "[v%d]" % i
            tmap.append((s, e, sp, total, fz))
            total += sd + fz
        parts.append("%sconcat=n=%d:v=1:a=%d[v]%s" % (labels, n, 1 if st["has_audio"] else 0,
                                                       "[a]" if st["has_audio"] else ""))
        return ";".join(parts), total, tmap

    def map_points(self, tmap):
        new = []
        for t in self.points:
            for s, e, sp, off, fz in tmap:
                if s <= t < e:
                    new.append(off + (t - s) / sp)
                    break
        self.points = new

    def run(self):
        spec = self.spec
        ops = spec.get("ops") or []
        info = probe(self.src)
        self.fps = info["fps"]
        warn = []
        if info["duration"] > 600 or info["height"] >= 1080 or info["width"] >= 1920:
            warn.append("Long or high-resolution video: editing is slow. Offer 720p ({'scale': 720} op) if it times out.")
        if not ops:
            return {"ok": True, "mode": "probe", "input": self.src, "info": info, "warnings": warn}
        self.warnings += warn
        out = spec.get("output") or os.path.splitext(self.src)[0] + "-edited.mp4"
        ext = os.path.splitext(out)[1].lower()
        if ext not in (".mp4", ".mov", ".mkv", ".m4v"):
            self.warnings.append("Output container %s is not supported here; wrote .mp4 instead." % ext)
            out = os.path.splitext(out)[0] + ".mp4"
            ext = ".mp4"
        st = dict(info)
        cur = self.src
        expected = info["duration"]
        for idx, o in enumerate(ops):
            final = idx == len(ops) - 1
            op = o["op"]
            W, H, D = st["width"], st["height"], st["duration"]
            extra, v_copy, has_a = [], False, st["has_audio"]
            graph = None
            if op in ("keep", "remove", "trim", "speed", "freeze"):
                if op == "trim":
                    s = tparse(o.get("start", 0))
                    e = tparse(o["end"]) if "end" in o else (s + tparse(o["duration"]) if "duration" in o else D)
                    keep = [(s, min(e, D))]
                    self.changes.append("Trim to %s - %s" % (fmt(s), fmt(min(e, D))))
                elif op in ("keep", "remove"):
                    rng = sorted((tparse(r["start"]), min(tparse(r["end"]), D)) for r in o["ranges"])
                    for a, b in rng:
                        if b <= a:
                            raise Fail("range %s - %s is empty or reversed" % (fmt(a), fmt(b)))
                    if op == "keep":
                        keep = rng
                        self.changes.append("Keep only " + ", ".join("%s - %s" % (fmt(a), fmt(b)) for a, b in rng))
                    else:
                        keep, pos = [], 0.0
                        for a, b in rng:
                            if a - pos > 0.001:
                                keep.append((pos, a))
                            pos = max(pos, b)
                        if D - pos > 0.001:
                            keep.append((pos, D))
                        self.changes.append("Remove " + ", ".join("%s - %s" % (fmt(a), fmt(b)) for a, b in rng))
                    if not keep:
                        raise Fail("nothing would be left")
                segs = None
                if op in ("keep", "remove", "trim"):
                    segs = [{"start": a, "end": b} for a, b in keep]
                elif op == "speed":
                    f = float(o["factor"])
                    if not 0.25 <= f <= 8:
                        raise Fail("speed factor must be between 0.25 and 8")
                    if o.get("start") is None and o.get("end") is None:
                        segs = [{"start": 0.0, "end": D, "speed": f}]
                        self.changes.append("Speed x%g for the whole video" % f)
                    else:
                        s = tparse(o.get("start", 0))
                        e = min(tparse(o["end"]), D) if o.get("end") is not None else D
                        segs = [x for x in ({"start": 0.0, "end": s}, {"start": s, "end": e, "speed": f},
                                            {"start": e, "end": D}) if x["end"] - x["start"] > 0.001]
                        self.changes.append("Speed x%g from %s to %s" % (f, fmt(s), fmt(e)))
                else:  # freeze
                    at = tparse(o["at"])
                    fd = float(o["duration"])
                    segs = [x for x in ({"start": 0.0, "end": at, "freeze": fd}, {"start": at, "end": D})
                            if x["end"] - x["start"] > 0.001]
                    self.changes.append("Freeze the frame at %s for %g s" % (fmt(at), fd))
                if segs:
                    graph, newdur, tmap = self.segments(st, segs)
                    # edit points: the joins between kept pieces, in the new timeline
                    self.map_points(tmap)
                    acc = 0.0
                    for g in segs[:-1]:
                        acc += (g["end"] - g["start"]) / g.get("speed", 1.0) + g.get("freeze", 0.0)
                        self.points.append(acc)
                    if op == "freeze":
                        self.points.append(segs[0]["end"])
                    expected = newdur
            elif op == "join":
                files = o["files"] if "files" in o else [o["file"]]
                infos = [probe(f) for f in files]
                allp = [st] + infos
                any_a = any(p["has_audio"] for p in allp)
                extra = [x for f in files for x in ("-i", f)]
                parts, labels = [], ""
                for i, p in enumerate(allp):
                    parts.append("[%d:v]scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:black,"
                                 "setsar=1,fps=%s,format=yuv420p[v%d]" % (i, W, H, W, H, self.fps, i))
                    if any_a:
                        if p["has_audio"]:
                            parts.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo[a%d]" % (i, i))
                        else:
                            parts.append("anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=%.4f,"
                                         "asetpts=PTS-STARTPTS[a%d]" % (p["duration"], i))
                        labels += "[v%d][a%d]" % (i, i)
                    else:
                        labels += "[v%d]" % i
                parts.append("%sconcat=n=%d:v=1:a=%d[v]%s" % (labels, len(allp), 1 if any_a else 0, "[a]" if any_a else ""))
                graph = ";".join(parts)
                has_a = any_a
                self.points += [D + sum(p["duration"] for p in infos[:i]) for i in range(len(infos))]
                expected = D + sum(p["duration"] for p in infos)
                self.changes.append("Join %s after the video (all scaled to %dx%d, %g fps)" % (
                    ", ".join(os.path.basename(f) for f in files), W, H, self.fps))
                if any(not p["has_audio"] for p in allp) and any_a:
                    self.warnings.append("Some joined clips have no sound: silence was used for them.")
            elif op in ("resize", "scale"):
                if op == "scale":
                    if o.get("height"):
                        TH = even(float(o["height"]))
                        TW = even(W * TH / H)
                    else:
                        TW = even(float(o["width"]))
                        TH = even(H * TW / W)
                    graph = "[0:v]scale=%d:%d:flags=lanczos[v]" % (TW, TH)
                    self.changes.append("Scale to %dx%d" % (TW, TH))
                else:
                    if o.get("size"):
                        TW, TH = [int(x) for x in str(o["size"]).lower().split("x")]
                    else:
                        aw, ah = [float(x) for x in str(o["aspect"]).split(":")]
                        big = max(W, H) >= 1080
                        if aw >= ah:
                            TW = (1920 if big else 1280) if aw > ah else (1080 if big else 720)
                            TH = TW * ah / aw
                        else:
                            TH = (1920 if big else 1280) if ah / aw > 1.5 else (1350 if big else 900)
                            TW = TH * aw / ah
                            if ah / aw <= 1.5:
                                TW, TH = (1080, 1350) if big else (720, 900)
                    TW, TH = even(TW), even(TH)
                    mode = o.get("mode", "blur")
                    A = TW / TH
                    if mode == "crop":
                        cw, ch = (H * A, H) if W / H > A else (W, W / A)
                        cw, ch = even(cw), even(ch)
                        fx, fy = float(o.get("focus_x", 0.5)), float(o.get("focus_y", 0.5))
                        x = int(min(max(fx * W - cw / 2, 0), W - cw))
                        y = int(min(max(fy * H - ch / 2, 0), H - ch))
                        graph = "[0:v]crop=%d:%d:%d:%d,scale=%d:%d:flags=lanczos[v]" % (cw, ch, x, y, TW, TH)
                        self.warnings.append("Crop mode cuts away the parts of the picture outside the window.")
                    elif mode == "pad":
                        graph = ("[0:v]scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,"
                                 "pad=%d:%d:(ow-iw)/2:(oh-ih)/2:%s[v]" % (TW, TH, TW, TH, o.get("color", "black")))
                    else:
                        graph = ("[0:v]split[b][f];[b]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,"
                                 "boxblur=20:3[bb];[f]scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos[ff];"
                                 "[bb][ff]overlay=(W-w)/2:(H-h)/2[v]" % (TW, TH, TW, TH, TW, TH))
                    self.expect_size = (TW, TH)
                    self.changes.append("Resize to %dx%d (%s), mode %s, nothing stretched" % (TW, TH, o.get("aspect", ""), mode))
                    if max(TW, TH) > max(W, H) * 1.2:
                        self.warnings.append("The new frame is larger than the source, so the picture is upscaled and not sharper.")
            elif op in ("overlay_image", "text"):
                en, s, e = enable(o, D)
                if op == "text":
                    png = self.tmp(".png")
                    ow, oh = render_text_png(o, W, H, png, self.warnings)
                    extra = ["-i", png]
                    self.changes.append("Text %r %s" % (o["text"], "from %s to %s" % (fmt(s), fmt(e)) if s is not None else "for the whole video"))
                    if any(c >= "֐" and c <= "ۿ" for c in o["text"]):
                        self.warnings.append("Right-to-left text may not be shaped correctly: check the frame.")
                    scale = ""
                else:
                    if not os.path.isfile(o["file"]):
                        raise Fail("image not found: " + o["file"])
                    extra = ["-i", o["file"]]
                    iw = int(num(o.get("width", 0.15), W))
                    ip = probe_image(o["file"])
                    ow, oh = iw, even(iw * ip[1] / ip[0])
                    scale = "scale=%d:%d," % (ow, oh)
                    self.changes.append("Image %s %s" % (os.path.basename(o["file"]), "from %s to %s" % (fmt(s), fmt(e)) if s is not None else "for the whole video"))
                x, y = place(o.get("position"), W, H, ow, oh, num(o.get("margin", 0.03), W))
                op_ = float(o.get("opacity", 1))
                fl = "format=rgba," + scale + ("colorchannelmixer=aa=%.3f," % op_ if op_ < 1 else "")
                graph = "[1:v]%sformat=rgba[ov];[0:v][ov]overlay=%d:%d%s[v]" % (fl, x, y, en)
                if s is not None:
                    self.points += [s + 0.3, e - 0.1 if e - s > 0.5 else e]
                else:
                    self.points += [min(1.0, D / 2)]
            elif op == "cover":
                en, s, e = enable(o, D)
                x, y = int(num(o["x"], W)), int(num(o["y"], H))
                w_, h_ = int(num(o["w"], W)), int(num(o["h"], H))
                x, y = max(0, x), max(0, y)
                w_, h_ = min(w_, W - x), min(h_, H - y)
                mode = o.get("mode", "blur")
                if mode == "box":
                    graph = "[0:v]drawbox=x=%d:y=%d:w=%d:h=%d:color=%s:t=fill%s[v]" % (x, y, w_, h_, o.get("color", "black"), en)
                elif mode == "pixelate":
                    graph = ("[0:v]split[xa][xb];[xb]crop=%d:%d:%d:%d,scale=max(2\\,iw/12):max(2\\,ih/12),scale=%d:%d:flags=neighbor[p];"
                             "[xa][p]overlay=%d:%d%s[v]" % (w_, h_, x, y, w_, h_, x, y, en))
                else:
                    r = max(1, min(20, int(min(w_, h_) / 8)))
                    graph = ("[0:v]split[xa][xb];[xb]crop=%d:%d:%d:%d,boxblur=%d:3[p];[xa][p]overlay=%d:%d%s[v]"
                             % (w_, h_, x, y, r, x, y, en))
                self.changes.append("Cover the area x=%d y=%d %dx%d px with a %s%s" % (x, y, w_, h_, mode, " from %s to %s" % (fmt(s), fmt(e)) if s is not None else ""))
                self.warnings.append("This hides the area; it does not remove what was there, and burned-in branding cannot be truly removed.")
                self.points += [(s or 0) + 0.3]
            elif op == "pip":
                en, s, e = enable(o, D)
                s0 = s or 0.0
                pw = even(num(o.get("width", 0.3), W))
                b = int(o.get("border", 0))
                bpad = ",pad=iw+%d:ih+%d:%d:%d:white" % (2 * b, 2 * b, b, b) if b else ""
                if o.get("file"):
                    pi = probe(o["file"])
                    ph = even(pw * pi["height"] / pi["width"])
                    extra = ["-i", o["file"]]
                    pre = "[1:v]setpts=PTS-STARTPTS+%.3f/TB,scale=%d:%d%s[p];" % (s0, pw, ph, bpad)
                    if e is None or e > s0 + pi["duration"]:
                        en = ":enable='between(t,%.3f,%.3f)'" % (s0, min(D, s0 + pi["duration"]))
                    base = "[0:v]"
                    self.changes.append("Picture-in-picture of %s from %s" % (os.path.basename(o["file"]), fmt(s0)))
                else:
                    r = o["region"]
                    rx, ry = int(num(r["x"], W)), int(num(r["y"], H))
                    rw, rh = int(num(r["w"], W)), int(num(r["h"], H))
                    ph = even(pw * rh / rw)
                    pre = "[0:v]split[xa][xb];[xb]crop=%d:%d:%d:%d,scale=%d:%d%s[p];" % (rw, rh, rx, ry, pw, ph, bpad)
                    base = "[xa]"
                    self.changes.append("Picture-in-picture of the area x=%d y=%d %dx%d px of the video" % (rx, ry, rw, rh))
                x, y = place(o.get("position", "bottom-right"), W, H, pw + 2 * b, ph + 2 * b, num(o.get("margin", 0.03), W))
                graph = "%s%soverlay=%d:%d:eof_action=pass%s[v]" % (pre, base + "[p]", x, y, en)
                if o.get("file") and o.get("audio") == "mix":
                    pi = probe(o["file"])
                    if pi["has_audio"]:
                        delay = int(s0 * 1000)
                        if st["has_audio"]:
                            graph += (";[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay=%d|%d[pa];"
                                      "[0:a]aformat=channel_layouts=stereo[ma];[ma][pa]amix=inputs=2:duration=first:normalize=0[a]" % (delay, delay))
                        else:
                            graph += ";[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay=%d|%d,apad,atrim=0:%.3f[a]" % (delay, delay, D)
                        has_a = True
                elif o.get("file"):
                    self.warnings.append("The small clip's own sound was left out (say 'audio: mix' to include it).")
                if "[a]" not in graph and st["has_audio"]:
                    graph += ";[0:a]anull[a]"
                self.points += [s0 + 0.3]
            elif op == "image_segment":
                en, s, e = enable(o, D)
                if s is None:
                    raise Fail("image_segment needs start and end")
                extra = ["-i", o["file"]]
                graph = ("[1:v]scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:%s,setsar=1,format=rgba[im];"
                         "[0:v][im]overlay=0:0%s[v]" % (W, H, W, H, o.get("color", "black"), en))
                if o.get("mute") and st["has_audio"]:
                    graph += ";[0:a]volume=0:enable='between(t,%.3f,%.3f)'[a]" % (s, e)
                self.changes.append("Show %s from %s to %s%s" % (os.path.basename(o["file"]), fmt(s), fmt(e), " (sound muted)" if o.get("mute") else ""))
                self.points += [s + 0.3, e + 0.2 if e + 0.2 < D else e]
            elif op in ("mute", "volume", "replace_audio"):
                if not st["has_audio"] and op != "replace_audio":
                    raise Fail("the video has no audio track")
                v_copy = True
                graph = ""
                if op == "replace_audio":
                    if not os.path.isfile(o["file"]):
                        raise Fail("audio file not found: " + o["file"])
                    extra = (["-stream_loop", "-1"] if o.get("loop") else []) + ["-i", o["file"]]
                    g = 10 ** (float(o.get("gain_db", 0)) / 20.0)
                    graph = ("[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.4f,apad,atrim=0:%.4f,"
                             "afade=t=out:st=%.3f:d=%.3f[a]" % (g, D, max(0, D - 1.0), min(1.0, D / 2)))
                    has_a = True
                    self.changes.append("Replace the sound with %s" % os.path.basename(o["file"]))
                else:
                    en, s, e = enable(o, D)
                    gdb = -200.0 if op == "mute" else float(o["gain_db"])
                    g = 10 ** (gdb / 20.0)
                    if s is None:
                        a = "volume=%.6f" % g
                    else:
                        r = min(0.05, (e - s) / 2)
                        a = ("volume='1+(%.6f-1)*(min(1,max(0,(t-%.4f)/%.4f))-min(1,max(0,(t-%.4f)/%.4f)))':eval=frame"
                             % (g, s, r, e - r, r))
                        self.points += [s + 0.1]
                    graph = "[0:a]%s[a]" % a
                    self.changes.append("%s %s" % ("Mute" if op == "mute" else "Volume %+g dB" % gdb,
                                                   "from %s to %s" % (fmt(s), fmt(e)) if s is not None else "for the whole video"))
            else:
                raise Fail("unknown op: " + op)
            if graph is None:
                raise Fail("nothing to do for op " + op)
            has_out_a = "[a]" in graph
            if st["has_audio"] and not has_out_a:
                # untouched audio is passed through
                graph += ";[0:a]anull[a]"
                has_out_a = True
            cur = self.stage(cur, graph, extra, has_out_a, final, v_copy=v_copy, ext=ext)
            st = probe(cur)
            st["has_audio"] = has_out_a
        shutil.copyfile(cur, out)
        after = probe(out)
        ok = abs(after["duration"] - expected) <= 0.2
        res = {"ok": True, "input": self.src, "output": out, "change_list": self.changes,
               "before": info, "after": after,
               "expected_duration": round(expected, 3), "actual_duration": after["duration"], "duration_ok": ok,
               "size_ok": (self.expect_size is None or (after["width"], after["height"]) == tuple(self.expect_size)),
               "audio_present": after["has_audio"], "warnings": self.warnings}
        if not ok:
            res["warnings"].append("Output length differs from the expected %.2f s by more than 0.2 s" % expected)
        pts = sorted({round(min(max(p, 0.0), max(0.0, after["duration"] - 0.05)), 2) for p in self.points})[:8]
        if spec.get("check_frames", True) and pts:
            fd = os.path.splitext(out)[0] + "-frames"
            os.makedirs(fd, exist_ok=True)
            fr = []
            for i, t in enumerate(pts):
                fp = os.path.join(fd, "point%d_%.2fs.jpg" % (i + 1, t))
                run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % t, "-i", out, "-frames:v", "1",
                     "-vf", "scale=480:-2", "-q:v", "3", fp])
                fr.append(fp)
            res["edit_points_in_output_seconds"] = pts
            res["check_frames"] = fr
        return res


def probe_image(path):
    p = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path])
    w, h = p.stdout.strip().split(",")[:2]
    return int(w), int(h)


def action_frame(spec):
    out = spec.get("output") or os.path.splitext(spec["input"])[0] + "-frame.png"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % tparse(spec["at"]), "-i", spec["input"], "-frames:v", "1", out])
    return {"ok": True, "output": out, "size_bytes": os.path.getsize(out)}


def action_gif(spec):
    out = spec.get("output") or os.path.splitext(spec["input"])[0] + ".gif"
    s = tparse(spec.get("start", 0))
    e = tparse(spec["end"])
    wd, fps = int(spec.get("width", 480)), int(spec.get("fps", 12))
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % s, "-t", "%.3f" % (e - s), "-i", spec["input"],
         "-vf", "fps=%d,scale=%d:-2:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" % (fps, wd), "-loop", "0", out])
    size = os.path.getsize(out)
    res = {"ok": True, "output": out, "size_bytes": size, "duration": round(e - s, 2), "warnings": []}
    if size > 10 * 1024 * 1024:
        res["warnings"].append("The GIF is over 10 MB: lower width or fps.")
    return res


if __name__ == "__main__":
    ed = None
    try:
        spec = json.load(open(sys.argv[1]))
        act = spec.get("action", "edit")
        if act == "frame":
            r = action_frame(spec)
        elif act == "gif":
            r = action_gif(spec)
        else:
            ed = Edit(spec)
            r = ed.run()
        print(json.dumps(r, indent=1))
    except Fail as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=1))
        sys.exit(1)
    except Exception as e:  # noqa
        print(json.dumps({"ok": False, "error": "%s: %s" % (type(e).__name__, e)}, indent=1))
        sys.exit(1)
    finally:
        if ed:
            shutil.rmtree(ed.work, ignore_errors=True)
