#!/usr/bin/env python3
"""Build a multi-page certificate PDF (one landscape page per recipient) from a JSON file.

Usage: python3 build.py DATA.json OUTDIR
Fills templates/certificate.html, renders with headless Chrome, checks the page count with pypdf and that every name is in the HTML.
Any field not given is a visible blank line.
"""
import html, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "certificate.html")
PAGES = {"a4": ("A4", "297mm", "210mm"), "letter": ("Letter", "11in", "8.5in")}
THEMES = {"navy": "#1f3a5f", "burgundy": "#7a1f2b", "green": "#2f5d3a", "gold": "#8a6a1e", "teal": "#176b6b",
          "purple": "#5b3a8c", "charcoal": "#333333"}
RTL = {"ar", "he", "fa", "ur"}
BLANK = '<span class="blank"></span>'


def esc(s):
    return html.escape(str(s), quote=True)


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
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    name = d.get("filename", "certificates")
    lang = d.get("lang", "en")
    recips = [r if isinstance(r, dict) else {"name": r} for r in d.get("recipients", [])]
    pname, pw, ph = PAGES.get(str(d.get("size", "a4")).lower(), PAGES["a4"])
    blocks = []
    for r in recips:
        g = lambda k: str(r.get(k, d.get(k, "")) or "").strip()
        nm = str(r.get("name", "")).strip()
        n = len(nm)
        name_pt = 38 if n <= 22 else 32 if n <= 32 else 26 if n <= 44 else 20
        org = f'<div class="org">{esc(g("organisation"))}</div>' if g("organisation") else '<div class="org"></div>'
        subject = f'<div class="subject">{esc(g("subject"))}</div>' if g("subject") else f'<div class="subject">{BLANK}</div>'
        extra = f'<div class="extra">{esc(g("extra"))}</div>' if g("extra") else ""
        date = esc(g("date")) if g("date") else ""
        sname = f'<b>{esc(g("signatory_name"))}</b>' if g("signatory_name") else ""
        srole = esc(g("signatory_role")) if g("signatory_role") else ""
        sigcap = esc(d.get("signature_label", "")) if not (sname or srole) else ""
        blocks.append(
            f'<section class="cert"><div class="outer"><div class="inner">'
            f'{org}'
            f'<div><h1>{esc(d.get("title", ""))}</h1><div class="intro">{esc(d.get("intro", ""))}</div></div>'
            f'<div class="name" style="font-size:{name_pt}pt">{esc(nm)}</div>'
            f'<div><div class="reason">{esc(d.get("reason", ""))}</div>{subject}{extra}</div>'
            f'<div class="sig"><div class="sigbox datebox"><div class="val">{date}</div><div class="sigline"><span class="cap">{esc(d.get("date_label", ""))}</span></div></div>'
            f'<div class="sigbox"><div class="sigspace"></div><div class="sigline">{sname}{srole}<span class="cap">{sigcap}</span></div></div></div>'
            f'</div></div></section>')
    rep = {"LANG": esc(lang), "DIR": "rtl" if lang.split("-")[0] in RTL else "ltr", "DOC_TITLE": esc(d.get("title", "")),
           "PAGE": pname, "PW": pw, "PH": ph, "ACCENT": THEMES.get(str(d.get("theme", "navy")).lower(), THEMES["navy"]),
           "PAGES": "\n".join(blocks)}
    page = open(TEMPLATE, encoding="utf-8").read()
    for k, v in rep.items():
        page = page.replace("{{" + k + "}}", str(v))
    hp = os.path.abspath(os.path.join(out, name + ".html"))
    open(hp, "w", encoding="utf-8").write(page)
    missing = [r.get("name") for r in recips if esc(str(r.get("name", "")).strip()) not in page]
    summary = {"html": hp, "recipients": len(recips), "certificates_in_html": page.count('class="cert"'), "missing_names": missing}
    chrome = find_chrome()
    if not chrome:
        summary["error"] = "Chrome not found: publish the .html as html_preview"
        print(json.dumps(summary, ensure_ascii=False)); return
    pdf = os.path.abspath(os.path.join(out, name + ".pdf"))
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + pdf,
                    "file://" + hp], capture_output=True, timeout=180)
    summary["pdf"] = pdf if os.path.exists(pdf) else None
    try:
        from pypdf import PdfReader
        summary["pdf_pages"] = len(PdfReader(pdf).pages)
    except Exception:
        try:
            summary["pdf_pages"] = len(re.findall(rb"/Type\s*/Page[^s]", open(pdf, "rb").read()))
        except Exception:
            summary["pdf_pages"] = None
    summary["pages_match"] = summary["pdf_pages"] == len(recips)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
