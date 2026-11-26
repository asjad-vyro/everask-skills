#!/usr/bin/env python3
"""Apply a formatting rule list to a .docx in place (the text is never retyped).

  audit FILE                      what the file looks like now (JSON)
  apply FILE RULES.json OUT.docx  apply the rules, write OUT.docx, print a JSON audit
  new TEXT.txt OUT.docx           make a plain .docx from pasted text (one paragraph per line;
                                  "# " = title, "## " = heading 1, "### " = heading 2), then use apply

RULES.json keys (all optional; a key that is missing means "leave as it is"):
  page        {"size":"A4|Letter|Legal|A5", "orientation":"portrait|landscape",
               "margins_cm":{"top":2.5,"bottom":2.5,"left":2.5,"right":2.5} or a number}
  body        {"font","east_asian_font","size","line_spacing" (multiple),"line_spacing_pt" (exact),
               "space_before_pt","space_after_pt","alignment":"left|center|right|justify",
               "first_line_indent_cm","first_line_indent_chars"}
  title       same keys as body, plus "bold","italic","color"; applies to the Title style paragraph,
              or to paragraph {"paragraph_index": n}
  headings    {"1":{font,size,bold,italic,color,alignment,space_before_pt,space_after_pt,line_spacing},"2":{...}}
  detect_manual_headings  true: short all-bold Normal paragraphs become headings
  promote     [{"index":12,"level":1}, {"text":"Introduction","level":1}]
  demote      [index, ...]  heading-styled paragraphs that are really body text
  heading_numbering {"max_level":3,"level1_trailing_dot":false,"separator":" ","unnumbered":["References"]}
  captions    {"size","bold","italic","alignment","font","renumber":true,"separator":". "}
  references  {"heading":"References","sort":"alphabetical|none","hanging_indent_cm":1.27,
               font,size,line_spacing,space_after_pt,alignment}
  reference_edits [{"index":40,"text":"new punctuation of the same words"}]
  tables      {"font","size","line_spacing","alignment"}
  page_numbers {"position":"center|left|right","format":"{n}"}   (also "Page {n} of {total}")
  toc         {"title":"Contents","levels":3}
"""
import sys, json, re, copy, collections
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.run import Run

ALIGN = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER,
         "right": WD_ALIGN_PARAGRAPH.RIGHT, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}
SIZES = {"a4": (21.0, 29.7), "letter": (21.59, 27.94), "legal": (21.59, 35.56), "a5": (14.8, 21.0)}
LABELS = r"Table|Figure|Fig\.|Tabla|Figura|Tableau|Abbildung|Tabelle|Tabela|表|图|圖|Таблица|Рисунок"
CAP_RE = re.compile(r"^\s*(?P<label>%s)\s*(?P<num>\d+)(?P<sep>\s*[.:：\-–—]\s*|\s+)" % LABELS, re.I)
NUM_RE = re.compile(r"^\s*\d{1,2}(\.\d{1,2})*[.)]?\s+")
KNOWN = {"page", "body", "title", "headings", "detect_manual_headings", "promote", "demote",
         "heading_numbering", "captions", "references", "reference_edits", "tables",
         "page_numbers", "toc"}


def norm_ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def norm_loose(s):
    return re.sub(r"[\W_]+", "", (s or "").casefold())


def style_name(p):
    try:
        return p.style.name or ""
    except Exception:
        return ""


def heading_level(p):
    m = re.match(r"^Heading (\d)$", style_name(p))
    return int(m.group(1)) if m else 0


def runs_of(p):
    return [Run(r, p) for r in p._p.iter(qn("w:r"))]


def style_chain_value(style, getter):
    while style is not None:
        v = getter(style)
        if v is not None:
            return v
        style = style.base_style
    return None


def eff_font(p, r):
    if r.font.name:
        return r.font.name
    v = style_chain_value(p.style, lambda s: s.font.name)
    return v or "(default)"


def eff_size(p, r):
    if r.font.size:
        return r.font.size.pt
    v = style_chain_value(p.style, lambda s: s.font.size)
    return v.pt if v else None


def eff_spacing(p):
    pf = p.paragraph_format
    ls = pf.line_spacing
    if ls is None:
        ls = style_chain_value(p.style, lambda s: s.paragraph_format.line_spacing)
    if ls is None:
        return "(default)"
    if hasattr(ls, "pt"):
        return "%spt exact/min" % round(ls.pt, 1)
    return round(float(ls), 2)


# ---------- audit ----------

def all_paragraphs(doc):
    out = list(doc.paragraphs)
    return out


def find_ref_block(doc, heading_text):
    """Return (heading_index, [paragraph indexes]) for the reference list, or (None, [])."""
    paras = doc.paragraphs
    h = None
    for i, p in enumerate(paras):
        if heading_text and norm_ws(p.text).casefold() == heading_text.casefold() and \
                (heading_level(p) or len(p.text) < 40):
            h = i
    if h is None:
        return None, []
    idx = []
    for j in range(h + 1, len(paras)):
        p = paras[j]
        if heading_level(p):
            break
        if norm_ws(p.text):
            idx.append(j)
    return h, idx


def manual_heading_candidates(doc):
    paras = doc.paragraphs
    out = []
    for i, p in enumerate(paras):
        t = norm_ws(p.text)
        if not t or heading_level(p) or style_name(p) in ("Title", "Subtitle", "Caption") or len(t) > 100:
            continue
        if style_name(p).startswith("List") or CAP_RE.match(t) or t.endswith((".", "。", ":", ",")) and not NUM_RE.match(t + " "):
            if not NUM_RE.match(t):
                continue
        rs = [r for r in runs_of(p) if r.text.strip()]
        if not rs:
            continue
        bold = all((r.bold is True) or (r.bold is None and style_chain_value(p.style, lambda s: s.font.bold)) for r in rs)
        if not bold:
            continue
        m = NUM_RE.match(t if t[-1:] != "." else t)
        level = 1
        if m:
            level = min(3, m.group(0).strip().rstrip(".)").count(".") + 1)
        out.append({"index": i, "text": t[:70], "level": level})
    return out


def summary(doc, ref_heading="References"):
    paras = doc.paragraphs
    fonts, sizes, spacing = collections.Counter(), collections.Counter(), collections.Counter()
    for p in paras:
        if not norm_ws(p.text) or heading_level(p) or style_name(p) == "Title":
            continue
        spacing[str(eff_spacing(p))] += 1
        for r in runs_of(p):
            if r.text.strip():
                fonts[eff_font(p, r)] += 1
                sizes[str(eff_size(p, r))] += 1
    s = doc.sections[0]
    heads = [{"index": i, "level": heading_level(p), "text": norm_ws(p.text)[:70]}
             for i, p in enumerate(paras) if heading_level(p)]
    caps = [{"index": i, "text": norm_ws(p.text)[:70]} for i, p in enumerate(paras)
            if style_name(p) == "Caption" or CAP_RE.match(p.text or "")]
    h, idx = find_ref_block(doc, ref_heading)
    xml = doc.element.body.xml
    return {
        "paragraphs": len(paras), "tables": len(doc.tables), "pictures": len(doc.inline_shapes),
        "page": {"width_cm": round(s.page_width.cm, 2), "height_cm": round(s.page_height.cm, 2),
                 "margins_cm": {k: round(getattr(s, k + "_margin").cm, 2) for k in ("top", "bottom", "left", "right")}},
        "body_fonts": dict(fonts), "body_sizes": dict(sizes), "body_line_spacing": dict(spacing),
        "headings": heads, "manual_heading_candidates": manual_heading_candidates(doc),
        "captions": caps,
        "reference_block": {"heading_index": h, "entries": [{"index": j, "text": norm_ws(paras[j].text)[:90]} for j in idx]},
        "has_toc_field": "TOC \\" in xml, "has_page_number_field": any(
            "PAGE" in sec.footer._element.xml for sec in doc.sections),
    }


# ---------- helpers that write ----------

def set_rfonts(rpr, name, east):
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(a), name)
    rf.set(qn("w:eastAsia"), east or name)


def fmt_font(font_obj, rpr, spec):
    """font_obj: Run.font or Style.font; rpr: its rPr element."""
    if spec.get("font") or spec.get("east_asian_font"):
        name = spec.get("font") or spec.get("east_asian_font")
        set_rfonts(rpr, name, spec.get("east_asian_font"))
    if spec.get("size") is not None:
        font_obj.size = Pt(spec["size"])
        sz = rpr.find(qn("w:szCs"))
        if sz is None:
            sz = OxmlElement("w:szCs")
            rpr.append(sz)
        sz.set(qn("w:val"), str(int(round(spec["size"] * 2))))
    if "bold" in spec:
        font_obj.bold = bool(spec["bold"])
    if "italic" in spec:
        font_obj.italic = bool(spec["italic"])
    if spec.get("color"):
        font_obj.color.rgb = RGBColor.from_string(spec["color"].lstrip("#").upper())


def fmt_para(p, spec):
    pf = p.paragraph_format
    if spec.get("alignment"):
        pf.alignment = ALIGN[spec["alignment"]]
    if spec.get("line_spacing_pt") is not None:
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        pf.line_spacing = Pt(spec["line_spacing_pt"])
    elif spec.get("line_spacing") is not None:
        pf.line_spacing = float(spec["line_spacing"])
    if spec.get("space_before_pt") is not None:
        pf.space_before = Pt(spec["space_before_pt"])
    if spec.get("space_after_pt") is not None:
        pf.space_after = Pt(spec["space_after_pt"])
    if spec.get("hanging_indent_cm") is not None:
        pf.left_indent = Cm(spec["hanging_indent_cm"])
        pf.first_line_indent = Cm(-spec["hanging_indent_cm"])
    elif spec.get("first_line_indent_chars") is not None:
        n = spec["first_line_indent_chars"]
        pf.first_line_indent = Pt((spec.get("size") or 12) * n)
        ind = p._p.get_or_add_pPr().find(qn("w:ind"))
        for a in ("w:hanging", "w:hangingChars"):
            if ind.get(qn(a)) is not None:
                del ind.attrib[qn(a)]
        ind.set(qn("w:firstLineChars"), str(int(n * 100)))
    elif spec.get("first_line_indent_cm") is not None:
        pf.first_line_indent = Cm(spec["first_line_indent_cm"])
        ind = p._p.get_or_add_pPr().find(qn("w:ind"))
        if ind is not None and ind.get(qn("w:firstLineChars")) is not None:
            del ind.attrib[qn("w:firstLineChars")]


def fmt_all(p, spec):
    fmt_para(p, spec)
    for r in runs_of(p):
        fmt_font(r.font, r._r.get_or_add_rPr(), spec)


def get_style(doc, name, base="Normal"):
    try:
        return doc.styles[name]
    except KeyError:
        st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        try:
            st.base_style = doc.styles[base]
        except KeyError:
            pass
        return st


def style_apply(doc, name, spec):
    try:
        st = doc.styles[name]
    except KeyError:
        return
    fmt_font(st.font, st.element.get_or_add_rPr(), spec)
    pf = st.paragraph_format
    if spec.get("line_spacing") is not None and spec.get("line_spacing_pt") is None:
        pf.line_spacing = float(spec["line_spacing"])
    if spec.get("space_before_pt") is not None:
        pf.space_before = Pt(spec["space_before_pt"])
    if spec.get("space_after_pt") is not None:
        pf.space_after = Pt(spec["space_after_pt"])
    if spec.get("alignment"):
        pf.alignment = ALIGN[spec["alignment"]]


def plain_title_style(doc):
    """Remove the template's coloured rule under the Title style and its colour."""
    try:
        st = doc.styles["Title"]
    except KeyError:
        return
    ppr = st.element.pPr
    if ppr is not None:
        for b in ppr.findall(qn("w:pBdr")):
            ppr.remove(b)
    rpr = st.element.rPr
    if rpr is not None:
        for c in rpr.findall(qn("w:color")):
            rpr.remove(c)


def replace_prefix(p, remove_len, new_prefix):
    remaining = remove_len
    rs = p.runs
    for r in rs:
        if remaining <= 0:
            break
        t = r.text
        cut = min(len(t), remaining)
        r.text = t[cut:]
        remaining -= cut
    if p.runs:
        p.runs[0].text = new_prefix + p.runs[0].text
    else:
        p.add_run(new_prefix)


def add_field(paragraph, instr, placeholder="1"):
    def mk(kind):
        r = OxmlElement("w:r")
        fc = OxmlElement("w:fldChar")
        fc.set(qn("w:fldCharType"), kind)
        r.append(fc)
        return r
    paragraph._p.append(mk("begin"))
    r = OxmlElement("w:r")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = " %s " % instr
    r.append(it)
    paragraph._p.append(r)
    paragraph._p.append(mk("separate"))
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = placeholder
    r.append(t)
    paragraph._p.append(r)
    paragraph._p.append(mk("end"))


# ---------- apply ----------

def apply(doc, rules, notes):
    log = []
    added = []  # elements we create (ignored by the text check)

    def note(rule, status, count=None, detail=None):
        e = {"rule": rule, "status": status}
        if count is not None:
            e["places"] = count
        if detail:
            e["detail"] = detail
        log.append(e)

    for k in rules:
        if k not in KNOWN:
            notes.append("unknown rule key ignored: %s" % k)

    orig = list(doc.paragraphs)
    ref_cfg = rules.get("references") or {}
    ref_head, ref_idx = find_ref_block(doc, ref_cfg.get("heading", "References")) if ref_cfg else (None, [])
    ref_els = [orig[j]._p for j in ref_idx]
    ref_head_el = orig[ref_head]._p if ref_head is not None else None

    # classify (before any change)
    before = {}
    for p in orig:
        before[p._p] = norm_ws(p.text)

    # page
    if "page" in rules:
        pg = rules["page"]
        n = 0
        for s in doc.sections:
            if pg.get("size"):
                w, h = SIZES[pg["size"].lower()]
                land = s.page_width > s.page_height
                if pg.get("orientation"):
                    land = pg["orientation"] == "landscape"
                s.page_width, s.page_height = (Cm(max(w, h)), Cm(min(w, h))) if land else (Cm(min(w, h)), Cm(max(w, h)))
                s.orientation = WD_ORIENT.LANDSCAPE if land else WD_ORIENT.PORTRAIT
            m = pg.get("margins_cm")
            if m is not None:
                if not isinstance(m, dict):
                    m = {k: m for k in ("top", "bottom", "left", "right")}
                for k, v in m.items():
                    setattr(s, k + "_margin", Cm(v))
            n += 1
        note("page size, orientation and margins", "applied", n, "%d section(s)" % n)

    # promote / demote / detect
    promoted = []
    for it in rules.get("promote", []):
        p = None
        if "index" in it:
            p = orig[it["index"]]
        else:
            for q in orig:
                if norm_ws(q.text) == norm_ws(it.get("text")):
                    p = q
                    break
        if p is None:
            note("promote %s" % it, "NOT DONE", 0, "paragraph not found")
            continue
        p.style = get_style(doc, "Heading %d" % it["level"])
        promoted.append(p)
    if rules.get("detect_manual_headings"):
        skip_i = (rules.get("title") or {}).get("paragraph_index")
        for c in manual_heading_candidates(doc):
            if c["index"] == skip_i:
                continue
            p = orig[c["index"]]
            if p in promoted or heading_level(p):
                continue
            p.style = get_style(doc, "Heading %d" % c["level"])
            promoted.append(p)
    if promoted:
        note("manual headings turned into real headings", "applied", len(promoted),
             "; ".join("%d: %s" % (orig.index(p), norm_ws(p.text)[:40]) for p in promoted))
    for i in rules.get("demote", []):
        orig[i].style = doc.styles["Normal"]

    # classify now
    kinds = {}
    cap_cfg = rules.get("captions")
    for i, p in enumerate(orig):
        t = norm_ws(p.text)
        if not t:
            continue
        if p._p in ref_els:
            kinds[p._p] = "ref"
        elif heading_level(p):
            kinds[p._p] = "heading"
        elif style_name(p) == "Title" or (rules.get("title", {}).get("paragraph_index") == i):
            kinds[p._p] = "title"
        elif style_name(p) == "Caption" or CAP_RE.match(t):
            kinds[p._p] = "caption"
        else:
            kinds[p._p] = "body"

    # styles
    if "body" in rules:
        style_apply(doc, "Normal", rules["body"])
        style_apply(doc, "Body Text", rules["body"])
    for lv, spec in (rules.get("headings") or {}).items():
        spec = dict(spec)
        spec.setdefault("color", "000000")
        style_apply(doc, "Heading %s" % lv, spec)
    if "title" in rules:
        style_apply(doc, "Title", rules["title"])
        plain_title_style(doc)
    if cap_cfg:
        style_apply(doc, "Caption", cap_cfg)

    counts = collections.Counter()
    # headings
    hspec = rules.get("headings") or {}
    for p in orig:
        k = kinds.get(p._p)
        if k == "heading" and hspec:
            lv = heading_level(p)
            below = [int(x) for x in hspec if int(x) <= lv]
            spec = dict(hspec.get(str(lv)) or hspec.get(str(max(below) if below else min(int(x) for x in hspec))) or {})
            spec.setdefault("color", "000000")
            spec.setdefault("keep_with_next", True)
            fmt_all(p, spec)
            p.paragraph_format.keep_with_next = True
            counts["headings"] += 1
    if hspec:
        note("heading fonts, sizes and spacing", "applied", counts["headings"])

    # title
    if "title" in rules:
        spec = dict(rules["title"])
        spec.setdefault("color", "000000")
        n = 0
        for p in orig:
            if kinds.get(p._p) == "title":
                fmt_all(p, spec)
                n += 1
        note("title format", "applied" if n else "NOT DONE", n, None if n else "no Title-style paragraph; give paragraph_index")

    # body
    if "body" in rules:
        spec = dict(rules["body"])
        n = 0
        for p in orig:
            if kinds.get(p._p) == "body":
                is_list = style_name(p).startswith("List") or p._p.find(".//" + qn("w:numPr")) is not None
                s2 = {k: v for k, v in spec.items() if k not in ("bold", "italic", "color")}
                if is_list:
                    s2 = {k: v for k, v in s2.items() if not k.startswith("first_line")}
                fmt_para(p, s2)
                for r in runs_of(p):
                    fmt_font(r.font, r._r.get_or_add_rPr(), {k: v for k, v in s2.items() if k in ("font", "east_asian_font", "size")})
                n += 1
        note("body font, size, spacing, alignment, indent", "applied", n)
        # empty paragraphs: font only, so blank lines have the same height
        for p in orig:
            if p._p not in kinds:
                fmt_para(p, {k: v for k, v in spec.items() if k in ("line_spacing", "line_spacing_pt")})

    # captions
    if cap_cfg:
        n = 0
        counters = collections.Counter()
        for p in orig:
            if kinds.get(p._p) != "caption":
                continue
            cspec = dict(cap_cfg)
            for k in ("font", "east_asian_font"):
                if k not in cspec and k in rules.get("body", {}):
                    cspec[k] = rules["body"][k]
            fmt_all(p, {k: v for k, v in cspec.items() if k in (
                "font", "east_asian_font", "size", "bold", "italic", "alignment", "line_spacing", "space_before_pt", "space_after_pt")})
            m = CAP_RE.match(p.text or "")
            if m and (cap_cfg.get("renumber") or cap_cfg.get("separator") is not None):
                lab = m.group("label")
                key = "fig" if lab.lower().startswith(("fig", "图", "圖", "рис")) else "tab"
                counters[key] += 1
                num = counters[key] if cap_cfg.get("renumber") else int(m.group("num"))
                sep = cap_cfg.get("separator", m.group("sep"))
                space = "" if re.match(r"[表图圖]", lab) else " "
                replace_prefix(p, m.end(), "%s%s%s%s" % (lab, space, num, sep))
            n += 1
        note("caption format and numbering", "applied" if n else "nothing found", n)

    # references
    if ref_cfg:
        n = 0
        spec = {k: v for k, v in ref_cfg.items() if k in (
            "font", "east_asian_font", "size", "line_spacing", "line_spacing_pt", "space_before_pt",
            "space_after_pt", "alignment", "hanging_indent_cm")}
        if "body" in rules:
            for k in ("font", "east_asian_font", "size", "line_spacing", "line_spacing_pt"):
                if k in rules["body"] and k not in spec and not (k == "line_spacing" and "line_spacing_pt" in spec):
                    spec[k] = rules["body"][k]
        for e in rules.get("reference_edits", []):
            p = orig[e["index"]]
            if p._p not in ref_els:
                note("reference edit %s" % e["index"], "NOT DONE", 0, "paragraph is not in the reference list")
                continue
            rs = p.runs
            if rs:
                rs[0].text = e["text"]
                for r in rs[1:]:
                    r._r.getparent().remove(r._r)
            n += 1
        if rules.get("reference_edits"):
            note("reference punctuation edits", "applied", n)
        for p in orig:
            if p._p in ref_els:
                fmt_para(p, spec)
                for r in runs_of(p):
                    fmt_font(r.font, r._r.get_or_add_rPr(), spec)
        note("reference list format (hanging indent)", "applied" if ref_els else "NOT DONE", len(ref_els),
             None if ref_els else "no reference list found under heading '%s'" % ref_cfg.get("heading", "References"))
        if ref_cfg.get("sort", "none") == "alphabetical" and ref_els:
            def key(el):
                t = norm_ws("".join(x.text or "" for x in el.iter(qn("w:t"))))
                t = re.sub(r"^\s*(\[\d+\]|\d+[.)])\s*", "", t)
                return t.casefold()
            ordered = sorted(ref_els, key=key)
            moved = ordered != ref_els
            anchor = ref_els[0].getprevious()
            for el in ref_els:
                el.getparent().remove(el)
            for el in reversed(ordered):
                anchor.addnext(el)
            note("reference list sorted alphabetically", "applied", len(ref_els),
                 "order changed" if moved else "was already in order")
        elif ref_els:
            note("reference list order", "kept as it was")

    # tables
    if "tables" in rules:
        spec = dict(rules["tables"])
        if "font" not in spec and "body" in rules and "font" in rules["body"]:
            spec["font"] = rules["body"]["font"]
            if "east_asian_font" in rules["body"]:
                spec["east_asian_font"] = rules["body"]["east_asian_font"]
        n = 0
        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        fmt_para(p, {k: v for k, v in spec.items() if k in ("line_spacing", "line_spacing_pt", "alignment")})
                        for r in runs_of(p):
                            fmt_font(r.font, r._r.get_or_add_rPr(), {k: v for k, v in spec.items() if k in ("font", "east_asian_font", "size")})
                        n += 1
        note("table text", "applied", n)

    # heading numbering (after fonts so the new text takes the run format)
    hn = rules.get("heading_numbering")
    if hn:
        maxl = hn.get("max_level", 3)
        sep = hn.get("separator", " ")
        skip = {x.casefold() for x in hn.get("unnumbered", [])}
        cnt = [0] * 10
        n = 0
        for p in orig:
            if kinds.get(p._p) != "heading":
                continue
            lv = heading_level(p)
            txt = norm_ws(p.text)
            m = NUM_RE.match(p.text)
            bare = txt[len(m.group(0).strip()):].strip() if m else txt
            if bare.casefold() in skip or lv > maxl:
                if m:
                    replace_prefix(p, m.end(), "")
                continue
            cnt[lv] += 1
            for j in range(lv + 1, 10):
                cnt[j] = 0
            label = ".".join(str(cnt[j] or 1) for j in range(1, lv + 1))
            if lv == 1 and hn.get("level1_trailing_dot"):
                label += "."
            replace_prefix(p, m.end() if m else 0, label + sep)
            n += 1
        note("heading numbering", "applied", n)

    # page numbers
    pn = rules.get("page_numbers")
    if pn:
        fmt = pn.get("format", "{n}")
        pos = pn.get("position", "center")
        for s in doc.sections:
            f = s.footer
            f.is_linked_to_previous = False
            p = f.paragraphs[0] if f.paragraphs else f.add_paragraph()
            for r in list(p._p):
                if r.tag != qn("w:pPr"):
                    p._p.remove(r)
            p.alignment = ALIGN[pos]
            for part in re.split(r"(\{n\}|\{total\})", fmt):
                if part == "{n}":
                    add_field(p, "PAGE")
                elif part == "{total}":
                    add_field(p, "NUMPAGES")
                elif part:
                    p.add_run(part)
            if "body" in rules:
                for r in runs_of(p):
                    fmt_font(r.font, r._r.get_or_add_rPr(), {k: v for k, v in rules["body"].items() if k in ("font", "east_asian_font")})
        note("page numbers", "applied", len(doc.sections), "footer, %s" % pos)

    # toc
    tc = rules.get("toc")
    if tc:
        first_h = next((p for p in doc.paragraphs if heading_level(p)), None)
        if first_h is None:
            note("table of contents", "NOT DONE", 0, "no headings to list")
        else:
            title = doc.add_paragraph(tc.get("title", "Contents"))
            if "headings" in rules and "1" in rules["headings"]:
                fmt_all(title, {k: v for k, v in rules["headings"]["1"].items() if k in ("font", "east_asian_font", "size", "bold")})
            toc_p = doc.add_paragraph()
            add_field(toc_p, 'TOC \\o "1-%d" \\h \\z \\u' % tc.get("levels", 3),
                      "Right-click here and choose Update Field to build the table of contents.")
            for el in (title._p, toc_p._p):
                first_h._p.addprevious(el)
                added.append(el)
            st = doc.settings.element
            if st.find(qn("w:updateFields")) is None:
                uf = OxmlElement("w:updateFields")
                uf.set(qn("w:val"), "true")
                st.append(uf)
            note("table of contents", "applied", 1, "a real Word TOC field; Word fills it in when the file is opened (choose Update Field if asked)")

    return log, orig, kinds, before, ref_els


def text_check(orig, kinds, before, ref_els):
    problems = []
    changed_ok = collections.Counter()
    for p in orig:
        t0 = before[p._p]
        t1 = norm_ws(p.text)
        if t0 == t1:
            continue
        k = kinds.get(p._p)
        if k == "heading" and NUM_RE.sub("", t0 + " ", 1).strip() == NUM_RE.sub("", t1 + " ", 1).strip() or \
                (k == "heading" and norm_loose(NUM_RE.sub("", t0)) == norm_loose(NUM_RE.sub("", t1))):
            changed_ok["heading numbers"] += 1
        elif k == "caption" and CAP_RE.sub("", t0 + " ", 1).strip() == CAP_RE.sub("", t1 + " ", 1).strip():
            changed_ok["caption numbers"] += 1
        elif k == "ref" and norm_loose(t0) == norm_loose(t1):
            changed_ok["reference punctuation"] += 1
        elif t1 == "" and t0 == "":
            pass
        else:
            problems.append({"before": t0[:80], "after": t1[:80]})
    return {"text_identical_apart_from": dict(changed_ok), "unexpected_text_changes": problems,
            "ok": not problems}


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("audit", "apply", "new"):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "new":
        d = Document()
        sec = d.sections[0]
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)  # A4 unless the rules say otherwise
        plain_title_style(d)
        for line in open(sys.argv[2], encoding="utf-8").read().splitlines():
            if not line.strip():
                continue
            m = re.match(r"^(#{1,3}) (.*)$", line)
            if not m:
                d.add_paragraph(line.strip())
            elif len(m.group(1)) == 1:
                d.add_paragraph(m.group(2).strip(), style="Title")
            else:
                d.add_paragraph(m.group(2).strip(), style="Heading %d" % (len(m.group(1)) - 1))
        d.save(sys.argv[3])
        print(json.dumps({"output": sys.argv[3], "paragraphs": len(d.paragraphs)}))
        return
    doc = Document(sys.argv[2])
    if sys.argv[1] == "audit":
        print(json.dumps(summary(doc), ensure_ascii=False, indent=1))
        return
    rules = json.load(open(sys.argv[3], encoding="utf-8"))
    out = sys.argv[4]
    notes = []
    ref_h = (rules.get("references") or {}).get("heading", "References")
    pre = summary(doc, ref_h)
    # body text before, in document order (for the order check)
    seq_before = [norm_loose(p.text) for p in doc.paragraphs if norm_ws(p.text)]
    tbl_before = [norm_loose(c.text) for t in doc.tables for r in t.rows for c in r.cells]
    log, orig, kinds, before, ref_els = apply(doc, rules, notes)
    chk = text_check(orig, kinds, before, ref_els)
    tbl_after = [norm_loose(c.text) for t in doc.tables for r in t.rows for c in r.cells]
    chk["table_text_identical"] = tbl_before == tbl_after
    chk["ok"] = chk["ok"] and chk["table_text_identical"]
    doc.save(out)
    post = summary(Document(out), ref_h)
    for k in ("manual_heading_candidates", "reference_block"):
        pre.pop(k, None)
        post.pop(k, None)
    post["headings"] = post["headings"][:40]
    pre["headings"] = pre["headings"][:40]
    print(json.dumps({"output": out, "rules": log, "text_check": chk, "before": pre, "after": post,
                      "notes": notes + ["only fonts, spacing, margins, styles, numbering, captions and reference "
                                        "order were touched; text boxes, footnotes and pictures are not reformatted"]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
