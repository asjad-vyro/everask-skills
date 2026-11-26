#!/usr/bin/env python3
"""Assemble a coloring book PDF from line-art images.

Usage: python3 build_coloring.py DATA.json OUTDIR
Each image is converted to pure black and white (so greys print clean), the edges are whitened, and
the share of dark pixels is measured. The PDF (cover, optional 'belongs to' page, one image per page,
optional blank page behind each) is rendered with headless Chrome so any language and direction works.
Prints one JSON result.
"""
import base64, glob, html, json, os, shutil, subprocess, sys, urllib.request

SIZES = {"a4": ("210mm", "297mm", "A4"), "letter": ("8.5in", "11in", "Letter")}
THEMES = {"blue": "#1f5fa8", "green": "#2f7d4f", "orange": "#d9731f", "purple": "#6a3fa0", "red": "#c0392b", "teal": "#17808a"}
RTL = {"ar", "he", "fa", "ur"}
MAX_DARK = 40.0


def find_chrome():
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(n)
        if p:
            return p
    pats = ["/root/.cache/puppeteer/chrome/*/chrome-linux64/chrome",
            "/root/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell",
            "/root/.cache/ms-playwright/chromium-*/chrome-linux*/chrome",
            "/root/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
            os.path.expanduser("~/.cache/puppeteer/chrome/*/chrome-linux64/chrome"),
            os.path.expanduser("~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell")]
    for pat in pats:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return mac if os.path.exists(mac) else None


def esc(s):
    return html.escape(str(s), quote=True)


def to_bw(src, dst, threshold):
    """Return (dark_pct, size). Threshold to pure black/white and whiten a 2 percent border."""
    from PIL import Image
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im.convert("RGBA"))
    g = im.convert("L")
    bw = g.point(lambda v: 255 if v >= threshold else 0).convert("1")
    w, h = bw.size
    mx, my = max(2, int(w * 0.02)), max(2, int(h * 0.02))
    from PIL import ImageDraw
    d = ImageDraw.Draw(bw)
    d.rectangle([0, 0, w, my], fill=1); d.rectangle([0, h - my, w, h], fill=1)
    d.rectangle([0, 0, mx, h], fill=1); d.rectangle([w - mx, 0, w, h], fill=1)
    hist = bw.convert("L").histogram()
    dark = hist[0] / float(w * h) * 100.0
    bw.convert("L").save(dst, "PNG", optimize=True)
    return round(dark, 1), (w, h)


def uri(path):
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()


def main():
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    out = os.path.abspath(sys.argv[2])
    os.makedirs(os.path.join(out, "bw"), exist_ok=True)
    name = d.get("filename", "coloring-book")
    lang = d.get("lang", "en")
    threshold = int(d.get("threshold", 170))
    W, H, page = SIZES.get(str(d.get("size", "a4")).lower(), SIZES["a4"])
    accent = THEMES.get(str(d.get("theme", "blue")).lower(), THEMES["blue"])
    srcs = list(d.get("pages", []))
    pages_info, cover_uri, imgs = [], None, []
    summary = {"pages_in_plan": len(srcs)}

    def fetch(i, p):
        if str(p).startswith("http"):
            local = os.path.join(out, f"dl-{i}.png")
            urllib.request.urlretrieve(p, local)
            return local
        return p

    if d.get("cover_image"):
        try:
            c = fetch("cover", d["cover_image"])
            dst = os.path.join(out, "bw", "cover.png")
            pct, _ = to_bw(c, dst, threshold)
            cover_uri = uri(dst)
            summary["cover"] = {"dark_pct": pct, "ok": pct <= MAX_DARK}
        except Exception as e:
            summary["cover"] = {"error": str(e)}
    for i, p in enumerate(srcs, 1):
        info = {"page": i, "source": os.path.basename(str(p))}
        try:
            local = fetch(i, p)
            dst = os.path.join(out, "bw", f"page-{i:02d}.png")
            pct, size = to_bw(local, dst, threshold)
            info.update(dark_pct=pct, size=list(size), ok=(pct <= MAX_DARK and pct >= 0.5), bw=dst)
            if pct > MAX_DARK:
                info["problem"] = "too dark: regenerate"
            elif pct < 0.5:
                info["problem"] = "almost blank: regenerate"
            imgs.append(dst)
        except Exception as e:
            info.update(ok=False, problem=f"{type(e).__name__}: {e}")
            imgs.append(None)
        pages_info.append(info)
    summary["pages"] = pages_info
    summary["rejected"] = [p["page"] for p in pages_info if not p["ok"]]

    blank_backs = bool(d.get("blank_backs"))
    css = f"""
@page {{ size: {page}; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Noto Sans", "Helvetica Neue", Arial, "Noto Sans CJK SC", "Noto Naskh Arabic", sans-serif; color: #222; }}
.pg {{ width: {W}; height: calc({H} - 0.4mm); overflow: hidden; break-after: page; position: relative; }}
.pg:last-child {{ break-after: auto; }}
.cover {{ border: 14px solid {accent}; padding: 12% 9% 8%; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
.cover h1 {{ font-size: 44pt; line-height: 1.15; margin: 0; color: {accent}; }}
.cover .sub {{ font-size: 17pt; margin: .5em 0 0; color: #444; }}
.cover img {{ max-width: 100%; max-height: 52%; object-fit: contain; }}
.cover .by {{ font-size: 14pt; letter-spacing: .05em; }}
.belongs {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border: 3px dashed #999; margin: 14mm; width: calc({W} - 28mm); height: calc({H} - 28mm - 0.4mm); }}
.belongs h2 {{ font-size: 28pt; margin: 0 0 1.2em; color: {accent}; }}
.belongs .line {{ width: 60%; border-bottom: 2px solid #333; height: 2em; }}
.art {{ padding: 11mm; display: flex; align-items: center; justify-content: center; }}
.art img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
"""
    dirattr = "rtl" if lang.split("-")[0] in RTL else "ltr"
    body = []
    sub = f'<p class="sub">{esc(d["subtitle"])}</p>' if d.get("subtitle") else ""
    by = f'<div class="by">{esc(d["author"])}</div>' if d.get("author") else "<div></div>"
    ci = f'<img src="{cover_uri}">' if cover_uri else "<div></div>"
    body.append(f'<section class="pg cover"><div><h1>{esc(d["title"])}</h1>{sub}</div>{ci}{by}</section>')
    if d.get("belongs_label"):
        body.append(f'<section class="pg"><div class="belongs"><h2>{esc(d["belongs_label"])}</h2><div class="line"></div></div></section>')
    for p in imgs:
        if p:
            body.append(f'<section class="pg art"><img src="{uri(p)}"></section>')
        else:
            body.append('<section class="pg art"></section>')
        if blank_backs:
            body.append('<section class="pg"></section>')
    doc = (f'<!DOCTYPE html><html lang="{esc(lang)}" dir="{dirattr}"><head><meta charset="utf-8"><title>{esc(d["title"])}</title>'
           f'<style>{css}</style></head><body>{"".join(body)}</body></html>')
    hp = os.path.abspath(os.path.join(out, name + ".html"))
    open(hp, "w", encoding="utf-8").write(doc)
    summary["html"] = hp
    expected = 1 + (1 if d.get("belongs_label") else 0) + len(imgs) * (2 if blank_backs else 1)
    summary["expected_pdf_pages"] = expected
    chrome = find_chrome()
    if not chrome:
        summary["error"] = "Chrome not found: publish the .html as html_preview and say the PDF could not be made"
        print(json.dumps(summary, ensure_ascii=False)); return
    pdf = os.path.abspath(os.path.join(out, name + ".pdf"))
    if os.path.exists(pdf):
        os.remove(pdf)
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=4000", "--print-to-pdf=" + pdf, "file://" + hp], capture_output=True, timeout=180)
    if not os.path.exists(pdf):
        summary["error"] = "Chrome did not produce a PDF"
        print(json.dumps(summary, ensure_ascii=False)); return
    from pypdf import PdfReader
    rd = PdfReader(pdf)
    summary["pdf"] = pdf
    summary["pdf_pages"] = len(rd.pages)
    summary["pages_match_plan"] = len(rd.pages) == expected and not summary["rejected"]
    summary["page_size_pt"] = [round(float(rd.pages[0].mediabox.width)), round(float(rd.pages[0].mediabox.height))]
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
