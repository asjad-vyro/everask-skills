#!/usr/bin/env python3
"""Replace text on a flat-background image (poster, flyer, invitation) in code.

Usage: python3 edit_image.py job.json
job.json:
{"image": "in.png", "output": "out.png", "crops_dir": "/tmp/.scratch/poster-text-editor/crops",
 "edits": [{"box": [x0, y0, x1, y1],      # pixels, tight around the OLD text   (or "box_frac": [x0,y0,x1,y1] as 0..1)
            "old": "12 March 2027",        # the exact old text (used to match font size and weight)
            "new": "19 March 2027",
            "align": "auto|left|center|right",   # optional
            "color": "#RRGGBB",            # optional, default: sampled from the old text
            "bold": true,                  # optional, default: matched to the old text
            "font": "/path/font.ttf"}]}    # optional
Prints one JSON object. The output keeps the pixel size and file type of the input.
"""
import glob, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------- fonts ----------
def _script_of(text):
    for ch in text:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7AF or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F:
            return "hangul"
        if 0x4E00 <= o <= 0x9FFF or 0x3040 <= o <= 0x30FF or 0x3400 <= o <= 0x4DBF:
            return "cjk"
        if 0x0E00 <= o <= 0x0E7F:
            return "thai"
        if 0x0600 <= o <= 0x06FF or 0x0750 <= o <= 0x077F:
            return "arabic"
        if 0x0590 <= o <= 0x05FF:
            return "hebrew"
        if 0x0900 <= o <= 0x097F:
            return "devanagari"
    return "latin"

_PATTERNS = {
    "hangul": ["NotoSansCJK*-{w}.*", "NotoSansKR*{w}*", "AppleSDGothicNeo.ttc", "NanumGothic*", "Arial Unicode*"],
    "cjk": ["NotoSansCJK*-{w}.*", "NotoSansSC*{w}*", "PingFang*", "Arial Unicode*"],
    "thai": ["NotoSansThai-{w}.*", "NotoSansThai*", "Thonburi*", "Arial Unicode*"],
    "arabic": ["NotoNaskhArabic-{w}.*", "NotoSansArabic-{w}.*", "NotoNaskhArabic*", "NotoSansArabic*", "DejaVuSans.ttf", "Arial Unicode*"],
    "hebrew": ["NotoSansHebrew-{w}.*", "DejaVuSans.ttf", "Arial Unicode*"],
    "devanagari": ["NotoSansDevanagari-{w}.*", "NotoSansDevanagari*", "Arial Unicode*"],
    "latin": ["NotoSans-{w}.*", "DejaVuSans{b}.ttf", "LiberationSans-{w}.*", "Arial{b}.ttf", "Arial {w2}.ttf", "Helvetica*", "Arial*"],
}
_ROOTS = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
          "/System/Library/Fonts", "/System/Library/Fonts/Supplemental", "/Library/Fonts"]

def find_font(text, bold=False):
    """Return (path, is_bold_file). Falls back to any font that loads."""
    script = _script_of(text)
    w = "Bold" if bold else "Regular"
    b = "-Bold" if bold else ""
    for pat in _PATTERNS[script]:
        pat = pat.replace("{w}", w).replace("{b}", b).replace("{w2}", "Bold" if bold else "")
        for root in _ROOTS:
            hits = sorted(glob.glob(os.path.join(root, "**", pat), recursive=True))
            if hits:
                return hits[0], bold and ("Bold" in os.path.basename(hits[0]))
    return None, False

def load_font(path, size):
    return ImageFont.truetype(path, max(6, int(round(size)))) if path else ImageFont.load_default()

# ---------- helpers ----------
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def rgb_to_hex(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)

def bg_fill(arr, x0, y0, x1, y1, ring=4, gap=2):
    """Rebuild the area x0..x1,y0..y1 from the pixels just left and right of it, row by row.
    Returns (fill array, texture score). Texture score is the average residual of the ring
    pixels from a straight line; small (<8) means a flat or smoothly shaded background."""
    H, W = arr.shape[:2]
    lx0, lx1 = max(0, x0 - gap - ring), max(0, x0 - gap)
    rx0, rx1 = min(W, x1 + gap), min(W, x1 + gap + ring)
    if lx1 <= lx0: lx0, lx1 = rx0, rx1
    if rx1 <= rx0: rx0, rx1 = lx0, lx1
    ys = np.arange(y0, y1)
    # smooth per-row colours over a few rows
    def side(a, b):
        strip = arr[:, a:b, :].astype(float).mean(axis=1)  # H x 3
        k = 5
        pad = np.pad(strip, ((k, k), (0, 0)), mode="edge")
        sm = np.stack([pad[i:i + H] for i in range(2 * k + 1)]).mean(axis=0)
        return sm
    L, R = side(lx0, lx1), side(rx0, rx1)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    fill = L[ys][:, None, :] * (1 - t) + R[ys][:, None, :] * t
    # texture: residual of left/right strips from their own smoothed row colour
    resid = []
    for a, b, sm in ((lx0, lx1, L), (rx0, rx1, R)):
        seg = arr[y0:y1, a:b, :].astype(float)
        resid.append(np.abs(seg - sm[y0:y1][:, None, :]).mean())
    return fill, float(np.mean(resid))

def best_weight(old, ink_w, ink_h, bold_hint):
    """Pick regular or bold and a font size so the old text rendered in our font matches the measured ink box."""
    out = []
    for bold in ([bold_hint] if bold_hint is not None else [False, True]):
        path, _ = find_font(old, bold)
        f = load_font(path, 100)
        bb = f.getbbox(old, anchor="ls")
        h = max(1, bb[3] - bb[1])
        size = 100.0 * ink_h / h
        f2 = load_font(path, size)
        bb2 = f2.getbbox(old, anchor="ls")
        err = abs((bb2[2] - bb2[0]) - ink_w) / max(1, ink_w)
        out.append((err, bold, path, size))
    out.sort(key=lambda r: r[0])
    return out[0]

def main(job):
    img = Image.open(job["image"])
    fmt = (img.format or os.path.splitext(job["output"])[1][1:] or "PNG").upper()
    W, H = img.size
    mode_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
    base = img.convert("RGBA") if mode_alpha else img.convert("RGB")
    arr = np.array(base.convert("RGB"))
    result = {"input_size": [W, H], "edits": [], "warnings": []}
    crops_dir = job.get("crops_dir")
    if crops_dir:
        os.makedirs(crops_dir, exist_ok=True)
    draw_img = base.copy()
    for i, e in enumerate(job["edits"], 1):
        if "box_frac" in e:
            fx0, fy0, fx1, fy1 = e["box_frac"]
            box = [fx0 * W, fy0 * H, fx1 * W, fy1 * H]
        else:
            box = e["box"]
        pad = int(job.get("pad", 3))
        x0, y0 = max(0, int(box[0]) - pad), max(0, int(box[1]) - pad)
        x1, y1 = min(W, int(box[2]) + pad), min(H, int(box[3]) + pad)
        info = {"n": i, "old": e.get("old"), "new": e["new"], "box": [x0, y0, x1, y1], "warnings": []}
        fill, tex = bg_fill(arr, x0, y0, x1, y1)
        region = arr[y0:y1, x0:x1, :].astype(float)
        dist = np.abs(region - fill).max(axis=2)
        mx = dist.max()
        if mx < 25:
            info["warnings"].append("No old text found in this box (box may be in the wrong place).")
        mask = dist > max(25, 0.35 * mx)
        ys, xs = np.where(mask)
        if len(xs) == 0:
            ink = (0, 0, x1 - x0, y1 - y0)
        else:
            ink = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        ink_w, ink_h = ink[2] - ink[0], ink[3] - ink[1]
        # old text colour: the most distant pixels
        if "color" in e:
            col = hex_to_rgb(e["color"])
        elif len(xs):
            strong = dist > 0.6 * mx
            col = tuple(np.median(region[strong], axis=0))
        else:
            col = (0, 0, 0)
        info["background_flat"] = bool(tex < 8)
        info["texture_score"] = round(tex, 1)
        if tex >= 8:
            info["warnings"].append("Background around this text is textured or a photo: a patched fill will show. Use the image_generate route instead.")
        old = e.get("old") or e["new"]
        err, bold, fpath, size = best_weight(old, ink_w, ink_h, e.get("bold"))
        if e.get("font"):
            fpath = e["font"]
        # new text must be drawable with the chosen font
        new = e["new"]
        if _script_of(new) != _script_of(old) and not e.get("font"):
            fpath, _ = find_font(new, bold)
        font = load_font(fpath, size)
        # baseline: old ink bottom minus the old text's descender depth in our font
        obb = font.getbbox(old, anchor="ls")
        baseline = y0 + ink[3] - obb[3]
        # alignment
        align = e.get("align", "auto")
        old_cx = x0 + (ink[0] + ink[2]) / 2
        if align == "auto":
            align = "center" if abs(old_cx - W / 2) < 0.02 * W else ("right" if (x0 + ink[2]) > 0.98 * W - 1 else "left")
        # fit width: never run past the old box by more than the room to the edges of the image
        nbb = font.getbbox(new, anchor="ls")
        nw = nbb[2] - nbb[0]
        margin = max(10, int(0.04 * W))
        if align == "center":
            room = 2 * min(old_cx, W - old_cx) - 2 * margin
        elif align == "right":
            room = (x0 + ink[2]) - margin
        else:
            room = (W - margin) - (x0 + ink[0])
        shrunk = False
        if nw > room and room > 20:
            size = size * room / nw
            font = load_font(fpath, size)
            nbb = font.getbbox(new, anchor="ls")
            nw = nbb[2] - nbb[0]
            shrunk = True
            info["warnings"].append("New text is longer than the space, so it was set smaller (%d px) to fit." % round(size))
        if align == "center":
            left = old_cx - nw / 2
        elif align == "right":
            left = x0 + ink[2] - nw
        else:
            left = x0 + ink[0]
        # make sure the old text is fully covered when the new text is longer
        ex0, ex1 = x0, x1
        if left + nbb[0] < ex0:
            ex0 = max(0, int(left + nbb[0]) - pad)
        if left + nbb[2] > ex1:
            ex1 = min(W, int(left + nbb[2]) + pad)
        if (ex0, ex1) != (x0, x1):
            fill, tex2 = bg_fill(arr, ex0, y0, ex1, y1)
            if tex2 >= 8 and tex < 8:
                info["warnings"].append("The wider text area runs into something other than plain background; check the crop.")
        patch = Image.fromarray(np.clip(fill, 0, 255).astype("uint8"), "RGB")
        if mode_alpha:
            patch = patch.convert("RGBA")
        draw_img.paste(patch, (ex0, y0))
        d = ImageDraw.Draw(draw_img)
        faux = bold and fpath and "Bold" not in os.path.basename(fpath)
        d.text((left - nbb[0] * 0 , baseline), new, font=font, fill=tuple(int(v) for v in col) + ((255,) if mode_alpha else ()),
               anchor="ls", stroke_width=max(1, int(size / 40)) if faux else 0,
               stroke_fill=tuple(int(v) for v in col) + ((255,) if mode_alpha else ()))
        info.update({"font": os.path.basename(fpath) if fpath else "PIL default", "font_size": round(size),
                     "bold": bool(bold), "align": align, "text_color": rgb_to_hex(col),
                     "old_text_size_px": [int(ink_w), int(ink_h)], "shrunk_to_fit": shrunk})
        if fpath is None:
            info["warnings"].append("No TrueType font was found; text is set in a default font.")
        if crops_dir:
            cx0, cy0 = max(0, min(x0, ex0) - 20), max(0, y0 - 20)
            cx1, cy1 = min(W, max(x1, ex1) + 20), min(H, y1 + 20)
            before = base.crop((cx0, cy0, cx1, cy1)).convert("RGB")
            after = draw_img.crop((cx0, cy0, cx1, cy1)).convert("RGB")
            sheet = Image.new("RGB", (before.width, before.height * 2 + 6), (255, 0, 255))
            sheet.paste(before, (0, 0)); sheet.paste(after, (0, before.height + 6))
            sc = max(1, min(3, 1400 // max(1, sheet.width)))
            if sc > 1:
                sheet = sheet.resize((sheet.width * sc, sheet.height * sc), Image.LANCZOS)
            cp = os.path.join(crops_dir, "edit-%d-before-after.png" % i)
            sheet.save(cp)
            info["crop"] = cp
        result["edits"].append(info)
        arr = np.array(draw_img.convert("RGB"))
        if info["warnings"]:
            result["warnings"].extend("edit %d: %s" % (i, w) for w in info["warnings"])
    out = draw_img
    ext = os.path.splitext(job["output"])[1].lower()
    if ext in (".jpg", ".jpeg"):
        out.convert("RGB").save(job["output"], "JPEG", quality=95, subsampling=0)
    elif ext == ".webp":
        out.save(job["output"], "WEBP", quality=95)
    else:
        out.save(job["output"], "PNG")
    chk = Image.open(job["output"])
    result["output"] = job["output"]
    result["output_size"] = list(chk.size)
    result["same_size_as_input"] = chk.size == (W, H)
    print(json.dumps(result, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
