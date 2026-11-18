#!/usr/bin/env python3
"""Stamp a visible "VIRTUALLY STAGED" label on staged photos (keeps the input file).

Usage:
    python3 label_staged.py --in living_staged.jpg [--out living_staged_labelled.jpg]
    python3 label_staged.py --file staged.json
        staged.json: [{"in": "living_staged.jpg", "out": "living_labelled.jpg"}, ...]
Options: --text "VIRTUALLY STAGED" (letters A-Z, digits, space, - . : only)
         --corner bl|br|tl|tr (default bl)

Draws white capital letters on a dark band in a corner, sized to the photo (label
height about 5% of the image height, never smaller than 18 px). The letters come from a
built-in bitmap font, so it needs no font files; the image work is done by ffmpeg.
When --out is missing, writes <name>_labelled.<ext> next to the input.

Prints a JSON list: {"in", "out", "width", "height", "label", "ok", "error"}.
Exit code 1 if any photo failed. Needs ffmpeg and ffprobe on PATH. Stdlib only.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

FONT = {  # 5x7, rows top to bottom, '#' = ink
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
}


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "json", path],
        capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError("ffprobe could not read the image: " + out.stderr.strip()[:200])
    st = json.loads(out.stdout)["streams"][0]
    return int(st["width"]), int(st["height"])


def render_label(text, scale):
    """Return (width, height, bytes) of an RGB PPM: white letters on a near-black band."""
    pad = 2  # in font cells
    cols = len(text) * 6 - 1 + 2 * pad
    rows = 7 + 2 * pad
    grid = [[False] * cols for _ in range(rows)]
    for i, ch in enumerate(text):
        glyph = FONT[ch]
        for r, line in enumerate(glyph):
            for c, px in enumerate(line):
                if px == "#":
                    grid[pad + r][pad + i * 6 + c] = True
    w, h = cols * scale, rows * scale
    ink, band = b"\xff\xff\xff", b"\x1a\x1a\x1a"
    body = bytearray()
    for r in range(rows):
        line = b"".join((ink if grid[r][c] else band) * scale for c in range(cols))
        body += line * scale
    return w, h, b"P6\n%d %d\n255\n" % (w, h) + bytes(body)


def label_one(src, dst, text, corner):
    w, h = probe(src)
    target = max(18, int(h * 0.05))
    scale = max(2, target // 11)
    # keep the label within 90% of the photo width
    while scale > 1 and (len(text) * 6 + 3) * scale > w * 0.9:
        scale -= 1
    lw, lh, ppm = render_label(text, scale)
    margin = max(8, int(min(w, h) * 0.025))
    x = margin if corner in ("bl", "tl") else "W-w-%d" % margin
    y = margin if corner in ("tl", "tr") else "H-h-%d" % margin
    with tempfile.TemporaryDirectory(prefix="llk_label_") as tmp:
        lab = os.path.join(tmp, "label.ppm")
        with open(lab, "wb") as fh:
            fh.write(ppm)
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-i", lab, "-filter_complex",
               "[0:v][1:v]overlay=x=%s:y=%s" % (x, y), "-frames:v", "1", "-update", "1"]
        if dst.lower().endswith((".jpg", ".jpeg")):
            cmd += ["-q:v", "2"]
        cmd.append(dst)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0 or not os.path.exists(dst):
            first = (res.stderr.strip().splitlines() or ["unknown error"])[0]
            raise RuntimeError("Not a readable image, or the output could not be written "
                               "(ffmpeg: %s)" % first[:160])
    return w, h


def default_out(src):
    base, ext = os.path.splitext(src)
    return base + "_labelled" + (ext or ".jpg")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="src")
    ap.add_argument("--out")
    ap.add_argument("--file")
    ap.add_argument("--text", default="VIRTUALLY STAGED")
    ap.add_argument("--corner", default="bl", choices=["bl", "br", "tl", "tr"])
    a = ap.parse_args()

    text = a.text.upper()
    bad = sorted({c for c in text if c not in FONT})
    if bad or not text.strip():
        print(json.dumps({"error": "Label text can only use A-Z, 0-9, space, - . : "
                                   "(not: %s)" % "".join(bad)}))
        return 2
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(json.dumps({"error": "ffmpeg/ffprobe not found; cannot label photos here."}))
        return 1

    if a.file:
        with open(a.file, encoding="utf-8") as fh:
            jobs = [(j.get("in", ""), j.get("out") or default_out(j.get("in", ""))) for j in json.load(fh)]
    elif a.src:
        jobs = [(a.src, a.out or default_out(a.src))]
    else:
        print(json.dumps({"error": "Give --in <photo> or --file <list.json>."}))
        return 2

    results, failed = [], False
    for src, dst in jobs:
        item = {"in": src, "out": dst, "width": None, "height": None, "label": text,
                "ok": False, "error": ""}
        try:
            if not src or not os.path.isfile(src):
                raise RuntimeError("Input file not found")
            if os.path.abspath(src) == os.path.abspath(dst):
                raise RuntimeError("--out must differ from the input; the original is kept")
            item["width"], item["height"] = label_one(src, dst, text, a.corner)
            item["ok"] = True
        except Exception as exc:
            item["error"] = str(exc)
            failed = True
        results.append(item)
    print(json.dumps(results, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
