#!/usr/bin/env python3
"""Render a one-page infographic HTML to PNG and PDF with headless Chrome and check the sizes.
Usage: python3 render.py PAGE.html OUT_DIR [NAME]
Writes OUT_DIR/NAME.png (1080x1920) and OUT_DIR/NAME.pdf (1 page). Exit 1 if Chrome is missing or a check fails."""
import glob, os, shutil, subprocess, sys, pathlib


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
out = pathlib.Path(sys.argv[2]).resolve()
name = sys.argv[3] if len(sys.argv) > 3 else "infographic"
out.mkdir(parents=True, exist_ok=True)
chrome = find_chrome()
if not chrome:
    print("CHROME NOT FOUND")
    sys.exit(1)
png, pdf = out / f"{name}.png", out / f"{name}.pdf"
base = [chrome, "--headless", "--no-sandbox", "--disable-gpu"]
kw = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
subprocess.run(base + ["--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1080,1920",
                       f"--screenshot={png}", page.as_uri()], **kw)
subprocess.run(base + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", page.as_uri()], **kw)
bad = 0
try:
    from PIL import Image
    size = Image.open(png).size
except Exception:
    size = None
print(png.name, size, "OK" if size == (1080, 1920) else "WRONG SIZE")
bad += size != (1080, 1920)
try:
    from pypdf import PdfReader
    n = len(PdfReader(str(pdf)).pages)
except Exception:
    n = None
print(pdf.name, "pages", n, "OK" if n == 1 else "WRONG PAGE COUNT")
bad += n != 1
sys.exit(1 if bad else 0)
