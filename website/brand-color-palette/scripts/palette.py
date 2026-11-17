#!/usr/bin/env python3
"""Brand colour palette generator (standard library only).

Usage: python3 palette.py HEX [--name primary] [--out DIR]

Builds an 11-shade scale (50-950) from one hex, anchors the exact brand hex on the
nearest shade, maps light and dark semantic tokens, measures WCAG contrast for the
pairs that matter, and writes palette.css, palette.html and palette.json to DIR.
Prints a markdown report to stdout. Reads no files and uses no network.
"""
import argparse
import colorsys
import json
import os
import re
import sys

STEPS = [(50, 97, .80), (100, 94, .80), (200, 87, .85), (300, 75, .90), (400, 62, .95),
         (500, 48, 1.0), (600, 40, 1.0), (700, 33, 1.0), (800, 27, 1.0), (900, 20, 1.0), (950, 10, 1.0)]
KEYS = [k for k, _, _ in STEPS]
WHITE = "#FFFFFF"
RED = "#DC2626"


def parse_hex(s):
    s = s.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{3}", s):
        s = "".join(c * 2 for c in s)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s):
        sys.exit("Not a valid hex colour: %r (use #RRGGBB or #RGB)" % s)
    return "#" + s.upper()


def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def to_hex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v * 255))) for v in (r, g, b))


def hsl_of(h):
    hue, light, sat = colorsys.rgb_to_hls(*rgb(h))
    return hue * 360, sat * 100, light * 100


def from_hsl(h, s, l):
    return to_hex(*colorsys.hls_to_rgb(h / 360, l / 100, s / 100))


def lum(h):
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def build_scale(brand):
    hue, sat, light = hsl_of(brand)
    scale = {k: from_hsl(hue, sat * m, l) for k, l, m in STEPS}
    anchor = min(STEPS, key=lambda t: abs(t[1] - light))[0]
    scale[anchor] = brand
    return scale, anchor


def tokens(scale, anchor):
    def hx(v):
        return scale[v] if isinstance(v, int) else v

    def first(bgs, cands, mn):
        for c in cands:
            if all(ratio(hx(c), b) >= mn for b in bgs):
                return c
        return max(cands, key=lambda c: min(ratio(hx(c), b) for b in bgs))

    def best_fg(bg):
        return max([WHITE, 950], key=lambda c: ratio(hx(c), hx(bg)))

    darker = [k for k in KEYS if k >= anchor]
    light, dark = {}, {}
    # Light mode
    p = anchor if max(ratio(scale[anchor], WHITE), ratio(scale[anchor], scale[950])) >= 4.5 else first([WHITE], darker, 4.5)
    light.update({"background": WHITE, "foreground": 950, "card": WHITE, "card-foreground": 900,
                  "popover": WHITE, "popover-foreground": 950, "primary": p, "primary-foreground": best_fg(p),
                  "secondary": 100, "secondary-foreground": 900, "muted": 50,
                  "muted-foreground": first([scale[50], WHITE], [600, 700, 800, 900], 4.5),
                  "accent": 100, "accent-foreground": 900, "destructive": RED, "destructive-foreground": WHITE,
                  "border": 200, "input": first([WHITE], [300, 400, 500, 600, 700, 800], 3),
                  "ring": first([WHITE], darker, 3), "link": first([WHITE], darker, 4.5)})
    # Dark mode
    dp = first([scale[950]], [anchor, 500, 400, 300, 200], 4.5)
    dark.update({"background": 950, "foreground": 50, "card": 900, "card-foreground": 50,
                 "popover": 900, "popover-foreground": 50, "primary": dp, "primary-foreground": best_fg(dp),
                 "secondary": 800, "secondary-foreground": 50, "muted": 800,
                 "muted-foreground": first([scale[800], scale[950]], [400, 300, 200, 100], 4.5),
                 "accent": 800, "accent-foreground": 50, "destructive": RED, "destructive-foreground": WHITE,
                 "border": 800, "input": first([scale[950]], [700, 600, 500, 400, 300], 3),
                 "ring": dp, "link": dp})
    return light, dark, hx


PAIRS = [("Body text", "foreground", "background", 4.5), ("Card text", "card-foreground", "card", 4.5),
         ("Popover text", "popover-foreground", "popover", 4.5), ("Primary button text", "primary-foreground", "primary", 4.5),
         ("Secondary button text", "secondary-foreground", "secondary", 4.5), ("Muted text on muted", "muted-foreground", "muted", 4.5),
         ("Muted text on page", "muted-foreground", "background", 4.5), ("Accent text", "accent-foreground", "accent", 4.5),
         ("Destructive button text", "destructive-foreground", "destructive", 4.5), ("Links on page", "link", "background", 4.5),
         ("Input border vs page (UI)", "input", "background", 3), ("Focus ring vs page (UI)", "ring", "background", 3),
         ("Primary button vs page (UI)", "primary", "background", 3)]


def check(mode, hx):
    out = []
    for label, f, b, mn in PAIRS:
        r = ratio(hx(mode[f]), hx(mode[b]))
        lvl = ("AAA" if r >= 7 else "AA" if r >= 4.5 else "FAIL") if mn == 4.5 else ("PASS" if r >= 3 else "FAIL")
        out.append({"check": label, "fg": f, "bg": b, "fg_hex": hx(mode[f]), "bg_hex": hx(mode[b]),
                    "ratio": round(r, 2), "needs": mn, "result": lvl})
    out.append({"check": "Border vs page (decorative, no minimum)", "fg": "border", "bg": "background",
                "fg_hex": hx(mode["border"]), "bg_hex": hx(mode["background"]),
                "ratio": round(ratio(hx(mode["border"]), hx(mode["background"])), 2), "needs": 0, "result": "info"})
    return out


def css_val(v, name):
    return "var(--color-%s-%d)" % (name, v) if isinstance(v, int) else v


def make_css(scale, light, dark, name):
    L = ['@import "tailwindcss";', '', '/* Class-based dark mode: add class="dark" to <html> */',
         '@custom-variant dark (&:where(.dark, .dark *));', '', '@theme {', '  /* Shade scale */']
    L += ["  --color-%s-%d: %s;" % (name, k, scale[k]) for k in KEYS]
    L += ['', '  /* Light mode semantic tokens */']
    L += ["  --color-%s: %s;" % (t, css_val(v, name)) for t, v in light.items()]
    L += ['  --radius: 0.5rem;', '}', '', '/* Dark mode overrides */', '.dark {']
    L += ["  --color-%s: %s;" % (t, css_val(v, name)) for t, v in dark.items()]
    L += ['}', '']
    return "\n".join(L)


def text_on(h):
    return "#FFFFFF" if ratio(h, WHITE) >= ratio(h, "#000000") else "#000000"


def make_html(brand, scale, anchor, light, dark, hx, checks):
    sw = "".join('<div class="sw" style="background:%s;color:%s"><b>%d</b><span>%s</span>%s</div>' % (
        scale[k], text_on(scale[k]), k, scale[k], "<i>brand</i>" if k == anchor else "") for k in KEYS)

    def panel(cls, m):
        v = "".join("--%s:%s;" % (t, hx(x)) for t, x in m.items())
        return ('<div class="panel" style="%sbackground:var(--background);color:var(--foreground)">'
                '<h3>%s mode</h3><div class="card" style="background:var(--card);color:var(--card-foreground);'
                'border:1px solid var(--border)"><b>Card title</b><p style="color:var(--muted-foreground)">Muted caption text</p>'
                '<p><a style="color:var(--link)" href="#">A link</a></p>'
                '<button style="background:var(--primary);color:var(--primary-foreground)">Primary</button> '
                '<button style="background:var(--secondary);color:var(--secondary-foreground)">Secondary</button> '
                '<button style="background:var(--destructive);color:var(--destructive-foreground)">Delete</button><br><br>'
                '<input placeholder="Input" style="background:var(--background);color:var(--foreground);'
                'border:1px solid var(--input);padding:6px;border-radius:6px"></div></div>') % (v, cls.title())

    def table(cs):
        rows = "".join("<tr><td>%s</td><td><code>%s</code> on <code>%s</code></td><td>%s</td><td>%s</td></tr>" % (
            c["check"], c["fg_hex"], c["bg_hex"], c["ratio"], c["result"]) for c in cs)
        return "<table><tr><th>Check</th><th>Colours</th><th>Ratio</th><th>Result</th></tr>%s</table>" % rows

    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palette from %s</title><style>
body{font-family:system-ui,sans-serif;margin:0;padding:24px;background:#fafafa;color:#111}
h1{margin:0 0 4px}h2{margin-top:32px}.scale{display:grid;grid-template-columns:repeat(11,1fr);gap:0;border-radius:10px;overflow:hidden}
.sw{padding:28px 6px 10px;font-size:12px;display:flex;flex-direction:column;gap:2px}.sw b{font-size:14px}.sw i{font-style:normal;opacity:.8}
.modes{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{padding:18px;border-radius:12px;border:1px solid #ddd}
.card{padding:14px;border-radius:10px}button{border:0;padding:8px 14px;border-radius:6px;font-size:14px}
table{border-collapse:collapse;width:100%%;font-size:13px;background:#fff}td,th{border:1px solid #e3e3e3;padding:6px 8px;text-align:left}
@media(max-width:800px){.scale{grid-template-columns:repeat(4,1fr)}.modes{grid-template-columns:1fr}}
</style></head><body><h1>Palette from %s</h1><p>Exact brand colour sits on shade %d. Ratios are WCAG 2.x.</p>
<div class="scale">%s</div><h2>Light and dark previews</h2><div class="modes">%s%s</div>
<h2>Contrast, light mode</h2>%s<h2>Contrast, dark mode</h2>%s</body></html>""" % (
        brand, brand, anchor, sw, panel("light", light), panel("dark", dark), table(checks["light"]), table(checks["dark"]))


def md_report(brand, scale, anchor, light, dark, hx, checks, name):
    o = ["## Shade scale (brand %s sits on %d)" % (brand, anchor), "", "| Shade | Hex | White text | Black text |", "|---|---|---|---|"]
    o += ["| %d | %s | %.2f | %.2f |" % (k, scale[k], ratio(scale[k], WHITE), ratio(scale[k], "#000000")) for k in KEYS]
    o += ["", "## Semantic tokens", "", "| Token | Light | Dark |", "|---|---|---|"]

    def lab(v):
        return ("%s-%d (%s)" % (name, v, scale[v])) if isinstance(v, int) else v
    o += ["| %s | %s | %s |" % (t, lab(light[t]), lab(dark[t])) for t in light]
    for mode in ("light", "dark"):
        o += ["", "## Contrast, %s mode" % mode, "", "| Check | Colours | Ratio | Needs | Result |", "|---|---|---|---|---|"]
        o += ["| %s | %s on %s | %.2f | %s | %s |" % (c["check"], c["fg_hex"], c["bg_hex"], c["ratio"],
                                                    "-" if not c["needs"] else "%s:1" % c["needs"], c["result"]) for c in checks[mode]]
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hex")
    ap.add_argument("--name", default="primary")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    name = re.sub(r"[^a-z0-9-]", "", a.name.lower()) or "primary"
    brand = parse_hex(a.hex)
    scale, anchor = build_scale(brand)
    light, dark, hx = tokens(scale, anchor)
    checks = {"light": check(light, hx), "dark": check(dark, hx)}
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "palette.css"), "w") as f:
        f.write(make_css(scale, light, dark, name))
    with open(os.path.join(a.out, "palette.html"), "w") as f:
        f.write(make_html(brand, scale, anchor, light, dark, hx, checks))
    with open(os.path.join(a.out, "palette.json"), "w") as f:
        json.dump({"brand": brand, "anchor_shade": anchor, "scale": {str(k): v for k, v in scale.items()},
                   "light": {t: hx(v) for t, v in light.items()}, "dark": {t: hx(v) for t, v in dark.items()},
                   "checks": checks}, f, indent=1)
    print(md_report(brand, scale, anchor, light, dark, hx, checks, name))
    print("\nFiles written to %s: palette.css, palette.html, palette.json" % os.path.abspath(a.out))
    print("\n## CSS\n\n```css\n%s```" % make_css(scale, light, dark, name))


if __name__ == "__main__":
    main()
