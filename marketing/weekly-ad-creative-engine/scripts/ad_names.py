#!/usr/bin/env python3
"""Name each new ad by the convention date_angle_hook_format_v1 and list the sizes it needs.

Usage:
    python3 ad_names.py --file ads.json [--date 2026-11-16] [--existing names.txt]

ads.json: [{"angle": "No more sticky hands", "hook": "POV unboxing",
            "format": "ugc", "platforms": ["meta", "tiktok", "google"]}, ...]
    format: static | ugc | product_video (also "product video", "video", "image")
    platforms: any of meta, tiktok, google (default: all three)
--date: the week's date (default today), written as YYYYMMDD.
--existing: optional text file of names already used (one per line, e.g. last
    week's ads); a name that is taken gets the next version (v2, v3, ...).

Prints a JSON list, one per ad, in input order:
    {"name", "angle", "hook", "format", "platforms",
     "sizes": [{"platform", "ratio", "width", "height", "file"}], "note"}
Each "file" is the name plus the ratio, e.g. 20261116_no-more-sticky-hands_pov-unboxing_ugc_v1_9x16.
Sizes: TikTok 9:16; Meta 9:16 (Stories/Reels), 4:5 and 1:1 (Feed); Google 1:1, 4:5,
9:16, plus 1.91:1 landscape for statics (most Google image placements require it).

Stdlib only. No network.
"""

import datetime
import json
import re
import sys
import unicodedata

FORMATS = {
    "static": "static", "image": "static", "still": "static",
    "ugc": "ugc", "ugc_video": "ugc", "ugc-style": "ugc",
    "product_video": "product", "product video": "product", "product": "product",
    "video": "product",
}
SIZES = {
    ("tiktok", "video"): [("9:16", 1080, 1920)],
    ("tiktok", "static"): [("9:16", 1080, 1920)],
    ("meta", "video"): [("9:16", 1080, 1920), ("4:5", 1080, 1350), ("1:1", 1080, 1080)],
    ("meta", "static"): [("9:16", 1080, 1920), ("4:5", 1080, 1350), ("1:1", 1080, 1080)],
    ("google", "video"): [("9:16", 1080, 1920), ("1:1", 1080, 1080), ("4:5", 1080, 1350)],
    ("google", "static"): [("1.91:1", 1200, 628), ("1:1", 1200, 1200), ("4:5", 960, 1200),
                           ("9:16", 1080, 1920)],
}
PLATFORMS = ("meta", "tiktok", "google")


def slug(text, limit=28):
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(text) > limit:
        text = text[:limit].rsplit("-", 1)[0] or text[:limit]
    return text


def main(argv):
    opts = {"--file": None, "--date": None, "--existing": None}
    i = 0
    while i < len(argv):
        if argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            print(f"Unknown or incomplete argument: {argv[i]}\n\n{__doc__}", file=sys.stderr)
            return 2
    if not opts["--file"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        day = (datetime.date.fromisoformat(opts["--date"]) if opts["--date"]
               else datetime.date.today())
    except ValueError:
        print(json.dumps({"error": f"--date must be YYYY-MM-DD, got {opts['--date']}"}))
        return 1
    try:
        with open(opts["--file"], encoding="utf-8") as fh:
            ads = json.load(fh)
        taken = set()
        if opts["--existing"]:
            with open(opts["--existing"], encoding="utf-8") as fh:
                taken = {line.strip() for line in fh if line.strip()}
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read input: {exc}"}))
        return 1
    if not isinstance(ads, list):
        print(json.dumps({"error": "ads.json must be a JSON list"}))
        return 1

    out = []
    for ad in ads:
        notes = []
        fmt_raw = str(ad.get("format", "")).strip().lower()
        fmt = FORMATS.get(fmt_raw)
        if not fmt:
            notes.append(f"unknown format '{fmt_raw}', treated as static")
            fmt = "static"
        angle, hook = slug(ad.get("angle")), slug(ad.get("hook"))
        if not angle:
            angle = "angle"
            notes.append("no angle given")
        if not hook:
            hook = "hook"
            notes.append("no hook given")
        base = f"{day:%Y%m%d}_{angle}_{hook}_{fmt}"
        version = 1
        while f"{base}_v{version}" in taken:
            version += 1
        name = f"{base}_v{version}"
        taken.add(name)

        platforms = [str(p).strip().lower() for p in (ad.get("platforms") or PLATFORMS)]
        platforms = [p for p in platforms if p in PLATFORMS] or list(PLATFORMS)
        kind = "static" if fmt == "static" else "video"
        sizes = []
        for p in platforms:
            for ratio, w, h in SIZES[(p, kind)]:
                sizes.append({"platform": p, "ratio": ratio, "width": w, "height": h,
                              "file": f"{name}_{ratio.replace(':', 'x').replace('.', '')}"})
        out.append({"name": name, "angle": ad.get("angle", ""), "hook": ad.get("hook", ""),
                    "format": fmt, "platforms": platforms, "sizes": sizes,
                    "note": "; ".join(notes)})
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
