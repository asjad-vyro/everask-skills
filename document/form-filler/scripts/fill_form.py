#!/usr/bin/env python3
"""List the blanks of a form and fill them from values the user gave.

  fields FILE                    every blank (PDF form fields, blanks on a flat PDF, .docx blanks and
                                 empty cells next to labels, .xlsx empty cells next to labels) as JSON
  fill FILE VALUES.json OUT      write the values into a copy, re-read it, print what is filled and what is blank
  render FILE OUT.png [PAGE]     draw a PDF page to a PNG (PAGE counts from 1) to look at it

VALUES.json: {"values": [{"id": "<id from fields>", "value": "text" | true | false}]}
Text is written exactly as given: this script never reformats a date or number.
A signature, consent, declaration or "I agree" box is never ticked and a signature field is never filled:
those are reported as blocked, for the user to do.
"""
import sys, json, re, shutil, glob, os, collections

BLANK = re.compile(r"_{3,}|\.{5,}|…{2,}|-{6,}")
BOX = "☐"
CHECKED = "☒"
GUARD = re.compile(
    r"consent|agree|declar|certif|attest|acknowledg|signature|signed|sign here|sign below|i confirm|i accept|"
    r"i understand|terms|authori[sz]|permission|waive|oath|swear|"
    r"consentim|concord|acuerd|acepto|declaro|firma|assinatura|autoriz|"
    r"einverstanden|erkl[aä]r|unterschrift|accord|je certifie|signature|"
    r"同意|声明|聲明|签名|簽名|签字|サイン|同意し|동의|서명|согласен|согласи|подпис|заявля|"
    r"kabul|onay|imza|beyan|موافق|توقيع|setuju|tanda tangan|persetujuan", re.I)


def is_guarded(*texts):
    return bool(GUARD.search(" ".join(t for t in texts if t)))


def nl(s):
    return re.sub(r"\s+", " ", s or "").strip()


# ---------------- PDF ----------------

def pdf_label(page, rect, words):
    midy = (rect.y0 + rect.y1) / 2
    if rect.height > 20:
        midy = rect.y0 + 4
    tol = max(10.0 if rect.height > 20 else 5.0, min(rect.height, 16) * 0.6)
    left = [w for w in words if abs((w[1] + w[3]) / 2 - midy) <= tol and w[2] <= rect.x0 + 3]
    left.sort(key=lambda w: w[0])
    chunk = []
    for w in reversed(left):
        if chunk and chunk[-1][0] - w[2] > 40:
            break
        chunk.append(w)
    if chunk:
        return nl(" ".join(w[4] for w in reversed(chunk)))[:80]
    above = [w for w in words if w[3] <= rect.y0 + 2 and w[1] >= rect.y0 - 26
             and w[2] > rect.x0 - 4 and w[0] < rect.x1]
    if above:
        ymax = max(w[3] for w in above)
        line = sorted([w for w in above if abs(w[3] - ymax) < 3], key=lambda w: w[0])
        return nl(" ".join(w[4] for w in line))[:80]
    return ""


def pdf_fields(path):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    doc = fitz.open(path)
    out = []
    n_widgets = 0
    for pno, page in enumerate(doc):
        words = page.get_text("words")
        for w in page.widgets() or []:
            n_widgets += 1
            t = w.field_type_string
            kind = {"Text": "text", "CheckBox": "checkbox", "RadioButton": "radio", "ComboBox": "choice",
                    "ListBox": "choice", "Signature": "signature", "Button": "button"}.get(t, t.lower())
            label = pdf_label(page, w.rect, words)
            if kind in ("checkbox", "radio"):
                mid = (w.rect.y0 + w.rect.y1) / 2
                right = sorted([x for x in words if abs((x[1] + x[3]) / 2 - mid) <= 8 and x[0] >= w.rect.x1 - 2],
                               key=lambda x: x[0])
                if right:
                    label = nl(" ".join(x[4] for x in right))[:90]
            e = {"id": w.field_name, "kind": kind, "label": label, "page": pno + 1,
                 "current": w.field_value if w.field_value not in (None, "", "Off") else ""}
            if kind in ("choice",):
                e["options"] = [str(c[0] if isinstance(c, (list, tuple)) else c) for c in (w.choice_values or [])]
            if kind == "radio" or kind == "checkbox":
                try:
                    e["on_state"] = w.on_state()
                except Exception:
                    pass
            if kind == "signature" or is_guarded(w.field_name, label):
                e["protected"] = True
            if w.field_flags & 1:
                e["read_only"] = True
            out.append(e)
        # flat blanks: lines, underscore runs and empty boxes (only when the page has no widgets)
        if not any(True for _ in (page.widgets() or [])):
            blanks = []
            underscore_rects = []
            for d in page.get_drawings():
                r = d["rect"]
                if r.width >= 40 and r.height <= 1.5 and r.y0 > 20:
                    blanks.append(fitz.Rect(r.x0, r.y0 - 12, r.x1, r.y0 + 0.5))
                elif d.get("items") and len(d["items"]) == 1 and d["items"][0][0] == "l":
                    p1, p2 = d["items"][0][1], d["items"][0][2]
                    if abs(p1.y - p2.y) < 1 and abs(p1.x - p2.x) >= 40:
                        blanks.append(fitz.Rect(min(p1.x, p2.x), p1.y - 12, max(p1.x, p2.x), p1.y + 0.5))
            for w in words:
                if BLANK.fullmatch(w[4].strip()):
                    blanks.append(fitz.Rect(w[0], w[1], w[2], w[3]))
                    underscore_rects.append(blanks[-1])
            for d in page.get_drawings():
                r = d["rect"]
                if 40 <= r.width <= 400 and 12 <= r.height <= 40 and d.get("fill") is None and \
                        d.get("items") and d["items"][0][0] == "re" and not page.get_textbox(r).strip():
                    blanks.append(r)
            seen = []
            blanks.sort(key=lambda r: (round(r.y0 / 4), r.x0))
            k = 0
            for r in blanks:
                if any(abs(r.y1 - s.y1) < 3 and abs(r.x0 - s.x0) < 3 for s in seen):
                    continue
                seen.append(r)
                label = pdf_label(page, r, [w for w in words if not BLANK.fullmatch(w[4].strip())])
                e = {"id": "p%d.f%d" % (pno + 1, k), "kind": "blank", "label": label, "page": pno + 1,
                     "box": [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)]}
                if r in underscore_rects:
                    e["underscore"] = True
                if is_guarded(label):
                    e["protected"] = True
                out.append(e)
                k += 1
    return out, {"pages": len(doc), "form_fields": n_widgets}


def pick_font(text):
    if all(ord(c) < 256 for c in text):
        return "helv", None
    pats = ["/usr/share/fonts/**/NotoSans-Regular.ttf", "/usr/share/fonts/**/DejaVuSans.ttf",
            "/usr/share/fonts/**/NotoSansCJK*.ttc", "/usr/share/fonts/**/NotoSansSC*.otf",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"]
    for pat in pats:
        hits = sorted(glob.glob(pat, recursive=True))
        if hits:
            return "uf", hits[0]
    return None, None


def pdf_fill(src, values, out):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    fields, _ = pdf_fields(src)
    by_id = {f["id"]: f for f in fields}
    doc = fitz.open(src)
    log, blocked = [], []
    done = {}
    for v in values:
        fid, val = v["id"], v["value"]
        f = by_id.get(fid)
        if not f:
            log.append("NOT DONE: no field with id %s" % fid)
            continue
        if f.get("protected"):
            blocked.append({"id": fid, "label": f["label"], "reason": "signature, consent or declaration: left for the user"})
            continue
        if f.get("read_only"):
            log.append("NOT DONE: %s is read-only" % fid)
            continue
        page = doc[f["page"] - 1]
        if f["kind"] == "blank":
            text = str(val)
            r = fitz.Rect(*f["box"])
            fn, ff = pick_font(text)
            if fn is None:
                log.append("NOT DONE: %s needs a font for these characters and none was found" % fid)
                continue
            size = min(11.0, max(r.height - 2, 6))
            font = fitz.Font(fontfile=ff) if ff else fitz.Font("helv")
            while size > 6 and font.text_length(text, fontsize=size) > r.width - 4:
                size -= 0.5
            if font.text_length(text, fontsize=size) > r.width - 4:
                log.append("NOT DONE: %s: text too long for the blank (%.0f pt wide); shorten it" % (fid, r.width))
                continue
            kw = {"fontname": "F0", "fontfile": ff} if ff else {"fontname": "helv"}
            page.insert_text((r.x0 + 2, (r.y0 + size + 3) if r.height > 24 else r.y1 - (4.5 if f.get('underscore') else 2.5)), text, fontsize=size, color=(0, 0, 0.55 * 0), **kw)
            log.append("done: %s (%s) filled at size %.1f" % (fid, f["label"], size))
            done[fid] = text
            continue
        for w in page.widgets():
            if w.field_name != fid:
                continue
            if f["kind"] == "checkbox":
                w.field_value = w.on_state() if val in (True, "true", "True", "yes", "Yes") else "Off"
            elif f["kind"] == "radio":
                w.field_value = str(val)
            elif f["kind"] == "choice":
                opts = f.get("options") or []
                if opts and str(val) not in opts:
                    log.append("NOT DONE: %s: '%s' is not one of %s" % (fid, val, opts))
                    break
                w.field_value = str(val)
            else:
                w.field_value = str(val)
                if w.text_maxlen and len(str(val)) > w.text_maxlen:
                    log.append("NOT DONE: %s: longer than the field's limit of %d characters" % (fid, w.text_maxlen))
                    break
            w.update()
            log.append("done: %s (%s)" % (fid, f["label"]))
            done[fid] = val
            break
    doc.save(out)
    # read back
    chk, _ = pdf_fields(out)
    back = {c["id"]: c for c in chk}
    readback = []
    for v in values:
        fid = v["id"]
        if fid not in done:
            continue
        f = by_id[fid]
        if f["kind"] == "blank":
            doc2 = fitz.open(out)
            r = fitz.Rect(*f["box"])
            actual = nl(doc2[f["page"] - 1].get_textbox(r + (-1, -3, 1, 3)))
            ok = nl(str(v["value"])) in actual
        elif f["kind"] == "checkbox":
            actual = back[fid]["current"]
            ok = bool(actual) == (v["value"] in (True, "true", "True", "yes", "Yes"))
        else:
            actual = back[fid]["current"]
            ok = str(actual) == str(v["value"])
        readback.append({"id": fid, "label": f["label"], "expected": v["value"], "actual": actual, "ok": ok})
    return fields, log, blocked, done, readback


# ---------------- DOCX ----------------

def docx_fields(path):
    from docx import Document
    from docx.oxml.ns import qn
    d = Document(path)
    out = []

    def para_blanks(p, pid, where):
        k = 0
        pre = ""
        for r in p.runs:
            t = r.text
            for m in sorted(list(BLANK.finditer(t)) + list(re.finditer(BOX, t)), key=lambda m: m.start()):
                if m.group(0) == BOX:
                    label = nl(t[m.end():m.end() + 60] or "")
                    e = {"id": "%s.c%d" % (pid, k), "kind": "checkbox", "label": label or nl(p.text)[:60], "where": where}
                else:
                    label = nl((pre + t[:m.start()]))[-60:]
                    e = {"id": "%s.b%d" % (pid, k), "kind": "blank", "label": label, "where": where}
                if is_guarded(label, p.text):
                    e["protected"] = True
                out.append(e)
                k += 1
            pre += t
    for i, p in enumerate(d.paragraphs):
        para_blanks(p, "p%d" % i, "paragraph %d" % i)
    for ti, t in enumerate(d.tables):
        for ri, row in enumerate(t.rows):
            cells = row.cells
            for ci, c in enumerate(cells):
                if cells.index(c) != ci:
                    continue
                if not nl(c.text):
                    left = nl(cells[ci - 1].text) if ci > 0 else ""
                    above = nl(t.rows[ri - 1].cells[ci].text) if ri > 0 else ""
                    label = left or above
                    if label:
                        e = {"id": "t%dr%dc%d" % (ti, ri, ci), "kind": "cell", "label": label[:60],
                             "where": "table %d row %d column %d" % (ti, ri, ci)}
                        if is_guarded(label):
                            e["protected"] = True
                        out.append(e)
                else:
                    for pi, p in enumerate(c.paragraphs):
                        para_blanks(p, "t%dr%dc%dp%d" % (ti, ri, ci, pi), "table %d row %d column %d" % (ti, ri, ci))
    # content controls
    for si, sdt in enumerate(d.element.body.iter(qn("w:sdt"))):
        txt = "".join(t.text or "" for t in sdt.iter(qn("w:t")))
        out.append({"id": "sdt%d" % si, "kind": "content_control", "label": nl(txt)[:60], "where": "content control %d" % si,
                    "note": "placeholder text; fill with fill op"})
    return out, {"paragraphs": len(d.paragraphs), "tables": len(d.tables)}


def docx_fill(src, values, out):
    from docx import Document
    from docx.oxml.ns import qn
    from docx.text.run import Run
    fields, _ = docx_fields(src)
    by_id = {f["id"]: f for f in fields}
    shutil.copyfile(src, out)
    d = Document(out)
    log, blocked, done = [], [], {}

    def find_par(pid):
        m = re.match(r"^p(\d+)$", pid)
        if m:
            return d.paragraphs[int(m.group(1))]
        m = re.match(r"^t(\d+)r(\d+)c(\d+)p(\d+)$", pid)
        return d.tables[int(m.group(1))].rows[int(m.group(2))].cells[int(m.group(3))].paragraphs[int(m.group(4))]

    for v in values:
        fid, val = v["id"], v["value"]
        f = by_id.get(fid)
        if not f:
            log.append("NOT DONE: no field with id %s" % fid)
            continue
        if f.get("protected"):
            blocked.append({"id": fid, "label": f["label"], "reason": "signature, consent or declaration: left for the user"})
            continue
        try:
            if f["kind"] == "cell":
                m = re.match(r"^t(\d+)r(\d+)c(\d+)$", fid)
                cell = d.tables[int(m.group(1))].rows[int(m.group(2))].cells[int(m.group(3))]
                p = cell.paragraphs[0]
                run = p.add_run(str(val))
                left = d.tables[int(m.group(1))].rows[int(m.group(2))].cells[max(0, int(m.group(3)) - 1)]
                src_run = next((r for pp in left.paragraphs for r in pp.runs if r.text.strip()), None)
                if src_run is not None and src_run.font.size:
                    run.font.size = src_run.font.size
                if src_run is not None and src_run.font.name:
                    run.font.name = src_run.font.name
                log.append("done: %s (%s)" % (fid, f["label"]))
                done[fid] = str(val)
            elif f["kind"] in ("blank", "checkbox"):
                pid, tail = fid.rsplit(".", 1)
                p = find_par(pid)
                target = int(tail[1:])
                k = 0
                hit = False
                for r in p.runs:
                    t = r.text
                    pieces = []
                    pos = 0
                    for m in sorted(list(BLANK.finditer(t)) + list(re.finditer(BOX, t)), key=lambda m: m.start()):
                        if k == target:
                            repl = str(val) if m.group(0) != BOX else (CHECKED if val in (True, "true", "True", "yes", "Yes") else BOX)
                            pieces.append(t[pos:m.start()] + repl)
                            pos = m.end()
                            hit = True
                        k += 1
                    if pieces:
                        r.text = "".join(pieces) + t[pos:]
                        break
                if hit:
                    log.append("done: %s (%s)" % (fid, f["label"]))
                    done[fid] = str(val)
                else:
                    log.append("NOT DONE: %s not found" % fid)
            elif f["kind"] == "content_control":
                idx = int(fid[3:])
                sdt = list(d.element.body.iter(qn("w:sdt")))[idx]
                ts = list(sdt.iter(qn("w:t")))
                if ts:
                    ts[0].text = str(val)
                    for t in ts[1:]:
                        t.text = ""
                    for pr in sdt.iter(qn("w:showingPlcHdr")):
                        pr.getparent().remove(pr)
                    log.append("done: %s" % fid)
                    done[fid] = str(val)
        except Exception as e:
            log.append("NOT DONE: %s: %s" % (fid, e))
    d.save(out)
    # read back
    fresh, _ = docx_fields(out)
    d2 = Document(out)
    text_all = "\n".join(p.text for p in d2.paragraphs) + "\n" + "\n".join(
        c.text for t in d2.tables for r in t.rows for c in r.cells)
    readback = []
    for v in values:
        fid = v["id"]
        if fid in done:
            ok = nl(str(done[fid])) in nl(text_all) or (by_id[fid]["kind"] == "checkbox" and CHECKED in text_all)
            readback.append({"id": fid, "label": by_id[fid]["label"], "expected": v["value"],
                             "actual": "found in the file" if ok else "NOT FOUND", "ok": ok})
    return fields, log, blocked, done, readback


# ---------------- XLSX ----------------

def xlsx_fields(path):
    import openpyxl
    wb = openpyxl.load_workbook(path)
    out = []
    for ws in wb.worksheets:
        merged = {}
        for mr in ws.merged_cells.ranges:
            for row in ws.iter_rows(min_row=mr.min_row, max_row=mr.max_row, min_col=mr.min_col, max_col=mr.max_col):
                for c in row:
                    merged[c.coordinate] = mr.start_cell.coordinate if hasattr(mr, "start_cell") else None
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column + 3):
            for c in row:
                if c.value is None and c.coordinate not in merged:
                    left = ws.cell(c.row, c.column - 1).value if c.column > 1 else None
                    above = ws.cell(c.row - 1, c.column).value if c.row > 1 else None
                    lab = left if isinstance(left, str) and left.strip() else (above if isinstance(above, str) and above.strip() and not str(above).startswith("=") else None)
                    if lab and c.row <= 200 and len(out) < 250:
                        e = {"id": "%s!%s" % (ws.title, c.coordinate), "kind": "cell", "label": nl(lab)[:60]}
                        if is_guarded(lab):
                            e["protected"] = True
                        out.append(e)
    return out, {"sheets": wb.sheetnames}


def xlsx_fill(src, values, out):
    import openpyxl
    fields, _ = xlsx_fields(src)
    by_id = {f["id"]: f for f in fields}
    shutil.copyfile(src, out)
    wb = openpyxl.load_workbook(out)
    log, blocked, done = [], [], {}
    for v in values:
        fid, val = v["id"], v["value"]
        sheet, cell = fid.rsplit("!", 1)
        f = by_id.get(fid, {"label": ""})
        if f.get("protected") or is_guarded(f.get("label")):
            blocked.append({"id": fid, "label": f.get("label"), "reason": "signature, consent or declaration: left for the user"})
            continue
        try:
            c = wb[sheet][cell]
            if isinstance(c.value, str) and c.value.startswith("="):
                log.append("NOT DONE: %s holds a formula" % fid)
                continue
            if c.value is not None and not v.get("overwrite"):
                log.append("NOT DONE: %s already holds a value (%r); set overwrite to replace" % (fid, c.value))
                continue
            c.value = val
            log.append("done: %s (%s)" % (fid, f.get("label", "")))
            done[fid] = val
        except Exception as e:
            log.append("NOT DONE: %s: %s" % (fid, e))
    wb.save(out)
    wb2 = openpyxl.load_workbook(out)
    readback = []
    for fid, val in done.items():
        s, c = fid.rsplit("!", 1)
        actual = wb2[s][c].value
        readback.append({"id": fid, "label": by_id.get(fid, {}).get("label", ""), "expected": val, "actual": actual,
                         "ok": actual == val})
    return fields, log, blocked, done, readback


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("fields", "fill", "render"):
        print(__doc__)
        sys.exit(1)
    cmd, path = sys.argv[1], sys.argv[2]
    ext = path.lower().rsplit(".", 1)[-1]
    if cmd == "render":
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        pg = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        d = fitz.open(path)
        d[pg - 1].get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(sys.argv[3])
        print(json.dumps({"png": sys.argv[3], "page": pg, "pages": len(d)}))
        return
    fn = {"pdf": (pdf_fields, pdf_fill), "docx": (docx_fields, docx_fill), "xlsx": (xlsx_fields, xlsx_fill)}.get(ext)
    if not fn:
        print(json.dumps({"error": "supported: .pdf, .docx, .xlsx"}))
        sys.exit(1)
    if cmd == "fields":
        fields, info = fn[0](path)
        print(json.dumps({"file": path, "info": info, "count": len(fields), "fields": fields}, ensure_ascii=False, indent=1))
        return
    values = json.load(open(sys.argv[3], encoding="utf-8"))["values"]
    out = sys.argv[4]
    fields, log, blocked, done, readback = fn[1](path, values, out)
    blank = [{"id": f["id"], "label": f["label"], "protected": bool(f.get("protected"))} for f in fields
             if f["id"] not in done and f["kind"] not in ("button",) and not f.get("current")]
    print(json.dumps({"output": out, "log": log, "blocked": blocked, "readback": readback,
                      "all_readback_ok": all(r["ok"] for r in readback),
                      "left_blank": blank}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
