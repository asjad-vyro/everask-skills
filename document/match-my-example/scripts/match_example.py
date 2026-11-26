#!/usr/bin/env python3
"""Copy an example .docx or .xlsx and fill the copy with new content (the example file is never changed).

  skeleton FILE                 the example's structure as JSON (indexes are what the plan refers to)
  fill FILE PLAN.json OUT       copy FILE to OUT, apply the plan, print a JSON check

PLAN.json: {"fixed": ["text that is meant to stay the same, e.g. headings and labels"], "ops": [...]}

.docx ops (indexes are the example's paragraph / table numbers from `skeleton`):
  {"op":"set_paragraph","index":3,"text":"new text"}
  {"op":"set_paragraph","index":3,"keep_prefix":"Date: ","text":"value after the label"}
  {"op":"delete_paragraph","index":7}
  {"op":"insert_after","index":5,"like":5,"text":"another bullet in the same format"}
  {"op":"set_cell","table":0,"row":1,"col":2,"text":"..."}
  {"op":"set_table_rows","table":0,"rows":[["a","b","c"],["d","e","f"]]}   (the header row is kept;
        rows are added or removed so the table holds exactly these data rows, formatted like the last data row)
  {"op":"replace_in_headers","find":"old","with":"new"}   (header and footer text)

.xlsx ops:
  {"op":"clear_values","sheet":"Sheet1","range":"A2:F30"}   (formulas are kept unless "include_formulas":true)
  {"op":"set_cell","sheet":"Sheet1","cell":"B4","value":12}
  {"op":"set_rows","sheet":"Sheet1","start_row":2,"start_col":1,"rows":[[..],[..]]}
        (new rows copy the format of start_row; a None value under a formula keeps the formula, adjusted)
"""
import sys, json, re, copy, shutil, collections

W = lambda tag: "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}" + tag
NUM = re.compile(r"\d[\d.,:/\-]*\d|\d")


def words(t):
    t = re.sub(r"[㐀-鿿가-힯぀-ヿ]", lambda m: " %s " % m.group(0), t or "")
    return re.findall(r"\w+", t.casefold())


def ngrams(t, n=4):
    w = words(t)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def kind_of(p):
    n = p.style.name if p.style is not None else ""
    if n.startswith("Heading") or n == "Title":
        return "heading"
    if n.startswith("List"):
        return "list"
    return "body"


def doc_text(doc):
    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                parts.append(c.text)
    for s in doc.sections:
        for part in (s.header, s.footer):
            parts += [p.text for p in part.paragraphs]
    return "\n".join(parts)


def run_props(p):
    out = set()
    for r in p.runs:
        if r.text.strip():
            out.add((r.font.name or "", r.font.size.pt if r.font.size else None, bool(r.bold)))
    return sorted(out, key=str)[:3]


# ---------------- docx ----------------

def docx_skeleton(path):
    from docx import Document
    d = Document(path)
    blocks = []
    for i, p in enumerate(d.paragraphs):
        t = p.text.strip()
        if not t:
            continue
        blocks.append({"index": i, "kind": kind_of(p), "style": p.style.name, "words": len(words(t)),
                       "text": t[:110], "runs": run_props(p), "align": str(p.alignment) if p.alignment is not None else None,
                       "pictures": 1 if p._p.findall(".//" + W("drawing")) else 0})
    tables = []
    for ti, t in enumerate(d.tables):
        rows = [[c.text.strip()[:30] for c in r.cells] for r in t.rows]
        tables.append({"table": ti, "rows": len(t.rows), "cols": len(t.columns), "first_rows": rows[:3]})
    s = d.sections[0]
    hf = [p.text for sec in d.sections for part in (sec.header, sec.footer) for p in part.paragraphs if p.text.strip()]
    return {"type": "docx", "paragraph_count": len(d.paragraphs), "blocks": blocks, "tables": tables,
            "headers_footers": hf, "pictures": len(d.inline_shapes),
            "page_cm": [round(s.page_width.cm, 1), round(s.page_height.cm, 1)],
            "word_count": len(words(doc_text(d))),
            "words_per_section": section_words(d)}


def section_words(d):
    out, cur, n = [], None, 0
    for p in d.paragraphs:
        if kind_of(p) == "heading":
            if cur is not None:
                out.append({"section": cur, "words": n})
            cur, n = p.text.strip()[:50], 0
        else:
            n += len(words(p.text))
    if cur is not None:
        out.append({"section": cur, "words": n})
    return out


def set_runs(p, text):
    """Put text in the paragraph, in the format of its first non-empty run."""
    runs = p.runs
    keep = next((r for r in runs if r.text.strip()), runs[0] if runs else None)
    if keep is None:
        p.add_run(text)
        return
    keep.text = text
    for r in runs:
        if r is not keep:
            r._r.getparent().remove(r._r)


def set_after_prefix(p, prefix, text):
    full = p.text
    if not full.startswith(prefix):
        return False
    pos, value_run = 0, None
    for r in p.runs:
        end = pos + len(r.text)
        if pos >= len(prefix) and value_run is None:
            value_run = r
        elif pos < len(prefix) < end:  # run straddles the label end
            cut = len(prefix) - pos
            tail = copy.deepcopy(r._r)
            r.text = r.text[:cut]
            r._r.addnext(tail)
            from docx.text.run import Run
            value_run = Run(tail, p)
            value_run.text = ""
        pos = end
    if value_run is None:
        p.add_run(text)
        return True
    value_run.text = text
    started = False
    for r in list(p.runs):
        if r._r is value_run._r:
            started = True
        elif started:
            r._r.getparent().remove(r._r)
    return True


def set_cell_text(cell, text):
    ps = cell.paragraphs
    set_runs(ps[0], text) if ps[0].runs else ps[0].add_run(text)
    for extra in ps[1:]:
        extra._p.getparent().remove(extra._p)


def docx_fill(src, plan, out):
    from docx import Document
    shutil.copyfile(src, out)
    d = Document(out)
    orig = list(d.paragraphs)
    tables = list(d.tables)
    log = []

    def ok(msg):
        log.append("done: " + msg)

    def bad(msg):
        log.append("NOT DONE: " + msg)

    for op in plan.get("ops", []):
        k = op.get("op")
        try:
            if k == "set_paragraph":
                p = orig[op["index"]]
                if op.get("keep_prefix"):
                    if set_after_prefix(p, op["keep_prefix"], op["text"]):
                        ok("paragraph %d value after '%s'" % (op["index"], op["keep_prefix"]))
                    else:
                        bad("paragraph %d does not start with '%s'" % (op["index"], op["keep_prefix"]))
                else:
                    set_runs(p, op["text"])
                    ok("paragraph %d" % op["index"])
            elif k == "delete_paragraph":
                p = orig[op["index"]]
                p._p.getparent().remove(p._p)
                ok("deleted paragraph %d" % op["index"])
            elif k == "insert_after":
                base, like = orig[op["index"]], orig[op.get("like", op["index"])]
                new = copy.deepcopy(like._p)
                base._p.addnext(new)
                from docx.text.paragraph import Paragraph
                np_ = Paragraph(new, base._parent)
                set_runs(np_, op["text"])
                ok("inserted a paragraph after %d formatted like %d" % (op["index"], op.get("like", op["index"])))
            elif k == "set_cell":
                set_cell_text(tables[op["table"]].cell(op["row"], op["col"]), op["text"])
                ok("table %d cell (%d,%d)" % (op["table"], op["row"], op["col"]))
            elif k == "set_table_rows":
                t = tables[op["table"]]
                want = op["rows"]
                have = len(t.rows) - 1
                tpl = copy.deepcopy(t.rows[-1]._tr)
                while have < len(want):
                    t.rows[-1]._tr.addnext(copy.deepcopy(tpl))
                    have += 1
                while have > len(want) and len(t.rows) > 2:
                    t._tbl.remove(t.rows[-1]._tr)
                    have -= 1
                if len(want) == 0 and len(t.rows) == 2:
                    t._tbl.remove(t.rows[-1]._tr)
                    have = 0
                for ri, row in enumerate(want):
                    for ci, val in enumerate(row):
                        set_cell_text(t.cell(ri + 1, ci), str(val))
                ok("table %d now has %d data rows" % (op["table"], len(want)))
            elif k == "replace_in_headers":
                n = 0
                for sec in d.sections:
                    for part in (sec.header, sec.footer):
                        for p in part.paragraphs:
                            if op["find"] in p.text:
                                set_runs(p, p.text.replace(op["find"], op["with"]))
                                n += 1
                ok("header/footer text replaced in %d paragraph(s)" % n) if n else bad("'%s' not found in headers or footers" % op["find"])
            else:
                bad("unknown op %s" % k)
        except Exception as e:
            bad("%s: %s" % (op, e))
    d.save(out)

    # checks
    d0, d1 = Document(src), Document(out)
    head0 = [p.text.strip() for p in d0.paragraphs if kind_of(p) == "heading"]
    head1 = [p.text.strip() for p in d1.paragraphs if kind_of(p) == "heading"]
    shapes0 = [(len(t.rows), len(t.columns)) for t in d0.tables]
    shapes1 = [(len(t.rows), len(t.columns)) for t in d1.tables]
    res = {"log": log, "headings_before": head0, "headings_after": head1,
           "table_columns_same": [a[1] for a in shapes0] == [b[1] for b in shapes1],
           "table_shapes_before": shapes0, "table_shapes_after": shapes1,
           "placeholders_left": len(re.findall(r"\[to add:", doc_text(d1))),
           "words_per_section_after": section_words(d1)}
    res.update(leftovers(doc_text(d0), doc_text(d1), plan.get("fixed", [])))
    return res


def leftovers(text0, text1, fixed):
    fixed_t = " ".join(fixed)
    fixed_ng = ngrams(fixed_t, 4)
    fixed_words = set(words(fixed_t))
    old = ngrams(text0, 4) - fixed_ng
    new = ngrams(text1, 4)
    shared = sorted(g for g in (old & new) if not all(w in fixed_words for w in g.split()))
    nums0 = {m.group(0) for m in NUM.finditer(text0)} - {m.group(0) for m in NUM.finditer(fixed_t)}
    nums1 = [m.group(0) for m in NUM.finditer(text1)]
    shared_nums = sorted({n for n in nums1 if n in nums0 and (len(n) > 1)})
    return {"leftover_phrases_from_example": shared[:25], "leftover_phrase_count": len(shared),
            "numbers_also_in_example": shared_nums[:25]}


# ---------------- xlsx ----------------

def xlsx_skeleton(path):
    import openpyxl
    wb = openpyxl.load_workbook(path)
    out = {"type": "xlsx", "sheets": []}
    for ws in wb.worksheets:
        formulas = [(c.coordinate, c.value) for row in ws.iter_rows() for c in row
                    if isinstance(c.value, str) and c.value.startswith("=")]
        rows = []
        for r in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 4)):
            rows.append([("" if c.value is None else str(c.value))[:25] for c in r])
        out["sheets"].append({"name": ws.title, "dims": ws.dimensions, "max_row": ws.max_row, "max_col": ws.max_column,
                              "first_rows": rows, "formula_count": len(formulas), "formula_examples": formulas[:6],
                              "merged": [str(m) for m in ws.merged_cells.ranges][:8],
                              "charts": len(getattr(ws, "_charts", [])), "images": len(getattr(ws, "_images", []))})
    return out


def xlsx_fill(src, plan, out):
    import openpyxl
    from openpyxl.formula.translate import Translator
    from openpyxl.utils import get_column_letter
    shutil.copyfile(src, out)
    wb = openpyxl.load_workbook(out)
    log = []
    for op in plan.get("ops", []):
        k = op.get("op")
        try:
            ws = wb[op["sheet"]]
            if k == "clear_values":
                n = 0
                for row in ws[op["range"]]:
                    for c in row:
                        if c.value is not None and (op.get("include_formulas") or not (isinstance(c.value, str) and c.value.startswith("="))):
                            c.value = None
                            n += 1
                log.append("done: cleared %d values in %s!%s (formulas kept)" % (n, op["sheet"], op["range"]))
            elif k == "set_cell":
                ws[op["cell"]].value = op["value"]
                log.append("done: %s!%s" % (op["sheet"], op["cell"]))
            elif k == "set_rows":
                r0, c0 = op["start_row"], op.get("start_col", 1)
                width = max(len(r) for r in op["rows"])
                width = max(width, ws.max_column - c0 + 1)
                for ri, row in enumerate(op["rows"]):
                    for ci in range(width):
                        tpl = ws.cell(r0, c0 + ci)
                        tgt = ws.cell(r0 + ri, c0 + ci)
                        if ri > 0:
                            tgt._style = copy.copy(tpl._style)
                        val = row[ci] if ci < len(row) else None
                        if val is None and isinstance(tpl.value, str) and tpl.value.startswith("="):
                            tgt.value = Translator(tpl.value, origin=tpl.coordinate).translate_formula(tgt.coordinate)
                        else:
                            tgt.value = val
                    if ri > 0 and ws.row_dimensions[r0].height:
                        ws.row_dimensions[r0 + ri].height = ws.row_dimensions[r0].height
                log.append("done: wrote %d rows from row %d on %s" % (len(op["rows"]), r0, op["sheet"]))
            else:
                log.append("NOT DONE: unknown op %s" % k)
        except Exception as e:
            log.append("NOT DONE: %s: %s" % (op, e))
    wb.save(out)
    wb0, wb1 = openpyxl.load_workbook(src), openpyxl.load_workbook(out)
    fixed = {str(x).strip().casefold() for x in plan.get("fixed", [])}
    same = []
    for ws0 in wb0.worksheets:
        ws1 = wb1[ws0.title] if ws0.title in wb1.sheetnames else None
        if ws1 is None:
            continue
        for row in ws0.iter_rows():
            for c in row:
                v = c.value
                if v is None or (isinstance(v, str) and v.startswith("=")):
                    continue
                if str(v).strip().casefold() in fixed:
                    continue
                if ws1[c.coordinate].value == v:
                    same.append("%s!%s=%r" % (ws0.title, c.coordinate, v))
    return {"log": log, "same_as_example_not_marked_fixed": same[:30], "same_count": len(same),
            "sheets_before": wb0.sheetnames, "sheets_after": wb1.sheetnames,
            "formulas_before": sum(1 for ws in wb0.worksheets for r in ws.iter_rows() for c in r if isinstance(c.value, str) and c.value.startswith("=")),
            "formulas_after": sum(1 for ws in wb1.worksheets for r in ws.iter_rows() for c in r if isinstance(c.value, str) and c.value.startswith("=")),
            "note": "charts and pictures in the workbook may not survive saving" }


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("skeleton", "fill"):
        print(__doc__)
        sys.exit(1)
    path = sys.argv[2]
    ext = path.lower().rsplit(".", 1)[-1]
    if ext not in ("docx", "xlsx"):
        print(json.dumps({"error": "only .docx and .xlsx examples are supported"}))
        sys.exit(1)
    if sys.argv[1] == "skeleton":
        res = docx_skeleton(path) if ext == "docx" else xlsx_skeleton(path)
    else:
        plan = json.load(open(sys.argv[3], encoding="utf-8"))
        res = (docx_fill if ext == "docx" else xlsx_fill)(path, plan, sys.argv[4])
        res["output"] = sys.argv[4]
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
