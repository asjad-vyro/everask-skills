#!/usr/bin/env python3
"""Helper for translating .docx, .xlsx and .pdf files unit by unit.

  extract FILE UNITS.json
      Writes every translatable unit as {"id", "text"}.
      docx: each non-empty paragraph (body, tables, headers, footers).
      xlsx: each text cell that is not a formula.
      pdf : each text block, page by page (for rebuilding, not in-place).
  apply FILE OUT UNITS.json MODE ORDER RTL T1.json [T2.json ...]
      docx/xlsx only. Each T file is a JSON object {id: translated text}.
      MODE  = replace | bilingual
      ORDER = source-first | translation-first   (bilingual only)
      RTL   = rtl | ltr   (rtl sets right-to-left on translated docx paragraphs)
      Units with no translation stay as they were and are listed.
  check UNITS.json T1.json [T2.json ...]
      Prints counts, untranslated ids and numbers of the source that
      do not appear in the translation.
"""
import copy
import json
import re
import sys
from collections import Counter

NUM = re.compile(r"\d+(?:[.,:/-]\d+)*")


def load_trans(paths):
    t = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            t.update(json.load(f))
    return t


# ---------------- docx ----------------
def docx_paragraphs(doc):
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    roots = [doc.element.body]
    for s in doc.sections:
        for part in (s.header, s.footer, s.first_page_header, s.first_page_footer,
                     s.even_page_header, s.even_page_footer):
            try:
                roots.append(part._element)
            except Exception:
                pass
    seen, out = set(), []
    for root in roots:
        for p in root.iter(qn("w:p")):
            # keep the element itself in the set: id() of a freed lxml proxy can be
            # reused, which silently skipped paragraphs and shifted the numbering
            if p in seen:
                continue
            seen.add(p)
            para = Paragraph(p, None)
            if para_text(p).strip():
                out.append(para)
    return out


def _own(el, p):
    """True when the nearest w:p above el is p itself (not a text box inside it)."""
    from docx.oxml.ns import qn
    a = el.getparent()
    while a is not None and a.tag != qn("w:p"):
        a = a.getparent()
    return a is p


def _is_line_break(el):
    from docx.oxml.ns import qn
    return el.get(qn("w:type")) in (None, "textWrapping")


def para_text(p):
    """Text of one paragraph: tabs as \t and line breaks as \n (page breaks and the
    tab stops defined in the paragraph properties are not text)."""
    from docx.oxml.ns import qn
    parts = []
    for el in p.iter():
        par = el.getparent()
        if par is None or par.tag != qn("w:r") or not _own(el, p):
            continue
        if el.tag == qn("w:t"):
            parts.append(el.text or "")
        elif el.tag == qn("w:tab"):
            parts.append("	")
        elif el.tag in (qn("w:br"), qn("w:cr")) and _is_line_break(el):
            parts.append("\n")
    return "".join(parts)


def set_para_text(p, text):
    """Put the translation into the paragraph's longest run (so that run's font,
    size, bold and so on carry over); the other runs are emptied. Words that were
    bold or italic inside a mixed paragraph therefore lose that emphasis."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    runs = [r for r in p.iter(qn("w:r")) if _own(r, p) and r.find(qn("w:t")) is not None]
    if not runs:
        return
    main = max(runs, key=lambda r: sum(len(t.text or "") for t in r.findall(qn("w:t"))))
    for r in p.iter(qn("w:r")):
        if not _own(r, p):
            continue
        for ch in list(r):
            if ch.tag in (qn("w:t"), qn("w:tab"), qn("w:cr")) or (
                    ch.tag == qn("w:br") and _is_line_break(ch)):
                r.remove(ch)
    buf = ""

    def flush():
        nonlocal buf
        if buf:
            t = OxmlElement("w:t")
            t.text = buf
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            main.append(t)
            buf = ""

    for ch in text:
        if ch == "	":
            flush()
            main.append(OxmlElement("w:tab"))
        elif ch == "\n":
            flush()
            main.append(OxmlElement("w:br"))
        else:
            buf += ch
    flush()


def set_rtl(p):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    pPr = p.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        p.insert(0, pPr)
    if pPr.find(qn("w:bidi")) is None:
        pPr.insert_element_before(
            OxmlElement("w:bidi"), "w:adjustRightInd", "w:snapToGrid", "w:spacing",
            "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
            "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap",
            "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange")


def extract_docx(path):
    import docx
    doc = docx.Document(path)
    return [{"id": f"p{i}", "text": para_text(p._p)} for i, p in enumerate(docx_paragraphs(doc), 1)]


def apply_docx(path, out, trans, mode, order, rtl):
    import docx
    from docx.oxml.ns import qn
    doc = docx.Document(path)
    for i, para in enumerate(docx_paragraphs(doc), 1):
        uid = f"p{i}"
        if uid not in trans:
            continue
        p = para._p
        if mode == "bilingual":
            c = copy.deepcopy(p)
            ppr = c.find(qn("w:pPr"))
            if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
                ppr.remove(ppr.find(qn("w:sectPr")))  # do not repeat a section break
            set_para_text(c, trans[uid])
            if rtl:
                set_rtl(c)
            if order == "translation-first":
                p.addprevious(c)
            else:
                p.addnext(c)
        else:
            set_para_text(p, trans[uid])
            if rtl:
                set_rtl(p)
    doc.save(out)


# ---------------- xlsx ----------------
def xlsx_cells(wb):
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str) and v.strip() and not v.startswith("="):
                    yield f"{ws.title}!{c.coordinate}", c


def extract_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path)
    return [{"id": i, "text": c.value} for i, c in xlsx_cells(wb)]


def apply_xlsx(path, out, trans, mode, order):
    import openpyxl
    wb = openpyxl.load_workbook(path)
    for uid, c in xlsx_cells(wb):
        if uid not in trans:
            continue
        if mode == "bilingual":
            a, b = (c.value, trans[uid]) if order == "source-first" else (trans[uid], c.value)
            c.value = a + "\n" + b
            c.alignment = copy.copy(c.alignment).__class__(
                wrap_text=True, horizontal=c.alignment.horizontal, vertical=c.alignment.vertical)
        else:
            c.value = trans[uid]
    wb.save(out)


# ---------------- pdf ----------------
def extract_pdf(path):
    import fitz
    units = []
    for pn, page in enumerate(fitz.open(path), 1):
        blocks = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]
        blocks.sort(key=lambda b: (round(b[1] / 5), b[0]))
        for bn, b in enumerate(blocks, 1):
            units.append({"id": f"pg{pn}-b{bn}", "text": " ".join(b[4].split())})
    return units


# ---------------- check ----------------
def check(units, trans):
    missing_ids = [u["id"] for u in units if u["id"] not in trans]
    src = Counter(n for u in units for n in NUM.findall(u["text"]))
    dst = Counter(n for u in units for n in NUM.findall(trans.get(u["id"], "")))
    lost = [n for n in src if src[n] > dst[n]]
    print(f"units in source: {len(units)}")
    print(f"units translated: {len(units) - len(missing_ids)}")
    print(f"untranslated ids: {missing_ids if missing_ids else 'none'}")
    print(f"numbers missing from translation: {lost if lost else 'none'}")


def main(a):
    if len(a) < 2:
        print(__doc__)
        return 2
    cmd = a[0]
    if cmd == "extract":
        path, outp = a[1], a[2]
        ext = path.lower().rsplit(".", 1)[-1]
        units = {"docx": extract_docx, "xlsx": extract_xlsx, "pdf": extract_pdf}[ext](path)
        with open(outp, "w", encoding="utf-8") as f:
            json.dump(units, f, ensure_ascii=False, indent=1)
        print(f"{len(units)} units, {sum(len(u['text']) for u in units)} characters -> {outp}")
    elif cmd == "apply":
        path, out, upath, mode, order, rtl = a[1:7]
        trans = load_trans(a[7:])
        ext = path.lower().rsplit(".", 1)[-1]
        if ext == "docx":
            apply_docx(path, out, trans, mode, order, rtl == "rtl")
        elif ext == "xlsx":
            apply_xlsx(path, out, trans, mode, order)
        else:
            print("apply works for .docx and .xlsx only")
            return 2
        with open(upath, encoding="utf-8") as f:
            check(json.load(f), trans)
        print("saved", out)
    elif cmd == "check":
        with open(a[1], encoding="utf-8") as f:
            check(json.load(f), load_trans(a[2:]))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
