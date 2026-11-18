#!/usr/bin/env python3
"""Turn a video ad's script or transcript into subtitles: an .srt file and caption timings.

Usage:
    python3 make_subtitles.py --file scripts.json --out subtitles/

scripts.json: a list, one per video:
    {"name": "20261116_..._ugc_v1", "duration_seconds": 15,
     "script": "Spoken words of the ad ..."}
  or, better, with real timings from a transcript (e.g. from transcribing the clip):
    {"name": "...", "segments": [{"start": 0.0, "end": 2.4, "text": "..."}, ...]}

With only a script, captions are spread over duration_seconds in proportion to
their word count (or at 2.5 words a second when no duration is given). With
segments, their own timings are kept and long segments are split.
Captions are at most 6 words / 32 characters each, sized for a phone screen.

Writes <out>/<name>.srt for each video and prints a JSON list:
    {"name", "srt", "captions": [{"start", "end", "text", "from_frame",
     "duration_frames"}], "note"}
Frames are at 30 fps, for caption clips in the video editor.

Stdlib only. Writes only into --out.
"""

import json
import os
import re
import sys

MAX_WORDS = 6
MAX_CHARS = 32
WORDS_PER_SECOND = 2.5
FPS = 30


def chunk(text):
    words = text.split()
    out, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and (len(cur) >= MAX_WORDS or len(trial) > MAX_CHARS):
            out.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
        if re.search(r"[.!?]$", w):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def from_script(script, duration):
    pieces = chunk(re.sub(r"\s+", " ", script).strip())
    counts = [len(p.split()) for p in pieces]
    total = sum(counts)
    if not total:
        return []
    span = float(duration) if duration else total / WORDS_PER_SECOND
    caps, t = [], 0.0
    for p, n in zip(pieces, counts):
        d = span * n / total
        caps.append((t, t + d, p))
        t += d
    return caps


def from_segments(segments):
    caps = []
    for s in segments:
        start, end = float(s["start"]), float(s["end"])
        pieces = chunk(str(s.get("text", "")).strip())
        counts = [len(p.split()) for p in pieces]
        total = sum(counts)
        t = start
        for p, n in zip(pieces, counts):
            d = (end - start) * n / total
            caps.append((t, t + d, p))
            t += d
    return caps


def stamp(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "video"


def main(argv):
    opts = {"--file": None, "--out": None}
    i = 0
    while i < len(argv):
        if argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            print(f"Unknown or incomplete argument: {argv[i]}\n\n{__doc__}", file=sys.stderr)
            return 2
    if not opts["--file"] or not opts["--out"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(opts["--file"], encoding="utf-8") as fh:
            videos = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read {opts['--file']}: {exc}"}))
        return 1
    if not isinstance(videos, list):
        print(json.dumps({"error": "scripts.json must be a JSON list"}))
        return 1
    os.makedirs(opts["--out"], exist_ok=True)
    results = []
    for v in videos:
        name = safe_name(str(v.get("name", "video")))
        note = ""
        try:
            if v.get("segments"):
                caps = from_segments(v["segments"])
            else:
                caps = from_script(str(v.get("script", "")), v.get("duration_seconds"))
                if not v.get("duration_seconds"):
                    note = "no duration given; timed at 2.5 words a second"
        except (KeyError, TypeError, ValueError) as exc:
            results.append({"name": name, "srt": "", "captions": [],
                            "note": f"bad segments: {exc}"})
            continue
        if not caps:
            results.append({"name": name, "srt": "", "captions": [], "note": "no words to caption"})
            continue
        path = os.path.join(opts["--out"], name + ".srt")
        with open(path, "w", encoding="utf-8") as fh:
            for n, (a, b, text) in enumerate(caps, 1):
                fh.write(f"{n}\n{stamp(a)} --> {stamp(b)}\n{text}\n\n")
        results.append({
            "name": name, "srt": path, "note": note,
            "captions": [{"start": round(a, 2), "end": round(b, 2), "text": t,
                          "from_frame": int(round(a * FPS)),
                          "duration_frames": max(1, int(round(b * FPS)) - int(round(a * FPS)))}
                         for a, b, t in caps],
        })
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
