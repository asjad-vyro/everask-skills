#!/usr/bin/env python3
"""Replace live text in a PDF in place (PyMuPDF), keeping position, size and colour.

Usage: python3 edit_pdf.py job.json
Dump the text first:   {"pdf": "in.pdf", "dump": true}
Then edit:             {"pdf": "in.pdf", "output": "out.pdf",
                        "edits": [{"old": "12 March 2027", "new": "19 March 2027", "page": 1, "occurrence": 0}]}
"page" (1-based) and "occurrence" (0-based, default: all matches on the page) are optional.
Prints JSON. A PDF with no live text (a scan or an image inside a PDF) says so: use the image route.
"""
import json, sys, os
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_image import find_font, _script_of  # same font finder

def spans_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    out.append(s)
    return out

def base14(font_name, flags):
    n = font_name.lower()
    bold = bool(flags & 16) or "bold" in n or "black" in n or "heavy" in n
    ital = bool(flags & 2) or "italic" in n or "oblique" in n
    serif = bool(flags & 4) or any(k in n for k in ("times", "serif", "georgia", "garamond", "palatino", "minion", "playfair")) and "sans" not in n
    mono = bool(flags & 8) or any(k in n for k in ("courier", "mono", "consolas"))
    if mono:
        return "cobo" if bold and ital else "cobo" if bold else "coit" if ital else "cour"
    if serif:
        return "tibi" if bold and ital else "tibo" if bold else "tiit" if ital else "tiro"
    return "hebi" if bold and ital else "hebo" if bold else "heit" if ital else "helv"

def main(job):
    doc = fitz.open(job["pdf"])
    if job.get("dump"):
        pages = []
        total = 0
        for pn, page in enumerate(doc, 1):
            sp = [{"text": s["text"], "bbox": [round(v, 1) for v in s["bbox"]], "font": s["font"], "size": round(s["size"], 1),
                   "color": "#%06X" % s["color"]} for s in spans_of(page)]
            total += len(sp)
            pages.append({"page": pn, "size": [page.rect.width, page.rect.height], "images": len(page.get_images()), "spans": sp})
        print(json.dumps({"pages": pages, "live_text_spans": total,
                          "note": "no live text: this PDF is an image; use the image route" if total == 0 else ""}, ensure_ascii=False, indent=1))
        return
    result = {"edits": [], "warnings": []}
    for e in job["edits"]:
        old, new = e["old"], e["new"]
        pages = [doc[e["page"] - 1]] if e.get("page") else list(doc)
        done = 0
        for page in pages:
            rects = page.search_for(old)
            if not rects:
                continue
            if "occurrence" in e:
                rects = rects[e["occurrence"]:e["occurrence"] + 1]
            sps = spans_of(page)
            for rect in rects:
                # span that holds this phrase
                span = next((s for s in sps if fitz.Rect(s["bbox"]).intersects(rect) and old.split()[0] in s["text"]), None) \
                    or next((s for s in sps if fitz.Rect(s["bbox"]).intersects(rect)), None)
                if span is None:
                    continue
                line_spans = []
                for b in page.get_text("dict")["blocks"]:
                    for l in b.get("lines", []):
                        if any(sp is not None and sp["bbox"] == span["bbox"] and sp["text"] == span["text"] for sp in l["spans"]):
                            line_spans = l["spans"]
                trailing = [t for t in line_spans if t["bbox"][0] >= rect.x1 - 1 and t["text"].strip() and t is not span]
                suffix = span["text"].split(old, 1)[1] if old in span["text"] else ""
                suffix_rect = fitz.Rect(rect.x1, span["bbox"][1], span["bbox"][2] + 1, span["bbox"][3]) if suffix.strip() else None
                # background colour: sample a thin ring around the phrase from a render
                clip = fitz.Rect(rect.x0 - 6, rect.y0 - 6, rect.x1 + 6, rect.y1 + 6) & page.rect
                pix = page.get_pixmap(clip=clip, dpi=144)
                samples = pix.samples
                n = pix.n
                w, h = pix.width, pix.height
                ring = []
                for x in range(w):
                    for y in (0, 1, h - 2, h - 1):
                        o = (y * w + x) * n; ring.append(tuple(samples[o:o + 3]))
                for y in range(h):
                    for x in (0, 1, w - 2, w - 1):
                        o = (y * w + x) * n; ring.append(tuple(samples[o:o + 3]))
                ring.sort()
                med = ring[len(ring) // 2]
                bg = tuple(v / 255 for v in med)
                col = span["color"]
                color = (((col >> 16) & 255) / 255, ((col >> 8) & 255) / 255, (col & 255) / 255)
                size = span["size"]
                origin = fitz.Point(span["origin"])
                # place the new text where the old phrase began
                x_start = rect.x0
                page.add_redact_annot(rect, fill=bg)
                for t in trailing:
                    page.add_redact_annot(fitz.Rect(t["bbox"]), fill=bg)
                if suffix_rect is not None:
                    page.add_redact_annot(suffix_rect, fill=bg)
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                script = _script_of(new)
                font_note = None
                fontfile = None
                fname = base14(span["font"], span["flags"])
                if script != "latin" or any(ord(c) > 255 for c in new):
                    fontfile, _ = find_font(new, bool(span["flags"] & 16))
                    font_note = "closest available font for this script: " + (os.path.basename(fontfile) if fontfile else "none found")
                else:
                    font_note = "set in %s, the closest standard match to %s" % (fname, span["font"])
                font = fitz.Font(fontfile=fontfile) if fontfile else fitz.Font(fname)
                width = font.text_length(new, fontsize=size)
                # fit: keep inside the page margin
                room = page.rect.x1 - 18 - x_start
                shrunk = False
                if width > room and room > 20:
                    size = size * room / width
                    shrunk = True
                    result["warnings"].append("'%s' set smaller (%.1f pt) to fit the page." % (new, size))
                tw = fitz.TextWriter(page.rect, color=color)
                tw.append((x_start, origin.y), new, font=font, fontsize=size)
                tw.write_text(page)
                delta = (x_start + width * (size / span["size"] if shrunk else 1)) - rect.x1
                if abs(delta) <= 0.5:
                    delta = 0.0
                if trailing or suffix_rect is not None:
                    if suffix_rect is not None:
                        sf = fitz.Font(base14(span["font"], span["flags"]))
                        tw3 = fitz.TextWriter(page.rect, color=color)
                        tw3.append((rect.x1 + delta, origin.y), suffix, font=sf, fontsize=span["size"])
                        tw3.write_text(page)
                    for t in trailing:
                        tc = t["color"]
                        tcol = (((tc >> 16) & 255) / 255, ((tc >> 8) & 255) / 255, (tc & 255) / 255)
                        tf = fitz.Font(base14(t["font"], t["flags"]))
                        tw2 = fitz.TextWriter(page.rect, color=tcol)
                        tw2.append((t["origin"][0] + delta, t["origin"][1]), t["text"], font=tf, fontsize=t["size"])
                        tw2.write_text(page)
                    if delta:
                        result["warnings"].append("Text after '%s' on the same line was moved %.1f pt to make room." % (new, delta))
                done += 1
                result["edits"].append({"old": old, "new": new, "page": page.number + 1, "font_size": round(size, 1),
                                        "color": "#%06X" % col, "background": "#%02X%02X%02X" % med,
                                        "font": font_note, "shrunk_to_fit": shrunk})
        if done == 0:
            result["warnings"].append("'%s' was not found as live text. Dump the page text to see how it is split." % old)
    doc.save(job["output"], garbage=3, deflate=True)
    result["output"] = job["output"]
    result["pages"] = len(doc)
    print(json.dumps(result, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
