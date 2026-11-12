#!/usr/bin/env python3
"""Build one self-contained generative-art page from a spec and a p5.js sketch.

Usage:
    python3 build_art.py --spec spec.json --sketch sketch.js --out piece.html

The page shell is ../templates/viewer.html. The script checks the spec and the
sketch first; if anything is wrong it prints ERROR lines and writes nothing.
It reads the two input files and the template, and writes the one output file.
Standard library only (it calls `node --check` for a syntax check when node exists).
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "viewer.html"

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
RESERVED_IDS = {"seed", "colorPalette"}
PAGE_NAMES = ("params", "defaultParams", "SPEC", "Studio")
MAX_PARAMS = 10
MAX_COLORS = 8

# p5 functions and constants that do not exist yet while the file loads.
P5_FUNCS = (
    "color|random|randomGaussian|noise|createVector|createGraphics|lerpColor|constrain|map|dist|lerp|norm|"
    "sin|cos|tan|atan2|sqrt|abs|floor|ceil|round|radians|degrees"
)
P5_NAMES = "width|height|PI|TWO_PI|HALF_PI|QUARTER_PI|TAU"
# Names of p5 functions that a sketch should not redeclare at the top level.
P5_SHADOW = (
    "color|random|noise|map|scale|rotate|translate|filter|text|image|fill|stroke|line|point|rect|circle|"
    "ellipse|shuffle|sort|split|join|round|floor|ceil|dist|lerp|norm|min|max|constrain|red|green|blue|alpha|"
    "hue|brightness|saturation|push|pop|key|frameCount|width|height|print|blend|copy|get|set|erase|fract|sq|"
    "sqrt|pow|exp|log|mag|loop|clear|shape|vertex|curve|bezier|triangle|quad|arc|square|save|millis"
)


# ---------------------------------------------------------------- helpers

def clean(x):
    """1.0 -> 1, so numbers print the same in Python and in JavaScript."""
    return int(x) if float(x).is_integer() else x


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and abs(x) != float("inf")


def decimals(step):
    s = repr(step)
    if "e-" in s:
        return min(8, int(s.split("e-")[1]))
    return len(s.split(".")[1]) if "." in s else 0


def fmt(value, step):
    return f"{value:.{decimals(step)}f}"


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "generative-art"


def mask(code, blank_strings):
    """Blank out comments (and, if asked, the inside of strings), keeping line breaks and length."""
    out = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = code.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        elif c == "/" and nxt == "*":
            j = code.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append(re.sub(r"[^\n]", " ", code[i:j]))
            i = j
        elif c in "\"'`":
            j = i + 1
            while j < n and code[j] != c:
                if code[j] == "\\":
                    j += 1
                j += 1
            j = min(j + 1, n)
            if blank_strings:
                out.append(c + re.sub(r"[^\n]", " ", code[i + 1:max(i + 1, j - 1)]) + (c if j - i >= 2 else ""))
            else:
                out.append(code[i:j])
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def top_level_lines(code):
    """(line number, text) for the parts of the file that sit outside every { } block."""
    text = mask(code, True)
    text = re.sub(r"\bfunction\b[^(){]*\([^)]*\)", "function", text)  # drop function headers
    text = re.sub(r"\([^()]*\)\s*=>", "=>", text)                      # drop arrow-function parameter lists
    depth = 0
    lines = []
    for number, line in enumerate(text.split("\n"), 1):
        kept = []
        for ch in line:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            elif depth == 0:
                kept.append(ch)
        lines.append((number, "".join(kept)))
    return lines


# ---------------------------------------------------------------- spec

def check_spec(spec):
    """Return (errors, cleaned spec)."""
    errors = []
    if not isinstance(spec, dict):
        return ["spec.json must be a JSON object."], None
    out = {}

    title = spec.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append('"title" is required: a short name for the piece.')
        title = "Untitled"
    out["title"] = title.strip()[:80]

    subtitle = spec.get("subtitle", "")
    out["subtitle"] = subtitle.strip()[:200] if isinstance(subtitle, str) else ""

    seed = spec.get("seed")
    if not (is_num(seed) and float(seed).is_integer() and 1 <= seed <= 999999):
        errors.append('"seed" must be a whole number from 1 to 999999.')
        seed = 1
    out["seed"] = int(seed)

    canvas = spec.get("canvas", [1200, 1200])
    if not (isinstance(canvas, list) and len(canvas) == 2
            and all(is_num(v) and float(v).is_integer() and 300 <= v <= 2400 for v in canvas)):
        errors.append('"canvas" must be [width, height], whole numbers from 300 to 2400 (default [1200, 1200]).')
        canvas = [1200, 1200]
    out["canvas"] = [int(canvas[0]), int(canvas[1])]

    params = spec.get("params", [])
    if not isinstance(params, list) or len(params) > MAX_PARAMS:
        errors.append(f'"params" must be a list of at most {MAX_PARAMS} sliders.')
        params = []
    out["params"] = []
    seen = set()
    for i, p in enumerate(params):
        where = f"params[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{where} must be an object.")
            continue
        pid = p.get("id")
        if not (isinstance(pid, str) and IDENT.match(pid)) or pid in RESERVED_IDS:
            errors.append(f'{where}: "id" must be letters, digits or underscore, must not start with a digit, '
                          'and must not be "seed" or "colorPalette".')
            continue
        if pid in seen:
            errors.append(f'{where}: the id "{pid}" is used twice.')
            continue
        seen.add(pid)
        label = p.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(f'{where} ({pid}): "label" is required.')
            label = pid
        values = [p.get(k) for k in ("min", "max", "step", "value")]
        if not all(is_num(v) for v in values):
            errors.append(f'{where} ({pid}): "min", "max", "step" and "value" must all be numbers.')
            continue
        lo, hi, step, val = (clean(v) for v in values)
        if not lo < hi:
            errors.append(f'{where} ({pid}): "min" must be below "max".')
            continue
        if not 0 < step <= hi - lo:
            errors.append(f'{where} ({pid}): "step" must be above 0 and no larger than max minus min.')
            continue
        if not lo <= val <= hi:
            errors.append(f'{where} ({pid}): "value" must be between "min" and "max".')
            continue
        k = (val - lo) / step
        if abs(k - round(k)) > 1e-6:
            errors.append(f'{where} ({pid}): "value" {val} is not on the slider grid. '
                          f'It must be min ({lo}) plus a whole number of steps ({step}).')
            continue
        live = p.get("live", False)
        if not isinstance(live, bool):
            errors.append(f'{where} ({pid}): "live" must be true or false.')
            live = False
        out["params"].append({"id": pid, "label": label.strip()[:60], "min": lo, "max": hi,
                              "step": step, "value": val, "live": live})

    colors = spec.get("colors", [])
    if not isinstance(colors, list) or len(colors) > MAX_COLORS:
        errors.append(f'"colors" must be a list of at most {MAX_COLORS} colour pickers.')
        colors = []
    out["colors"] = []
    for i, c in enumerate(colors):
        where = f"colors[{i}]"
        if not isinstance(c, dict):
            errors.append(f"{where} must be an object.")
            continue
        label = c.get("label")
        value = c.get("value")
        if not isinstance(label, str) or not label.strip():
            errors.append(f'{where}: "label" is required.')
            label = f"Colour {i + 1}"
        if not (isinstance(value, str) and HEX.match(value)):
            errors.append(f'{where}: "value" must be a hex colour like "#1a2b3c".')
            continue
        out["colors"].append({"label": label.strip()[:40], "value": value.lower()})

    return errors, out


# ---------------------------------------------------------------- sketch

def check_sketch(code, spec):
    """Return (errors, warnings, is_animated)."""
    errors, warnings = [], []
    if not code.strip():
        return ["sketch.js is empty."], warnings, False

    body = mask(code, False)  # comments blanked, strings kept
    if "</script" in code.lower():
        errors.append('The sketch contains "</script", which would end the page early. Remove it.')
    if not re.search(r"\bfunction\s+initializeSystem\s*\(", body):
        errors.append("Define function initializeSystem(). The page calls it on load and again on every change "
                      "of seed, slider or colour.")
    if re.search(r"\b(?:const|let|var)\s+(?:draw|initializeSystem)\b", body):
        errors.append("Define draw() and initializeSystem() with the function keyword (function draw() { ... }), "
                      "not const, let or var: p5 only finds function declarations.")
    if re.search(r"\bfunction\s+setup\s*\(|\bsetup\s*=", body):
        errors.append("Remove setup(): the page already has one that makes the canvas. "
                      "Put your start-up code in initializeSystem().")
    for name in PAGE_NAMES:
        if re.search(rf"\b(?:const|let|var|function|class)\s+{name}\b", body):
            errors.append(f"Do not declare '{name}': the page already defines it.")
    if re.search(r"\b(?:createCanvas|resizeCanvas)\s*\(", body):
        errors.append('Remove createCanvas()/resizeCanvas(): the page makes the canvas (size from "canvas" in the '
                      "spec). Use width and height.")
    if re.search(r"\bMath\.random\s*\(", body):
        errors.append("Math.random() is not seeded, so the same seed would draw different pictures. "
                      "Use random() after randomSeed(params.seed).")
    if re.search(r"(?<![.\w])(?:random|randomGaussian)\s*\(", body) and not (
            re.search(r"\brandomSeed\s*\(", body) and "params.seed" in body):
        errors.append("The sketch uses random() but does not call randomSeed(params.seed) in initializeSystem().")
    if re.search(r"(?<![.\w])noise\s*\(", body) and not (
            re.search(r"\bnoiseSeed\s*\(", body) and "params.seed" in body):
        errors.append("The sketch uses noise() but does not call noiseSeed(params.seed) in initializeSystem().")
    if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|importScripts)\b|\bnavigator\s*\.\s*sendBeacon\b", body):
        errors.append("The sketch must not make network requests.")
    if re.search(r"\b(?:eval|Function)\s*\(|\bimport\s*\(", body):
        errors.append("The sketch must not use eval(), new Function() or import().")
    if re.search(r"\b(?:loadImage|loadFont|loadJSON|loadStrings|loadTable|loadXML|loadSound|loadModel|loadShader)\s*\(", body):
        errors.append("The sketch must not load outside files (images, fonts, data). Generate everything in code.")

    ids = [p["id"] for p in spec["params"]]
    for pid in ids:
        if not re.search(rf"\bparams\s*\.\s*{pid}\b|\bparams\s*\[\s*['\"]{pid}['\"]\s*\]", body):
            errors.append(f'The slider "{pid}" is in the spec but the sketch never reads params.{pid}, so the '
                          "slider would do nothing. Use it or remove it.")
    used = set(re.findall(r"\bparams\s*\.\s*([A-Za-z_]\w*)", body))
    for name in sorted(used - set(ids) - RESERVED_IDS):
        errors.append(f'The sketch reads params.{name}, which is not in the spec. Add a slider with the id '
                      f'"{name}" to spec.json or fix the name.')
    n_colors = len(spec["colors"])
    if n_colors and not re.search(r"\bparams\s*\.\s*colorPalette\b", body):
        errors.append("The spec has colour pickers but the sketch never reads params.colorPalette.")
    for idx in sorted({int(m) for m in re.findall(r"\bparams\s*\.\s*colorPalette\s*\[\s*(\d+)\s*\]", body)}):
        if idx >= n_colors:
            errors.append(f"The sketch reads params.colorPalette[{idx}] but the spec has only {n_colors} colours "
                          f"(indexes 0 to {max(n_colors - 1, 0)}).")

    # p5 is not ready while the file loads, so p5 calls outside every function fail.
    try:
        hits = []
        shadows = []
        for number, text in top_level_lines(code):
            for m in re.finditer(rf"(?<![.\w$])({P5_FUNCS})\s*\(", text):
                hits.append((number, m.group(1) + "()"))
            for m in re.finditer(rf"(?<![.\w$])({P5_NAMES})\b(?!\s*:)", text):
                hits.append((number, m.group(1)))
            for m in re.finditer(rf"\b(?:let|const|var)\s+({P5_SHADOW})\b", text):
                shadows.append((number, m.group(1)))
        if hits:
            shown = ", ".join(f"{name} (line {number})" for number, name in hits[:6])
            errors.append("These p5 names are used outside any function, where p5 is not ready yet and they fail: "
                          f"{shown}. Move that code into initializeSystem() and keep only plain values at the top.")
        if shadows:
            shown = ", ".join(f"{name} (line {number})" for number, name in shadows[:6])
            warnings.append(f"The sketch declares variables named like p5 functions: {shown}. This can break p5. "
                            "Rename them.")
    except Exception:
        pass

    if re.search(r"\bframeCount\b|\bmillis\s*\(|\bDate\b|\bperformance\s*\.\s*now", body):
        warnings.append("The sketch uses frameCount, millis() or Date, so Regenerate will not replay the same "
                        "picture. Keep your own tick counter and reset it in initializeSystem().")
    if re.search(r"\b(?:windowWidth|windowHeight|innerWidth|innerHeight)\b", body):
        warnings.append("The sketch uses the window size. Use width and height (the canvas size) instead.")
    if re.search(r"\bpixelDensity\s*\(", body):
        warnings.append("The page already sets pixelDensity(1). Remove pixelDensity() from the sketch.")
    if len(code) > 60000:
        warnings.append("The sketch is very long (over 60 KB). Simplify it.")

    return errors, warnings, bool(re.search(r"\bfunction\s+draw\s*\(", body))


def syntax_error(code):
    """Return an error message, or None if the sketch parses (or node is missing)."""
    node = shutil.which("node")
    if not node:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sketch.js"
        path.write_text(code, encoding="utf-8")
        try:
            result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True, timeout=30)
        except Exception:
            return None
    if result.returncode != 0:
        return result.stderr.strip().replace(str(path), "sketch.js")[-1500:]
    return None


# ---------------------------------------------------------------- page

def sliders_html(params):
    if not params:
        return ""
    rows = []
    for p in params:
        pid = p["id"]
        rows.append(
            '      <div class="control-group">\n'
            f'        <label for="p-{pid}">{html.escape(p["label"])}</label>\n'
            '        <div class="slider-container">\n'
            f'          <input type="range" id="p-{pid}" min="{p["min"]}" max="{p["max"]}" step="{p["step"]}" '
            f'value="{p["value"]}" oninput="Studio.param(\'{pid}\', this.value, false)" '
            f'onchange="Studio.param(\'{pid}\', this.value, true)">\n'
            f'          <span class="value-display" id="v-{pid}">{fmt(p["value"], p["step"])}</span>\n'
            "        </div>\n"
            "      </div>"
        )
    return '<section class="control-section">\n      <h3>Settings</h3>\n' + "\n".join(rows) + "\n    </section>"


def colors_html(colors):
    if not colors:
        return ""
    rows = []
    for i, c in enumerate(colors):
        rows.append(
            '      <div class="color-group">\n'
            f'        <label for="c-{i}">{html.escape(c["label"])}</label>\n'
            '        <div class="color-picker-container">\n'
            f'          <input type="color" id="c-{i}" value="{c["value"]}" oninput="Studio.color({i}, this.value)">\n'
            f'          <span class="color-value" id="cv-{i}">{c["value"]}</span>\n'
            "        </div>\n"
            "      </div>"
        )
    return '<section class="control-section">\n      <h3>Colours</h3>\n' + "\n".join(rows) + "\n    </section>"


def build_page(spec, code):
    template = TEMPLATE.read_text(encoding="utf-8")
    page_spec = dict(spec)
    page_spec["fileName"] = slug(spec["title"])
    values = {
        "TITLE": html.escape(spec["title"]),
        "SUBTITLE": html.escape(spec["subtitle"]),
        "SEED": str(spec["seed"]),
        "PARAM_SECTION": sliders_html(spec["params"]),
        "COLOR_SECTION": colors_html(spec["colors"]),
        "SPEC_JSON": json.dumps(page_spec, ensure_ascii=False).replace("<", "\\u003c"),
        "SKETCH": code.rstrip() + "\n",
    }

    def fill(match):
        return values[match.group(1)]

    return re.sub(r"\{\{([A-Z_]+)\}\}", fill, template)


# ---------------------------------------------------------------- render check

CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
                "chrome-headless-shell")
PROBE_MS = 6000
BUDGET_MS = 9000

# Added to a temporary copy of the page only. After PROBE_MS of (virtual) time it measures the canvas.
PROBE_JS = """
<script>
(function () {
  function report(obj) {
    var pre = document.createElement('pre');
    pre.id = 'probe-result';
    pre.textContent = 'PROBE ' + JSON.stringify(obj);
    document.body.appendChild(pre);
  }
  setTimeout(function () {
    try {
      if (typeof p5 === 'undefined') { report({ error: 'p5 did not load' }); return; }
      var banner = document.getElementById('error-banner');
      if (banner && !banner.hidden) { report({ error: banner.textContent }); return; }
      var cv = document.querySelector('#canvas-container canvas');
      if (!cv) { report({ error: 'no canvas was created' }); return; }
      var w = cv.width, h = cv.height;
      var data = cv.getContext('2d').getImageData(0, 0, w, h).data;
      var step = 3, n = 0, buckets = {};
      for (var y = 0; y < h; y += step) {
        for (var x = 0; x < w; x += step) {
          var i = (y * w + x) * 4;
          var key = ((data[i] >> 4) << 8) | ((data[i + 1] >> 4) << 4) | (data[i + 2] >> 4);
          var b = buckets[key] || (buckets[key] = [0, 0, 0, 0]);
          b[0]++; b[1] += data[i]; b[2] += data[i + 1]; b[3] += data[i + 2]; n++;
        }
      }
      var best = null;
      for (var k in buckets) { if (!best || buckets[k][0] > best[0]) best = buckets[k]; }
      var bgR = best[1] / best[0], bgG = best[2] / best[0], bgB = best[3] / best[0];
      var visible = 0;
      for (var y2 = 0; y2 < h; y2 += step) {
        for (var x2 = 0; x2 < w; x2 += step) {
          var j = (y2 * w + x2) * 4;
          var d = Math.abs(data[j] - bgR) + Math.abs(data[j + 1] - bgG) + Math.abs(data[j + 2] - bgB);
          if (d >= 48) visible++;
        }
      }
      report({ visible: visible / n });
    } catch (e) { report({ error: String((e && e.message) || e) }); }
  }, %PROBE_MS%);
})();
</script>
""".replace("%PROBE_MS%", str(PROBE_MS))


def render_check(page):
    """Load a temporary copy of the page in headless Chrome, if the sandbox has one, and measure the canvas.

    Returns one line of text for the person running the script. It never raises and never blocks the build."""
    try:
        chrome = next((path for path in (shutil.which(name) for name in CHROME_NAMES) if path), None)
        if not chrome:
            return "RENDER CHECK: skipped (no Chrome in this sandbox)."
        with tempfile.TemporaryDirectory() as tmp:
            probe_page = Path(tmp) / "probe.html"
            cut = page.rfind("</body>")
            probe_page.write_text(page[:cut] + PROBE_JS + page[cut:], encoding="utf-8")
            command = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                       "--hide-scrollbars", "--mute-audio", f"--user-data-dir={Path(tmp) / 'profile'}",
                       "--window-size=1400,900", f"--virtual-time-budget={BUDGET_MS}", "--dump-dom",
                       probe_page.as_uri()]
            result = subprocess.run(command, capture_output=True, text=True, timeout=45)
        found = re.search(r"PROBE (\{.*?\})</pre>", result.stdout)
        if not found:
            return "RENDER CHECK: skipped (Chrome gave no result)."
        data = json.loads(found.group(1))
        if "error" in data:
            message = str(data["error"])
            if "p5 did not load" in message or "drawing library" in message:
                return "RENDER CHECK: skipped (this sandbox could not load p5.js, so the page was not drawn)."
            return (f"RENDER PROBLEM: the page reported an error: {message} "
                    "Fix sketch.js and run this script again.")
        share = f"{data['visible'] * 100:.1f}%"
        if data["visible"] < 0.005:
            return (f"RENDER PROBLEM: the picture is almost blank. Marks show on only {share} of the canvas after "
                    "about 6 seconds. Make the marks clearly visible (stroke alpha of at least 80 or opaque, "
                    "thicker lines, more elements, or a slower fade of the trails) and run this script again.")
        if data["visible"] < 0.015:
            return (f"RENDER NOTE: the picture is sparse. Marks show on {share} of the canvas after about "
                    "6 seconds. If that is not intended, raise stroke alpha, size or count and run this script again.")
        return f"RENDER CHECK: ok. Marks show on {share} of the canvas after about 6 seconds."
    except Exception as err:
        return f"RENDER CHECK: skipped ({type(err).__name__})."


def read_text(path, what):
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except OSError as err:
        print(f"ERROR: cannot read {what}: {err}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build a generative-art page from spec.json and sketch.js.")
    parser.add_argument("--spec", required=True, help="path to spec.json")
    parser.add_argument("--sketch", required=True, help="path to sketch.js")
    parser.add_argument("--out", required=True, help="path of the .html file to write")
    args = parser.parse_args()

    try:
        raw_spec = json.loads(read_text(args.spec, "the spec"))
    except json.JSONDecodeError as err:
        print(f"ERROR: spec.json is not valid JSON: {err.msg} (line {err.lineno}, column {err.colno}).")
        return 1
    code = read_text(args.sketch, "the sketch")

    errors, spec = check_spec(raw_spec)
    if errors:
        for message in errors:
            print(f"ERROR: {message}")
        print("Nothing was written. Fix spec.json and run the script again.")
        return 1

    errors, warnings, animated = check_sketch(code, spec)
    message = syntax_error(code)
    if message:
        errors.append("JavaScript syntax error in the sketch:\n" + message)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        print("Nothing was written. Fix sketch.js (or spec.json) and run the script again.")
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    page = build_page(spec, code)
    out.write_text(page, encoding="utf-8")

    width, height = spec["canvas"]
    print(f"OK: wrote {out} ({len(page) // 1024 + 1} KB)")
    print(f"    {spec['title']} | seed {spec['seed']} | canvas {width}x{height} | {len(spec['params'])} sliders | "
          f"{len(spec['colors'])} colours | {'animated' if animated else 'static'}")
    for item in warnings:
        print(f"WARNING: {item}")
    print(render_check(page))
    print("Next: publish this file with publish_artifact, kind html_preview.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
