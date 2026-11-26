#!/usr/bin/env python3
"""Build a short ebook or booklet PDF from a JSON file, using headless Chrome.

Usage: python3 build_ebook.py DATA.json OUTDIR
Writes OUTDIR/<filename>.html (self-contained) and OUTDIR/<filename>.pdf, then prints one JSON result:
page count, contents page numbers checked against the real pages, word counts, placeholders left in the text.
The contents page numbers and the footer page numbers are filled in after a first render, so they are always right.
"""
import base64, glob, html, io, json, mimetypes, os, re, shutil, subprocess, sys

SIZES = {"a4": ("210mm", "297mm", "A4", 22), "letter": ("8.5in", "11in", "Letter", 22),
         "a5": ("148mm", "210mm", "A5", 16), "6x9": ("6in", "9in", "6in 9in", 17)}
THEMES = {"navy": "#1f3a5f", "green": "#2f5d3a", "burgundy": "#7a1f2b", "terracotta": "#b5542f",
          "charcoal": "#333333", "teal": "#176b6b", "purple": "#4b2e83", "gold": "#8a6a1e"}
RTL = {"ar", "he", "fa", "ur"}


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
    return html.escape(str(s), quote=False)


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\*\w])\*([^\*\n]+?)\*(?![\*\w])", r"<i>\1</i>", s)
    return s


def body_html(body):
    """Small markdown: blank line = new paragraph; '## ' sub-heading; '- ' bullets; '1. ' numbered; '> ' call-out."""
    out, para, lst, kind = [], [], [], None

    def flush_p():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_l():
        nonlocal kind
        if lst:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + f"</{kind}>")
            lst.clear()
            kind = None

    callout = []

    def flush_c():
        if callout:
            out.append('<aside class="callout">' + inline(" ".join(callout)) + "</aside>")
            callout.clear()

    for raw in str(body).replace("\r", "").split("\n"):
        line = raw.strip()
        if not line:
            flush_p(); flush_l(); flush_c(); continue
        if line.startswith("## "):
            flush_p(); flush_l(); flush_c(); out.append("<h3>" + inline(line[3:]) + "</h3>")
        elif line.startswith("> "):
            flush_p(); flush_l(); callout.append(line[2:])
        elif re.match(r"^[-*] ", line):
            flush_p(); flush_c()
            if kind == "ol": flush_l()
            kind = "ul"; lst.append(line[2:])
        elif re.match(r"^\d+[.)] ", line):
            flush_p(); flush_c()
            if kind == "ul": flush_l()
            kind = "ol"; lst.append(re.sub(r"^\d+[.)] ", "", line))
        else:
            flush_l(); flush_c(); para.append(line)
    flush_p(); flush_l(); flush_c()
    return "\n".join(out)


def img_uri(path):
    if not path or not os.path.exists(path):
        return None
    mt = mimetypes.guess_type(path)[0] or "image/png"
    return f"data:{mt};base64," + base64.b64encode(open(path, "rb").read()).decode()


CSS = """
@page { size: __PAGE__; margin: __MT__mm __MS__mm __MB__mm __MS__mm; }
@page :first { margin: 0; }
* { box-sizing: border-box; }
html { font-size: __FS__pt; }
body { margin: 0; font-family: Georgia, "Noto Serif", "Noto Naskh Arabic", "Noto Serif CJK SC", serif; line-height: 1.55; color: #222; }
h1, h2, h3, .sans { font-family: "Noto Sans", "Helvetica Neue", Arial, "Noto Sans CJK SC", "Noto Naskh Arabic", sans-serif; }
.pg { break-before: page; }
.cover { break-before: auto; position: relative; width: __W__; height: calc(__H__ - 0.4mm); overflow: hidden; color: #fff;
  background: __ACCENT__; display: flex; flex-direction: column; justify-content: center; padding: 14%; }
.cover .bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
.cover .shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.25), rgba(0,0,0,.65)); }
.cover .in { position: relative; }
.cover h1 { font-size: 2.6rem; line-height: 1.12; margin: 0 0 .6em; letter-spacing: -.01em; }
.cover .sub { font-size: 1.2rem; opacity: .92; margin: 0 0 2.2em; font-family: "Noto Sans", Arial, sans-serif; }
.cover .by { font-size: 1rem; letter-spacing: .08em; font-family: "Noto Sans", Arial, sans-serif; border-top: 2px solid rgba(255,255,255,.7); padding-top: .8em; display: inline-block; }
.front { display: flex; flex-direction: column; justify-content: flex-end; min-height: 80vh; font-size: .85rem; color: #555; }
.front h2 { color: __ACCENT__; font-size: 1.1rem; margin: 0 0 .4em; }
.front p { margin: .3em 0; }
.toc h2, .plain h2 { font-size: 1.7rem; color: __ACCENT__; margin: 0 0 1em; }
.toc ol { list-style: none; padding: 0; margin: 0; }
.toc li { display: flex; align-items: baseline; gap: .6em; padding: .55em 0; border-bottom: 1px solid #ddd; font-size: 1.02rem; }
.toc li .t { flex: 1; }
.toc li .n { font-family: "Noto Sans", Arial, sans-serif; color: __ACCENT__; font-weight: 700; min-width: 2.2em; }
.toc li .p { font-family: "Noto Sans", Arial, sans-serif; font-weight: 700; }
.opener { padding-top: 14vh; }
.opener .lab { font-family: "Noto Sans", Arial, sans-serif; color: __ACCENT__; letter-spacing: .14em; font-size: .85rem; font-weight: 700; text-transform: uppercase; }
.opener h2 { font-size: 2.1rem; line-height: 1.15; margin: .25em 0 .4em; color: #111; }
.opener .rule { width: 3.2rem; height: 4px; background: __ACCENT__; margin: .2em 0 1em; }
.opener .lead { font-size: 1.12rem; font-style: italic; color: #444; margin: 0 0 1.4em; }
p { margin: 0 0 .85em; text-align: start; orphans: 3; widows: 3; }
h3 { font-size: 1.15rem; color: __ACCENT__; margin: 1.3em 0 .4em; break-after: avoid; }
ul, ol { margin: 0 0 .9em; padding-inline-start: 1.4em; }
li { margin-bottom: .3em; }
.callout { margin: 1.1em 0; padding: .8em 1em; border-inline-start: 5px solid __ACCENT__; background: __TINT__; font-family: "Noto Sans", Arial, "Noto Naskh Arabic", sans-serif; font-size: .93rem; break-inside: avoid; }
.sources ul { font-size: .9rem; word-break: break-word; }
.closing { display: flex; flex-direction: column; justify-content: center; min-height: 70vh; text-align: center; }
.closing h2 { font-size: 1.8rem; color: __ACCENT__; }
.closing p { text-align: center; }
"""


def build_html(d, toc_pages):
    size = SIZES.get(str(d.get("size", "a4")).lower(), SIZES["a4"])
    w, h, page, ms = size
    lang = d.get("lang", "en")
    accent = THEMES.get(str(d.get("theme", "navy")).lower(), d.get("theme") if re.match(r"^#[0-9a-fA-F]{6}$", str(d.get("theme", ""))) else THEMES["navy"])
    r, g, b = (int(accent[i:i + 2], 16) for i in (1, 3, 5))
    tint = f"rgba({r},{g},{b},.09)"
    fs = 10.5 if d.get("size", "a4") in ("a5", "6x9") else 11.5
    css = CSS
    for k, v in {"__PAGE__": page, "__MT__": ms, "__MS__": ms, "__MB__": ms + 4, "__FS__": fs, "__W__": w, "__H__": h,
                 "__ACCENT__": accent, "__TINT__": tint}.items():
        css = css.replace(k, str(v))
    L = d.get("labels", {})
    contents_word = L.get("contents", "Contents")
    chapter_word = L.get("chapter", "Chapter")
    sources_word = L.get("sources", "Sources")
    parts = []
    uri = img_uri(d.get("cover_image"))
    bg = f'<div class="bg" style="background-image:url({uri})"></div><div class="shade"></div>' if uri else ""
    sub = f'<p class="sub">{esc(d["subtitle"])}</p>' if d.get("subtitle") else ""
    by = f'<div class="by">{esc(d["author"])}</div>' if d.get("author") else ""
    parts.append(f'<section class="cover">{bg}<div class="in"><h1>{esc(d["title"])}</h1>{sub}{by}</div></section>')
    if d.get("copyright_page", True):
        lines = d.get("front_lines") or []
        fl = "".join(f"<p>{inline(x)}</p>" for x in lines)
        parts.append(f'<section class="pg front"><h2>{esc(d["title"])}</h2>{fl}</section>')
    entries = [(c["title"], f"c{i}") for i, c in enumerate(d["chapters"], 1)]
    if d.get("sources"):
        entries.append((sources_word, "src"))
    lis = []
    for i, (t, key) in enumerate(entries, 1):
        num = f'<span class="n">{i}</span>' if key != "src" else '<span class="n"></span>'
        lis.append(f'<li>{num}<span class="t">{esc(t)}</span><span class="p">{toc_pages.get(key, "")}</span></li>')
    parts.append(f'<section class="pg toc"><h2>{esc(contents_word)}</h2><ol>{"".join(lis)}</ol></section>')
    for i, c in enumerate(d["chapters"], 1):
        lead = f'<p class="lead">{inline(c["lead"])}</p>' if c.get("lead") else ""
        parts.append(f'<section class="pg chap"><div class="opener"><div class="lab">{esc(chapter_word)} {i}</div>'
                     f'<h2>{esc(c["title"])}</h2><div class="rule"></div>{lead}</div>{body_html(c.get("body", ""))}</section>')
    if d.get("sources"):
        items = "".join(f"<li>{inline(s)}</li>" for s in d["sources"])
        parts.append(f'<section class="pg plain sources"><h2>{esc(sources_word)}</h2><ul>{items}</ul></section>')
    cl = d.get("closing")
    if cl:
        t = f'<h2>{esc(cl["title"])}</h2>' if cl.get("title") else ""
        parts.append(f'<section class="pg closing">{t}{body_html(cl.get("body", ""))}</section>')
    return (f'<!DOCTYPE html><html lang="{esc(lang)}" dir="{"rtl" if lang.split("-")[0] in RTL else "ltr"}"><head><meta charset="utf-8">'
            f'<title>{esc(d["title"])}</title><style>{css}</style></head><body>{"".join(parts)}</body></html>'), entries


def render(chrome, hp, pdf):
    if os.path.exists(pdf):
        os.remove(pdf)
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=4000", "--print-to-pdf=" + pdf, "file://" + hp],
                   capture_output=True, timeout=180)
    return os.path.exists(pdf)


def norm(s):
    import unicodedata
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s)).lower()


def locate(pdf, entries, d):
    from pypdf import PdfReader
    rd = PdfReader(pdf)
    texts = [norm(p.extract_text() or "") for p in rd.pages]
    # contents page = first page containing the contents word after the cover/front pages
    start = 1
    res, last = {}, 0
    toc_idx = None
    cw = norm(d.get("labels", {}).get("contents", "Contents"))
    for i, t in enumerate(texts):
        if i > 0 and cw in t and all(norm(e[0]) in t for e in entries):
            toc_idx = i
            break
    last = toc_idx if toc_idx is not None else 1
    for title, key in entries:
        nt = norm(title)
        found = None
        for i in range(last + 1, len(texts)):
            if nt in texts[i]:
                found = i
                break
        if found is not None:
            res[key] = found + 1
            last = found
    return res, len(texts)


def stamp_numbers(pdf, d):
    """Add a centred page number to every page except the cover."""
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    rd = PdfReader(pdf)
    wr = PdfWriter()
    for i, p0 in enumerate(rd.pages):
        p = wr.add_page(p0)
        if i > 0:
            wd, ht = float(p.mediabox.width), float(p.mediabox.height)
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=(wd, ht))
            c.setFont("Helvetica", 9)
            c.setFillGray(0.4)
            c.drawCentredString(wd / 2, 26, str(i + 1))
            c.save()
            buf.seek(0)
            p.merge_page(PdfReader(buf).pages[0])
    with open(pdf, "wb") as f:
        wr.write(f)


def main():
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    name = d.get("filename", "ebook")
    hp = os.path.abspath(os.path.join(out, name + ".html"))
    pdf = os.path.abspath(os.path.join(out, name + ".pdf"))
    toc = {}
    page, entries = build_html(d, toc)
    open(hp, "w", encoding="utf-8").write(page)
    words = {c["title"]: len(re.findall(r"\S+", re.sub(r"^(##|>|[-*]|\d+[.)]) ", "", c.get("body", ""), flags=re.M))) for c in d["chapters"]}
    alltext = " ".join(c.get("body", "") + " " + c.get("lead", "") for c in d["chapters"])
    summary = {"html": hp, "chapters": len(d["chapters"]), "words_per_chapter": words, "words_total": sum(words.values()),
               "placeholders_in_text": sorted(set(re.findall(r"\[[^\]\n]{2,80}\]", alltext + " " + " ".join(d.get("front_lines") or []))))}
    chrome = find_chrome()
    if not chrome:
        summary["error"] = "Chrome not found: publish the .html as html_preview and say the PDF could not be made"
        print(json.dumps(summary, ensure_ascii=False)); return
    try:
        pages = 0
        for _ in range(3):
            if not render(chrome, hp, pdf):
                summary["error"] = "Chrome did not produce a PDF"
                print(json.dumps(summary, ensure_ascii=False)); return
            found, pages = locate(pdf, entries, d)
            if found == toc:
                break
            toc = found
            page, entries = build_html(d, toc)
            open(hp, "w", encoding="utf-8").write(page)
        else:
            render(chrome, hp, pdf)
            found, pages = locate(pdf, entries, d)
        stamp_numbers(pdf, d)
        found, pages = locate(pdf, entries, d)
        summary["pdf"] = pdf
        summary["pdf_pages"] = pages
        summary["contents"] = [{"title": t, "page_in_contents": toc.get(k), "page_in_pdf": found.get(k)} for t, k in entries]
        summary["contents_match"] = all(toc.get(k) is not None and toc.get(k) == found.get(k) for _, k in entries)
        summary["cover_image_used"] = bool(img_uri(d.get("cover_image")))
        from pypdf import PdfReader
        pg0 = PdfReader(pdf).pages[0]
        summary["page_size_pt"] = [round(float(pg0.mediabox.width)), round(float(pg0.mediabox.height))]
        # standalone html: the page with contents numbers filled in is already saved
    except Exception as e:
        summary["error"] = f"{type(e).__name__}: {e}"
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
