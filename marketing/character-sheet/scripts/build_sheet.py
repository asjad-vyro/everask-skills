#!/usr/bin/env python3
"""Assemble a character reference sheet (PNG, optionally PDF) with Pillow.

Usage: python3 build_sheet.py job.json
{"output": "sheet.png", "pdf": "sheet.pdf",                     # pdf optional
 "title": "<character name>", "subtitle": "<style line>",
 "labels": {"turnaround": "Turnaround", "expressions": "Expressions", "palette": "Colour palette", "traits": "Character notes"},
 "turnaround": "turnaround.png", "expressions": "expressions.png",
 "extras": [{"path": "action.png", "caption": "Action pose"}],  # optional
 "palette": [{"name": "Fur", "hex": "#2F6FD0"}],                 # swatches and hex codes drawn in code
 "traits": [{"label": "Age", "value": "<as in the bible>"}],
 "footer": "<optional small line>"}
Write every text in the user's language (labels too). Prints JSON with the file's size and any warnings.
"""
import glob, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

_ROOTS = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
          "/System/Library/Fonts", "/System/Library/Fonts/Supplemental", "/Library/Fonts"]
_PAT = {
    "hangul": ["NotoSansCJK*-{w}.*", "NotoSansKR*{w}*", "AppleSDGothicNeo.ttc", "NanumGothic*", "Arial Unicode*"],
    "cjk": ["NotoSansCJK*-{w}.*", "NotoSansSC*{w}*", "PingFang*", "Arial Unicode*"],
    "thai": ["NotoSansThai-{w}.*", "NotoSansThai*", "Thonburi*", "Arial Unicode*"],
    "devanagari": ["NotoSansDevanagari-{w}.*", "NotoSansDevanagari*", "Arial Unicode*"],
    "arabic": ["NotoNaskhArabic-{w}.*", "NotoSansArabic-{w}.*", "DejaVuSans.ttf", "Arial Unicode*"],
    "hebrew": ["NotoSansHebrew-{w}.*", "DejaVuSans.ttf", "Arial Unicode*"],
    "latin": ["NotoSans-{w}.*", "DejaVuSans{b}.ttf", "LiberationSans-{w}.*", "Arial{b}.ttf", "Arial {w2}.ttf", "Helvetica*", "Arial*"],
}

def script_of(text):
    for ch in text:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7AF or 0x1100 <= o <= 0x11FF: return "hangul"
        if 0x4E00 <= o <= 0x9FFF or 0x3040 <= o <= 0x30FF: return "cjk"
        if 0x0E00 <= o <= 0x0E7F: return "thai"
        if 0x0900 <= o <= 0x097F: return "devanagari"
        if 0x0600 <= o <= 0x06FF: return "arabic"
        if 0x0590 <= o <= 0x05FF: return "hebrew"
    return "latin"

_cache = {}
def font_path(script, bold):
    key = (script, bold)
    if key in _cache: return _cache[key]
    w, b = ("Bold", "-Bold") if bold else ("Regular", "")
    for pat in _PAT[script]:
        pat = pat.replace("{w}", w).replace("{b}", b).replace("{w2}", "Bold" if bold else "")
        for root in _ROOTS:
            hits = sorted(glob.glob(os.path.join(root, "**", pat), recursive=True))
            if hits:
                _cache[key] = hits[0]; return hits[0]
    _cache[key] = None
    return None

def font_for(text, size, bold=False):
    p = font_path(script_of(text), bold)
    try:
        return ImageFont.truetype(p, size) if p else ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def wrap(draw, text, font, width):
    """Wrap by words, or by characters for scripts written without spaces."""
    tokens = list(text) if script_of(text) in ("cjk", "hangul", "thai") else re.findall(r"\S+\s*", text)
    lines, cur = [], ""
    for t in tokens:
        if draw.textlength(cur + t, font=font) <= width or not cur:
            cur += t
        else:
            lines.append(cur.rstrip()); cur = t
    if cur: lines.append(cur.rstrip())
    return lines or [""]

def contrast(rgb):
    lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return (20, 20, 24) if lum > 150 else (255, 255, 255)

def valid_hex(h):
    return bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", h or ""))

def main(job):
    W, M = 2400, 90
    BG, INK, GREY = (250, 248, 244), (28, 28, 34), (110, 110, 118)
    warnings = []
    lab = {"turnaround": "Turnaround", "expressions": "Expressions", "palette": "Colour palette", "traits": "Character notes"}
    lab.update(job.get("labels", {}))
    alltext = " ".join([job.get("title", ""), job.get("subtitle", ""), *lab.values(),
                        *[t.get("label", "") + t.get("value", "") for t in job.get("traits", [])]])
    if any(script_of(c) in ("arabic", "hebrew") for c in alltext):
        warnings.append("Arabic or Hebrew text is drawn without right-to-left shaping and may look wrong. Use English labels on the sheet and give the translation in the reply.")
    probe = Image.new("RGB", (10, 10)); d0 = ImageDraw.Draw(probe)
    blocks = []   # (kind, payload, height)
    y = M
    # title
    tf = font_for(job.get("title", ""), 96, True)
    blocks.append(("title", job.get("title", ""), 130))
    sub = job.get("subtitle", "")
    sf = font_for(sub, 36)
    sublines = wrap(d0, sub, sf, W - 2 * M) if sub else []
    if sublines:
        blocks.append(("sub", sublines, 50 * len(sublines) + 20))

    def image_block(path, label, max_h):
        if not path or not os.path.exists(path):
            warnings.append("Missing image: %s" % path); return
        im = Image.open(path).convert("RGB")
        s = min((W - 2 * M) / im.width, max_h / im.height)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        blocks.append(("label", label, 90))
        blocks.append(("image", im, im.height + 40))

    image_block(job.get("turnaround"), lab["turnaround"], 1150)
    image_block(job.get("expressions"), lab["expressions"], 760)
    for ex in job.get("extras", []):
        image_block(ex.get("path"), ex.get("caption", ""), 1000)
    pal = job.get("palette", [])
    for p in pal:
        if not valid_hex(p.get("hex")):
            warnings.append("Palette entry %r has no valid #RRGGBB code." % p.get("name"))
    pal = [p for p in pal if valid_hex(p.get("hex"))]
    if pal:
        sw_w, gap = 250, 30
        per_row = max(1, (W - 2 * M + gap) // (sw_w + gap))
        rows = (len(pal) + per_row - 1) // per_row
        blocks.append(("label", lab["palette"], 90))
        blocks.append(("palette", pal, rows * 290 + 20))
    traits = job.get("traits", [])
    if traits:
        colw = (W - 2 * M - 60) // 2
        bf, rf = font_for("".join(t.get("label", "") for t in traits), 34, True), None
        items = []
        for t in traits:
            vf = font_for(t.get("value", ""), 32)
            lines = wrap(d0, t.get("value", ""), vf, colw - 10)
            items.append((t.get("label", ""), lines, vf, 44 + 42 * len(lines) + 18))
        left, right, hl, hr = [], [], 0, 0
        for it in items:               # balance columns by height
            if hl <= hr: left.append(it); hl += it[3]
            else: right.append(it); hr += it[3]
        blocks.append(("label", lab["traits"], 90))
        blocks.append(("traits", (left, right, colw), max(hl, hr) + 20))
    if job.get("footer"):
        blocks.append(("footer", job["footer"], 70))
    H = M + sum(b[2] for b in blocks) + M // 2
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    y = M
    for kind, payload, h in blocks:
        if kind == "title":
            d.text((M, y), payload, font=tf, fill=INK)
        elif kind == "sub":
            for i, ln in enumerate(payload):
                d.text((M, y + i * 50), ln, font=sf, fill=GREY)
        elif kind == "label":
            f = font_for(payload, 48, True)
            d.text((M, y + 14), payload, font=f, fill=INK)
            d.line((M, y + 76, W - M, y + 76), fill=(210, 206, 198), width=3)
        elif kind == "image":
            x = (W - payload.width) // 2
            d.rectangle((x - 2, y - 2, x + payload.width + 1, y + payload.height + 1), outline=(215, 211, 203), width=2)
            sheet.paste(payload, (x, y))
        elif kind == "palette":
            sw_w, gap = 250, 30
            per_row = max(1, (W - 2 * M + gap) // (sw_w + gap))
            for i, p in enumerate(payload):
                r, c = divmod(i, per_row)
                x0, y0 = M + c * (sw_w + gap), y + r * 290
                rgb = tuple(int(p["hex"][k:k + 2], 16) for k in (1, 3, 5))
                d.rounded_rectangle((x0, y0, x0 + sw_w, y0 + 160), radius=18, fill=rgb, outline=(205, 201, 193), width=2)
                d.text((x0 + 14, y0 + 118), p["hex"].upper(), font=font_for(p["hex"], 30, True), fill=contrast(rgb))
                nm = p.get("name", "")
                nf = font_for(nm, 30)
                for j, ln in enumerate(wrap(d, nm, nf, sw_w)[:2]):
                    d.text((x0, y0 + 174 + j * 38), ln, font=nf, fill=INK)
        elif kind == "traits":
            left, right, colw = payload
            for ci, col in enumerate((left, right)):
                x0, yy = M + ci * (colw + 60), y
                for label, lines, vf, hh in col:
                    d.text((x0, yy), label, font=font_for(label, 34, True), fill=GREY)
                    for j, ln in enumerate(lines):
                        d.text((x0, yy + 44 + j * 42), ln, font=vf, fill=INK)
                    yy += hh
        elif kind == "footer":
            d.text((M, y + 20), payload, font=font_for(payload, 28), fill=GREY)
        y += h
    out = job["output"]
    sheet.save(out, "PNG")
    res = {"output": out, "size": list(Image.open(out).size), "warnings": warnings}
    if job.get("pdf"):
        sheet.save(job["pdf"], "PDF", resolution=200.0)
        res["pdf"] = job["pdf"]
    print(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
