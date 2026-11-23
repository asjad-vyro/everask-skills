#!/usr/bin/env python3
"""Fill templates/flyer.html from a JSON file, then render PDF and PNG with headless Chrome.

Usage: python3 build.py DATA.json OUTDIR
Writes OUTDIR/<name>.html, .pdf, .png and prints a JSON summary. Standard library only (pypdf optional).
"""
import base64, html, json, mimetypes, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "flyer.html")
# size name -> (width px, height px) at 96 dpi
SIZES = {"a4": (794, 1123), "a5": (559, 794), "letter": (816, 1056), "a3": (1123, 1587),
         "square": (1080, 1080), "story": (1080, 1920)}
THEMES = {  # accent, dark accent
    "red": ("#d62839", "#8f1624"), "orange": ("#e8590c", "#9c3a06"), "yellow": ("#e0a100", "#8a6300"),
    "green": ("#2f8f4e", "#1d5a31"), "teal": ("#0f8b8d", "#08595b"), "blue": ("#2563eb", "#173f9c"),
    "purple": ("#7c3aed", "#4c1d95"), "pink": ("#d6336c", "#8e1f47"), "black": ("#222222", "#000000"),
}
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
    name = data.get("filename", "flyer")
    size = str(data.get("size", "a4")).lower()
    w, h = SIZES.get(size, SIZES["a4"])
    if data.get("landscape") and size in ("a4", "a5", "letter", "a3"):
        w, h = h, w
    theme = str(data.get("theme", "blue")).lower()
    accent, dark = THEMES.get(theme, THEMES["blue"])
    lang = data.get("lang", "en")
    title = str(data.get("title", ""))
    longest = max([len(x) for x in title.split()] or [1])
    scale = 11.5 if len(title) <= 18 else 9.5 if len(title) <= 36 else 7.5 if len(title) <= 70 else 6
    if longest > 14:
        scale = min(scale, 6.5)
    if w > h:
        scale *= 0.7
    u = w / 100 if w <= h else h / 100 * 1.15

    bg_css, shade, text, lab = "background: #fffdf8;", "transparent", "#1b1b1f", accent
    bg = data.get("background_image")
    if bg and os.path.exists(bg):
        mime = mimetypes.guess_type(bg)[0] or "image/png"
        b64 = base64.b64encode(open(bg, "rb").read()).decode()
        bg_css = f"background: url(data:{mime};base64,{b64}) center/cover no-repeat;"
        shade = "linear-gradient(180deg, rgba(0,0,0,.55), rgba(0,0,0,.72))"
        text = "#ffffff"
        lab = "#ffffff"
    kicker = f'<div class="kicker">{esc(data["kicker"])}</div>' if data.get("kicker") else ""
    sub = f'<p class="sub">{esc(data["subtitle"])}</p>' if data.get("subtitle") else ""
    det = "".join(f'<div class="row"><div class="label">{esc(d.get("label",""))}</div><div class="value">{esc(d.get("value",""))}</div></div>'
                  for d in data.get("details", []))
    details = f'<div class="details">{det}</div>' if det else ""
    pr = "".join(f'<div class="price"><span>{esc(p.get("item",""))}</span><b>{esc(p.get("price",""))}</b></div>'
                 for p in data.get("prices", []))
    prices = f'<div class="prices">{pr}</div>' if pr else ""
    body = f'<p class="body">{esc(data["body"])}</p>' if data.get("body") else ""
    cta = f'<div class="cta">{esc(data["cta"])}</div>' if data.get("cta") else ""
    contact = f'<div class="contact">{esc(data["contact"])}</div>' if data.get("contact") else ""

    rep = {"LANG": esc(lang), "DIR": "rtl" if lang.split("-")[0] in RTL else "ltr", "DOC_TITLE": esc(title),
           "W": w, "H": h, "U": round(u, 3), "ACCENT": accent, "ACCENT_DARK": dark, "BG_CSS": bg_css, "SHADE": shade,
           "TEXT": text, "LAB": lab, "TITLE_SCALE": scale, "KICKER": kicker, "TITLE": esc(title), "SUBTITLE": sub,
           "DETAILS": details, "PRICES": prices, "BODY": body, "CTA": cta, "CONTACT": contact}
    page = open(TEMPLATE, encoding="utf-8").read()
    for k, v in rep.items():
        page = page.replace("{{" + k + "}}", str(v))
    hp = os.path.abspath(os.path.join(out, name + ".html"))
    open(hp, "w", encoding="utf-8").write(page)

    summary = {"html": hp, "size": size, "width": w, "height": h}
    chrome = find_chrome()
    if not chrome:
        summary["error"] = "Chrome not found: publish the .html as html_preview"
        print(json.dumps(summary)); return
    pdf = os.path.abspath(os.path.join(out, name + ".pdf"))
    png = os.path.abspath(os.path.join(out, name + ".png"))
    base = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars"]
    subprocess.run(base + ["--no-pdf-header-footer", "--print-to-pdf=" + pdf, "file://" + hp], capture_output=True, timeout=120)
    subprocess.run(base + [f"--window-size={w},{h}", "--force-device-scale-factor=2", "--screenshot=" + png, "file://" + hp],
                   capture_output=True, timeout=120)
    summary.update({"pdf": pdf if os.path.exists(pdf) else None, "png": png if os.path.exists(png) else None})
    try:
        from pypdf import PdfReader
        summary["pdf_pages"] = len(PdfReader(pdf).pages)
    except Exception:
        import re
        try:
            summary["pdf_pages"] = len(re.findall(rb"/Type\s*/Page[^s]", open(pdf, "rb").read()))
        except Exception:
            summary["pdf_pages"] = None
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
