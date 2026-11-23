#!/usr/bin/env python3
"""Turn the picture-book page.html into a PDF with headless Chrome and check it.
Usage: python3 build_pdf.py PAGE.html OUT.pdf EXPECTED_PAGES
Also writes OUT-standalone.html next to the PDF (pictures inlined) for use when Chrome is missing.
Prints page count, page size and any page whose text comes within 25 points of the bottom edge.
Exit 1 if Chrome is missing, the page count is wrong or text is too close to an edge."""
import base64, glob, os, re, shutil, subprocess, sys, pathlib


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


page = pathlib.Path(sys.argv[1]).resolve()
pdf = pathlib.Path(sys.argv[2]).resolve()
expected = int(sys.argv[3])
html = page.read_text(encoding="utf-8")


def inline(m):
    f = page.parent / m.group(1)
    if not f.exists():
        return m.group(0)
    return 'src="data:image/png;base64,' + base64.b64encode(f.read_bytes()).decode() + '"'


standalone = pdf.with_name(pdf.stem + "-standalone.html")
standalone.write_text(re.sub(r'src="([^"]+\.png)"', inline, html), encoding="utf-8")
print("standalone html:", standalone)

chrome = find_chrome()
if not chrome:
    print("CHROME NOT FOUND")
    sys.exit(1)
subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                "--virtual-time-budget=4000", f"--print-to-pdf={pdf}", page.as_uri()],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
bad = 0
try:
    import fitz
    d = fitz.open(str(pdf))
    n = len(d)
    print("pages", n, "expected", expected, "OK" if n == expected else "WRONG PAGE COUNT", "size", tuple(round(x) for x in d[0].rect)[2:])
    bad += n != expected
    for i, p in enumerate(d, 1):
        mx = max([b[3] for b in p.get_text("blocks") if not b[4].strip().isdigit()] or [0])
        if mx > p.rect.height - 25:
            print(f"page {i}: text reaches {round(mx)} of {round(p.rect.height)} - TOO CLOSE TO THE EDGE, shorten or shrink it")
            bad += 1
except Exception as e:
    print("could not check the PDF:", e)
    bad += 1
sys.exit(1 if bad else 0)
