#!/usr/bin/env python3
"""Apply specific edits to a .docx, .xlsx, .pptx or .pdf in place.

  scan FILE                 counts of what the file holds, plus an outline
  find FILE "TEXT"          every place TEXT occurs, numbered in file order
  edit FILE OUT EDITS.json  apply the edits, write OUT, print before/after counts

EDITS.json is a list of objects, applied in order. "occurrence" is "all" or a
number counted in file order (as shown by `find`); default "all".
  all formats : {"op":"replace","find":"..","with":"..","occurrence":"all"}
  docx        : {"op":"delete_paragraph","starts_with":"..","occurrence":1}
                {"op":"move_section","heading":"..","after":".."}   (or "before")
                {"op":"format","contains":"..","size":14,"bold":true,"italic":false}
  xlsx        : {"op":"set_cell","sheet":"..","cell":"B4","value":..}
  pptx        : {"op":"delete_slide","slide":3}  {"op":"move_slide","slide":3,"to":1}
                {"op":"format","contains":"..","size":28}
  pdf         : {"op":"delete_page","page":2}
Slide and page numbers start at 1 and refer to the file as it is after the earlier edits.
"""
import json
import sys


# ---------- text replacement across runs ----------
def replace_in_runs(texts, find, repl, want, counter):
    """texts: list of run strings. Returns (new_texts, number_of_matches_changed)."""
    joined = "".join(texts)
    if not find or find not in joined:
        return texts, 0
    owner = [i for i, t in enumerate(texts) for _ in t]
    spans, pos = [], 0
    while True:
        k = joined.find(find, pos)
        if k < 0:
            break
        counter["n"] += 1
        if want == "all" or int(want) == counter["n"]:
            spans.append((k, k + len(find)))
        pos = k + len(find)
    if not spans:
        return texts, 0
    starts = {s: e for s, e in spans}
    new = [[] for _ in texts]
    i = 0
    while i < len(joined):
        if i in starts:
            new[owner[i]].append(repl)
            i = starts[i]
        else:
            new[owner[i]].append(joined[i])
            i += 1
    return ["".join(x) for x in new], len(spans)


def count_in_runs(texts, find, counter, log, where):
    joined = "".join(texts)
    pos = 0
    while True:
        k = joined.find(find, pos)
        if k < 0:
            break
        counter["n"] += 1
        a = max(0, k - 25)
        log.append(f"#{counter['n']} {where}: ...{joined[a:k + len(find) + 25]}...".replace("\n", " "))
        pos = k + len(find)


# ---------- docx ----------
def d_paragraphs(doc):
    from docx.oxml.ns import qn
    roots = [doc.element.body]
    for s in doc.sections:
        for part in (s.header, s.footer, s.first_page_header, s.first_page_footer,
                     s.even_page_header, s.even_page_footer):
            try:
                # reading .paragraphs of a header with no definition would create an
                # empty header part in the saved file; only use existing ones
                if part.is_linked_to_previous:
                    continue
                roots.append(part._element)
            except Exception:
                pass
    seen, out = set(), []
    for r in roots:
        for p in r.iter(qn("w:p")):
            # the set keeps the elements alive: id() of a freed lxml proxy can be
            # reused, which silently skipped paragraphs
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def d_ts(p):
    """The w:t elements of this paragraph only (not of a text box inside it)."""
    from docx.oxml.ns import qn
    out = []
    for t in p.iter(qn("w:t")):
        a = t.getparent()
        while a is not None and a.tag != qn("w:p"):
            a = a.getparent()
        if a is p:
            out.append(t)
    return out


def d_text(p):
    return "".join(t.text or "" for t in d_ts(p))


def d_stats(doc):
    ps = d_paragraphs(doc)
    cells = sum(len(r.cells) for t in doc.tables for r in t.rows)
    return {"paragraphs_with_text": sum(1 for p in ps if d_text(p).strip()),
            "paragraphs_total": len(ps), "tables": len(doc.tables), "table_cells": cells,
            "images": len(doc.inline_shapes), "sections": len(doc.sections)}


def d_style(p):
    from docx.oxml.ns import qn
    ps = p.find(qn("w:pPr") + "/" + qn("w:pStyle"))
    return ps.get(qn("w:val")) if ps is not None else ""


def d_level(p):
    s = d_style(p).lower().replace(" ", "")
    if s == "title":
        return 0
    if s.startswith("heading") and s[7:].isdigit():
        return int(s[7:])
    return None


def d_edit(doc, e, log):
    from docx.oxml.ns import qn
    op = e["op"]
    want = e.get("occurrence", "all")
    ps = d_paragraphs(doc)
    if op == "replace":
        c, n = {"n": 0}, 0
        for p in ps:
            ts = d_ts(p)
            new, m = replace_in_runs([t.text or "" for t in ts], e["find"], e["with"], want, c)
            if m:
                for t, s in zip(ts, new):
                    t.text = s
                    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                n += m
        log.append(f"replace '{e['find']}': found {c['n']}, changed {n}")
    elif op == "delete_paragraph":
        c, n = 0, 0
        for p in ps:
            if d_text(p).strip().startswith(e["starts_with"]):
                c += 1
                if want == "all" or int(want) == c:
                    parent = p.getparent()
                    ppr = p.find(qn("w:pPr"))
                    keeps_section = ppr is not None and ppr.find(qn("w:sectPr")) is not None
                    if keeps_section or (parent.tag == qn("w:tc") and len(parent.findall(qn("w:p"))) == 1):
                        for t in d_ts(p):
                            t.text = ""
                    else:
                        parent.remove(p)
                    n += 1
        log.append(f"delete_paragraph '{e['starts_with']}': found {c}, deleted {n}")
    elif op == "move_section":
        body = doc.element.body
        kids = list(body)
        def find_head(txt):
            for k in kids:
                if k.tag == qn("w:p") and d_text(k).strip().startswith(txt) and d_level(k) is not None:
                    return k
        h = find_head(e["heading"])
        tgt_txt = e.get("after") or e.get("before")
        t = find_head(tgt_txt)
        if h is None or t is None:
            log.append(f"move_section NOT DONE: heading '{e['heading'] if h is None else tgt_txt}' not found")
            return
        def block(head):
            lvl, i, out = d_level(head), kids.index(head), [head]
            for k in kids[i + 1:]:
                if k.tag == qn("w:sectPr"):
                    break
                if k.tag == qn("w:p") and d_level(k) is not None and d_level(k) <= lvl:
                    break
                out.append(k)
            return out
        moving = block(h)
        if t in moving:
            log.append("move_section NOT DONE: target is inside the section being moved")
            return
        if "after" in e:
            anchor = block(t)[-1]
            for k in reversed(moving):
                anchor.addnext(k)
        else:
            for k in moving:
                t.addprevious(k)
        log.append(f"move_section '{e['heading']}': moved {len(moving)} blocks")
    elif op == "format":
        n = 0
        from docx.shared import Pt
        from docx.text.paragraph import Paragraph
        for p in ps:
            if e["contains"] in d_text(p):
                for r in Paragraph(p, None).runs:
                    if "size" in e:
                        r.font.size = Pt(e["size"])
                    if "bold" in e:
                        r.font.bold = e["bold"]
                    if "italic" in e:
                        r.font.italic = e["italic"]
                n += 1
        log.append(f"format paragraphs containing '{e['contains']}': {n}")
    else:
        log.append(f"unknown op for docx: {op}")


def d_find(doc, text):
    log, c = [], {"n": 0}
    for i, p in enumerate(d_paragraphs(doc), 1):
        count_in_runs([t.text or "" for t in d_ts(p)], text, c, log, f"paragraph {i}")
    return log


def d_scan(doc):
    lines = []
    for i, p in enumerate(d_paragraphs(doc), 1):
        t = d_text(p).strip()
        if t:
            lines.append(f"{i} [{d_style(p) or 'Normal'}] {t[:70]}")
    return lines


# ---------- xlsx ----------
def x_stats(wb):
    vals = forms = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    vals += 1
                    if isinstance(c.value, str) and c.value.startswith("="):
                        forms += 1
    return {"sheets": len(wb.worksheets), "cells_with_values": vals, "formulas": forms}


def x_text_cells(wb):
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.strip() and not c.value.startswith("="):
                    yield ws, c


def x_edit(wb, e, log):
    op = e["op"]
    if op == "replace":
        c, n = {"n": 0}, 0
        for ws, cell in x_text_cells(wb):
            new, m = replace_in_runs([cell.value], e["find"], e["with"], e.get("occurrence", "all"), c)
            if m:
                cell.value = new[0]
                n += m
        log.append(f"replace '{e['find']}': found {c['n']}, changed {n} (formula cells are never touched)")
    elif op == "set_cell":
        if e["sheet"] not in wb.sheetnames:
            log.append(f"set_cell NOT DONE: sheet '{e['sheet']}' not found; sheets are {wb.sheetnames}")
            return
        cell = wb[e["sheet"]][e["cell"]]
        old = cell.value
        cell.value = e["value"]
        log.append(f"set_cell {e['sheet']}!{e['cell']}: {old!r} -> {e['value']!r}")
    else:
        log.append(f"unknown op for xlsx: {op}")


def x_find(wb, text):
    log, c = [], {"n": 0}
    for ws, cell in x_text_cells(wb):
        count_in_runs([cell.value], text, c, log, f"{ws.title}!{cell.coordinate}")
    return log


# ---------- pptx ----------
def p_paragraphs(prs):
    def shapes(shs):
        for s in shs:
            if s.shape_type == 6:
                yield from shapes(s.shapes)
            else:
                yield s
    for n, slide in enumerate(prs.slides, 1):
        for s in shapes(slide.shapes):
            if s.has_text_frame:
                for para in s.text_frame.paragraphs:
                    yield n, para
            if getattr(s, "has_table", False) and s.has_table:
                for row in s.table.rows:
                    for cell in row.cells:
                        for para in cell.text_frame.paragraphs:
                            yield n, para


def p_stats(prs):
    return {"slides": len(prs.slides),
            "shapes": sum(len(s.shapes) for s in prs.slides),
            "paragraphs_with_text": sum(1 for _, p in p_paragraphs(prs) if "".join(r.text for r in p.runs).strip())}


def p_edit(prs, e, log):
    op = e["op"]
    if op == "replace":
        c, n = {"n": 0}, 0
        for _, para in p_paragraphs(prs):
            runs = para.runs
            new, m = replace_in_runs([r.text for r in runs], e["find"], e["with"], e.get("occurrence", "all"), c)
            if m:
                for r, s in zip(runs, new):
                    r.text = s
                n += m
        log.append(f"replace '{e['find']}': found {c['n']}, changed {n}")
    elif op == "delete_slide":
        ids = prs.slides._sldIdLst
        i = e["slide"] - 1
        if not 0 <= i < len(ids):
            log.append(f"delete_slide NOT DONE: no slide {e['slide']}")
            return
        sid = list(ids)[i]
        prs.part.drop_rel(sid.rId)
        ids.remove(sid)
        log.append(f"delete_slide {e['slide']}: done")
    elif op == "move_slide":
        ids = prs.slides._sldIdLst
        lst = list(ids)
        i, j = e["slide"] - 1, e["to"] - 1
        if not (0 <= i < len(lst) and 0 <= j < len(lst)):
            log.append("move_slide NOT DONE: slide number out of range")
            return
        el = lst[i]
        ids.remove(el)
        ids.insert(j, el)
        log.append(f"move_slide {e['slide']} -> {e['to']}: done")
    elif op == "format":
        from pptx.util import Pt
        n = 0
        for _, para in p_paragraphs(prs):
            if e["contains"] in "".join(r.text for r in para.runs):
                for r in para.runs:
                    if "size" in e:
                        r.font.size = Pt(e["size"])
                    if "bold" in e:
                        r.font.bold = e["bold"]
                n += 1
        log.append(f"format paragraphs containing '{e['contains']}': {n}")
    else:
        log.append(f"unknown op for pptx: {op}")


def p_find(prs, text):
    log, c = [], {"n": 0}
    for n, para in p_paragraphs(prs):
        count_in_runs([r.text for r in para.runs], text, c, log, f"slide {n}")
    return log


# ---------- pdf ----------
def _mu():
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    return pymupdf


def _font_for(flags):
    """A built-in PDF font close to the original span (serif, mono, bold, italic)."""
    bold, italic = bool(flags & 16), bool(flags & 2)
    if flags & 8:
        return ("cobo" if bold else "coit" if italic else "cour")
    if flags & 4:
        return ("tibo" if bold else "tiit" if italic else "tiro")
    return ("hebo" if bold else "heit" if italic else "helv")


def f_replace(doc, e, log):
    mu = _mu()
    want, c, n = e.get("occurrence", "all"), 0, 0
    if any(ord(ch) > 255 for ch in e["with"]):
        log.append(f"replace '{e['find']}' NOT DONE: the new text has letters the PDF font cannot draw")
        return
    want_text = " ".join(e["find"].split())
    for page in doc:
        # search_for ignores case: keep only hits whose text matches exactly
        chosen = []
        for r in page.search_for(e["find"]):
            if want_text not in " ".join(page.get_textbox(r).split()):
                continue
            c += 1
            if want == "all" or int(want) == c:
                chosen.append(r)
        if not chosen:
            continue
        spans = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for sp in l["spans"]:
                    col = sp["color"]
                    spans.append((mu.Rect(sp["bbox"]), sp["size"], sp["flags"], sp["origin"][1],
                                  (((col >> 16) & 255) / 255, ((col >> 8) & 255) / 255, (col & 255) / 255)))

        def style(rect):
            cx, cy = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
            for sb, size, flags, base, color in spans:
                if sb.contains(mu.Point(cx, cy)):
                    return size, flags, base, color
            return 11, 0, rect.y1 - 2.5, (0, 0, 0)

        # Redaction removes the old text but can pull the rest of the line to the
        # left, so the words to the right of each match are redrawn where they were.
        tails = {}
        for r in chosen:
            for w in page.get_text("words"):
                wr = mu.Rect(w[:4])
                if abs(w[3] - r.y1) < 2 and w[0] >= r.x1 - 0.5 and not any(wr.intersects(x) for x in chosen):
                    tails[(round(w[0], 1), round(w[1], 1), w[4])] = wr
        draws = [(r.x0, style(r), e["with"]) for r in chosen if e["with"]]
        for (x0, y0, text), wr in tails.items():
            size, flags, base, color = style(wr)
            draws.append((wr.x0, (size, flags, base, color), text))
        for rect in list(chosen) + list(tails.values()):
            page.add_redact_annot(mu.Rect(rect.x0 + 0.6, rect.y0 + 0.6, rect.x1 - 0.6, rect.y1 - 0.6),
                                  fill=(1, 1, 1))
        page.apply_redactions()
        for x0, (size, flags, base, color), text in draws:
            page.insert_text((x0, base), text, fontname=_font_for(flags), fontsize=size, color=color)
        n += len(chosen)
    log.append(f"replace '{e['find']}': found {c}, changed {n} (text does not reflow; Latin letters only)")


def f_edit(doc, e, log):
    op = e["op"]
    if op == "replace":
        f_replace(doc, e, log)
    elif op == "delete_page":
        if not 1 <= e["page"] <= len(doc):
            log.append(f"delete_page NOT DONE: no page {e['page']}")
            return
        doc.delete_page(e["page"] - 1)
        log.append(f"delete_page {e['page']}: done")
    else:
        log.append(f"unknown op for pdf: {op}")


def f_find(doc, text):
    log, c = [], 0
    for pn, page in enumerate(doc, 1):
        for r in page.search_for(text):
            c += 1
            log.append(f"#{c} page {pn} at ({r.x0:.0f},{r.y0:.0f})")
    return log


# ---------- main ----------
def ext_of(path):
    return path.lower().rsplit(".", 1)[-1]


def main(a):
    if len(a) < 2:
        print(__doc__)
        return 2
    cmd, path = a[0], a[1]
    ext = ext_of(path)
    if ext == "docx":
        import docx
        obj = docx.Document(path)
        stats, find, edit, scan = d_stats, d_find, d_edit, d_scan
    elif ext == "xlsx":
        import openpyxl
        obj = openpyxl.load_workbook(path)
        stats, find, edit, scan = x_stats, x_find, x_edit, lambda o: [f"{ws.title}: {ws.dimensions}" for ws in o.worksheets]
    elif ext == "pptx":
        import pptx
        obj = pptx.Presentation(path)
        stats, find, edit = p_stats, p_find, p_edit
        scan = lambda o: [f"slide {n}: " + "".join(r.text for r in p.runs)[:70] for n, p in p_paragraphs(o) if "".join(r.text for r in p.runs).strip()]
    elif ext == "pdf":
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        obj = fitz.open(path)
        stats = lambda o: {"pages": len(o), "text_characters": sum(len(p.get_text()) for p in o)}
        find, edit = f_find, f_edit
        scan = lambda o: [f"page {i}: " + " ".join(p.get_text().split())[:70] for i, p in enumerate(o, 1)]
    else:
        print("supported: .docx .xlsx .pptx .pdf")
        return 2
    if cmd == "scan":
        print("counts:", json.dumps(stats(obj)))
        for line in scan(obj)[:250]:
            print(line)
    elif cmd == "find":
        hits = find(obj, a[2])
        print(f"{len(hits)} occurrence(s) of {a[2]!r}")
        for h in hits:
            print(h)
    elif cmd == "edit":
        out = a[2]
        with open(a[3], encoding="utf-8") as f:
            edits = json.load(f)
        before = stats(obj)
        log = []
        for e in edits:
            edit(obj, e, log)
        if ext == "pdf":
            obj.save(out, garbage=1, deflate=True)
        else:
            obj.save(out)
        if ext == "pdf":
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            after = stats(fitz.open(out))
        elif ext == "docx":
            import docx
            after = stats(docx.Document(out))
        elif ext == "xlsx":
            import openpyxl
            after = stats(openpyxl.load_workbook(out))
        else:
            import pptx
            after = stats(pptx.Presentation(out))
        for line in log:
            print(line)
        print("before:", json.dumps(before))
        print("after: ", json.dumps(after))
        print("saved", out)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
