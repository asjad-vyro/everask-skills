#!/usr/bin/env python3
"""Static accessibility helper for the WCAG audit skill.

Standard library only. It reads the files you name, prints a report, writes nothing and uses no network.

    python3 a11y_scan.py contrast FG BG [FG BG ...]
    python3 a11y_scan.py scan PAGE.html [STYLES.css ...] [--base PAGE_URL]

`contrast` prints the WCAG contrast ratio of each text-colour / background pair.
`scan` reads one HTML file (plus optional CSS files) and lists likely WCAG 2.1 problems that can be
seen in the source, the text colour pairs it can work out with their ratios, and what it cannot check.
Every line is a lead to confirm against the code, not a verdict.
"""
import colorsys
import math
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

NAMED = {
    'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0), 'green': (0, 128, 0),
    'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'orange': (255, 165, 0), 'purple': (128, 0, 128),
    'gray': (128, 128, 128), 'grey': (128, 128, 128), 'silver': (192, 192, 192), 'maroon': (128, 0, 0),
    'navy': (0, 0, 128), 'teal': (0, 128, 128), 'lime': (0, 255, 0), 'aqua': (0, 255, 255),
    'cyan': (0, 255, 255), 'fuchsia': (255, 0, 255), 'magenta': (255, 0, 255), 'olive': (128, 128, 0),
    'pink': (255, 192, 203), 'brown': (165, 42, 42), 'gold': (255, 215, 0),
    'lightgray': (211, 211, 211), 'lightgrey': (211, 211, 211), 'darkgray': (169, 169, 169),
    'darkgrey': (169, 169, 169), 'dimgray': (105, 105, 105), 'dimgrey': (105, 105, 105),
    'whitesmoke': (245, 245, 245), 'gainsboro': (220, 220, 220), 'darkred': (139, 0, 0),
    'darkblue': (0, 0, 139), 'darkgreen': (0, 100, 0), 'crimson': (220, 20, 60),
    'coral': (255, 127, 80), 'tomato': (255, 99, 71), 'lightblue': (173, 216, 230),
    'skyblue': (135, 206, 235), 'royalblue': (65, 105, 225), 'steelblue': (70, 130, 180),
    'slategray': (112, 128, 144), 'slategrey': (112, 128, 144), 'lightyellow': (255, 255, 224),
    'beige': (245, 245, 220), 'ivory': (255, 255, 240), 'khaki': (240, 230, 140),
    'tan': (210, 180, 140), 'salmon': (250, 128, 114), 'indigo': (75, 0, 130), 'violet': (238, 130, 238),
}


# ---------------------------------------------------------------- colour maths

def parse_color(value, legacy=False):
    """CSS colour text -> (r, g, b, a), or None when it is not a plain colour.
    legacy=True also accepts a bare six-digit hex such as D7D7CD (old bgcolor attributes)."""
    if not value:
        return None
    v = re.sub(r'\s*!important\s*$', '', value.strip().lower())
    if v in NAMED:
        return NAMED[v] + (1.0,)
    m = re.fullmatch(r'#([0-9a-f]+)', v)
    if not m and legacy:
        m = re.fullmatch(r'([0-9a-f]{6})', v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = ''.join(ch * 2 for ch in h)
        if len(h) in (6, 8):
            alpha = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
        return None
    m = re.fullmatch(r'(rgb|hsl)a?\(([^)]*)\)', v)
    if m:
        parts = [x for x in re.split(r'[\s,/]+', m.group(2).strip()) if x]
        if len(parts) < 3:
            return None
        try:
            alpha = 1.0
            if len(parts) > 3:
                alpha = float(parts[3][:-1]) / 100 if parts[3].endswith('%') else float(parts[3])
            if m.group(1) == 'rgb':
                rgb = [float(x[:-1]) * 2.55 if x.endswith('%') else float(x) for x in parts[:3]]
            else:
                hue = (float(re.sub(r'[a-z]+$', '', parts[0])) / 360.0) % 1.0
                sat = float(parts[1].rstrip('%')) / 100
                lig = float(parts[2].rstrip('%')) / 100
                rgb = [c * 255 for c in colorsys.hls_to_rgb(hue, lig, sat)]
            return tuple(int(max(0, min(255, round(c)))) for c in rgb) + (max(0.0, min(1.0, alpha)),)
        except ValueError:
            return None
    return None


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])


def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    hi, lo = (a, b) if a >= b else (b, a)
    return (hi + 0.05) / (lo + 0.05)


def opaque(c, under):
    """Flatten colour c (r, g, b, a) over the opaque colour `under`; returns (r, g, b)."""
    a = c[3]
    if a >= 1.0:
        return tuple(c[:3])
    return tuple(int(round(c[i] * a + under[i] * (1 - a))) for i in range(3))


def hexs(rgb):
    return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])


def fmt_ratio(r):
    """Two decimals, but never show a failing ratio rounded up to the threshold it misses."""
    s = '%.2f' % r
    for t in (3.0, 4.5, 7.0):
        if r < t <= float(s):
            s = '%.2f' % (math.floor(r * 100) / 100.0)
            break
    return s


def verdict(ok):
    return 'pass' if ok else 'FAIL'


def cmd_contrast(args):
    if len(args) < 2 or len(args) % 2:
        print('usage: a11y_scan.py contrast FG BG [FG BG ...]   (quote colours such as "#999999", or leave off the #)')
        return 2
    for i in range(0, len(args), 2):
        fg_raw, bg_raw = args[i], args[i + 1]
        fg, bg = parse_color(fg_raw, True), parse_color(bg_raw, True)
        if fg is None or bg is None:
            print('%s on %s: could not read the colour (use #rrggbb, rgb(), hsl() or a basic colour name)' % (fg_raw, bg_raw))
            continue
        notes = []
        if bg[3] < 1:
            notes.append('background has transparency: flattened over white')
        bg_rgb = opaque(bg, WHITE)
        if fg[3] < 1:
            notes.append('text colour has transparency: flattened over the background')
        fg_rgb = opaque(fg, bg_rgb)
        r = ratio(fg_rgb, bg_rgb)
        print('%s on %s = %s:1 | normal text needs 4.5 %s | large text needs 3 %s | UI component or graphic needs 3 %s%s' % (
            hexs(fg_rgb), hexs(bg_rgb), fmt_ratio(r), verdict(r >= 4.5), verdict(r >= 3.0), verdict(r >= 3.0),
            ('  (' + '; '.join(notes) + ')') if notes else ''))
    return 0


# ---------------------------------------------------------------- HTML parsing

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
NO_TEXT = {'script', 'style', 'title', 'head', 'noscript', 'template', 'option'}
WIDGET_ROLES = {'button', 'link', 'tab', 'checkbox', 'switch', 'menuitem', 'menuitemcheckbox', 'menuitemradio',
                'option', 'radio', 'treeitem', 'slider', 'spinbutton', 'textbox', 'combobox', 'searchbox'}
CLICK_ATTRS = ('onclick', 'onmousedown', 'onmouseup', 'ondblclick')
KEY_ATTRS = ('onkeydown', 'onkeyup', 'onkeypress')
GENERIC_LINKS = {'click here', 'here', 'read more', 'more', 'learn more', 'link', 'this', 'details', 'continue', 'click'}
NATIVE_OK = {'input', 'select', 'textarea', 'button', 'summary', 'option', 'label', 'details', 'iframe',
             'audio', 'video', 'embed', 'object', 'area'}


class Page(HTMLParser):
    """Collects every element with its attributes, line number, parent and the text inside it."""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.nodes = []
        self.stack = []
        self.styles = []
        self.sheets = []
        self.metas = []
        self.ids = {}
        self.label_for = {}
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {}
        for k, v in attrs:
            k = k.lower()
            if k not in a:
                a[k] = '' if v is None else v
        i = len(self.nodes)
        parent = self.stack[-1] if self.stack else None
        node = {'tag': tag, 'a': a, 'line': self.getpos()[0], 'parent': parent,
                'tlen': 0, 'own': 0, 'snip': '', 'hint': 0, 'th': 0, 'tracks': 0}
        self.nodes.append(node)
        if a.get('id'):
            self.ids.setdefault(a['id'], []).append(i)
        if tag == 'label' and a.get('for'):
            self.label_for.setdefault(a['for'], []).append(i)
        if tag == 'link' and 'stylesheet' in a.get('rel', '').lower() and a.get('href'):
            self.sheets.append(a['href'])
        if tag == 'meta':
            self.metas.append((a.get('name', a.get('http-equiv', '')).lower(), a.get('content', ''), node['line']))
        if tag == 'script':
            self.scripts += 1
        if tag == 'track' and parent is not None:
            self.nodes[parent]['tracks'] += 1
        if tag == 'th':
            for j in reversed(self.stack):
                if self.nodes[j]['tag'] == 'table':
                    self.nodes[j]['th'] += 1
                    break
        if (tag == 'img' and a.get('alt', '').strip()) or a.get('aria-label', '').strip():
            for j in self.stack:
                self.nodes[j]['hint'] += 1
        if tag not in VOID:
            self.stack.append(i)

    def handle_endtag(self, tag):
        tag = tag.lower()
        for j in range(len(self.stack) - 1, -1, -1):
            if self.nodes[self.stack[j]]['tag'] == tag:
                del self.stack[j:]
                return

    def handle_data(self, data):
        if not self.stack:
            return
        top = self.nodes[self.stack[-1]]
        if top['tag'] == 'style':
            if 'print' not in top['a'].get('media', '').lower():
                self.styles.append(data)
            return
        if top['tag'] == 'script':
            return
        s = data.strip()
        if not s:
            return
        top['own'] += len(s)
        for j in self.stack:
            n = self.nodes[j]
            n['tlen'] += len(s)
            if len(n['snip']) < 60:
                n['snip'] = (n['snip'] + ' ' + s).strip()[:60]


def show(n):
    parts = [n['tag']]
    for k, v in list(n['a'].items())[:4]:
        v = v if len(v) <= 40 else v[:37] + '...'
        parts.append(k if v == '' else '%s="%s"' % (k, v))
    return ('<' + ' '.join(parts) + '>')[:120]


def tabindex_of(a):
    try:
        return int(a.get('tabindex', '').strip())
    except ValueError:
        return None


def native(n):
    t, a = n['tag'], n['a']
    if t == 'a':
        return 'href' in a
    return t in NATIVE_OK


# ---------------------------------------------------------------- CSS reading

PROPS = ('color', 'background', 'background-color', 'display', 'visibility')


def strip_css(text):
    text = text.replace('<!--', ' ').replace('-->', ' ')
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'@(?:import|charset|namespace|layer)\b[^;{]*;', '', text, flags=re.I)


def css_blocks(text, ctx=''):
    """Flat list of (selector text, declaration text, media context). Print and dark-mode media are skipped."""
    out, i, n = [], 0, len(text)
    while i < n:
        j = text.find('{', i)
        if j < 0:
            break
        prelude = text[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if text[k] == '{':
                depth += 1
            elif text[k] == '}':
                depth -= 1
            k += 1
        body = text[j + 1:k - 1] if depth == 0 else text[j + 1:k]
        low = prelude.lower()
        if low.startswith('@media') or low.startswith('@supports') or low.startswith('@layer'):
            if not re.search(r'print|prefers-color-scheme\s*:\s*dark|prefers-contrast|forced-colors', low):
                out.extend(css_blocks(body, prelude))
        elif not prelude.startswith('@'):
            out.append((prelude, body, ctx))
        i = k
    return out


def decls(body):
    out = {}
    for part in body.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            k = k.strip().lower()
            if k:
                out[k] = v.strip()
    return out


def pick(d):
    return dict((k, d[k]) for k in PROPS if k in d)


def make_resolver(css_vars):
    def sub(m):
        return css_vars.get(m.group(1).lower(), m.group(2) or '')

    def resolve(v):
        for _ in range(3):
            if 'var(' not in v.lower():
                break
            v = re.sub(r'var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)', sub, v, flags=re.I)
        return v
    return resolve


def bg_of(v):
    """First colour in a background value; 'IMAGE' when it is a gradient or picture with no colour."""
    low = v.lower()
    had_image = 'url(' in low or 'gradient' in low
    v = re.sub(r'url\([^)]*\)', ' ', v)
    if 'gradient' in low:
        return 'IMAGE'
    for tok in re.findall(r'#[0-9a-fA-F]{3,8}\b|(?:rgb|hsl)a?\([^)]*\)|[A-Za-z]+', v):
        c = parse_color(tok)
        if c:
            return c
    return 'IMAGE' if had_image else None


def parse_selector(sel):
    """Simple selectors only (tag, .class, #id, descendant chains). Returns (parts, specificity) or None."""
    s = sel.strip().replace(':root', 'html')
    if not s or any(ch in s for ch in ':[+~'):
        return None
    s = re.sub(r'\s*>\s*', ' ', s)
    parts, spec = [], [0, 0, 0]
    for tok in s.split():
        m = re.fullmatch(r'(\*|[A-Za-z][\w-]*)?((?:[#.][\w-]+)*)', tok)
        if not m:
            return None
        tag = m.group(1)
        ids, classes = [], set()
        for x in re.findall(r'[#.][\w-]+', m.group(2) or ''):
            if x[0] == '#':
                ids.append(x[1:])
            else:
                classes.add(x[1:])
        if tag and tag != '*':
            tag = tag.lower()
            spec[2] += 1
        else:
            tag = None
        spec[0] += len(ids)
        spec[1] += len(classes)
        parts.append((tag, ids[0] if ids else None, classes))
    if not parts:
        return None
    return parts, tuple(spec)


def rule_key(parts):
    tag, id_, classes = parts[-1]
    if id_:
        return ('#', id_)
    if classes:
        return ('.', sorted(classes)[0])
    if tag:
        return ('t', tag)
    return ('*', '')


def match_compound(comp, n):
    tag, id_, classes = comp
    if tag and n['tag'] != tag:
        return False
    a = n['a']
    if id_ and a.get('id') != id_:
        return False
    if classes and not classes <= set(a.get('class', '').split()):
        return False
    return True


def match_selector(parts, i, N):
    if not match_compound(parts[-1], N[i]):
        return False
    j = N[i]['parent']
    for comp in reversed(parts[:-1]):
        while j is not None and not match_compound(comp, N[j]):
            j = N[j]['parent']
        if j is None:
            return False
        j = N[j]['parent']
    return True


def apply_props(seq, resolve):
    """Apply declaration dicts in order (later wins, !important last).
    Returns (fg, bg, hidden); bg is 'CLEAR' when the winning rule made the background transparent."""
    fg = bg = None
    display = visibility = ''
    for important in (False, True):
        for props in seq:
            for prop, val in props.items():
                if ('!important' in val.lower()) != important:
                    continue
                v = resolve(val)
                plain = re.sub(r'\s*!important\s*$', '', v.strip().lower())
                if prop == 'color':
                    c = parse_color(v)
                    if c:
                        fg = c
                elif prop in ('background', 'background-color'):
                    c = bg_of(v)
                    if c:
                        bg = c
                    elif plain in ('transparent', 'none', 'initial', 'unset', 'inherit'):
                        bg = 'CLEAR'
                elif prop == 'display':
                    display = plain
                elif prop == 'visibility':
                    visibility = plain
    return fg, bg, display.startswith('none') or visibility.startswith('hidden')


def resolve_colours(p, blocks, unloaded):
    """Work out the text and background colour of every element that holds text.
    Returns (rows, unknown, skipped_selectors); rows are (ratio, fg, bg, declared, count, example)."""
    N = p.nodes
    css_vars = {}
    for _sel, body, _ctx in blocks:
        for k, v in decls(body).items():
            if k.startswith('--'):
                css_vars[k] = v
    resolve = make_resolver(css_vars)
    rules, skipped, order = [], 0, 0
    for sel_text, body, _ctx in blocks:
        props = pick(decls(body))
        if not props:
            continue
        for sel in sel_text.split(','):
            order += 1
            parsed = parse_selector(sel)
            if parsed is None:
                skipped += 1
                continue
            rules.append({'parts': parsed[0], 'spec': parsed[1], 'order': order, 'props': props})
    index = {}
    for r in rules:
        index.setdefault(rule_key(r['parts']), []).append(r)

    base_fg, base_bg = BLACK + (1.0,), 'DEFAULT'
    roots = [r for r in rules if len(r['parts']) == 1 and r['parts'][0][0] in ('html', 'body')
             and not r['parts'][0][1] and not r['parts'][0][2]]
    roots.sort(key=lambda r: (r['spec'], r['order']))
    for r in roots:
        fg, bg, _h = apply_props([r['props']], resolve)
        if fg:
            base_fg = fg
        if bg and bg != 'CLEAR':
            base_bg = bg if bg == 'IMAGE' else opaque(bg, WHITE)

    body_link = None
    for n in N:
        if n['tag'] == 'body' and n['a'].get('link'):
            body_link = parse_color(n['a']['link'], True)

    eff = []
    for i, n in enumerate(N):
        a, t = n['a'], n['tag']
        legacy_fg = legacy_bg = None
        if a.get('bgcolor'):
            legacy_bg = parse_color(a['bgcolor'], True)
        if a.get('background') and t in ('body', 'table', 'tr', 'td', 'th'):
            legacy_bg = 'IMAGE'
        if t == 'font' and a.get('color'):
            legacy_fg = parse_color(a['color'], True)
        if t == 'body' and a.get('text'):
            legacy_fg = parse_color(a['text'], True)
        keys = [('*', ''), ('t', t)] + [('.', c) for c in a.get('class', '').split()]
        if a.get('id'):
            keys.append(('#', a['id']))
        hit = []
        for key in keys:
            for r in index.get(key, ()):
                if match_selector(r['parts'], i, N):
                    hit.append(r)
        hit.sort(key=lambda r: (r['spec'], r['order']))
        seq = [r['props'] for r in hit] + [pick(decls(a.get('style', '')))]
        fg, bg, hid = apply_props(seq, resolve)
        if bg == 'CLEAR':
            bg, legacy_bg = None, None
        if fg is None:
            fg = legacy_fg
        if bg is None:
            bg = legacy_bg
        if t == 'a' and 'href' in a and fg is None:
            if body_link is not None:
                fg = body_link
            elif unloaded == 0:
                fg = (0, 0, 238, 1.0)
            else:
                fg = 'UNKNOWN'
        parent = n['parent']
        pfg, pbg, phid = eff[parent] if parent is not None else (base_fg, base_bg, False)
        efg = fg if fg is not None else pfg
        if bg is None:
            ebg = pbg
        elif bg == 'IMAGE':
            ebg = 'IMAGE'
        else:
            ebg = opaque(bg, pbg if isinstance(pbg, tuple) else WHITE)
        eff.append((efg, ebg, phid or hid))

    pairs, unknown = {}, 0
    for i, n in enumerate(N):
        if n['own'] == 0 or n['tag'] in NO_TEXT:
            continue
        fg, bg, hid = eff[i]
        if hid:
            continue
        if fg is None or fg == 'UNKNOWN' or bg == 'IMAGE':
            unknown += 1
            continue
        declared = bg != 'DEFAULT'
        bg_rgb = bg if declared else WHITE
        fg_rgb = opaque(fg, bg_rgb)
        slot = pairs.setdefault((fg_rgb, bg_rgb, declared), [0, None])
        slot[0] += 1
        if slot[1] is None:
            slot[1] = 'line %d %s "%s"' % (n['line'], show(n)[:60], n['snip'][:40])
    rows = []
    for (fg, bg, declared), (count, example) in pairs.items():
        rows.append((ratio(fg, bg), fg, bg, declared, count, example))
    rows.sort(key=lambda x: x[0])
    return rows, unknown, skipped


# ---------------------------------------------------------------- the checks

def analyze(p, blocks):
    N = p.nodes
    findings = []
    stats = {}

    def add(kind, crit, n, msg, adv=False, extra=''):
        if isinstance(n, dict):
            detail = 'line %d: %s' % (n['line'], show(n))
            if extra:
                detail += '  ' + extra
        else:
            detail = extra
        findings.append((kind, crit, msg, adv, detail))

    def named_by_attr(a):
        return bool(a.get('aria-label', '').strip() or a.get('aria-labelledby', '').strip() or a.get('title', '').strip())

    def labelled(i):
        n = N[i]
        a = n['a']
        if a.get('aria-label', '').strip() or a.get('title', '').strip():
            return True
        if any(r in p.ids for r in a.get('aria-labelledby', '').split()):
            return True
        if a.get('id') and any(N[j]['tlen'] > 0 or N[j]['hint'] > 0 for j in p.label_for.get(a['id'], [])):
            return True
        j = n['parent']
        while j is not None:
            if N[j]['tag'] == 'label' and (N[j]['tlen'] > 0 or N[j]['hint'] > 0):
                return True
            j = N[j]['parent']
        return False

    html = next((n for n in N if n['tag'] == 'html'), None)
    is_page = html is not None
    stats['is_page'] = is_page
    fields = fields_ok = images = images_noalt = images_decor = links = buttons = 0

    if is_page:
        lang = html['a'].get('lang')
        if lang is None:
            lang = html['a'].get('xml:lang')
        stats['lang'] = lang
        if lang is None or not lang.strip():
            add('lang', '3.1.1', html, 'the <html> element has no lang attribute (screen readers cannot pick the right voice)')
        elif not re.fullmatch(r'[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*', lang.strip()):
            add('lang', '3.1.1', html, 'the lang attribute is not a valid language code', extra='lang="%s"' % lang)
        titles = []
        for n in N:
            if n['tag'] == 'title':
                j, in_svg = n['parent'], False
                while j is not None:
                    if N[j]['tag'] == 'svg':
                        in_svg = True
                    j = N[j]['parent']
                if not in_svg:
                    titles.append(n)
        stats['title'] = titles[0]['snip'] if titles else None
        if not titles or titles[0]['tlen'] == 0:
            add('title', '2.4.2', html, 'the page has no <title> or it is empty')

    for name, content, line in p.metas:
        if name == 'viewport':
            stats['viewport'] = content
            mx = re.search(r'maximum-scale\s*=\s*([0-9.]+)', content, re.I)
            blocked = re.search(r'user-scalable\s*=\s*(no|0)', content, re.I)
            try:
                small = bool(mx) and float(mx.group(1)) < 2
            except ValueError:
                small = False
            if blocked or small:
                add('viewport-zoom', '1.4.4', line, 'the viewport meta tag blocks or limits zoom', extra='line %d: content="%s"' % (line, content))
        if name == 'refresh':
            m = re.match(r'\s*(\d+)', content)
            if m and int(m.group(1)) > 0:
                add('meta-refresh', '2.2.1', line, 'the page refreshes or redirects on a timer', extra='line %d: content="%s"' % (line, content))

    for i, n in enumerate(N):
        t, a = n['tag'], n['a']
        role = a.get('role', '').strip().lower()

        # images
        if t == 'img':
            images += 1
            alt = a.get('alt')
            if alt is None:
                images_noalt += 1
                if role in ('presentation', 'none') or a.get('aria-hidden') == 'true':
                    pass
                elif named_by_attr(a):
                    add('img-alt-attr', '1.1.1', n, 'image is named only by aria/title and has no alt attribute', adv=True)
                else:
                    add('img-no-alt', '1.1.1', n, 'image has no alt attribute (a screen reader reads the file name or skips it)')
            else:
                if not alt.strip():
                    images_decor += 1
                if re.search(r'\.(png|jpe?g|gif|svg|webp|avif)\s*$', alt, re.I) or re.fullmatch(r'\s*(img|image|photo|picture|dsc|screenshot)[\s_-]*\d*\s*', alt, re.I):
                    add('img-alt-filename', '1.1.1', n, 'alt text looks like a file name or a placeholder, not a description')
        elif t == 'area' and 'href' in a and not a.get('alt', '').strip():
            add('area-no-alt', '1.1.1', n, 'image-map area has no alt text')
        elif t == 'svg' and role == 'img' and not (a.get('aria-label', '').strip() or a.get('aria-labelledby', '').strip() or n['tlen'] > 0):
            add('svg-no-name', '1.1.1', n, 'svg with role="img" has no accessible name')

        # form controls
        if t in ('input', 'select', 'textarea'):
            typ = a.get('type', 'text').strip().lower() if t == 'input' else t
            if typ in ('hidden', 'submit', 'reset'):
                pass
            elif typ == 'button':
                buttons += 1
                if not (a.get('value', '').strip() or named_by_attr(a)):
                    add('input-button-no-name', '4.1.2', n, 'button input has no value or label')
            elif typ == 'image':
                buttons += 1
                if not (a.get('alt', '').strip() or named_by_attr(a)):
                    add('input-image-no-alt', '1.1.1', n, 'image button has no alt text')
            else:
                fields += 1
                if labelled(i):
                    fields_ok += 1
                elif a.get('placeholder', '').strip():
                    add('field-placeholder-only', '3.3.2 / 1.3.1', n, 'field uses only placeholder text as its label (it vanishes on typing and is not a reliable name)')
                else:
                    add('field-no-label', '1.3.1 / 3.3.2 / 4.1.2', n, 'form field has no programmatic label (no <label for>, wrapping <label>, aria-label or aria-labelledby)')
            if t == 'input' and 'autocomplete' not in a and typ not in ('hidden', 'submit', 'button', 'reset', 'image', 'checkbox', 'radio', 'file', 'range'):
                key = '%s %s %s' % (a.get('name', ''), a.get('id', ''), typ)
                if typ in ('email', 'tel', 'password') or re.search(r'e-?mail|phone|first[-_ ]?name|last[-_ ]?name|full[-_ ]?name|given|family|street|address|postal|postcode|zip|city|country|card|cc-|username', key, re.I):
                    add('autocomplete-missing', '1.3.5', n, 'field collects personal data but has no autocomplete attribute', adv=True)

        # onchange that navigates or submits
        oc = a.get('onchange', '')
        if oc and re.search(r'location|\.submit\(|window\.open|href', oc):
            add('onchange-navigates', '3.2.2', n, 'changing this control navigates or submits at once, with no button or warning', extra='onchange="%s"' % oc[:50])

        # script that throws focus away as soon as it arrives
        of = a.get('onfocus', '')
        if of and re.search(r'blur\s*\(', of):
            add('focus-blur', '2.4.7 / 2.1.1 / 3.2.1', n, 'script moves focus away as soon as the element receives it (onfocus blur()), so keyboard users cannot use it')

        # links and buttons
        is_link = (t == 'a' and 'href' in a) or role == 'link'
        is_button = t == 'button' or role == 'button'
        if is_link:
            links += 1
        if is_button:
            buttons += 1
        if is_link or is_button:
            if not (n['tlen'] > 0 or n['hint'] > 0 or named_by_attr(a)):
                add('control-no-name', '4.1.2' + (' / 2.4.4' if is_link else ''), n,
                    'link or button has no accessible name (no text, no alt on an inner image, no aria-label)')
            elif is_link and len(n['snip']) < 60 and not a.get('aria-label') and n['snip'].strip(' .!:>').lower() in GENERIC_LINKS:
                add('link-generic', '2.4.4', n, 'link text is generic and does not say where it goes', adv=True, extra='text="%s"' % n['snip'].strip())
            href = a.get('href', '').strip().lower()
            if t == 'a' and 'onclick' in a and (href in ('', '#') or href.startswith('javascript:')):
                add('link-as-button', '4.1.2', n, 'link used as a button (href="#" or javascript:); a <button> is the right element', adv=True)

        # click handlers on things that are not controls
        if any(k in a for k in CLICK_ATTRS) and not native(n):
            miss = []
            if role not in WIDGET_ROLES:
                miss.append('no button/link role')
            if tabindex_of(a) is None:
                miss.append('not reachable with Tab (no tabindex)')
            if not any(k in a for k in KEY_ATTRS):
                miss.append('no key handler')
            if miss:
                add('click-non-interactive', '2.1.1 / 4.1.2', n,
                    'click handler on an element that is not a real button or link (mouse-only unless script adds more)', extra='[' + '; '.join(miss) + ']')
        elif role in WIDGET_ROLES and not native(n) and tabindex_of(a) is None:
            add('role-not-focusable', '2.1.1', n, 'element with a widget role cannot be reached with Tab (no tabindex)', extra='role="%s"' % role)
        if ('onmouseover' in a or 'onmouseenter' in a) and 'onfocus' not in a and 'onfocusin' not in a:
            add('hover-only', '2.1.1 / 1.4.13', n, 'behaviour starts on mouse hover with no focus equivalent', adv=True)

        ti = tabindex_of(a)
        if ti is not None and ti > 0:
            add('tabindex-positive', '2.4.3', n, 'positive tabindex overrides the natural focus order', extra='tabindex="%d"' % ti)
        if a.get('aria-hidden', '').lower() == 'true':
            focusable = (t == 'a' and 'href' in a) or t in ('button', 'select', 'textarea') or \
                (t == 'input' and a.get('type', '').lower() != 'hidden') or (ti is not None and ti >= 0)
            if focusable:
                add('aria-hidden-focusable', '4.1.2', n, 'aria-hidden="true" on a focusable element: keyboard users reach it, screen readers skip it')
        if re.search(r'outline\s*:\s*(none|0)\b', a.get('style', '')) and (native(n) or ti is not None):
            add('focus-outline-removed', '2.4.7', n, 'the focus outline is removed; check that a visible replacement exists')

        # frames, media, motion
        if t == 'iframe' and not (a.get('title', '').strip() or a.get('aria-label', '').strip()) and a.get('aria-hidden') != 'true':
            add('iframe-no-title', '4.1.2', n, 'iframe has no title')
        if t in ('video', 'audio'):
            if 'autoplay' in a and (t == 'audio' or 'muted' not in a):
                add('autoplay-sound', '1.4.2', n, 'media starts playing with sound; users need to pause it or turn it off')
            elif 'autoplay' in a and 'controls' not in a:
                add('autoplay-motion', '2.2.2', n, 'moving media starts automatically with no visible pause control', adv=True)
            if t == 'video' and n['tracks'] == 0:
                add('video-no-captions', '1.2.2', n, 'video has no <track> element; confirm captions exist another way', adv=True)
        if t in ('marquee', 'blink'):
            add('moving-text', '2.2.2', n, 'blinking or scrolling element with no way to pause it')
        if t == 'table' and n['th'] == 0 and role not in ('presentation', 'none'):
            add('table-no-th', '1.3.1', n, 'table has no <th> header cells (fine if it is only used for layout; a data table needs headers)', adv=True)

    # references and duplicates
    for id_, idx in p.ids.items():
        if len(idx) > 1:
            add('dup-id', '4.1.1 (WCAG 2.1)', N[idx[1]], 'duplicate id (breaks label and ARIA references)', adv=True, extra='id="%s" x%d' % (id_, len(idx)))
    for for_id, idx in p.label_for.items():
        if for_id not in p.ids:
            add('label-for-missing', '1.3.1', N[idx[0]], 'label points to an id that does not exist', extra='for="%s"' % for_id)

    # headings and landmarks (whole pages only)
    heads = [n for n in N if re.fullmatch(r'h[1-6]', n['tag'])]
    stats['heads'] = heads
    prev = 0
    for n in heads:
        lvl = int(n['tag'][1])
        if n['tlen'] == 0 and n['hint'] == 0:
            add('heading-empty', '1.3.1 / 2.4.6', n, 'empty heading')
        if prev and lvl > prev + 1:
            add('heading-skip', '1.3.1', n, 'heading level jumps down more than one level', adv=True, extra='h%d after h%d' % (lvl, prev))
        prev = lvl
    land = {'main': 0, 'nav': 0, 'header': 0, 'footer': 0}
    roles_map = {'main': 'main', 'navigation': 'nav', 'banner': 'header', 'contentinfo': 'footer'}
    for n in N:
        if n['tag'] in land:
            land[n['tag']] += 1
        elif n['a'].get('role', '').strip().lower() in roles_map:
            land[roles_map[n['a']['role'].strip().lower()]] += 1
    stats['land'] = land
    skip = any(n['tag'] == 'a' and n['a'].get('href', '').startswith('#') and len(n['a']['href']) > 1
               and re.search(r'skip|jump to|go to (the )?(main|content)', n['snip'], re.I) for n in N)
    stats['skip'] = skip
    if is_page:
        h1s = [n for n in heads if n['tag'] == 'h1']
        if not heads:
            add('no-headings', '1.3.1 / 2.4.6', 1, 'the page has no headings', adv=True, extra='')
        elif not h1s:
            add('no-h1', '1.3.1 / 2.4.6', heads[0], 'the page has no <h1>', adv=True)
        elif len(h1s) > 1:
            add('many-h1', '1.3.1', h1s[1], 'more than one <h1>', adv=True, extra='%d found' % len(h1s))
        if land['main'] == 0:
            add('no-main', '1.3.1 / 2.4.1', html, 'no <main> landmark' + ('' if skip else ' and no skip link'), adv=skip)

    # CSS: focus outlines
    has_visible = any(':focus-visible' in sel for sel, _b, _c in blocks)
    for sel, body, _ctx in blocks:
        if ':focus' in sel and re.search(r'outline(-style)?\s*:\s*(none|0)\b', body) and not re.search(r'box-shadow|border|background|text-decoration|filter', body):
            add('focus-outline-removed', '2.4.7', None, 'CSS removes the focus outline; check that a visible replacement exists' + (' (a :focus-visible rule exists)' if has_visible else ''),
                extra=' '.join(sel.split())[:80] + ' { outline: none }')

    stats.update({'fields': fields, 'fields_ok': fields_ok, 'images': images, 'images_noalt': images_noalt,
                  'images_decor': images_decor, 'links': links, 'buttons': buttons})
    return findings, stats


NOT_CHECKED = [
    'Keyboard use at run time: whether every control can be reached and used, focus order, keyboard traps (2.1.1, 2.1.2, 2.4.3)',
    'Whether the focus indicator is actually visible (2.4.7) and not hidden behind sticky bars',
    'What a screen reader announces: names, roles, states, live updates, status messages (4.1.2, 4.1.3)',
    'Zoom to 200 percent, reflow at 320 CSS px, text spacing, content on hover or focus (1.4.4, 1.4.10, 1.4.12, 1.4.13)',
    'Whether alt text is accurate, captions and audio description exist and are right, reading order makes sense',
    'Click and key handlers added by JavaScript (addEventListener), content built by scripts, colours set by scripts',
    'Contrast of UI component borders, icons, placeholders and text over images (1.4.11, 1.4.3)',
]


def section(title, fn):
    print('== %s ==' % title)
    try:
        fn()
    except Exception as exc:  # one failing section must not hide the others
        print('[this section failed: %s: %s]' % (type(exc).__name__, exc))
    print('')


def cmd_scan(args):
    base, files, i = '', [], 0
    while i < len(args):
        if args[i] == '--base' and i + 1 < len(args):
            base = args[i + 1]
            i += 2
        else:
            files.append(args[i])
            i += 1
    if not files:
        print('usage: a11y_scan.py scan PAGE.html [STYLES.css ...] [--base PAGE_URL]')
        return 2
    with open(files[0], 'r', encoding='utf-8', errors='replace') as fh:
        html_text = fh.read(4000000)
    css_texts = []
    for f in files[1:]:
        with open(f, 'r', encoding='utf-8', errors='replace') as fh:
            css_texts.append(fh.read(4000000))
    p = Page()
    try:
        p.feed(html_text)
        p.close()
    except Exception as exc:
        print('[html parser stopped early: %s: %s]' % (type(exc).__name__, exc))
    blocks = css_blocks(strip_css('\n'.join(p.styles + css_texts)))
    unloaded = max(0, len(p.sheets) - len(css_texts))
    state = {}

    def run_checks():
        state['findings'], state['stats'] = analyze(p, blocks)

    def print_page():
        s = state['stats']
        text_chars = sum(n['own'] for n in p.nodes)
        print('file: %s | %d bytes | %d elements | %d characters of text | %d script tags' % (files[0], len(html_text), len(p.nodes), text_chars, p.scripts))
        if text_chars < 200 and p.scripts > 0:
            print('WARNING: almost no text in this HTML but it has scripts: the page is probably built by JavaScript. Fetch the rendered page with headless Chrome (--dump-dom) and scan that instead.')
        if not s['is_page']:
            print('this is a fragment (no <html> element): page-level checks (lang, title, headings, landmarks) were skipped')
        else:
            print('lang: %s' % (s.get('lang') if s.get('lang') is not None else 'MISSING'))
            print('title: %s' % (s.get('title') if s.get('title') else 'MISSING'))
        print('viewport: %s' % (s.get('viewport') or 'none'))
        land = s['land']
        print('landmarks: main %d, nav %d, header %d, footer %d | skip link: %s' % (land['main'], land['nav'], land['header'], land['footer'], 'yes' if s['skip'] else 'no'))
        print('images: %d (%d without alt, %d with empty alt) | form fields: %d (%d labelled) | links: %d | buttons: %d' % (
            s['images'], s['images_noalt'], s['images_decor'], s['fields'], s['fields_ok'], s['links'], s['buttons']))
        heads = s['heads']
        print('headings: %s' % ('none' if not heads else '%d' % len(heads)))
        for n in heads[:25]:
            print('  %s "%s" (line %d)' % (n['tag'], n['snip'][:60], n['line']))
        if len(heads) > 25:
            print('  (+%d more)' % (len(heads) - 25))

    def print_findings():
        findings = state['findings']
        groups, order = {}, []
        for kind, crit, msg, adv, detail in findings:
            if kind not in groups:
                groups[kind] = [crit, msg, adv, []]
                order.append(kind)
            groups[kind][3].append(detail)
        if not order:
            print('nothing flagged by the static checks')
        for kind in order:
            crit, msg, adv, details = groups[kind]
            print('[%s] %s%s%s' % (crit, ('%dx ' % len(details)) if len(details) > 1 else '', msg, '  (advisory: judge in context)' if adv else ''))
            for d in details[:3]:
                if d:
                    print('    ' + d)
            if len(details) > 3:
                print('    (+%d more)' % (len(details) - 3))
        print('%d kinds of finding, %d instances' % (len(order), len(findings)))

    def print_colours():
        if len(p.nodes) > 20000:
            print('skipped: page is too large for the colour pass')
            return
        rows, unknown, skipped = resolve_colours(p, blocks, unloaded)
        fails = [r for r in rows if r[0] < 4.5]
        for r, fg, bg, declared, count, example in fails[:20]:
            tail = ' (passes only if large text: 24px+, or 18.66px+ bold)' if r >= 3.0 else ''
            note = '' if declared else '  [page background not declared: assumed white]'
            print('FAIL %s:1  %s on %s  x%d%s  e.g. %s%s' % (fmt_ratio(r), hexs(fg), hexs(bg), count, tail, example, note))
        if len(fails) > 20:
            print('(+%d more failing pairs)' % (len(fails) - 20))
        passes = rows[len(fails):]
        for r, fg, bg, declared, count, example in passes[:8]:
            print('pass %s:1  %s on %s  x%d' % (fmt_ratio(r), hexs(fg), hexs(bg), count))
        if len(passes) > 8:
            print('(+%d more passing pairs)' % (len(passes) - 8))
        if not rows:
            print('no text colour pairs could be worked out from this HTML and CSS')
        print('%d text elements skipped (background image or gradient, colour from unread CSS, or script)' % unknown)
        if skipped:
            print('%d selectors with pseudo-classes, attributes or sibling combinators were not evaluated' % skipped)
        print('Ratios are for the declared colours only. Confirm each failing pair on the element before reporting it.')

    def print_sheets():
        if not p.sheets:
            print('no linked stylesheets')
        for href in p.sheets[:12]:
            print('  ' + (urljoin(base, href) if base else href))
        if unloaded:
            print('%d linked stylesheet(s) were not read: fetch the main ones and pass them after the HTML file to include their colours and focus rules' % unloaded)

    def print_not_checked():
        for line in NOT_CHECKED:
            print('- ' + line)

    section('PAGE', lambda: (run_checks(), print_page()))
    if 'findings' in state:
        section('FINDINGS FROM THE STATIC CHECKS (WCAG 2.1 criterion in brackets)', print_findings)
    section('TEXT COLOUR PAIRS', print_colours)
    section('LINKED STYLESHEETS', print_sheets)
    section('NOT CHECKED BY THIS SCAN (say so in the report)', print_not_checked)
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] not in ('contrast', 'scan'):
        print(__doc__)
        return 2
    if argv[1] == 'contrast':
        return cmd_contrast(argv[2:])
    return cmd_scan(argv[2:])


if __name__ == '__main__':
    sys.exit(main(sys.argv))
