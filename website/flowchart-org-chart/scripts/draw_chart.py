#!/usr/bin/env python3
"""Validate a node/edge table and draw an org chart, flowchart or timeline as SVG + PNG.

Usage: python draw_chart.py SPEC.json OUT_DIR BASENAME
SPEC.json:
 {"kind": "org" | "flow" | "timeline", "title": "optional", "dir": "ltr" | "rtl",
  "nodes": [{"id": "n1", "label": "text", "sub": "optional second line", "type": "...", "parent": "id (org only)"}],
  "edges": [{"from": "n1", "to": "n2", "label": "optional"}]}
 org: node type is ignored; give each non-root node "parent" (edges are made for you) or give edges.
 flow: node type is start | end | process | decision (default process).
 timeline: nodes in time order; "sub" holds the date or time exactly as the user wrote it; edges are not needed.
Writes OUT_DIR/BASENAME.svg, .png (if Chrome is found) and .mmd (Mermaid source, org and flow only).
"""
import html, json, os, shutil, subprocess, sys, unicodedata

FONT = 15
LINE_H = 20
PAD = 14
HGAP = 36
VGAP = 64
MARGIN = 30


def tw(s, size=FONT):
    w = 0.0
    for ch in s:
        e = unicodedata.east_asian_width(ch)
        w += 1.0 if e in ("W", "F") else 0.58
    return w * size


def wrap(s, limit=24):
    """Wrap on spaces; CJK text (no spaces) wraps by character count."""
    words = s.split(" ")
    if len(words) == 1:
        if tw(s) <= tw("m" * limit):
            return [s]
        out, cur = [], ""
        for ch in s:
            if tw(cur + ch) > tw("m" * limit):
                out.append(cur)
                cur = ch
            else:
                cur += ch
        return out + ([cur] if cur else [])
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t) > tw("m" * limit) and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


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


# ---------------------------------------------------------------- validation
def validate(spec):
    errs, warns = [], []
    kind = spec.get("kind")
    if kind not in ("org", "flow", "timeline"):
        errs.append("kind must be org, flow or timeline")
        return errs, warns
    nodes = spec.get("nodes", [])
    if not nodes:
        errs.append("no nodes")
        return errs, warns
    ids = [n.get("id") for n in nodes]
    for i in set(ids):
        if ids.count(i) > 1:
            errs.append(f"duplicate node id {i}")
    labels = [(n.get("label") or "").strip().lower() for n in nodes]
    for n in nodes:
        if not (n.get("label") or "").strip():
            errs.append(f"node {n.get('id')} has no label")
    if kind == "org":
        by = {n["id"]: n for n in nodes}
        edges = list(spec.get("edges", []))
        for n in nodes:
            if n.get("parent"):
                edges.append({"from": n["parent"], "to": n["id"]})
        spec["edges"] = edges
        parents = {}
        for e in edges:
            if e["from"] not in by or e["to"] not in by:
                errs.append(f"edge {e['from']}->{e['to']} names an unknown node")
                continue
            if e["to"] in parents:
                errs.append(f"{e['to']} has two bosses ({parents[e['to']]} and {e['from']})")
            parents[e["to"]] = e["from"]
        roots = [i for i in ids if i not in parents]
        if len(roots) != 1:
            (warns if len(roots) > 1 else errs).append(
                f"{len(roots)} top-level nodes ({', '.join(roots)}); an org chart has one root unless the user said otherwise")
        for i in ids:  # cycle / reachability
            seen, cur = set(), i
            while cur in parents:
                if cur in seen:
                    errs.append(f"reporting loop through {i}")
                    break
                seen.add(cur)
                cur = parents[cur]
    elif kind == "flow":
        by = {n["id"]: n for n in nodes}
        edges = spec.get("edges", [])
        for e in edges:
            if e["from"] not in by or e["to"] not in by:
                errs.append(f"edge {e['from']}->{e['to']} names an unknown node")
        if errs:
            return errs, warns
        seen_e = set()
        for e in edges:
            k = (e["from"], e["to"], e.get("label", ""))
            if k in seen_e:
                errs.append(f"duplicate connection {e['from']}->{e['to']}")
            seen_e.add(k)
        for n in nodes:
            n.setdefault("type", "process")
            if n["type"] not in ("start", "end", "process", "decision"):
                errs.append(f"node {n['id']}: type must be start, end, process or decision")
        starts = [n["id"] for n in nodes if n["type"] == "start"]
        ends = [n["id"] for n in nodes if n["type"] == "end"]
        if len(starts) != 1:
            errs.append(f"need exactly one start node, found {len(starts)}")
        if not ends:
            errs.append("need at least one end node")
        outs = {i: [e for e in edges if e["from"] == i] for i in by}
        ins = {i: [e for e in edges if e["to"] == i] for i in by}
        for i, n in by.items():
            if n["type"] == "decision":
                o = outs[i]
                if len(o) < 2:
                    errs.append(f"decision {i} needs at least two outgoing branches, has {len(o)}")
                for e in o:
                    if not (e.get("label") or "").strip():
                        errs.append(f"branch {i}->{e['to']} from a decision has no label")
            elif n["type"] == "end":
                if outs[i]:
                    errs.append(f"end node {i} has outgoing connections")
            elif not outs[i]:
                errs.append(f"{i} ({n['label']}) is a dead end: no outgoing connection")
            if n["type"] != "start" and not ins[i]:
                errs.append(f"{i} ({n['label']}) has no incoming connection")
        if len(starts) == 1:
            seen, stack = set(), [starts[0]]
            while stack:
                c = stack.pop()
                if c in seen:
                    continue
                seen.add(c)
                stack += [e["to"] for e in outs[c]]
            for i in by:
                if i not in seen:
                    errs.append(f"{i} ({by[i]['label']}) cannot be reached from the start")
    else:
        spec["edges"] = [{"from": nodes[i]["id"], "to": nodes[i + 1]["id"]} for i in range(len(nodes) - 1)]
    for i, l in enumerate(labels):
        if l and labels.count(l) > 1 and kind != "org":
            warns.append(f"label '{nodes[i]['label']}' appears more than once (fine only if the user wrote it twice)")
    return errs, warns


# ---------------------------------------------------------------- node geometry
def size_node(n, kind):
    lines = wrap(n["label"], 22 if kind != "timeline" else 16)
    sub = wrap(n["sub"], 26) if n.get("sub") and kind != "timeline" else []
    if kind == "timeline":
        sub = wrap(n["sub"], 16) if n.get("sub") else []
    n["lines"], n["sublines"] = lines, sub
    w = max([tw(l) for l in lines] + [tw(l, FONT - 2) for l in sub] + [60]) + 2 * PAD
    h = (len(lines) + len(sub)) * LINE_H + 2 * PAD - 6
    if n.get("type") == "decision":
        w, h = w * 1.55, h * 1.7
    n["w"], n["h"] = w, max(h, 44)


def text_block(n, cx, cy, kind):
    lines, sub = n["lines"], n["sublines"]
    total = len(lines) + len(sub)
    y = cy - total * LINE_H / 2 + LINE_H * 0.75
    out = []
    first = sub if (kind == "timeline" and sub) else None
    seq = []
    if first:
        seq += [(l, True) for l in sub] + [(l, False) for l in lines]
    else:
        seq += [(l, kind != "org" or True) for l in lines] + [(l, None) for l in sub]
    for text, flag in seq:
        if kind == "timeline" and first:
            cls = "date" if flag else "lab"
        else:
            cls = "lab" if flag is not None else "sub"
        out.append(f'<text class="{cls}" x="{cx:.1f}" y="{y:.1f}" text-anchor="middle">{html.escape(text)}</text>')
        y += LINE_H
    return "".join(out)


def node_svg(n, kind):
    x, y, w, h = n["x"], n["y"], n["w"], n["h"]
    cx, cy = x + w / 2, y + h / 2
    t = n.get("type", "process")
    if kind == "flow" and t == "decision":
        shape = f'<polygon class="decision" points="{cx:.1f},{y:.1f} {x + w:.1f},{cy:.1f} {cx:.1f},{y + h:.1f} {x:.1f},{cy:.1f}"/>'
    elif kind == "flow" and t in ("start", "end"):
        shape = f'<rect class="{t}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}"/>'
    elif kind == "org":
        shape = f'<rect class="person" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8"/><rect class="bar" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="6" rx="3"/>'
    else:
        shape = f'<rect class="process" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8"/>'
    return f'<g class="node" data-id="{html.escape(str(n["id"]))}">{shape}{text_block(n, cx, cy + (3 if kind == "org" else 0), kind)}</g>'


def edge_svg(pts, label, arrow, lx=None, ly=None, eid=""):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    m = ' marker-end="url(#arr)"' if arrow else ""
    s = f'<path class="edge" data-edge="{html.escape(eid)}" d="{d}" fill="none"{m}/>'
    if label:
        tw_ = tw(label, FONT - 2) + 8
        s += (f'<rect class="lbbg" x="{lx - tw_ / 2:.1f}" y="{ly - 12:.1f}" width="{tw_:.1f}" height="17" rx="4"/>'
              f'<text class="elab" x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{html.escape(label)}</text>')
    return s


# ---------------------------------------------------------------- layouts
def layout_org(spec):
    nodes = {n["id"]: n for n in spec["nodes"]}
    kids = {i: [] for i in nodes}
    has_parent = set()
    for e in spec["edges"]:
        kids[e["from"]].append(e["to"])
        has_parent.add(e["to"])
    roots = [n["id"] for n in spec["nodes"] if n["id"] not in has_parent]
    for n in nodes.values():
        size_node(n, "org")
    bw = max(n["w"] for n in nodes.values())
    bh = max(n["h"] for n in nodes.values())
    for n in nodes.values():
        n["w"], n["h"] = bw, bh
    width = {}

    def subw(i):
        c = kids[i]
        width[i] = max(bw, sum(subw(k) for k in c) + HGAP * (len(c) - 1)) if c else bw
        return width[i]

    def place(i, left, depth):
        n = nodes[i]
        n["y"] = MARGIN + (28 if spec.get("title") else 0) + depth * (bh + VGAP)
        c = kids[i]
        if not c:
            n["x"] = left + (width[i] - bw) / 2
            return
        cur = left + (width[i] - (sum(width[k] for k in c) + HGAP * (len(c) - 1))) / 2
        for k in c:
            place(k, cur, depth + 1)
            cur += width[k] + HGAP
        n["x"] = (nodes[c[0]]["x"] + nodes[c[-1]]["x"]) / 2

    left = MARGIN
    for r in roots:
        subw(r)
        place(r, left, 0)
        left += width[r] + HGAP * 2
    edges = []
    for e in spec["edges"]:
        a, b = nodes[e["from"]], nodes[e["to"]]
        ax, ay = a["x"] + bw / 2, a["y"] + bh
        bx, by_ = b["x"] + bw / 2, b["y"]
        my = ay + VGAP / 2
        pts = [(ax, ay), (ax, my), (bx, my), (bx, by_)] if abs(ax - bx) > 0.5 else [(ax, ay), (bx, by_)]
        edges.append(edge_svg(pts, "", False, eid=f"{e['from']}>{e['to']}"))
    return list(nodes.values()), edges


def layout_flow(spec):
    nodes = {n["id"]: n for n in spec["nodes"]}
    order_ids = [n["id"] for n in spec["nodes"]]
    edges_in = spec["edges"]
    out = {i: [] for i in nodes}
    for e in edges_in:
        out[e["from"]].append(e["to"])
    for n in nodes.values():
        size_node(n, "flow")
    start = [n["id"] for n in spec["nodes"] if n["type"] == "start"][0]
    # DFS: find back edges, discovery order
    state, back, disc = {}, set(), []

    def dfs(i):
        state[i] = 1
        disc.append(i)
        for j in out[i]:
            if state.get(j) == 1:
                back.add((i, j))
            elif j not in state:
                dfs(j)
        state[i] = 2

    sys.setrecursionlimit(5000)
    dfs(start)
    fwd = [(e["from"], e["to"]) for e in edges_in if (e["from"], e["to"]) not in back]
    layer = {i: 0 for i in nodes}
    for _ in range(len(nodes) + 1):  # longest path layering on the acyclic graph
        changed = False
        for a, b in fwd:
            if layer[b] < layer[a] + 1:
                layer[b] = layer[a] + 1
                changed = True
        if not changed:
            break
    # end nodes sink to the last layer reached by their predecessors only (keep as is)
    nl = max(layer.values()) + 1
    layers = [[] for _ in range(nl)]
    for i in disc:
        layers[layer[i]].append(i)
    preds = {i: [a for a, b in fwd if b == i] for i in nodes}
    succs = {i: [b for a, b in fwd if a == i] for i in nodes}
    for _ in range(3):  # barycenter sweeps, stable
        for li in range(1, nl):
            pos = {k: x for x, k in enumerate(layers[li - 1])}
            layers[li].sort(key=lambda k: sum(pos[p] for p in preds[k] if p in pos) / max(1, len([p for p in preds[k] if p in pos])) if any(p in pos for p in preds[k]) else 1e9)
        for li in range(nl - 2, -1, -1):
            pos = {k: x for x, k in enumerate(layers[li + 1])}
            layers[li].sort(key=lambda k: sum(pos[s] for s in succs[k] if s in pos) / max(1, len([s for s in succs[k] if s in pos])) if any(s in pos for s in succs[k]) else 1e9)
    # y per layer
    ly, y = [], MARGIN + (28 if spec.get("title") else 0)
    for li in range(nl):
        hmax = max(nodes[k]["h"] for k in layers[li])
        ly.append((y, hmax))
        y += hmax + VGAP
    for li in range(nl):
        for k in layers[li]:
            nodes[k]["y"] = ly[li][0] + (ly[li][1] - nodes[k]["h"]) / 2
    # x: initial centered rows, then relax toward neighbours
    for li in range(nl):
        x = 0.0
        for k in layers[li]:
            nodes[k]["x"] = x
            x += nodes[k]["w"] + HGAP

    def center(k):
        return nodes[k]["x"] + nodes[k]["w"] / 2

    def spread(li, desired):
        ks = layers[li]
        cur = {k: desired[k] for k in ks}
        xs, right = {}, None
        for k in ks:
            left = cur[k] - nodes[k]["w"] / 2
            if right is not None and left < right + HGAP:
                left = right + HGAP
            xs[k] = left
            right = left + nodes[k]["w"]
        shift = sum(cur[k] - (xs[k] + nodes[k]["w"] / 2) for k in ks) / len(ks)
        for k in ks:
            nodes[k]["x"] = xs[k] + shift

    for li in range(nl):  # center the first row on 0
        row = layers[li]
        tot = sum(nodes[k]["w"] for k in row) + HGAP * (len(row) - 1)
        x = -tot / 2
        for k in row:
            nodes[k]["x"] = x
            x += nodes[k]["w"] + HGAP
    for sweep in range(4):
        for li in range(1, nl):
            des = {}
            for k in layers[li]:
                p = [center(a) for a in preds[k]]
                des[k] = sum(p) / len(p) if p else center(k)
            spread(li, des)
        for li in range(nl - 2, -1, -1):
            des = {}
            for k in layers[li]:
                s = [center(b) for b in succs[k]]
                des[k] = (sum(s) / len(s) + center(k)) / 2 if s else center(k)
            spread(li, des)
    minx = min(n["x"] for n in nodes.values())
    for n in nodes.values():
        n["x"] += MARGIN - minx
    # edges
    rows_right = [max(nodes[k]["x"] + nodes[k]["w"] for k in layers[li]) for li in range(nl)]
    gap_below = [ly[li][0] + ly[li][1] + VGAP / 2 for li in range(nl)]
    gap_above = [ly[li][0] - VGAP / 2 for li in range(nl)]
    chan = 0
    svg_edges, maxx = [], max(n["x"] + n["w"] for n in nodes.values())
    outs_by = {i: [e for e in edges_in if e["from"] == i] for i in nodes}
    for e in edges_in:
        a, b = nodes[e["from"]], nodes[e["to"]]
        la, lb = layer[e["from"]], layer[e["to"]]
        acx, bcx = a["x"] + a["w"] / 2, b["x"] + b["w"] / 2
        lab = (e.get("label") or "").strip()
        eid = f"{e['from']}>{e['to']}"
        isback = (e["from"], e["to"]) in back
        if not isback and lb == la + 1:
            if a["type"] == "decision" and len(outs_by[e["from"]]) > 1 and abs(bcx - acx) > 8:
                left = bcx < acx
                sx = a["x"] if left else a["x"] + a["w"]
                sy = a["y"] + a["h"] / 2
                far = (bcx < sx - 20) if left else (bcx > sx + 20)
                if far:  # the side run must not cross another box in the same row
                    lo_, hi_ = min(sx, bcx), max(sx, bcx)
                    for k in layers[la]:
                        o = nodes[k]
                        if k != e["from"] and o["x"] < hi_ and o["x"] + o["w"] > lo_ and o["y"] < sy < o["y"] + o["h"]:
                            far = False
                lx = sx + (-1 if left else 1) * (tw(lab, FONT - 2) / 2 + 12)
                if far:
                    pts = [(sx, sy), (bcx, sy), (bcx, b["y"])]
                else:
                    ox = sx + (-24 if left else 24)
                    my = gap_below[la]
                    pts = [(sx, sy), (ox, sy), (ox, my), (bcx, my), (bcx, b["y"])]
                svg_edges.append(edge_svg(pts, lab, True, lx, sy - 6, eid))
            else:
                sy = a["y"] + a["h"]
                my = gap_below[la]
                lo_x, hi_x = max(a["x"], b["x"]) + 14, min(a["x"] + a["w"], b["x"] + b["w"]) - 14
                if a["type"] == "decision":
                    straight = b["type"] != "decision" and b["x"] + 14 <= acx <= b["x"] + b["w"] - 14
                    vx = acx
                elif b["type"] == "decision":
                    straight = a["x"] + 14 <= bcx <= a["x"] + a["w"] - 14
                    vx = bcx
                else:
                    straight = hi_x >= lo_x
                    vx = min(max(acx, lo_x), hi_x) if straight else acx
                if straight:
                    pts = [(vx, sy), (vx, b["y"])]
                else:
                    pts = [(acx, sy), (acx, my), (bcx, my), (bcx, b["y"])]
                svg_edges.append(edge_svg(pts, lab, True, pts[0][0] + (tw(lab, FONT - 2) / 2 + 8 if lab else 0), sy + 16, eid))
        else:
            lo, hi = min(la, lb), max(la, lb)
            cx = max(rows_right[lo:hi + 1]) + 30 + 14 * chan
            chan += 1
            maxx = max(maxx, cx)
            sy = a["y"] + a["h"]
            y1 = gap_below[la]
            y2 = gap_above[lb]
            ex = bcx if b["type"] == "decision" else min(bcx + 22, b["x"] + b["w"] - 14)
            pts = [(acx, sy), (acx, y1), (cx, y1), (cx, y2), (ex, y2), (ex, b["y"])]
            svg_edges.append(edge_svg(pts, lab, True, acx + (tw(lab, FONT - 2) / 2 + 8 if lab else 0), sy + 16, eid))
    return list(nodes.values()), svg_edges


def layout_timeline(spec):
    ns = spec["nodes"]
    for n in ns:
        size_node(n, "timeline")
    bw = max(n["w"] for n in ns)
    step = bw + 24
    rtl = spec.get("dir") == "rtl"
    top_h = max(n["h"] for n in ns)
    axis_y = MARGIN + (28 if spec.get("title") else 0) + top_h + 50
    pts = []
    for i, n in enumerate(ns):
        idx = (len(ns) - 1 - i) if rtl else i
        cx = MARGIN + bw / 2 + idx * step
        n["w"] = bw
        n["x"] = cx - bw / 2
        up = i % 2 == 0
        n["up"] = up
        n["y"] = axis_y - 40 - n["h"] if up else axis_y + 40
        n["cx"] = cx
        pts.append(cx)
    edges = []
    for i in range(len(ns) - 1):
        a, b = ns[i], ns[i + 1]
        edges.append(edge_svg([(a["cx"], axis_y), (b["cx"], axis_y)], "", False, eid=f"{a['id']}>{b['id']}"))
    stubs = ""
    for n in ns:
        y0 = n["y"] + n["h"] if n["up"] else n["y"]
        stubs += f'<line class="stub" x1="{n["cx"]:.1f}" y1="{y0:.1f}" x2="{n["cx"]:.1f}" y2="{axis_y:.1f}"/><circle class="dot" cx="{n["cx"]:.1f}" cy="{axis_y:.1f}" r="6"/>'
    return ns, edges, stubs


# ---------------------------------------------------------------- output
def mermaid(spec):
    def q(s):
        return '"' + s.replace('"', "'") + '"'
    kind = spec["kind"]
    out = ["flowchart TD"]
    for n in spec["nodes"]:
        lab = n["label"] + (" - " + n["sub"] if n.get("sub") else "")
        t = n.get("type", "process")
        i = n["id"]
        if kind == "flow" and t == "decision":
            out.append(f"  {i}{{{q(lab)}}}")
        elif kind == "flow" and t in ("start", "end"):
            out.append(f"  {i}([{q(lab)}])")
        else:
            out.append(f"  {i}[{q(lab)}]")
    for e in spec["edges"]:
        lb = (e.get("label") or "").strip()
        out.append(f"  {e['from']} -->{'|' + q(lb) + '|' if lb else ''} {e['to']}")
    return "\n".join(out) + "\n"


def main():
    spec_path, out_dir, base = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    spec = json.load(open(spec_path, encoding="utf-8"))
    for n in spec.get("nodes", []):
        n["id"] = str(n.get("id"))
        if n.get("parent") is not None:
            n["parent"] = str(n["parent"])
    for e in spec.get("edges", []):
        e["from"], e["to"] = str(e["from"]), str(e["to"])
    errs, warns = validate(spec)
    for w in warns:
        print("WARNING:", w)
    if errs:
        print("ERRORS (fix the table and run again):")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    kind = spec["kind"]
    stubs = ""
    if kind == "org":
        nodes, edges = layout_org(spec)
    elif kind == "flow":
        nodes, edges = layout_flow(spec)
    else:
        nodes, edges, stubs = layout_timeline(spec)
    maxx = max(n["x"] + n["w"] for n in nodes)
    maxy = max(n["y"] + n["h"] for n in nodes)
    if kind == "flow":
        import re
        for e in edges:
            for m in re.finditer(r'd="M([^"]+)"', e):
                for p in m.group(1).replace("L", " ").split():
                    maxx = max(maxx, float(p.split(",")[0]))
    title = spec.get("title", "")
    W = max(maxx + MARGIN, tw(title, 20) + 2 * MARGIN if title else 0, 320)
    H = maxy + MARGIN
    rtl = spec.get("dir") == "rtl"
    css = """
text{font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","Noto Sans CJK SC","Noto Sans CJK KR","Noto Naskh Arabic",sans-serif}
.lab{font-size:15px;font-weight:600;fill:#1c2233}.sub{font-size:13px;fill:#4a5368}.date{font-size:13px;font-weight:700;fill:#3b5bdb}
.ttl{font-size:20px;font-weight:700;fill:#1c2233}.elab{font-size:13px;font-weight:600;fill:#364fc7}.lbbg{fill:#ffffff}
.process{fill:#e7f0ff;stroke:#3b5bdb;stroke-width:2}.decision{fill:#fff4d6;stroke:#e08e0b;stroke-width:2}
.start{fill:#dff5e3;stroke:#2b8a3e;stroke-width:2}.end{fill:#ffe3e3;stroke:#c92a2a;stroke-width:2}
.person{fill:#ffffff;stroke:#8a93a8;stroke-width:1.5}.bar{fill:#3b5bdb}
.edge{stroke:#495057;stroke-width:2;stroke-linejoin:round}.stub{stroke:#8a93a8;stroke-width:1.5}.dot{fill:#3b5bdb}
"""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
             f"<style>{css}</style>", f'<rect width="100%" height="100%" fill="#ffffff"/>',
             '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#495057"/></marker></defs>']
    if title:
        parts.append(f'<text class="ttl" x="{W / 2:.0f}" y="{MARGIN - 4 + 8}" text-anchor="middle">{html.escape(title)}</text>')
    parts += edges
    parts.append(stubs)
    parts += [node_svg(n, kind) for n in nodes]
    parts.append("</svg>")
    svg = "".join(parts)
    svg_path = os.path.join(out_dir, base + ".svg")
    open(svg_path, "w", encoding="utf-8").write(svg)
    if kind != "timeline":
        open(os.path.join(out_dir, base + ".mmd"), "w", encoding="utf-8").write(mermaid(spec))
    n_nodes, n_edges = svg.count('class="node"'), svg.count('class="edge"')
    print(f"SVG {svg_path}")
    chrome = find_chrome()
    png_path = os.path.join(out_dir, base + ".png")
    if chrome:
        scale = 2 if W <= 1600 else 1
        wrapper = os.path.join(out_dir, base + "-wrap.html")
        open(wrapper, "w", encoding="utf-8").write(f'<!DOCTYPE html><html><body style="margin:0;background:#fff">{svg}</body></html>')
        subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        f"--force-device-scale-factor={scale}", f"--window-size={int(W)},{int(H)}",
                        "--screenshot=" + png_path, "file://" + os.path.abspath(wrapper)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        os.remove(wrapper)
        if os.path.exists(png_path):
            from PIL import Image
            print("PNG", png_path, Image.open(png_path).size)
        else:
            print("PNG NOT BUILT")
    else:
        print("PNG NOT BUILT (Chrome not found): publish the svg instead")
    exp_nodes = len(spec["nodes"])
    exp_edges = len(spec["edges"])
    print(f"COUNTS table nodes={exp_nodes} connections={exp_edges} | drawn nodes={n_nodes} connections={n_edges}")
    if (exp_nodes, exp_edges) != (n_nodes, n_edges):
        print("ERROR: drawn counts differ from the table")
        sys.exit(1)
    print("OK")


main()
