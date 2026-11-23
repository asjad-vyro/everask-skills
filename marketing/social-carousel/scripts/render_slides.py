#!/usr/bin/env python3
"""Render each <section class="slide" id="sN"> of a page to its own PNG with headless Chrome.
Usage: python3 render_slides.py PAGE.html OUT_DIR [WIDTH HEIGHT]
Writes OUT_DIR/slide-01.png ... and prints each file's size. Exit code 1 if Chrome is missing or a size is wrong."""
import re, shutil, subprocess, sys, pathlib

page = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
W = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
H = int(sys.argv[4]) if len(sys.argv) > 4 else 1350
out.mkdir(parents=True, exist_ok=True)

def find_chrome():
    import glob, os
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome", "google-chrome-stable"):
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
    return mac if pathlib.Path(mac).exists() else None


chrome = find_chrome()
if not chrome:
    print("CHROME NOT FOUND")
    sys.exit(1)

html = page.read_text(encoding="utf-8")
ids = re.findall(r'<section[^>]*class="[^"]*\bslide\b[^"]*"[^>]*id="(s\d+)"', html) or \
      re.findall(r'<section[^>]*id="(s\d+)"[^>]*class="[^"]*\bslide\b', html)
if not ids:
    print("NO SLIDES FOUND (need <section class=\"slide\" id=\"s1\"> ...)")
    sys.exit(1)

bad = 0
for i, sid in enumerate(ids, 1):
    css = (f"<style>:root{{--w:{W}px;--h:{H}px}}html,body{{width:{W}px;height:{H}px;overflow:hidden}}"
           f".slide{{display:none!important}}#{sid}{{display:flex!important}}</style>")
    tmp = page.parent / f"_render_{sid}.html"
    tmp.write_text(html.replace("</head>", css + "</head>", 1), encoding="utf-8")
    png = out / f"slide-{i:02d}.png"
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={W},{H}", f"--screenshot={png}", tmp.as_uri()],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    tmp.unlink(missing_ok=True)
    try:
        from PIL import Image
        size = Image.open(png).size
    except Exception as e:
        size = None
    ok = size == (W, H)
    bad += not ok
    print(f"{png.name} {size} {'OK' if ok else 'WRONG SIZE'}")
sys.exit(1 if bad else 0)
