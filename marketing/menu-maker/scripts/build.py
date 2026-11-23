#!/usr/bin/env python3
"""Build a menu PDF (and optional PNG pages) from a JSON file with templates/menu.html and headless Chrome.

Usage: python3 build.py DATA.json OUTDIR
Prints a JSON summary including a check that every item name and price in the data appears in the HTML.
"""
import html, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "menu.html")
PAGES = {"a4": "A4", "a5": "A5", "letter": "Letter"}
THEMES = {"burgundy": "#7a1f2b", "green": "#2f5d3a", "navy": "#1f3a5f", "terracotta": "#b5542f",
          "charcoal": "#333333", "gold": "#8a6a1e", "teal": "#176b6b"}
RTL = {"ar", "he", "fa", "ur"}


def esc(s):
    return html.escape(str(s), quote=True).replace("\n", "<br>")


def find_chrome():
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(n)
        if p:
            return p
    import glob
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


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    name = data.get("filename", "menu")
    lang = data.get("lang", "en")
    sections = data.get("sections", [])
    n_items = sum(len(s.get("items", [])) for s in sections)
    cols = data.get("columns") or (2 if n_items > 18 else 1)
    fs = 12.5 if n_items <= 8 else 11.5 if n_items <= 12 else 10.5 if n_items <= 24 else 9.5
    parts = []
    for s in sections:
        its = []
        for it in s.get("items", []):
            marks = f'<span class="marks">{esc(it["marks"])}</span>' if it.get("marks") else ""
            price = f'<span class="dots"></span><span class="price">{esc(it["price"])}</span>' if str(it.get("price", "")).strip() else ""
            n2 = f'<div class="name2">{esc(it["name2"])}</div>' if it.get("name2") else ""
            d = f'<div class="desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
            its.append(f'<div class="item"><div class="line"><span class="name">{esc(it.get("name",""))}{marks}</span>{price}</div>{n2}{d}</div>')
        sd = f'<p class="sdesc">{esc(s["note"])}</p>' if s.get("note") else ""
        h2 = f'<h2>{esc(s["name"])}</h2>' if str(s.get("name", "")).strip() else ""
        parts.append(f'<section>{h2}{sd}{"".join(its)}</section>')
    legend = ""
    if data.get("legend"):
        legend = "<p>" + " &nbsp; ".join(f"<b>{esc(k)}</b> = {esc(v)}" for k, v in data["legend"].items()) + "</p>"
    note = f'<p>{esc(data["note"])}</p>' if data.get("note") else ""
    tag = f'<div class="tag">{esc(data["tagline"])}</div>' if data.get("tagline") else ""
    rep = {"LANG": esc(lang), "DIR": "rtl" if lang.split("-")[0] in RTL else "ltr", "DOC_TITLE": esc(data.get("title", "")),
           "PAGE": PAGES.get(str(data.get("size", "a4")).lower(), "A4"), "FS": fs,
           "ACCENT": THEMES.get(str(data.get("theme", "burgundy")).lower(), THEMES["burgundy"]), "COLS": cols,
           "TITLE": esc(data.get("title", "")), "TAGLINE": tag, "SECTIONS": "\n".join(parts), "LEGEND": legend, "NOTE": note, "FOOTER_CSS": "" if (legend or note) else "footer { display: none; }"}
    page = open(TEMPLATE, encoding="utf-8").read()
    for k, v in rep.items():
        page = page.replace("{{" + k + "}}", str(v))
    hp = os.path.abspath(os.path.join(out, name + ".html"))
    open(hp, "w", encoding="utf-8").write(page)

    # check: every name and price from the data is in the page, item count matches
    missing = []
    for s in sections:
        for it in s.get("items", []):
            for key in ("name", "price"):
                v = str(it.get(key, "")).strip()
                if v and esc(v) not in page:
                    missing.append(v)
    summary = {"html": hp, "sections": len(sections), "items": n_items, "items_in_html": page.count('class="item"'),
               "missing_from_html": missing}
    chrome = find_chrome()
    if not chrome:
        summary["error"] = "Chrome not found: publish the .html as html_preview"
        print(json.dumps(summary)); return
    pdf = os.path.abspath(os.path.join(out, name + ".pdf"))
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + pdf,
                    "file://" + hp], capture_output=True, timeout=120)
    summary["pdf"] = pdf if os.path.exists(pdf) else None
    try:
        from pypdf import PdfReader
        summary["pdf_pages"] = len(PdfReader(pdf).pages)
    except Exception:
        import re
        try:
            summary["pdf_pages"] = len(re.findall(rb"/Type\s*/Page[^s]", open(pdf, "rb").read()))
        except Exception:
            summary["pdf_pages"] = None
    if data.get("png") and summary["pdf"]:
        try:
            import fitz
            d = fitz.open(pdf)
            pngs = []
            for i, pg in enumerate(d):
                p = os.path.abspath(os.path.join(out, f"{name}-page{i+1}.png"))
                pg.get_pixmap(dpi=150).save(p)
                pngs.append(p)
            summary["pngs"] = pngs
        except Exception as e:
            summary["png_error"] = str(e)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
