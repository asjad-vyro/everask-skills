#!/usr/bin/env python3
"""Build a rough-cut list from a timestamped transcript: cut long pauses, filler-only
lines and retakes (keeping the last take), and remap captions to the cut.

Usage:
    python3 cut_list.py --file transcript.json [--duration 612.4] [--max-pause 0.8]
                        [--keep-pause 0.35] [--fps 30] [--srt captions.srt]

transcript.json: the `audio_transcribe` result (with timestamps on), or just its
segment list. Accepted segment shapes:
    {"text": "...", "timestamp": [start, end]}         (Whisper chunks)
    {"text": "...", "start": s, "end": e}
    either one optionally with "words": [{"word"|"text", "start", "end"}, ...]
--duration: length of the recording in seconds (fills a missing last end time).

Prints one JSON object:
    {"source_seconds", "cut_seconds", "result_seconds",
     "cuts": [{"start", "end", "reason", "text"}],
     "keep": [{"start", "end"}],                      (source seconds)
     "clips": [{"from", "durationInFrames", "sourceInFrames"}],   (editor frames)
     "captions": [{"start", "end", "text"}],          (on the cut timeline)
     "fillers_left_in": n, "notes": [...]}
Fillers inside a sentence are cut only when word timings exist; otherwise they are
counted in "fillers_left_in" and left for the user to trim by hand. Nothing is
guessed. Stdlib only. Writes only the --srt file when asked.
"""

import difflib
import json
import re
import sys

FILLERS = {"um", "uh", "umm", "uhh", "erm", "er", "ah", "hmm", "mm", "like", "you know",
           "i mean", "so yeah", "yeah so", "okay so", "basically", "actually"}
HARD_FILLERS = {"um", "uh", "umm", "uhh", "erm", "er", "ah", "hmm", "mm"}
# words that only count as filler when a whole line is made of them ("Uh, so, basically.")
LINE_FILLERS = FILLERS | {"so", "okay", "ok", "right", "yeah", "well", "anyway", "and"}
WORD = re.compile(r"[a-z']+")


def norm(text):
    return " ".join(WORD.findall((text or "").lower()))


def load_segments(data, duration):
    if isinstance(data, dict):
        data = data.get("segments") or data.get("chunks") or []
    segs = []
    for i, s in enumerate(data):
        if "timestamp" in s:
            start, end = (list(s["timestamp"]) + [None, None])[:2]
        else:
            start, end = s.get("start"), s.get("end")
        if end is None:
            nxt = data[i + 1] if i + 1 < len(data) else None
            if nxt is not None:
                end = nxt.get("start", (nxt.get("timestamp") or [None])[0])
            elif duration:
                end = duration
        if start is None or end is None or end <= start:
            continue
        segs.append({"start": float(start), "end": float(end), "text": (s.get("text") or "").strip(),
                     "words": s.get("words") or []})
    segs.sort(key=lambda x: x["start"])
    return segs


def is_filler_only(text):
    t = norm(text)
    if not t:
        return True
    rest = t
    for f in sorted(LINE_FILLERS, key=len, reverse=True):
        rest = re.sub(r"\b" + re.escape(f) + r"\b", " ", rest)
    return not rest.strip()


def is_retake(a, b):
    """True when line a looks like a false start that line b says again."""
    na, nb = norm(a), norm(b)
    if len(na.split()) < 3:
        return False
    head = " ".join(na.split()[:4])
    if nb.startswith(head):
        return True
    ratio = difflib.SequenceMatcher(None, na, nb[:len(na) + 10]).ratio()
    return ratio >= 0.75


def merge(ranges):
    out = []
    for s, e in sorted(ranges):
        if out and s <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    opt = lambda k, d: float(argv[argv.index(k) + 1]) if k in argv else d
    duration = opt("--duration", 0.0)
    max_pause, keep_pause, fps = opt("--max-pause", 0.8), opt("--keep-pause", 0.35), int(opt("--fps", 30))
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            segs = load_segments(json.load(fh), duration)
    except (OSError, ValueError, IndexError) as exc:
        print(json.dumps({"error": f"Could not read the input file: {exc}"}))
        return 1
    if not segs:
        print(json.dumps({"error": "No timestamped segments. Run audio_transcribe with timestamps: true."}))
        return 1
    total = duration or segs[-1]["end"]
    cuts, notes, fillers_left = [], [], 0

    kept_segs = []
    for i, s in enumerate(segs):
        if is_filler_only(s["text"]):
            cuts.append((s["start"], s["end"], "filler", s["text"]))
            continue
        later = [n for n in segs[i + 1:i + 3] if not is_filler_only(n["text"])]
        if later and is_retake(s["text"], later[0]["text"]):
            cuts.append((s["start"], s["end"], "retake", s["text"]))
            continue
        kept_segs.append(s)
        timed = [w for w in s["words"] if w.get("start") is not None and w.get("end") is not None]
        for w in timed:
            if norm(w.get("word") or w.get("text")) in HARD_FILLERS:
                cuts.append((float(w["start"]), float(w["end"]), "filler", w.get("word") or w.get("text")))
        if not timed:
            fillers_left += sum(1 for t in norm(s["text"]).split() if t in HARD_FILLERS)

    # Between two kept lines, close the gap down to keep_pause when it is too long or
    # when a cut line sat in it, so no slivers of silence are left behind.
    for a, b in zip(kept_segs, kept_segs[1:]):
        gap = b["start"] - a["end"]
        had_cut = any(a["end"] <= c[0] < b["start"] for c in cuts)
        if (gap > max_pause or had_cut) and gap > keep_pause:
            cuts.append((a["end"] + keep_pause / 2, b["start"] - keep_pause / 2, "pause",
                         f"{gap:.1f}s gap"))
    if not kept_segs:
        print(json.dumps({"error": "Every line looks like filler or a retake; nothing to keep."}))
        return 1
    # leading and trailing silence (and any filler or retake there)
    first, last = kept_segs[0], kept_segs[-1]
    if first["start"] > keep_pause:
        cuts.append((0.0, first["start"] - keep_pause / 2, "silence", ""))
    if total - last["end"] > keep_pause:
        cuts.append((last["end"] + keep_pause / 2, total, "silence", ""))

    removed = merge([(c[0], c[1]) for c in cuts if c[1] > c[0]])
    keep, cursor = [], 0.0
    for s, e in removed:
        if s > cursor:
            keep.append([cursor, s])
        cursor = max(cursor, e)
    if cursor < total:
        keep.append([cursor, total])
    keep = [k for k in keep if k[1] - k[0] >= 1.0 / fps]

    clips, pos = [], 0
    for s, e in keep:
        dur = max(1, round((e - s) * fps))
        clips.append({"from": pos, "durationInFrames": dur, "sourceInFrames": round(s * fps)})
        pos += dur

    def remap(t):
        out = 0.0
        for s, e in keep:
            if t >= e:
                out += e - s
            elif t > s:
                return out + (t - s)
            else:
                return out
        return out

    cut_reasons = {(c[0], c[1]) for c in cuts if c[2] in ("filler", "retake")}
    captions = []
    for s in segs:
        if any(abs(s["start"] - a) < 1e-6 and abs(s["end"] - b) < 1e-6 for a, b in cut_reasons):
            continue
        a, b = remap(s["start"]), remap(s["end"])
        if b - a > 0.2:
            captions.append({"start": round(a, 2), "end": round(b, 2), "text": s["text"]})

    if fillers_left:
        notes.append(f"{fillers_left} um/uh inside sentences left in: the transcript has no word timings.")
    if any(c[2] == "retake" for c in cuts):
        notes.append("Retakes: the earlier take was cut and the last one kept. Check each in the editor.")

    result = round(sum(e - s for s, e in keep), 2)
    out = {"source_seconds": round(total, 2), "cut_seconds": round(total - result, 2),
           "result_seconds": result,
           "cuts": [{"start": round(c[0], 2), "end": round(c[1], 2), "reason": c[2], "text": c[3]}
                    for c in sorted(cuts) if c[1] > c[0]],
           "keep": [{"start": round(s, 2), "end": round(e, 2)} for s, e in keep],
           "clips": clips, "captions": captions, "fillers_left_in": fillers_left, "notes": notes}

    if "--srt" in argv:
        def ts(x):
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
        with open(argv[argv.index("--srt") + 1], "w", encoding="utf-8") as fh:
            for i, c in enumerate(captions, 1):
                fh.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")
        out["srt"] = argv[argv.index("--srt") + 1]
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
