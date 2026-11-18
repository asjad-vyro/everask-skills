#!/usr/bin/env python3
"""Check an explainer script's length and turn it into subtitle files (WebVTT + SRT).

Usage:
    python3 subtitles.py --file script.json [--duration 184.5] [--out-dir subs/]

script.json:
    {"language": "Arabic", "code": "ar", "segments": ["First spoken sentence...", ...]}
    "segments" are the script's lines in speaking order (one paragraph or sentence
    each). A plain string under "text" also works.

--duration: the length in seconds of this language's voiceover or dubbed video.
    Without it, only the length check runs (no subtitle files).

Prints JSON:
    {"language", "words", "characters", "estimated_minutes", "length_note",
     "cues": n, "vtt_file", "srt_file", "warnings": [...]}

Cue timing is spread over the audio in proportion to each cue's length, so it is
close but not frame-exact; a fluent speaker checks it while watching. Cues are at
most 2 lines of 42 characters. Stdlib only.
"""

import json
import os
import re
import sys

MAX_LINE = 42
MIN_CUE = 1.2
# Speaking rates for the length estimate (words per minute). Scripts in Chinese,
# Japanese or Thai have no spaces, so they are estimated by characters instead.
WPM = 140
CPM_NO_SPACES = 300
TARGET_MINUTES = (2.5, 3.5)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?؟۔。！？।])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def wrap(text, width):
    words, lines, line = text.split(), [], ""
    if len(words) <= 1 and len(text) > width:
        return [text[i:i + width] for i in range(0, len(text), width)]
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    return lines


def make_cues(segments):
    cues = []
    for seg in segments:
        for sentence in split_sentences(seg):
            # Balance the lines: two lines of 30 read better than 42 + one word.
            n = -(-len(sentence) // MAX_LINE)
            lines = wrap(sentence, MAX_LINE)
            if len(lines) == n and n > 1:
                even = wrap(sentence, min(MAX_LINE, -(-len(sentence) // n) + 6))
                if len(even) == n:
                    lines = even
            for i in range(0, len(lines), 2):
                cues.append("\n".join(lines[i:i + 2]))
    return cues


def stamp(seconds, sep):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d%s%03d" % (h, m, s, sep, ms)


def time_cues(cues, duration):
    weights = [max(len(c.replace("\n", " ")), 1) for c in cues]
    total = float(sum(weights))
    spans = [max(duration * w / total, MIN_CUE) for w in weights]
    scale = duration / sum(spans) if sum(spans) > duration else 1.0
    t, out = 0.0, []
    for cue, span in zip(cues, spans):
        end = min(t + span * scale, duration)
        out.append((t, end, cue))
        t = end
    return out


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    path = argv[argv.index("--file") + 1]
    duration = float(argv[argv.index("--duration") + 1]) if "--duration" in argv else None
    out_dir = argv[argv.index("--out-dir") + 1] if "--out-dir" in argv else "."
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read %s: %s" % (path, exc)}))
        return 1
    segments = data.get("segments") or ([data["text"]] if data.get("text") else [])
    segments = [s for s in segments if isinstance(s, str) and s.strip()]
    language = data.get("language", "")
    code = re.sub(r"[^a-z0-9-]", "", (data.get("code") or language or "script").lower()) or "script"
    if not segments:
        print(json.dumps({"error": "The script has no text", "language": language}))
        return 1

    text = " ".join(segments)
    words = len(text.split())
    chars = len(re.sub(r"\s", "", text))
    spaced = words >= chars / 15.0  # spaced scripts average well under 15 chars/word
    minutes = words / float(WPM) if spaced else chars / float(CPM_NO_SPACES)
    warnings = []
    if minutes < TARGET_MINUTES[0]:
        note = "Short for a three-minute video"
    elif minutes > TARGET_MINUTES[1]:
        note = "Long for a three-minute video: cut before recording"
    else:
        note = "About right for three minutes"

    result = {"language": language, "words": words, "characters": chars,
              "estimated_minutes": round(minutes, 1), "length_note": note,
              "cues": 0, "vtt_file": "", "srt_file": "", "warnings": warnings}

    if duration is not None:
        if duration <= 0:
            print(json.dumps({"error": "--duration must be the audio length in seconds"}))
            return 1
        cues = make_cues(segments)
        timed = time_cues(cues, duration)
        fast = [c for s, e, c in timed if len(c.replace("\n", " ")) / max(e - s, 0.001) > 20]
        if fast:
            warnings.append("%d cue(s) need more than 20 characters a second to read; "
                            "the voiceover may be too fast" % len(fast))
        os.makedirs(out_dir, exist_ok=True)
        vtt = os.path.join(out_dir, "subtitles-%s.vtt" % code)
        srt = os.path.join(out_dir, "subtitles-%s.srt" % code)
        with open(vtt, "w", encoding="utf-8") as fh:
            fh.write("WEBVTT\n\n")
            for s, e, c in timed:
                fh.write("%s --> %s\n%s\n\n" % (stamp(s, "."), stamp(e, "."), c))
        with open(srt, "w", encoding="utf-8") as fh:
            for i, (s, e, c) in enumerate(timed, 1):
                fh.write("%d\n%s --> %s\n%s\n\n" % (i, stamp(s, ","), stamp(e, ","), c))
        result.update({"cues": len(timed), "vtt_file": vtt, "srt_file": srt})
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
