#!/usr/bin/env python3
"""Build the printable floor poster (A3 portrait) for one language, with a QR code
to the training portal.

Usage:
    python3 poster.py --file poster-ar.json [--out-dir posters/] [--ecc Q]

poster-ar.json (all text already translated and checked; this script never
translates or rewrites anything):
    {"language": "Arabic", "code": "ar",
     "title": "<procedure name>", "subtitle": "<one line: who it is for / why>",
     "steps": [{"text": "<key step, short>", "critical": true}, ...],
     "critical_label": "<'Safety-critical' in this language>",
     "scan_label": "<'Scan to start your training' in this language>",
     "deadline_label": "<'Complete by 15 December 2026' in this language>",
     "portal_url": "https://...", "footer": "<owner, version, date>"}

Prints JSON: {"language", "html_file", "dir", "steps", "qr_version", "warnings"}.
The HTML prints straight to A3 from any browser (fonts load from Google Fonts), and
can be published as is. Right-to-left languages are laid out right to left.
Stdlib only; uses qr_code.py from the same folder.
"""

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qr_code  # noqa: E402

RTL = {"ar", "ur", "fa", "he", "ps", "sd", "ug", "yi", "ckb", "dv"}
FONTS = {
    "ar": "Noto+Sans+Arabic:wght@400;700;900", "fa": "Noto+Sans+Arabic:wght@400;700;900",
    "ps": "Noto+Sans+Arabic:wght@400;700;900", "sd": "Noto+Sans+Arabic:wght@400;700;900",
    "ur": "Noto+Nastaliq+Urdu:wght@400;700", "he": "Noto+Sans+Hebrew:wght@400;700;900",
    "hi": "Noto+Sans+Devanagari:wght@400;700;900", "mr": "Noto+Sans+Devanagari:wght@400;700;900",
    "ne": "Noto+Sans+Devanagari:wght@400;700;900", "bn": "Noto+Sans+Bengali:wght@400;700;900",
    "pa": "Noto+Sans+Gurmukhi:wght@400;700;900", "gu": "Noto+Sans+Gujarati:wght@400;700;900",
    "ta": "Noto+Sans+Tamil:wght@400;700;900", "te": "Noto+Sans+Telugu:wght@400;700;900",
    "ml": "Noto+Sans+Malayalam:wght@400;700;900", "th": "Noto+Sans+Thai:wght@400;700;900",
    "zh": "Noto+Sans+SC:wght@400;700;900", "ja": "Noto+Sans+JP:wght@400;700;900",
    "ko": "Noto+Sans+KR:wght@400;700;900", "am": "Noto+Sans+Ethiopic:wght@400;700;900",
}
FAMILY = lambda spec: spec.split(":")[0].replace("+", " ")
MAX_STEPS = 8
MAX_STEP_CHARS = 110

CSS = """
@page { size: A3 portrait; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #fff; }
body { font-family: %(font)s; color: #14110f; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.poster { width: 297mm; height: 420mm; padding: 18mm 18mm 14mm; display: flex; flex-direction: column; margin: 0 auto; }
header { border-bottom: 3mm solid #14110f; padding-bottom: 8mm; margin-bottom: 8mm; }
h1 { font-size: 30mm; line-height: 1.05; font-weight: 900; }
.sub { font-size: 9mm; margin-top: 4mm; color: #3d3833; }
ol { list-style: none; flex: 1; display: flex; flex-direction: column; gap: 5mm; }
li { display: flex; align-items: center; gap: 7mm; padding: 5mm 7mm; border: 1mm solid #14110f; border-radius: 4mm; font-size: 10mm; line-height: 1.25; font-weight: 700; }
li .n { flex: none; width: 18mm; height: 18mm; border-radius: 50%%; background: #14110f; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 10mm; font-weight: 900; }
li.critical { border: 2.2mm solid #b3261e; background: #fdeceb; }
li.critical .n { background: #b3261e; }
.tag { display: block; margin-top: 2mm; font-size: 6mm; font-weight: 900; color: #b3261e; letter-spacing: 0.02em; }
.tag::before { content: "\\26A0\\FE0E  "; }
footer { display: flex; align-items: center; gap: 10mm; border-top: 3mm solid #14110f; padding-top: 8mm; margin-top: 8mm; }
.qr { width: 75mm; height: 75mm; flex: none; }
.qr svg { width: 100%%; height: 100%%; display: block; }
.scan { font-size: 11mm; font-weight: 900; line-height: 1.15; }
.deadline { font-size: 8mm; margin-top: 4mm; }
.url { font-size: 4.5mm; margin-top: 4mm; color: #3d3833; direction: ltr; unicode-bidi: embed; word-break: break-all; }
.foot { font-size: 4.5mm; color: #57514b; margin-top: 4mm; }
html[lang="ur"] li, html[lang="ur"] .scan, html[lang="ur"] h1 { line-height: 1.7; }
@media screen { body { background: #e9e6e1; padding: 10mm 0; } .poster { background: #fff; box-shadow: 0 2mm 8mm rgba(0,0,0,.2); } }
"""


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    path = argv[argv.index("--file") + 1]
    out_dir = argv[argv.index("--out-dir") + 1] if "--out-dir" in argv else "."
    ecc = argv[argv.index("--ecc") + 1] if "--ecc" in argv else "Q"
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read %s: %s" % (path, exc)}))
        return 1

    warnings = []
    title = (data.get("title") or "").strip()
    url = (data.get("portal_url") or "").strip()
    steps = [s for s in data.get("steps") or [] if isinstance(s, dict) and str(s.get("text", "")).strip()]
    if not title or not steps or not url:
        print(json.dumps({"error": "title, steps and portal_url are all required"}))
        return 1
    if not re.match(r"^https?://", url):
        print(json.dumps({"error": "portal_url must start with https:// (the published portal link)"}))
        return 1
    if len(steps) > MAX_STEPS:
        warnings.append("%d steps: a floor poster reads best with %d or fewer" % (len(steps), MAX_STEPS))
    long_steps = [i + 1 for i, s in enumerate(steps) if len(s["text"]) > MAX_STEP_CHARS]
    if long_steps:
        warnings.append("Steps %s are long for a poster; shorten them (keep the meaning)" % long_steps)
    critical = any(s.get("critical") for s in steps)
    if critical and not data.get("critical_label"):
        warnings.append("No critical_label: safety-critical steps are marked in red but have no word label")
    if not data.get("scan_label"):
        warnings.append("No scan_label: the QR code has no caption")

    code = re.sub(r"[^a-z]", "", (data.get("code") or "").lower().split("-")[0])
    direction = "rtl" if code in RTL else "ltr"
    font_spec = FONTS.get(code)
    font_stack = ("'%s', " % FAMILY(font_spec) if font_spec else "") + "'Noto Sans', 'Segoe UI', Arial, sans-serif"
    fonts = "family=Noto+Sans:wght@400;700;900" + ("&family=" + font_spec if font_spec else "")

    try:
        mat, _ = qr_code.make_qr(url, ecc)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    qr_svg = qr_code.to_svg(mat)

    e = lambda v: html.escape(str(v or ""))
    items = []
    for i, s in enumerate(steps, 1):
        tag = '<div class="tag">%s</div>' % e(data.get("critical_label")) if s.get("critical") and data.get("critical_label") else ""
        items.append('<li class="%s"><span class="n">%d</span><div>%s%s</div></li>'
                     % ("critical" if s.get("critical") else "", i, e(s["text"]), tag))
    page = """<!doctype html>
<html lang="%(lang)s" dir="%(dir)s"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?%(fonts)s&display=swap" rel="stylesheet">
<style>%(css)s</style></head>
<body><main class="poster">
<header><h1>%(title)s</h1>%(sub)s</header>
<ol>%(items)s</ol>
<footer><div class="qr">%(qr)s</div><div>%(scan)s%(deadline)s<div class="url">%(url)s</div>%(foot)s</div></footer>
</main></body></html>
""" % {
        "lang": e(code or "en"), "dir": direction, "title": e(title), "fonts": fonts,
        "css": CSS % {"font": font_stack},
        "sub": '<p class="sub">%s</p>' % e(data["subtitle"]) if data.get("subtitle") else "",
        "items": "".join(items), "qr": qr_svg,
        "scan": '<div class="scan">%s</div>' % e(data["scan_label"]) if data.get("scan_label") else "",
        "deadline": '<div class="deadline">%s</div>' % e(data["deadline_label"]) if data.get("deadline_label") else "",
        "url": e(url),
        "foot": '<div class="foot">%s</div>' % e(data["footer"]) if data.get("footer") else "",
    }
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "poster-%s.html" % (code or "xx"))
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(json.dumps({"language": data.get("language", ""), "html_file": out, "dir": direction,
                      "steps": len(steps), "qr_version": mat.ver, "warnings": warnings}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
