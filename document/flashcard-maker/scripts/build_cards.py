#!/usr/bin/env python3
"""Build a flashcard deck (HTML), a print sheet (PDF) and a CSV from one spec file, and check they match.

Usage: python build_cards.py SKILL_DIR/templates/deck.html SPEC.json OUT_DIR BASENAME
SPEC.json: {"config": {title, lang, dir, frontLabel, backLabel, ui: {...}},
            "cards": [{"front": str, "back": str, "extra": str (optional)}, ...]}
Writes OUT_DIR/BASENAME.html, BASENAME-print.pdf (if Chrome is found), BASENAME.csv
"""
import csv, html, json, math, os, re, shutil, subprocess, sys

PER_PAGE = 8  # 2 columns x 4 rows


def between(text, start, end):
    return text.index(start) + len(start), text.index(end)


def find_chrome():
    env = os.environ.get("CHROME_BIN")
    if env and os.path.exists(env):
        return env
    for n in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable", "chrome"):
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


def cell(card, label, text, extra, rtl, size_class):
    d = ' dir="rtl"' if rtl else ""
    ex = f'<div class="ex">{html.escape(extra)}</div>' if extra else ""
    return (f'<div class="cell"><span class="lab">{html.escape(label)}</span>'
            f'<div class="t {size_class}"{d}>{html.escape(text)}</div>{ex}</div>')


def size_class(*texts):
    n = max(len(t) for t in texts if t is not None)
    return "s3" if n > 160 else "s2" if n > 80 else "s1"


def print_html(cfg, cards):
    rtl = cfg.get("dir") == "rtl"
    pages = []
    for start in range(0, len(cards), PER_PAGE):
        chunk = cards[start:start + PER_PAGE]
        chunk = chunk + [None] * (PER_PAGE - len(chunk))
        fronts, backs = [], []
        for i in range(0, PER_PAGE, 2):
            row = chunk[i:i + 2]
            fronts += row
            backs += row[::-1]  # mirror columns so the back sits behind its front when flipped on the long edge

        def make(seq, side):
            out = []
            for c in seq:
                if c is None:
                    out.append('<div class="cell empty"></div>')
                    continue
                sc = size_class(c["front"], c["back"], c.get("extra", ""))
                if side == "front":
                    out.append(cell(c, cfg["frontLabel"], c["front"], "", rtl, sc))
                else:
                    out.append(cell(c, cfg["backLabel"], c["back"], c.get("extra", ""), rtl, sc))
            return "".join(out)
        pages.append(f'<section class="page">{make(fronts, "front")}</section>')
        pages.append(f'<section class="page">{make(backs, "back")}</section>')
    css = """
@page{size:A4;margin:10mm}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","Noto Sans CJK SC","Noto Sans CJK KR","Noto Naskh Arabic",sans-serif;color:#1c2233}
.page{width:190mm;height:276mm;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(4,1fr);direction:ltr;break-after:page;overflow:hidden}
.page:last-child{break-after:auto}
.cell{position:relative;border:0.4mm dashed #8a93a8;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:8mm 6mm 6mm;overflow:hidden}
.cell.empty{border-color:transparent}
.lab{position:absolute;top:2.5mm;left:3mm;font-size:7pt;color:#6b7488;text-transform:uppercase;letter-spacing:.05em}
.t{font-weight:700;line-height:1.25}
.s1{font-size:18pt}.s2{font-size:14pt}.s3{font-size:10.5pt;font-weight:600}
.ex{margin-top:3mm;font-size:9.5pt;font-style:italic;color:#4a5368}
"""
    lang = html.escape(cfg.get("lang", "en"))
    return f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(pages)}</body></html>'


def main():
    tpl_path, spec_path, out_dir, base = sys.argv[1:5]
    os.makedirs(out_dir, exist_ok=True)
    tpl = open(tpl_path, encoding="utf-8").read()
    spec = json.load(open(spec_path, encoding="utf-8"))
    a, b = between(tpl, "/*CONFIG_START*/", "/*CONFIG_END*/")
    default = json.loads(re.search(r"const CONFIG = (\{.*\});", tpl[a:b], re.S).group(1))
    cfg = dict(default)
    for k, v in spec.get("config", {}).items():
        cfg[k] = {**default["ui"], **v} if k == "ui" else v
    if cfg["dir"] not in ("ltr", "rtl"):
        sys.exit("ERROR: config.dir must be ltr or rtl")
    if cfg.get("lang", "en") != "en":
        missing = [k for k in default["ui"] if cfg["ui"][k] == default["ui"][k]]
        if missing:
            print("WARNING: ui texts still in English, translate them unless identical in the language: " + ", ".join(missing))
        if cfg["frontLabel"] == default["frontLabel"] or cfg["backLabel"] == default["backLabel"]:
            print("WARNING: frontLabel/backLabel still English")
    cards = spec["cards"]
    errs = []
    if not 1 <= len(cards) <= 60:
        errs.append(f"{len(cards)} cards (expected 1 to 60)")
    seen = set()
    for i, c in enumerate(cards, 1):
        if not str(c.get("front", "")).strip() or not str(c.get("back", "")).strip():
            errs.append(f"card {i}: empty front or back")
        key = str(c.get("front", "")).strip().lower()
        if key in seen:
            errs.append(f"card {i}: duplicate front '{c.get('front')}'")
        seen.add(key)
    if errs:
        sys.exit("ERROR: " + "; ".join(errs))
    # 1. interactive deck
    out = tpl[:a] + "\nconst CONFIG = " + json.dumps(cfg, ensure_ascii=False, indent=2).replace("</", "<\\/") + ";\n" + tpl[b:]
    a, b = between(out, "/*CARDS_START*/", "/*CARDS_END*/")
    out = out[:a] + "\nconst CARDS = " + json.dumps(cards, ensure_ascii=False, indent=1).replace("</", "<\\/") + ";\n" + out[b:]
    deck_path = os.path.join(out_dir, base + ".html")
    open(deck_path, "w", encoding="utf-8").write(out)
    # 2. csv (UTF-8 with BOM so spreadsheets read other alphabets)
    csv_path = os.path.join(out_dir, base + ".csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        for c in cards:
            w.writerow([c["front"], c["back"] + (" | " + c["extra"] if c.get("extra") else "")])
    # 3. print pdf
    ph = print_html(cfg, cards)
    ph_path = os.path.join(out_dir, base + "-print.html")
    open(ph_path, "w", encoding="utf-8").write(ph)
    pdf_path = os.path.join(out_dir, base + "-print.pdf")
    chrome = find_chrome()
    expected_pages = 2 * math.ceil(len(cards) / PER_PAGE)
    pdf_ok = False
    if chrome:
        subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=" + pdf_path, "file://" + os.path.abspath(ph_path)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if os.path.exists(pdf_path):
            from pypdf import PdfReader
            n = len(PdfReader(pdf_path).pages)
            if n != expected_pages or n % 2:
                sys.exit(f"ERROR: PDF has {n} pages, expected {expected_pages} (even). Shorten very long card text and run again.")
            pdf_ok = True
    # 4. consistency report
    html_count = len(re.findall(r'"front":', open(deck_path, encoding="utf-8").read()))
    csv_count = len(list(csv.reader(open(csv_path, encoding="utf-8-sig"))))
    print_count = ph.count('class="cell"') // 2
    print(f"CHECK cards in spec={len(cards)} html={html_count} csv={csv_count} print_cells={print_count}")
    if not (len(cards) == html_count == csv_count == print_count):
        sys.exit("ERROR: counts differ between spec, html, csv and print sheet")
    print("DECK", deck_path)
    print("CSV", csv_path)
    print("PDF", pdf_path if pdf_ok else "NOT BUILT (Chrome not found): publish the print html instead: " + ph_path)
    if pdf_ok:
        print(f"PDF pages={expected_pages} (fronts and backs alternate, {math.ceil(len(cards)/PER_PAGE)} sheets)")
    for i, c in enumerate(cards, 1):
        print(f"{i}. {c['front']} -> {c['back']}")


main()
