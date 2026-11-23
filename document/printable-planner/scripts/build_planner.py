#!/usr/bin/env python3
"""Check a weekly plan and render it as a one-page PDF (HTML to PDF with headless Chrome).

Usage: python build_planner.py SPEC.json OUT_DIR BASENAME
SPEC.json common keys:
  mode: "time" | "grid";  title; subtitle (optional); lang; dir ("ltr"|"rtl");
  orientation: "landscape" | "portrait" (default landscape); days: [day names in the user's language];
  footer (optional one line, e.g. a note)
  avoid (optional): words the plan must not contain (foods the user cannot eat); checked in every label and cell
mode "time": a time grid, days across, hours down.
  entries: [{"day": 0-based index into days, "start": "HH:MM", "end": "HH:MM", "label": str,
             "kind": "fixed" | "task" | "rest"}]   fixed = commitments the user gave (school, work, class)
  limits (optional): {"earliest": "HH:MM", "latest": "HH:MM"}  applied to kind "task" entries
  targets (optional): {"<label>": hours per week}  checked against the entries (+- 0.01 h)
  step (optional): 30 or 60; default: 60 if every time is on the hour, else 30
mode "grid": named rows (meals, exercises, chores) x days.
  rows: [row names]; cells: [{"day": i, "row": j, "text": str}]
Writes OUT_DIR/BASENAME.html and BASENAME.pdf and prints a check report.
"""
import html, json, math, os, shutil, subprocess, sys

PALETTE = ["#dbe7ff", "#ffe3d1", "#dff3e1", "#f3e1fb", "#fff2c2", "#d9f2f4", "#fde0e8", "#e7ecd1"]


def hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def fmt(t):
    return f"{t // 60:02d}:{t % 60:02d}"


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


def check_time(spec):
    errs, report = [], []
    days = spec["days"]
    es = spec["entries"]
    for i, e in enumerate(es):
        try:
            e["s"], e["e"] = hm(e["start"]), hm(e["end"])
        except Exception:
            errs.append(f"entry {i + 1} ({e.get('label')}): times must look like 08:30")
            continue
        if not (isinstance(e.get("day"), int) and 0 <= e["day"] < len(days)):
            errs.append(f"entry {i + 1} ({e.get('label')}): day must be an index 0 to {len(days) - 1}")
        if e["e"] <= e["s"]:
            errs.append(f"entry {i + 1} ({e.get('label')}): end must be after start")
        e.setdefault("kind", "task")
    if errs:
        return errs, report
    lim = spec.get("limits", {})
    for e in es:
        if e["kind"] == "task":
            if "earliest" in lim and e["s"] < hm(lim["earliest"]):
                errs.append(f"{e['label']} on {days[e['day']]} starts at {e['start']}, before {lim['earliest']}")
            if "latest" in lim and e["e"] > hm(lim["latest"]):
                errs.append(f"{e['label']} on {days[e['day']]} ends at {e['end']}, after {lim['latest']}")
    for d in range(len(days)):
        day = sorted([e for e in es if e["day"] == d], key=lambda x: x["s"])
        for a, b in zip(day, day[1:]):
            if b["s"] < a["e"]:
                errs.append(f"overlap on {days[d]}: {a['label']} {a['start']}-{a['end']} and {b['label']} {b['start']}-{b['end']}")
    tot = {}
    for e in es:
        tot[e["label"]] = tot.get(e["label"], 0) + (e["e"] - e["s"]) / 60
    for k, v in tot.items():
        report.append(f"TOTAL {k}: {v:g} h per week")
    for k, v in spec.get("targets", {}).items():
        got = tot.get(k, 0)
        if abs(got - v) > 0.01:
            errs.append(f"{k}: plan has {got:g} h per week, wanted {v:g} h")
        else:
            report.append(f"TARGET OK {k}: {got:g} h")
    return errs, report


def render_time(spec):
    es = spec["entries"]
    days = spec["days"]
    step = spec.get("step")
    if not step:
        step = 60 if all(e["s"] % 60 == 0 and e["e"] % 60 == 0 for e in es) else 30
    for e in es:
        if e["s"] % step or e["e"] % step:
            raise SystemExit(f"ERROR: {e['label']} {e['start']}-{e['end']} does not fit the {step}-minute grid; set step to 30 or round the times")
    t0 = min(e["s"] for e in es) // 60 * 60
    t1 = math.ceil(max(e["e"] for e in es) / 60) * 60
    n = (t1 - t0) // step
    colors, cells = {}, []
    for c in range(len(days)):
        for r in range(n):
            cells.append(f'<div class="bg" style="grid-column:{c + 2};grid-row:{r + 2}"></div>')
    for r in range(n):
        t = t0 + r * step
        cells.append(f'<div class="tm" style="grid-column:1;grid-row:{r + 2}">{fmt(t)}</div>')
    for c, d in enumerate(days):
        cells.append(f'<div class="dh" style="grid-column:{c + 2};grid-row:1">{html.escape(d)}</div>')
    blocks = []
    for e in es:
        if e["kind"] == "fixed":
            bg = "#e3e6ec"
        else:
            bg = colors.setdefault(e["label"], PALETTE[len(colors) % len(PALETTE)])
        r0, r1 = (e["s"] - t0) // step, (e["e"] - t0) // step
        small = " sm" if r1 - r0 == 1 and step == 30 else ""
        blocks.append(f'<div class="blk{small}" style="grid-column:{e["day"] + 2};grid-row:{r0 + 2}/{r1 + 2};background:{bg}">'
                      f'<b>{html.escape(e["label"])}</b><span>{e["start"]}-{e["end"]}</span></div>')
    cols = f"13mm repeat({len(days)}, 1fr)"
    return cols, f"7mm repeat({n}, 1fr)", "".join(cells + blocks), n


def render_grid(spec):
    days, rows = spec["days"], spec["rows"]
    cells = []
    for c, d in enumerate(days):
        cells.append(f'<div class="dh" style="grid-column:{c + 2};grid-row:1">{html.escape(d)}</div>')
    for r, name in enumerate(rows):
        cells.append(f'<div class="rh" style="grid-column:1;grid-row:{r + 2}">{html.escape(name)}</div>')
        for c in range(len(days)):
            cells.append(f'<div class="bg" style="grid-column:{c + 2};grid-row:{r + 2}"></div>')
    for cell in spec["cells"]:
        cells.append(f'<div class="txt" style="grid-column:{cell["day"] + 2};grid-row:{cell["row"] + 2}">{html.escape(cell["text"])}</div>')
    return f"26mm repeat({len(days)}, 1fr)", f"7mm repeat({len(rows)}, 1fr)", "".join(cells), len(rows)


def main():
    spec_path, out_dir, base = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    spec = json.load(open(spec_path, encoding="utf-8"))
    mode = spec.get("mode")
    errs, report = [], []
    days = spec.get("days", [])
    if mode not in ("time", "grid") or not days:
        sys.exit("ERROR: mode must be time or grid, and days must be a list")
    if mode == "time":
        errs, report = check_time(spec)
    else:
        for i, c in enumerate(spec.get("cells", [])):
            if not (0 <= c.get("day", -1) < len(days) and 0 <= c.get("row", -1) < len(spec.get("rows", []))):
                errs.append(f"cell {i + 1}: day or row out of range")
        report.append(f"CELLS filled: {len(spec.get('cells', []))} of {len(days) * len(spec.get('rows', []))}")
    texts = [e.get("label", "") for e in spec.get("entries", [])] + [c.get("text", "") for c in spec.get("cells", [])]
    for w in spec.get("avoid", []):
        for t in texts:
            if w.lower() in t.lower():
                errs.append(f"'{t}' contains the word to avoid: {w}")
    if errs:
        print("ERRORS (fix the plan and run again):")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    cols, rows, body, nrows = render_time(spec) if mode == "time" else render_grid(spec)
    land = spec.get("orientation", "landscape") != "portrait"
    size = "A4 landscape" if land else "A4"
    dr = spec.get("dir", "ltr")
    ph = 190 if land else 277
    title_h = 16 if spec.get("subtitle") else 11
    foot = f'<div class="foot">{html.escape(spec["footer"])}</div>' if spec.get("footer") else ""
    fs = "7.5pt" if nrows > 16 else "9pt"
    css = f"""
@page{{size:{size};margin:10mm}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","Noto Sans CJK SC","Noto Sans CJK KR","Noto Naskh Arabic",sans-serif;color:#1c2233;font-size:{fs}}}
.page{{height:{ph - 2}mm;display:flex;flex-direction:column;overflow:hidden;direction:{dr}}}
h1{{margin:0;font-size:17pt;line-height:1.1}}
.sub{{color:#5b6478;font-size:9pt;margin-top:1mm}}
.head{{height:{title_h}mm;flex:none}}
.foot{{flex:none;height:6mm;color:#5b6478;font-size:8pt;padding-top:1.5mm}}
.grid{{flex:1;min-height:0;display:grid;grid-template-columns:{cols};grid-template-rows:{rows};gap:0;direction:{dr}}}
.bg{{border-bottom:0.25mm solid #c9cfdb;border-inline-end:0.25mm solid #c9cfdb}}
.grid{{border-top:0.25mm solid #c9cfdb;border-inline-start:0.25mm solid #c9cfdb}}
.dh{{background:#1c2233;color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:9.5pt;border-inline-end:0.25mm solid #fff}}
.tm,.rh{{font-size:7pt;color:#5b6478;display:flex;align-items:center;justify-content:center;border-bottom:0.25mm solid #c9cfdb;border-inline-end:0.25mm solid #c9cfdb;text-align:center;padding:0 1mm;font-weight:{'700' if mode == 'grid' else '400'}}}
.rh{{font-size:9pt;color:#1c2233;background:#f1f3f8}}
.blk{{margin:0.4mm;border-radius:1.5mm;padding:0.8mm 1.5mm;overflow:hidden;display:flex;flex-direction:column;justify-content:center;z-index:1;line-height:1.15}}
.blk b{{font-size:{fs}}}.blk span{{font-size:6.5pt;color:#4a5368}}
.blk.sm{{flex-direction:row;gap:2mm;align-items:center;padding:0 1.5mm}}
.txt{{padding:1.2mm;font-size:{'11pt' if mode == 'grid' and nrows <= 8 else fs};z-index:1;display:flex;align-items:center;justify-content:center;text-align:center;line-height:1.2;overflow:hidden}}
"""
    sub = f'<div class="sub">{html.escape(spec["subtitle"])}</div>' if spec.get("subtitle") else ""
    doc = (f'<!DOCTYPE html><html lang="{html.escape(spec.get("lang", "en"))}" dir="{dr}"><head><meta charset="utf-8"><style>{css}</style></head><body>'
           f'<div class="page"><div class="head"><h1>{html.escape(spec.get("title", ""))}</h1>{sub}</div>'
           f'<div class="grid">{body}</div>{foot}</div></body></html>')
    hp = os.path.join(out_dir, base + ".html")
    open(hp, "w", encoding="utf-8").write(doc)
    pdf = os.path.join(out_dir, base + ".pdf")
    chrome = find_chrome()
    for line in report:
        print(line)
    if not chrome:
        print("PDF NOT BUILT (Chrome not found): publish this html instead:", hp)
        return
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + pdf, "file://" + os.path.abspath(hp)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    from pypdf import PdfReader
    n = len(PdfReader(pdf).pages)
    print("PDF", pdf, "pages =", n)
    if n != 1:
        sys.exit("ERROR: the plan spilled onto more than one page: use fewer rows (step 60), shorter labels or portrait/landscape")
    print("OK one page")


main()
