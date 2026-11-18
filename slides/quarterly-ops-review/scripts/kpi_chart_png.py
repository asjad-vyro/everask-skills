#!/usr/bin/env python3
"""Draw one simple PNG bar chart per KPI for the review deck (last quarter vs this
quarter, with the target as a dashed line), in the template's colours.

Usage:
    python3 kpi_chart_png.py merged.json --out charts/ \
        [--colors "A5A5A5,1F4E79,ED7D31"] [--bg FFFFFF] [--ink 262626] [--data-url]

merged.json is the output of merge_kpis.py (it reads "kpis", "quarter",
"previous_quarter"). --colors: last quarter bar, this quarter bar, target line
(take them from the template's palette as import_pptx reports it). --bg / --ink:
background and text colour (match the slide background).

Prints a JSON list, one entry per KPI:
    {"name", "file", "data_url" (only with --data-url), "skipped": reason|null}
A KPI is skipped (no chart) when this quarter's value is missing: the slide must say
"missing" instead of showing a made-up bar.

Pass the data_url (or the file uploaded to a URL) to edit_pptx add_image.
Text is drawn with a built-in pixel font (capitals, digits, basic symbols), so the
chart needs no fonts or third-party packages. Stdlib only. No network.
"""

import base64
import json
import os
import re
import struct
import sys
import zlib

W, H = 1200, 720
SCALE = 4  # pixel-font scale: glyph cell = 6x8 -> 24x32 px

FONT = {  # 5x7 glyphs, '#' = ink
    " ": ["     "] * 7,
    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": ["  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "],
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": [" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "J": ["  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "#   #", "##  #", "# # #", "#  ##", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "# # #", " # # "],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    ".": ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "],
    ",": ["     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "],
    ":": ["     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "],
    "%": ["##   ", "##  #", "   # ", "  #  ", " #   ", "#  ##", "   ##"],
    "-": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    "+": ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
    "/": ["     ", "    #", "   # ", "  #  ", " #   ", "#    ", "     "],
    "(": ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
    ")": [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
    "$": ["  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "],
    "£": ["  ## ", " #  #", " #   ", "###  ", " #   ", " #   ", "#####"],
    "€": ["  ###", " #   ", "#### ", " #   ", "#### ", " #   ", "  ###"],
    "¥": ["#   #", " # # ", "#####", "  #  ", "#####", "  #  ", "  #  "],
    "₹": ["#####", "   # ", "#####", "   # ", "###  ", "  #  ", "   ##"],
    "&": [" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"],
    "'": ["  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "],
    "#": [" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "],
    "?": [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
}
CURRENCY = {"USD": "$", "GBP": "£", "EUR": "€", "JPY": "¥", "INR": "₹", "AUD": "A$",
            "CAD": "C$"}


def _rgb(hexstr, default):
    h = re.sub(r"[^0-9A-Fa-f]", "", hexstr or "")
    if len(h) != 6:
        h = default
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [bytearray(bytes(bg) * w) for _ in range(h)]

    def rect(self, x0, y0, x1, y1, color):
        x0, x1 = max(0, int(min(x0, x1))), min(self.w, int(max(x0, x1)))
        y0, y1 = max(0, int(min(y0, y1))), min(self.h, int(max(y0, y1)))
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            self.px[y][x0 * 3:x1 * 3] = row

    def text_width(self, text, scale=SCALE):
        return len(text) * 6 * scale - scale

    def text(self, x, y, text, color, scale=SCALE):
        for ch in text.upper():
            glyph = FONT.get(ch, FONT["?"])
            for gy, line in enumerate(glyph):
                for gx, cell in enumerate(line):
                    if cell == "#":
                        self.rect(x + gx * scale, y + gy * scale,
                                  x + (gx + 1) * scale, y + (gy + 1) * scale, color)
            x += 6 * scale

    def text_center(self, cx, y, text, color, scale=SCALE):
        self.text(int(cx - self.text_width(text, scale) / 2), y, text, color, scale)

    def png(self):
        raw = b"".join(b"\x00" + bytes(r) for r in self.px)
        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def _contrast(rgb):
    lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return (255, 255, 255) if lum < 150 else (38, 38, 38)


def label(value, unit):
    if value is None:
        return "MISSING"
    unit = (unit or "").strip()
    v = round(float(value), 2)
    text = "{:,.2f}".format(v).rstrip("0").rstrip(".") if v != int(v) else "{:,}".format(int(v))
    if unit == "%":
        return text + "%"
    if unit.upper() in CURRENCY:
        if v != int(v):
            text = "{:,.2f}".format(v)
        sign = "-" if text.startswith("-") else ""
        return sign + CURRENCY[unit.upper()] + text.lstrip("-")
    return text


def fit(text, max_chars):
    return text if len(text) <= max_chars else text[:max_chars - 1] + "."


def draw(kpi, prev_label, this_label, colors, bg, ink):
    c = Canvas(W, H, bg)
    grid = tuple((a * 3 + b) // 4 for a, b in zip(bg, ink))  # faint line colour
    unit = kpi.get("unit", "")
    last, this, target = kpi.get("last_quarter"), kpi.get("this_quarter"), kpi.get("target")
    values = [v for v in (last, this, target) if v is not None]
    top = max(values + [0.0])
    bottom = min(values + [0.0])
    span = (top - bottom) or 1.0
    top += span * 0.18
    if bottom < 0:
        bottom -= span * 0.12
    left, right, plot_top, plot_bottom = 90, W - 90, 170, H - 130

    def y_of(v):
        return plot_bottom - (v - bottom) / (top - bottom) * (plot_bottom - plot_top)

    zero_y = y_of(0.0)
    c.rect(left, zero_y - 2, right, zero_y + 2, grid)
    bars = [(prev_label, last, colors[0]), (this_label, this, colors[1])]
    slot = (right - left) / len(bars)
    bar_w = slot * 0.42
    for i, (name, v, col) in enumerate(bars):
        cx = left + slot * (i + 0.5)
        if v is None:
            c.text_center(cx, int(zero_y) - 60, "MISSING", ink)
        else:
            y = y_of(v)
            c.rect(cx - bar_w / 2, min(y, zero_y), cx + bar_w / 2, max(y, zero_y), col)
            text = label(v, unit)
            inside = abs(zero_y - y) > 80 and c.text_width(text, SCALE + 1) < bar_w - 16
            if inside:  # value inside the top of the bar, so it never hits the target line
                ly = int(y) + 18 if v >= 0 else int(y) - 58
                c.text_center(cx, ly, text, _contrast(col), SCALE + 1)
            else:
                ly = int(min(y, zero_y)) - 44 if v >= 0 else int(max(y, zero_y)) + 12
                c.text_center(cx, ly, text, ink, SCALE + 1)
        c.text_center(cx, plot_bottom + 30, fit(name, 16), ink)
    if target is not None:
        ty = int(y_of(target))
        x = left
        while x < right:  # dashed line
            c.rect(x, ty - 3, min(x + 28, right), ty + 3, colors[2])
            x += 44
        # legend under the title: dashed swatch + "TARGET <value>"
        c.rect(left, 112, left + 22, 118, colors[2])
        c.rect(left + 34, 112, left + 56, 118, colors[2])
        c.text(left + 72, 104, "TARGET " + label(target, unit), colors[2], SCALE - 1)
    c.text(left, 40, fit(kpi.get("name", ""), 34), ink, SCALE + 1)
    return c.png()


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "kpi"


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read %s: %s" % (argv[0], exc)}))
        return 1

    def opt(flag, default):
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) \
            else default

    out_dir = opt("--out", "charts")
    os.makedirs(out_dir, exist_ok=True)
    cols = [x for x in opt("--colors", "A5A5A5,1F4E79,ED7D31").split(",") if x.strip()]
    cols = (cols + ["A5A5A5", "1F4E79", "ED7D31"])[:3]
    colors = [_rgb(cols[0], "A5A5A5"), _rgb(cols[1], "1F4E79"), _rgb(cols[2], "ED7D31")]
    bg, ink = _rgb(opt("--bg", "FFFFFF"), "FFFFFF"), _rgb(opt("--ink", "262626"), "262626")
    prev_label = data.get("previous_quarter") or "Last quarter"
    this_label = data.get("quarter") or "This quarter"
    results = []
    for kpi in data.get("kpis") or []:
        name = kpi.get("name") or "KPI"
        if kpi.get("this_quarter") is None:
            results.append({"name": name, "file": None, "skipped": "This quarter is missing"})
            continue
        png = draw(kpi, prev_label, this_label, colors, bg, ink)
        path = os.path.join(out_dir, slug(name) + ".png")
        with open(path, "wb") as fh:
            fh.write(png)
        entry = {"name": name, "file": path, "skipped": None}
        if "--data-url" in argv:
            entry["data_url"] = "data:image/png;base64," + base64.b64encode(png).decode()
        results.append(entry)
    if not results:
        print(json.dumps({"error": "No \"kpis\" in %s (pass merge_kpis.py output)" % argv[0]}))
        return 1
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
