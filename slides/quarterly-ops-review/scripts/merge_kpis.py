#!/usr/bin/env python3
"""Merge a quarter's KPIs into one comparison and an Excel workbook with live formulas.

Usage:
    python3 merge_kpis.py kpis.json                       # comparison JSON only
    python3 merge_kpis.py kpis.json --xlsx "Q3 2026 ops review KPIs.xlsx"

kpis.json:
    {"company": "Acme Logistics", "quarter": "Q3 2026", "previous_quarter": "Q2 2026",
     "kpis": [
       {"name": "On-time delivery", "unit": "%", "better": "higher",
        "this_quarter": {"value": 94.2, "file": "Ops tracker.xlsx",
                         "location": "Shipments!D3:D812, share of 'Yes'",
                         "link": "https://..."},
        "last_quarter": {"value": 92.9, "file": "Q2 review deck.pptx",
                         "location": "slide 4"},
        "target":       {"value": 95, "file": "KPI targets (user, in chat)",
                         "location": "message of 2026-10-02"}}],
     "tables": [{"sheet": "Incidents", "columns": ["Date", "Severity", ...],
                 "rows": [["2026-07-04", "Sev 2", ...]]}]}       # optional
    "better": "higher" or "lower". Optional --colors "A5A5A5,1F4E79,ED7D31": hex bar
    colours for last quarter / this quarter / target (use the template's palette). A missing value is null (or the period left out):
    it stays blank and is flagged, never filled in.

The workbook has:
    KPIs     one row per KPI: last quarter, this quarter, target (each a formula that
             reads the Sources tab), change, change %, vs target, trend, status, all as
             live formulas.
    Charts   one native column chart per KPI (last quarter / this quarter / target),
             fed by the KPIs tab, so the charts update when a source value is fixed.
    Sources  every number with its file, sheet/cell or page, and a clickable link.
    any extra "tables" (e.g. Incidents, Action items) as their own tabs.

Prints JSON: {"quarter", "previous_quarter", "kpis": [{"name", "unit", "better",
"last_quarter", "this_quarter", "target", "change", "change_pct", "vs_target",
"trend", "status", "summary", "missing": [...]}], "missing": [...], "xlsx": path|null}.
trend: Improved / Worse / Flat / null.  status: Met / Missed / No target / Missing.

Stdlib only (writes the .xlsx with zipfile). No network.
"""

import datetime as dt
import json
import re
import sys
import zipfile
from xml.sax.saxutils import escape

PERIODS = ("last_quarter", "this_quarter", "target")
CURRENCY = {"USD": "$", "GBP": "£", "EUR": "€", "AUD": "A$", "CAD": "C$", "INR": "₹",
            "AED": "AED ", "PKR": "Rs ", "JPY": "¥"}
FLAT_TOLERANCE = 1e-9


# ---------- comparison ----------

def _num(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^\d.\-]", "", str(v))
    try:
        return float(s) if s not in ("", "-", ".") else None
    except ValueError:
        return None


def _period(kpi, key):
    p = kpi.get(key)
    if p is None:
        return {"value": None}
    if not isinstance(p, dict):
        return {"value": _num(p)}
    out = dict(p)
    out["value"] = _num(p.get("value"))
    return out


def fmt(value, unit):
    if value is None:
        return "n/a"
    unit = (unit or "").strip()
    v = round(value, 2)
    text = ("{:,.2f}".format(v)).rstrip("0").rstrip(".") if v != int(v) else "{:,}".format(int(v))
    if unit == "%":
        return text + "%"
    if unit.upper() in CURRENCY:
        sym = CURRENCY[unit.upper()]
        if v != int(v):
            text = "{:,.2f}".format(v)
        neg = text.startswith("-")
        return ("-" if neg else "") + sym + text.lstrip("-")
    return (text + " " + unit).strip()


def compare(kpi, prev_label):
    name = kpi.get("name") or "Unnamed KPI"
    unit = kpi.get("unit", "")
    better = (kpi.get("better") or "higher").lower()
    if better not in ("higher", "lower"):
        better = "higher"
    p = {k: _period(kpi, k) for k in PERIODS}
    last, this, target = (p[k]["value"] for k in PERIODS)
    missing = [k for k in PERIODS if p[k]["value"] is None]
    unsourced = [k for k in PERIODS if p[k]["value"] is not None and not p[k].get("file")]
    change = None if last is None or this is None else this - last
    change_pct = None if change is None or last == 0 else change / abs(last)
    vs_target = None if this is None or target is None else this - target
    trend = None
    if change is not None:
        if abs(change) <= FLAT_TOLERANCE:
            trend = "Flat"
        else:
            trend = "Improved" if (change > 0) == (better == "higher") else "Worse"
    if this is None:
        status = "Missing"
    elif target is None:
        status = "No target"
    else:
        status = "Met" if (this >= target if better == "higher" else this <= target) else "Missed"
    bits = [name + ": " + fmt(this, unit)]
    if change is not None:
        step = "pts" if unit == "%" else unit
        sign = "+" if change > 0 else ""
        diff = ("{:,.2f}".format(round(change, 2))).rstrip("0").rstrip(".")
        bits.append("%s%s %s vs %s" % (sign, diff, step, prev_label) if unit == "%"
                    else "%s%s vs %s" % (sign, fmt(change, unit), prev_label))
    if target is not None and this is not None:
        bits.append("target %s (%s)" % (fmt(target, unit), status.lower()))
    for k in missing:
        bits.append("%s MISSING" % k.replace("_", " "))
    return {"name": name, "unit": unit, "better": better,
            "last_quarter": last, "this_quarter": this, "target": target,
            "change": None if change is None else round(change, 4),
            "change_pct": None if change_pct is None else round(change_pct, 4),
            "vs_target": None if vs_target is None else round(vs_target, 4),
            "trend": trend, "status": status, "summary": "; ".join(bits),
            "missing": missing, "unsourced": unsourced, "_periods": p}


# ---------- xlsx writing ----------

def _col(i):  # 0-based -> A
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _xml(s):
    return escape(str(s), {'"': "&quot;"})


class Sheet:
    def __init__(self, name):
        self.name = name[:31]
        self.rows = {}
        self.widths = {}
        self.drawing_rid = None
        self.freeze = None

    def set(self, ref_col, row, value=None, formula=None, style=0, cached=None):
        self.rows.setdefault(row, {})[ref_col] = (value, formula, style, cached)

    def xml(self):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
               'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">']
        if self.freeze:
            out.append('<sheetViews><sheetView workbookViewId="0"><pane ySplit="%d" '
                       'topLeftCell="A%d" activePane="bottomLeft" state="frozen"/>'
                       '</sheetView></sheetViews>' % (self.freeze, self.freeze + 1))
        if self.widths:
            out.append("<cols>")
            for c in sorted(self.widths):
                out.append('<col min="%d" max="%d" width="%s" customWidth="1"/>'
                           % (c + 1, c + 1, self.widths[c]))
            out.append("</cols>")
        out.append("<sheetData>")
        for r in sorted(self.rows):
            out.append('<row r="%d">' % r)
            for c in sorted(self.rows[r]):
                out.append(self._cell(c, r, *self.rows[r][c]))
            out.append("</row>")
        out.append("</sheetData>")
        out.append('<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" '
                   'header="0.3" footer="0.3"/>')
        if self.drawing_rid:
            out.append('<drawing r:id="%s"/>' % self.drawing_rid)
        out.append("</worksheet>")
        return "".join(out)

    @staticmethod
    def _cell(c, r, value, formula, style, cached):
        ref = "%s%d" % (_col(c), r)
        s = ' s="%d"' % style if style else ""
        if formula is not None:
            f = "<f>%s</f>" % _xml(formula)
            if cached is None or cached == "":
                return '<c r="%s"%s t="str">%s<v></v></c>' % (ref, s, f)
            if isinstance(cached, str):
                return '<c r="%s"%s t="str">%s<v>%s</v></c>' % (ref, s, f, _xml(cached))
            return '<c r="%s"%s>%s<v>%s</v></c>' % (ref, s, f, repr(float(cached)))
        if value is None or value == "":
            return '<c r="%s"%s/>' % (ref, s)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return '<c r="%s"%s><v>%s</v></c>' % (ref, s, repr(float(value)))
        return '<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (
            ref, s, _xml(value))


# style ids (see STYLES)
TITLE, HEAD, NUM, PCT, MISSING, WRAP, LINK, NOTE = 1, 2, 3, 4, 5, 6, 7, 8
STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="2"><numFmt numFmtId="164" formatCode="#,##0.0#"/><numFmt numFmtId="165" formatCode="+0.0%;-0.0%;0.0%"/></numFmts>
<fonts count="5"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="14"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font><font><u/><sz val="11"/><color rgb="FF0563C1"/><name val="Calibri"/></font><font><i/><sz val="10"/><color rgb="FF595959"/><name val="Calibri"/></font></fonts>
<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE7E6E6"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFEB9C"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="9">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="2" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="164" fontId="0" fillId="3" borderId="0" xfId="0" applyNumberFormat="1" applyFill="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def _chart_xml(title, kpi_row, labels, values, colors):
    pts_cat = "".join('<c:pt idx="%d"><c:v>%s</c:v></c:pt>' % (i, _xml(l))
                      for i, l in enumerate(labels))
    pts_val = "".join('<c:pt idx="%d"><c:v>%s</c:v></c:pt>' % (i, repr(float(v)))
                      for i, v in enumerate(values) if v is not None)
    dpts = "".join('<c:dPt><c:idx val="%d"/><c:invertIfNegative val="0"/><c:bubble3D val="0"/>'
                   '<c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill></c:spPr></c:dPt>'
                   % (i, colors[i % len(colors)]) for i in range(3))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<c:roundedCorners val="0"/><c:chart>'
        '<c:title><c:tx><c:rich><a:bodyPr/><a:p><a:pPr><a:defRPr sz="1200" b="1"/></a:pPr>'
        '<a:r><a:rPr lang="en-US" sz="1200" b="1"/><a:t>%s</a:t></a:r></a:p></c:rich></c:tx>'
        '<c:overlay val="0"/></c:title><c:autoTitleDeleted val="0"/>'
        '<c:plotArea><c:layout/><c:barChart><c:barDir val="col"/><c:grouping val="clustered"/>'
        '<c:varyColors val="1"/><c:ser><c:idx val="0"/><c:order val="0"/>'
        '<c:tx><c:strRef><c:f>KPIs!$A$%d</c:f></c:strRef></c:tx>'
        '<c:invertIfNegative val="0"/>%s'
        '<c:dLbls><c:showLegendKey val="0"/><c:showVal val="1"/><c:showCatName val="0"/>'
        '<c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbls>'
        '<c:cat><c:strRef><c:f>KPIs!$C$3:$E$3</c:f><c:strCache><c:ptCount val="3"/>%s'
        '</c:strCache></c:strRef></c:cat>'
        '<c:val><c:numRef><c:f>KPIs!$C$%d:$E$%d</c:f><c:numCache><c:formatCode>General'
        '</c:formatCode><c:ptCount val="3"/>%s</c:numCache></c:numRef></c:val></c:ser>'
        '<c:gapWidth val="60"/><c:axId val="5001"/><c:axId val="5002"/></c:barChart>'
        '<c:catAx><c:axId val="5001"/><c:scaling><c:orientation val="minMax"/></c:scaling>'
        '<c:delete val="0"/><c:axPos val="b"/><c:numFmt formatCode="General" sourceLinked="0"/>'
        '<c:majorTickMark val="none"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/>'
        '<c:crossAx val="5002"/><c:crosses val="autoZero"/><c:auto val="1"/><c:lblAlgn val="ctr"/>'
        '<c:lblOffset val="100"/></c:catAx>'
        '<c:valAx><c:axId val="5002"/><c:scaling><c:orientation val="minMax"/></c:scaling>'
        '<c:delete val="0"/><c:axPos val="l"/><c:majorGridlines/>'
        '<c:numFmt formatCode="General" sourceLinked="1"/><c:majorTickMark val="none"/>'
        '<c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:crossAx val="5001"/>'
        '<c:crosses val="autoZero"/><c:crossBetween val="between"/></c:valAx></c:plotArea>'
        '<c:plotVisOnly val="1"/><c:dispBlanksAs val="gap"/></c:chart></c:chartSpace>'
    ) % (_xml(title), kpi_row, dpts, pts_cat, kpi_row, kpi_row, pts_val)


def _drawing_xml(n):
    anchors = []
    for i in range(n):
        col, row = (i % 2) * 8, 2 + (i // 2) * 18
        anchors.append(
            '<xdr:twoCellAnchor><xdr:from><xdr:col>%d</xdr:col><xdr:colOff>0</xdr:colOff>'
            '<xdr:row>%d</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:from><xdr:to>'
            '<xdr:col>%d</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>%d</xdr:row>'
            '<xdr:rowOff>0</xdr:rowOff></xdr:to><xdr:graphicFrame macro="">'
            '<xdr:nvGraphicFramePr><xdr:cNvPr id="%d" name="Chart %d"/><xdr:cNvGraphicFramePr/>'
            '</xdr:nvGraphicFramePr><xdr:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/></xdr:xfrm>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            '<c:chart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" r:id="rId%d"/>'
            '</a:graphicData></a:graphic></xdr:graphicFrame><xdr:clientData/></xdr:twoCellAnchor>'
            % (col, row, col + 7, row + 16, i + 2, i + 1, i + 1))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            + "".join(anchors) + "</xdr:wsDr>")


def _q(sheet):
    return "'%s'" % sheet.replace("'", "''")


def build_xlsx(path, data, results, colors):
    prev_label = data.get("previous_quarter") or "Last quarter"
    this_label = data.get("quarter") or "This quarter"
    title = "%s%s ops review KPIs" % (
        (data.get("company") + " ") if data.get("company") else "", this_label)

    # Sources: one row per number
    src = Sheet("Sources")
    src.freeze = 3
    src.set(0, 1, title + ": sources", style=TITLE)
    src.set(0, 2, "Every number in the review comes from this tab. Fix a value here and "
                  "the KPIs and Charts tabs update.", style=NOTE)
    heads = ["Ref", "KPI", "Period", "Value", "Unit", "File", "Sheet, cell or page", "Link",
             "Note"]
    for c, h in enumerate(heads):
        src.set(c, 3, h, style=HEAD)
    for c, w in enumerate([7, 30, 14, 12, 8, 34, 44, 40, 34]):
        src.widths[c] = w
    period_label = {"last_quarter": prev_label, "this_quarter": this_label, "target": "Target"}
    src_cell = {}
    r = 4
    for k_i, res in enumerate(results):
        for key in PERIODS:
            p = res["_periods"][key]
            src.set(0, r, "S%d" % (r - 3))
            src.set(1, r, res["name"])
            src.set(2, r, period_label[key])
            if p["value"] is None:
                src.set(3, r, None, style=MISSING)
                src.set(8, r, "MISSING: not found in the sources; left blank on purpose",
                        style=WRAP)
            else:
                src.set(3, r, p["value"], style=NUM)
                if not p.get("file"):
                    src.set(8, r, "No source given: check before use", style=WRAP)
                elif p.get("note"):
                    src.set(8, r, p["note"], style=WRAP)
            src.set(4, r, res["unit"])
            src.set(5, r, p.get("file", ""), style=WRAP)
            src.set(6, r, p.get("location", ""), style=WRAP)
            link = p.get("link") or ""
            if link.startswith(("http://", "https://")):
                src.set(7, r, formula='HYPERLINK("%s","Open source")' % link.replace('"', '""'),
                        style=LINK, cached="Open source")
            elif link:
                src.set(7, r, link, style=WRAP)
            src_cell[(k_i, key)] = "Sources!$D$%d" % r
            r += 1

    # KPIs
    k = Sheet("KPIs")
    k.freeze = 3
    k.set(0, 1, title, style=TITLE)
    k.set(0, 2, "Values read from the Sources tab. Change, trend and status are live formulas.",
          style=NOTE)
    heads = ["KPI", "Unit", prev_label, this_label, "Target", "Change", "Change %",
             "vs target", "Better when", "Trend", "Status", "Missing"]
    for c, h in enumerate(heads):
        k.set(c, 3, h, style=HEAD)
    for c, w in enumerate([30, 8, 13, 13, 13, 12, 11, 12, 12, 11, 11, 30]):
        k.widths[c] = w
    for i, res in enumerate(results):
        row = 4 + i
        C, D, E, I = ("%s%d" % (x, row) for x in "CDEI")
        k.set(0, row, res["name"])
        k.set(1, row, res["unit"])
        for col, key in ((2, "last_quarter"), (3, "this_quarter"), (4, "target")):
            ref = src_cell[(i, key)]
            k.set(col, row, formula='IF(%s="","",%s)' % (ref, ref),
                  style=MISSING if res[key] is None else NUM, cached=res[key])
        k.set(5, row, formula='IF(OR(%s="",%s=""),"",%s-%s)' % (C, D, D, C), style=NUM,
              cached=res["change"])
        k.set(6, row, formula='IF(OR(%s="",%s="",%s=0),"",(%s-%s)/ABS(%s))' % (C, D, C, D, C, C),
              style=PCT, cached=res["change_pct"])
        k.set(7, row, formula='IF(OR(%s="",%s=""),"",%s-%s)' % (D, E, D, E), style=NUM,
              cached=res["vs_target"])
        k.set(8, row, res["better"])
        k.set(9, row, formula='IF(OR(%s="",%s=""),"",IF(ABS(%s-%s)<1E-9,"Flat",'
                              'IF((%s>%s)=(%s="higher"),"Improved","Worse")))'
                              % (C, D, D, C, D, C, I), cached=res["trend"] or "")
        k.set(10, row, formula='IF(%s="","Missing",IF(%s="","No target",IF(%s="higher",'
                               'IF(%s>=%s,"Met","Missed"),IF(%s<=%s,"Met","Missed"))))'
                               % (D, E, I, D, E, D, E), cached=res["status"])
        k.set(11, row, ", ".join(m.replace("_", " ") for m in res["missing"]), style=WRAP)

    # Charts
    ch = Sheet("Charts")
    ch.set(0, 1, title + ": %s vs %s vs target" % (this_label, prev_label), style=TITLE)
    ch.drawing_rid = "rId1"

    extra = []
    for t in data.get("tables") or []:
        s = Sheet(t.get("sheet") or "Table %d" % (len(extra) + 1))
        s.freeze = 1
        for c, h in enumerate(t.get("columns") or []):
            s.set(c, 1, h, style=HEAD)
            s.widths[c] = max(10, min(50, len(str(h)) + 6))
        for r_i, row_vals in enumerate(t.get("rows") or []):
            for c, v in enumerate(row_vals):
                if isinstance(v, str) and v.startswith(("http://", "https://")):
                    s.set(c, r_i + 2, formula='HYPERLINK("%s","Open")' % v.replace('"', '""'),
                          style=LINK, cached="Open")
                else:
                    s.set(c, r_i + 2, v, style=WRAP if isinstance(v, str) and len(v) > 40 else 0)
        extra.append(s)

    sheets = [k, ch, src] + extra
    names = set()
    for s in sheets:
        base, n = s.name, 2
        while s.name.lower() in names:
            s.name = (base[:28] + " %d" % n)
            n += 1
        names.add(s.name.lower())

    labels = [prev_label, this_label, "Target"]
    n_charts = len(results)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
              '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
              '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
        for i in range(len(sheets)):
            ct.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/'
                      'vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1))
        if n_charts:
            ct.append('<Override PartName="/xl/drawings/drawing1.xml" ContentType="application/'
                      'vnd.openxmlformats-officedocument.drawing+xml"/>')
        for i in range(n_charts):
            ct.append('<Override PartName="/xl/charts/chart%d.xml" ContentType="application/'
                      'vnd.openxmlformats-officedocument.drawingml.chart+xml"/>' % (i + 1))
        ct.append("</Types>")
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                   '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
                   '</Relationships>')
        now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        z.writestr("docProps/core.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                   'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                   '<dc:title>%s</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
                   '</cp:coreProperties>' % (_xml(title), now))
        z.writestr("docProps/app.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
                   '<Application>Microsoft Excel</Application></Properties>')
        wb = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
              '<bookViews><workbookView/></bookViews><sheets>']
        for i, s in enumerate(sheets):
            wb.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (_xml(s.name), i + 1, i + 1))
        wb.append('</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
        z.writestr("xl/workbook.xml", "".join(wb))
        rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for i in range(len(sheets)):
            rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/'
                        'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>'
                        % (i + 1, i + 1))
        rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/'
                    'officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                    % (len(sheets) + 1))
        rels.append("</Relationships>")
        z.writestr("xl/_rels/workbook.xml.rels", "".join(rels))
        z.writestr("xl/styles.xml", STYLES)
        if not n_charts:
            ch.drawing_rid = None
        for i, s in enumerate(sheets):
            z.writestr("xl/worksheets/sheet%d.xml" % (i + 1), s.xml())
        if n_charts:
            z.writestr("xl/worksheets/_rels/sheet2.xml.rels",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/'
                       '2006/relationships/drawing" Target="../drawings/drawing1.xml"/></Relationships>')
            z.writestr("xl/drawings/drawing1.xml", _drawing_xml(n_charts))
            drels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
            for i in range(n_charts):
                drels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/'
                             'officeDocument/2006/relationships/chart" Target="../charts/chart%d.xml"/>'
                             % (i + 1, i + 1))
            drels.append("</Relationships>")
            z.writestr("xl/drawings/_rels/drawing1.xml.rels", "".join(drels))
            for i, res in enumerate(results):
                unit = (" (%s)" % res["unit"]) if res["unit"] else ""
                vals = [res["last_quarter"], res["this_quarter"], res["target"]]
                z.writestr("xl/charts/chart%d.xml" % (i + 1),
                           _chart_xml(res["name"] + unit, 4 + i, labels, vals, colors))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read %s: %s" % (argv[0], exc)}))
        return 1
    kpis = data.get("kpis") if isinstance(data, dict) else None
    if not kpis:
        print(json.dumps({"error": "kpis.json needs a non-empty \"kpis\" list"}))
        return 1
    prev = data.get("previous_quarter") or "last quarter"
    results = [compare(kpi, prev) for kpi in kpis]
    colors = [c.strip().lstrip("#").upper() for c in
              (argv[argv.index("--colors") + 1].split(",") if "--colors" in argv
               else ["A5A5A5", "1F4E79", "ED7D31"])]
    xlsx = None
    if "--xlsx" in argv:
        xlsx = argv[argv.index("--xlsx") + 1]
        build_xlsx(xlsx, data, results, colors)
    missing = ["%s: %s" % (r["name"], m.replace("_", " ")) for r in results for m in r["missing"]]
    unsourced = ["%s: %s" % (r["name"], m.replace("_", " ")) for r in results
                 for m in r["unsourced"]]
    for r in results:
        r.pop("_periods", None)
    print(json.dumps({"quarter": data.get("quarter"), "previous_quarter": data.get("previous_quarter"),
                      "kpis": results, "missing": missing, "unsourced": unsourced, "xlsx": xlsx},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
