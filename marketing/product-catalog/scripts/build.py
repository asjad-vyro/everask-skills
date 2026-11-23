#!/usr/bin/env python3
"""Build a catalogue / price list PDF from a JSON file with templates/catalog.html and headless Chrome.

Usage: python3 build.py DATA.json OUTDIR
Optional "price_change_percent" in the JSON changes every price that holds a number (done here with Decimal, rounded half up
to the same number of decimals as the original). Prints a JSON summary with checks.
"""
import base64, html, json, mimetypes, os, re, shutil, subprocess, sys
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "catalog.html")
PAGES = {"a4": ("A4", "297mm"), "letter": ("Letter", "11in"), "a5": ("A5", "210mm")}
THEMES = {"blue": ("#1f4e8c", "#f1f5fa"), "green": ("#2f6b45", "#f1f7f3"), "burgundy": ("#7a1f2b", "#f8f2f3"),
          "charcoal": ("#333333", "#f4f4f4"), "teal": ("#176b6b", "#f0f7f7"), "orange": ("#c2571a", "#fbf4ee"),
          "purple": ("#5b3a8c", "#f5f2fa")}
RTL = {"ar", "he", "fa", "ur"}
NUM = re.compile(r"\d[\d.,]*")


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


def change_price(text, pct):
    """Apply pct to the first number in text, keeping symbol, decimal mark and decimals. Returns text unchanged if no number."""
    m = NUM.search(str(text))
    if not m:
        return text
    raw = m.group(0).rstrip(".,")
    # decide decimal mark: the last separator followed by 1-2 digits is decimal
    dm = re.search(r"([.,])(\d{1,2})$", raw)
    if dm:
        dec_mark, decs = dm.group(1), len(dm.group(2))
        other = "," if dec_mark == "." else "."
        num = Decimal(raw.replace(other, "").replace(dec_mark, "."))
    else:
        dec_mark, decs, other = ".", 0, (re.search(r"[.,]", raw).group(0) if re.search(r"[.,]", raw) else "")
        num = Decimal(raw.replace(".", "").replace(",", ""))
    new = (num * (Decimal(100) + Decimal(str(pct))) / Decimal(100)).quantize(Decimal(1).scaleb(-decs), rounding=ROUND_HALF_UP)
    s = f"{new:,.{decs}f}"  # 1,234.50
    if other or dec_mark == ",":
        # rebuild with the original marks
        thousands = other if other else ("." if dec_mark == "," else ",")
        s = s.replace(",", "\0").replace(".", dec_mark).replace("\0", thousands if (other and num >= 1000) else "")
    return str(text)[:m.start()] + s + str(text)[m.start() + len(raw):]


def img_tag(path):
    if not path or not os.path.exists(path):
        return ""
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return f'<img src="data:{mime};base64,{base64.b64encode(open(path, "rb").read()).decode()}" alt="">'


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    name = data.get("filename", "catalogue")
    lang = data.get("lang", "en")
    pct = data.get("price_change_percent")
    labels = {"code": "Code", "name": "Product", "desc": "Description", "unit": "Unit", "price": "Price", "image": ""}
    labels.update(data.get("labels", {}))
    cats = data.get("categories", [])
    changed = []
    toc, blocks, n_items, heads = [], [], 0, {}
    for c in cats:
        items = c.get("items", [])
        n_items += len(items)
        if pct not in (None, 0, "0"):
            for it in items:
                old = it.get("price", "")
                if str(old).strip():
                    it["price"] = change_price(old, pct)
                    changed.append([old, it["price"]])
        cols = [k for k in ("image", "code", "name", "desc", "unit", "price")
                if any(str(it.get(k, "")).strip() for it in items)]
        head = "".join(f'<th class="{k}">{esc(labels.get(k, k))}</th>' for k in cols)
        rows = []
        for it in items:
            tds = []
            for k in cols:
                v = img_tag(it.get("image")) if k == "image" else esc(it.get(k, ""))
                tds.append(f'<td class="{k}">{v}</td>')
            rows.append(f'<tr class="product">{"".join(tds)}</tr>')
        cd = f'<p class="catdesc">{esc(c["note"])}</p>' if c.get("note") else ""
        np_ = " newpage" if data.get("page_per_category") else ""
        blocks.append(f'<div class="cat{np_}"><h2>{esc(c.get("name",""))}</h2>{cd}<table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
        toc.append(c.get("name", ""))
        heads[c.get("name", "")] = " ".join(str(labels.get(k, k)) for k in cols)
    theme = THEMES.get(str(data.get("theme", "blue")).lower(), THEMES["blue"])
    pname, ph = PAGES.get(str(data.get("size", "a4")).lower(), PAGES["a4"])
    def make_toc(pages):
        lis = "".join(f'<li><span>{esc(t)}</span><span>{esc(pages.get(t, ""))}</span></li>' for t in toc)
        return (f'<div class="toc"><h3>{esc(data.get("contents_label", "Contents"))}</h3><ul>{lis}</ul></div>'
                if len(cats) > 1 and data.get("cover", True) else "<div></div>")
    cover_on = data.get("cover", True)
    head_html = (f'<div class="cover"><div><div class="co">{esc(data.get("company", ""))}</div></div>'
                 f'<div><h1>{esc(data.get("title", ""))}</h1>{{SUB}}</div>{{TOC}}</div>' if cover_on else
                 f'<div class="plainhead"><div class="co">{esc(data.get("company", ""))}</div>'
                 f'<h1>{esc(data.get("title", ""))}</h1>{{SUB}}</div>')
    sub_html = f'<div class="sub">{esc(data["subtitle"])}</div>' if data.get("subtitle") else ""
    rep = {"LANG": esc(lang), "DIR": "rtl" if lang.split("-")[0] in RTL else "ltr", "DOC_TITLE": esc(data.get("title", "")),
           "PAGE": pname, "COVER_H": ph, "ACCENT": theme[0], "TINT": theme[1], "COMPANY": esc(data.get("company", "")),
           "CATEGORIES": "\n".join(blocks),
           "FIRST_PAGE_CSS": "@page :first { margin: 0; @bottom-center { content: none; } }" if cover_on else "",
           "NOTE": f'<p class="note">{esc(data["note"])}</p>' if data.get("note") else ""}
    tpl = open(TEMPLATE, encoding="utf-8").read()

    def render_page(pages):
        pg = tpl.replace("{{HEAD}}", head_html.replace("{SUB}", sub_html).replace("{TOC}", make_toc(pages)))
        for k, v in rep.items():
            pg = pg.replace("{{" + k + "}}", str(v))
        return pg
    page = render_page({})
    hp = os.path.abspath(os.path.join(out, name + ".html"))
    open(hp, "w", encoding="utf-8").write(page)
    # check every name, code and price is in the page
    missing = []
    for c in cats:
        for it in c.get("items", []):
            for k in ("name", "code", "price"):
                v = str(it.get(k, "")).strip()
                if v and esc(v) not in page:
                    missing.append(v)
    summary = {"html": hp, "categories": len(cats), "items": n_items, "items_in_html": page.count('class="product"'),
               "missing_from_html": missing}
    if changed:
        summary["price_changes"] = changed
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
        if cover_on and len(cats) > 1:
            # second pass: put real page numbers in the contents (first page after the cover with a line equal to the category name)
            texts = [" ".join((pg.extract_text() or "").split()).casefold() for pg in PdfReader(pdf).pages]
            found = {}
            for t in toc:
                key = " ".join((t + " " + heads.get(t, "")).split()).casefold()  # heading followed by its table header row
                for i in range(1, len(texts)):
                    if key in texts[i]:
                        found[t] = i + 1
                        break
            if len(found) == len(toc):
                page2 = render_page(found)
                open(hp, "w", encoding="utf-8").write(page2)
                subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                                "--print-to-pdf=" + pdf, "file://" + hp], capture_output=True, timeout=180)
                summary["contents_page_numbers"] = found
                summary["pdf_pages"] = len(PdfReader(pdf).pages)
    except Exception:
        try:
            summary["pdf_pages"] = len(re.findall(rb"/Type\s*/Page[^s]", open(pdf, "rb").read()))
        except Exception:
            summary["pdf_pages"] = None
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
