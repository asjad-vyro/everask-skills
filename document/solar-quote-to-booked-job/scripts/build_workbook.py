#!/usr/bin/env python3
"""Write the quote workbook (.xlsx) with live formulas: Assumptions, Sizing, Parts, Payback.

Usage:
    python3 build_workbook.py --job job.json --sizing sizing.json --payback-in payback_in.json \
        [--sources sources.json] [--customer "J. Smith, 4 Elm Road"] --out quote.xlsx

job.json and payback_in.json: the inputs given to size_system.py and payback.py.
sizing.json: the output of size_system.py.
sources.json (optional): {"<assumption key>": {"source": "<url or bill>", "checked_on": "YYYY-MM-DD"}}
    keys: kwh_per_kwp_year, import_tariff, tariff_rise_pct, export_rate, export_rise_pct,
    self_use_pct, degradation_pct, upfront_incentive, incentive_per_kwh, monthly_kwh

Every number the installer may change sits on the Assumptions tab (yellow cells).
Sizing, parts quantities, totals, deposit and the 25-year payback recalculate from
it when the file is opened in Excel, Google Sheets, Numbers or LibreOffice. Cached
values are written too, so previews show numbers before any recalculation.

Prints {"path", "sheets", "price_inc_tax", "deposit", "payback_years"}.
Stdlib only (no openpyxl needed). No network.
"""

import datetime
import json
import sys
import zipfile
from xml.sax.saxutils import escape

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# style ids (see STYLES): 0 plain, 1 bold, 2 money, 3 pct, 4 int, 5 input money,
# 6 input pct, 7 input text/number, 8 3dp, 9 bold money, 10 title, 11 1dp, 12 input 1dp
STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="3"><numFmt numFmtId="164" formatCode="0.000"/><numFmt numFmtId="165" formatCode="0.0"/><numFmt numFmtId="166" formatCode="0.0000"/></numFmts>
<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="14"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFDF3C4"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="14">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="10" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="3" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="4" fontId="0" fillId="2" borderId="0" xfId="0" applyNumberFormat="1" applyFill="1"/>
<xf numFmtId="10" fontId="0" fillId="2" borderId="0" xfId="0" applyNumberFormat="1" applyFill="1"/>
<xf numFmtId="0" fontId="0" fillId="2" borderId="0" xfId="0" applyFill="1"/>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="4" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1"/>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="165" fontId="0" fillId="2" borderId="0" xfId="0" applyNumberFormat="1" applyFill="1"/>
<xf numFmtId="166" fontId="0" fillId="2" borderId="0" xfId="0" applyNumberFormat="1" applyFill="1"/>
</cellXfs>
</styleSheet>"""


def col_letter(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def split_ref(ref):
    letters = "".join(ch for ch in ref if ch.isalpha())
    num = 0
    for ch in letters:
        num = num * 26 + ord(ch) - 64
    return int(ref[len(letters):]), num


class Sheet:
    def __init__(self, name, widths):
        self.name, self.widths, self.cells = name, widths, {}

    def set(self, ref, value, style=0, cache=None):
        row, col = split_ref(ref)
        if value is None or value == "":
            if style:
                self.cells[(row, col)] = f'<c r="{ref}" s="{style}"/>'
            return
        if isinstance(value, str) and value.startswith("="):
            f = escape(value[1:])
            if cache is None:
                xml = f'<c r="{ref}" s="{style}"><f>{f}</f></c>'
            elif isinstance(cache, str):
                xml = f'<c r="{ref}" s="{style}" t="str"><f>{f}</f><v>{escape(cache)}</v></c>'
            else:
                xml = f'<c r="{ref}" s="{style}"><f>{f}</f><v>{cache}</v></c>'
        elif isinstance(value, bool):
            xml = f'<c r="{ref}" s="{style}" t="b"><v>{int(value)}</v></c>'
        elif isinstance(value, (int, float)):
            xml = f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
        else:
            xml = f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{escape(str(value))}</t></is></c>'
        self.cells[(row, col)] = xml

    def xml(self):
        rows = {}
        for (r, c), x in sorted(self.cells.items()):
            rows.setdefault(r, []).append(x)
        cols = "".join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>'
                       for i, w in enumerate(self.widths, start=1))
        body = "".join(f'<row r="{r}">{"".join(xs)}</row>' for r, xs in rows.items())
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<cols>{cols}</cols><sheetData>{body}</sheetData></worksheet>')


def write_xlsx(path, sheets):
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
    rels, entries = [], []
    for i, sh in enumerate(sheets, start=1):
        ct.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                  'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    f'relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
        entries.append(f'<sheet name="{escape(sh.name)}" sheetId="{i}" r:id="rId{i}"/>')
    ct.append("</Types>")
    n = len(sheets) + 1
    rels.append(f'<Relationship Id="rId{n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/styles" Target="styles.xml"/>')
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<sheets>{"".join(entries)}</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                   'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(rels) + "</Relationships>")
        z.writestr("xl/styles.xml", STYLES)
        for i, sh in enumerate(sheets, start=1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", sh.xml())


def build(job, sizing, pin, sources, customer):
    s, cur = sizing["sizing"], pin.get("currency", "")
    src = lambda k: (sources.get(k) or {}).get("source", "")  # noqa: E731
    chk = lambda k: (sources.get(k) or {}).get("checked_on", "")  # noqa: E731
    pct = lambda v, d=0: float(v if v is not None else d) / 100  # noqa: E731
    today = datetime.date.today().isoformat()

    # ---------------- Assumptions (A label, B value, C unit, D source, E checked on)
    a = Sheet("Assumptions", [34, 14, 12, 60, 14])
    a.set("A1", f"Assumptions{' - ' + customer if customer else ''}", 10)
    for ref, text in (("A2", "Item"), ("B2", "Value"), ("C2", "Unit"), ("D2", "Source"), ("E2", "Checked on")):
        a.set(ref, text, 1)
    dep = job.get("deposit") or {}
    labour = dict(job.get("labour") or {})
    lab_part = next((x for x in sizing["parts"] if x["sku"] == "LABOUR"), None)
    if lab_part:
        labour["rate"] = lab_part["unit_cost"]  # may come from a labour row on the price list
    rows = [
        (3, "Yield per kWp per year", s["kwh_per_kwp_year"], 12, "kWh/kWp", "kwh_per_kwp_year"),
        (4, "Share of yearly use to cover", pct(job.get("offset_pct"), 100), 6, "", None),
        (5, "Panel size", s["panel_watts"], 7, "W", None),
        (6, "Roof limit (panels, blank = none)", job.get("max_panels") or "", 7, "panels", None),
        (7, "Margin", pct(job.get("margin_pct")), 6, "", None),
        (8, "Margin basis (margin or markup)", job.get("margin_basis", "margin"), 7, "", None),
        (9, "Tax rate", pct(job.get("tax_pct")), 6, "", None),
        (10, "Deposit rule (percent or fixed)", dep.get("type", "percent"), 7, "", None),
        (11, "Deposit value", float(dep.get("value", 0)), 7, "% or amount", None),
        (12, "Import price per kWh", float(pin["import_tariff"]), 13, f"{cur}/kWh", "import_tariff"),
        (13, "Import price rise per year", pct(pin.get("tariff_rise_pct"), 3), 6, "", "tariff_rise_pct"),
        (14, "Export payment per kWh", float(pin.get("export_rate") or 0), 13, f"{cur}/kWh", "export_rate"),
        (15, "Export payment rise per year", pct(pin.get("export_rise_pct"), 0), 6, "", "export_rise_pct"),
        (16, "Share of generation used at home", pct(pin.get("self_use_pct"), 40), 6, "", "self_use_pct"),
        (17, "Panel output loss per year", pct(pin.get("degradation_pct"), 0.5), 6, "", "degradation_pct"),
        (18, "Upfront incentive (grant, rebate, credit)", float(pin.get("upfront_incentive") or 0), 5, cur,
         "upfront_incentive"),
        (19, "Incentive per kWh generated", float(pin.get("incentive_per_kwh") or 0), 13, f"{cur}/kWh",
         "incentive_per_kwh"),
        (20, "Years the per-kWh incentive is paid", float(pin.get("incentive_years") or 0), 7, "years", None),
        (21, "Yearly upkeep", float(pin.get("annual_upkeep") or 0), 5, cur, None),
        (22, "Inverter size", s.get("inverter_kw") or "", 7, "kW", None),
        (23, "Labour rate", labour.get("rate", ""), 5, f"{cur}/hour", None),
        (24, "Labour hours per kWp", labour.get("hours_per_kw", 0) if labour.get("rate") is not None else "", 7,
         "hours", None),
        (25, "Labour fixed hours", labour.get("fixed_hours", 0) if labour.get("rate") is not None else "", 7,
         "hours", None),
        (26, "Include battery (yes/no)", "yes" if sizing["quoted_option"] == "with_battery" else "no", 7, "", None),
        (27, "Currency", cur, 7, "", None),
    ]
    for r, label, value, style, unit, key in rows:
        a.set(f"A{r}", label)
        a.set(f"B{r}", value, style)
        a.set(f"C{r}", unit)
        if key:
            a.set(f"D{r}", src(key))
            a.set(f"E{r}", chk(key))
    a.set("A29", "Yellow cells are inputs. Change them and every tab recalculates. Prices come only "
                 "from your price list. Savings are estimates from these assumptions, not a guarantee.")
    a.set("A30", f"Built {today}. Refresh tariff and incentive figures older than 30 days before quoting.")

    # ---------------- Sizing
    z = Sheet("Sizing", [34, 14, 12, 50])
    z.set("A1", "Sizing", 10)
    z.set("A2", "Month", 1)
    z.set("B2", "kWh on bill", 1)
    z.set("D2", src("monthly_kwh") or "From the customer's bills")
    months = job.get("monthly_kwh") or []
    for i in range(12):
        z.set(f"A{3+i}", f"Bill {i+1}" if months else MONTHS[i])
        z.set(f"B{3+i}", float(months[i]) if i < len(months) else "", 7)
    annual = s["annual_use_kwh"]
    if months:
        z.set("B16", "=SUM(B3:B14)*12/COUNT(B3:B14)", 4, annual)
    else:
        z.set("B16", float(annual), 7)
    target = s["target_kwp"]
    lines = [
        (16, "Yearly use (bills scaled to 12 months)", None, "kWh"),
        (17, "Target system size", ("=B16*Assumptions!B4/Assumptions!B3", 8, target), "kWp"),
        (18, "Panels", ("=IF(N(Assumptions!B6)>0,MIN(MAX(1,ROUNDUP(B17*1000/Assumptions!B5-0.000001,0)),"
                        "Assumptions!B6),MAX(1,ROUNDUP(B17*1000/Assumptions!B5-0.000001,0)))", 4, s["panels"]),
         "panels"),
        (19, "System size", ("=B18*Assumptions!B5/1000", 8, s["system_kwp"]), "kWp"),
        (20, "Expected generation per year", ("=ROUND(B19*Assumptions!B3,0)", 4,
                                              s["expected_generation_kwh_year"]), "kWh"),
        (21, "Share of yearly use covered", ("=B20/B16", 3, s["share_of_use_covered_pct"] / 100), ""),
        (22, "Panel kWp per inverter kW", ('=IF(N(Assumptions!B22)>0,B19/Assumptions!B22,"")', 11,
                                           s.get("dc_ac_ratio") or ""), ""),
    ]
    for r, label, f, unit in lines:
        z.set(f"A{r}", label)
        if f:
            z.set(f"B{r}", f[0], f[1], f[2])
        z.set(f"C{r}", unit)
    z.set("A24", "Panel")
    z.set("B24", s["panel"])
    z.set("A25", "Inverter")
    z.set("B25", s.get("inverter") or "Not on price list: see flags")
    z.set("A26", "Battery target")
    z.set("B26", s["battery_target_kwh"], 11)
    z.set("C26", "kWh")
    for i, flag in enumerate(sizing.get("flags", []) + sizing.get("assumptions", [])):
        z.set(f"A{28+i}", ("Flag: " if i < len(sizing.get("flags", [])) else "Assumed: ") + flag)

    # ---------------- Parts
    p = Sheet("Parts", [16, 12, 44, 10, 10, 12, 14])
    for i, h in enumerate(["SKU", "Category", "Description", "Unit", "Qty", f"Unit cost {cur}",
                           f"Line cost {cur}"], start=1):
        p.set(f"{col_letter(i)}1", h, 1)
    r = 2
    for part in sizing["parts"]:
        unit = part["unit"]
        if unit == "per_panel" or part["category"] == "panel":
            qty = "=Sizing!$B$18"
        elif unit == "per_kw":
            qty = "=Sizing!$B$19"
        elif part["sku"] == "LABOUR":
            qty = "=ROUND(N(Assumptions!$B$25)+N(Assumptions!$B$24)*Sizing!$B$19,2)"
        else:
            qty = None
        p.set(f"A{r}", part["sku"])
        p.set(f"B{r}", part["category"])
        p.set(f"C{r}", part["description"])
        p.set(f"D{r}", unit)
        if qty:
            p.set(f"E{r}", qty, 0, part["qty"])
        else:
            p.set(f"E{r}", part["qty"], 7)
        if part["sku"] == "LABOUR":
            p.set(f"F{r}", "=Assumptions!$B$23", 2, part["unit_cost"])
        else:
            p.set(f"F{r}", part["unit_cost"], 2)
        p.set(f"G{r}", f"=ROUND(E{r}*F{r},2)", 2, part["line_cost"])
        r += 1
    last = r - 1
    quoted = sizing["totals"].get(sizing["quoted_option"], sizing["totals"]["base"])
    batt = next((b for b in sizing.get("battery_options", []) if b.get("recommended")), None)
    base = sizing["totals"]["base"]
    t = r + 1
    sell = (f'IF(Assumptions!$B$8="markup",{{c}}*(1+Assumptions!$B$7),{{c}}/(1-Assumptions!$B$7))')
    rows = [
        (t, "Parts and labour cost", f"=SUM(G2:G{last})", base["cost"]),
        (t + 1, "Battery cost" + (f" ({batt['description']})" if batt else ""),
         f'=IF(Assumptions!$B$26="yes",{batt["unit_cost"] if batt else 0},0)',
         batt["unit_cost"] if batt and sizing["quoted_option"] == "with_battery" else 0),
        (t + 2, "Total cost", f"=G{t}+G{t+1}", quoted["cost"]),
        (t + 3, "Price before tax", "=ROUND(" + sell.format(c=f"G{t+2}") + ",2)", quoted["price_ex_tax"]),
        (t + 4, "Margin", f"=G{t+3}-G{t+2}", quoted["margin"]),
        (t + 5, "Tax", f"=ROUND(G{t+3}*Assumptions!$B$9,2)", quoted["tax"]),
        (t + 6, "Price including tax", f"=G{t+3}+G{t+5}", quoted["price_inc_tax"]),
        (t + 7, "Deposit", f'=IF(Assumptions!$B$10="fixed",MIN(Assumptions!$B$11,G{t+6}),'
                           f'ROUND(G{t+6}*Assumptions!$B$11/100,2))', sizing["deposit"]["amount"] or 0),
    ]
    for rr, label, f, cache in rows:
        p.set(f"C{rr}", label, 1)
        p.set(f"G{rr}", f, 9, cache)
    price_ref, deposit_ref = f"Parts!G{t+6}", f"Parts!G{t+7}"
    b0 = t + 9
    if sizing.get("battery_options"):
        p.set(f"A{b0}", "Battery options", 1)
        for i, h in enumerate(["SKU", "", "Description", "kWh", "", f"Unit cost {cur}",
                               f"Added price inc tax {cur}"], start=1):
            if h:
                p.set(f"{col_letter(i)}{b0+1}", h, 1)
        for j, b in enumerate(sizing["battery_options"]):
            rr = b0 + 2 + j
            p.set(f"A{rr}", b["sku"])
            p.set(f"C{rr}", b["description"] + ("  (recommended)" if b.get("recommended") else ""))
            p.set(f"D{rr}", b["kwh"])
            p.set(f"F{rr}", b["unit_cost"], 2)
            p.set(f"G{rr}", "=ROUND(" + sell.format(c=f"F{rr}") + "*(1+Assumptions!$B$9),2)", 2,
                  b["added_price_inc_tax"])

    # ---------------- Payback
    y = Sheet("Payback", [8, 14, 14, 14, 12, 12, 12, 14, 16, 12])
    y.set("A1", "25-year savings and payback (estimate, not a guarantee)", 10)
    heads = ["Year", "Generation kWh", "Used at home kWh", "Exported kWh", f"Import {cur}/kWh",
             f"Export {cur}/kWh", f"Incentive {cur}", f"Savings {cur}", f"Cumulative {cur}", "Payback year"]
    for i, h in enumerate(heads, start=1):
        y.set(f"{col_letter(i)}3", h, 1)
    years = int(pin.get("years", 25))
    pb = json.loads(json.dumps(pin.get("_result") or {}))
    cached = {row["year"]: row for row in pb.get("rows", [])}
    y.set("A4", 0)
    y.set("H4", f"=-({price_ref}-Assumptions!$B$18)", 2, -pb.get("net_cost", 0) if pb else None)
    y.set("I4", "=H4", 2, -pb.get("net_cost", 0) if pb else None)
    for k in range(1, years + 1):
        rr = 4 + k
        c = cached.get(k, {})
        y.set(f"A{rr}", k)
        y.set(f"B{rr}", f"=Sizing!$B$20*(1-Assumptions!$B$17)^(A{rr}-1)", 4, c.get("generation_kwh"))
        y.set(f"C{rr}", f"=MIN(B{rr}*Assumptions!$B$16,Sizing!$B$16)", 4, c.get("self_used_kwh"))
        y.set(f"D{rr}", f"=B{rr}-C{rr}", 4, c.get("exported_kwh"))
        y.set(f"E{rr}", f"=Assumptions!$B$12*(1+Assumptions!$B$13)^(A{rr}-1)", 8, c.get("import_tariff"))
        y.set(f"F{rr}", f"=Assumptions!$B$14*(1+Assumptions!$B$15)^(A{rr}-1)", 8, c.get("export_rate"))
        y.set(f"G{rr}", f"=IF(A{rr}<=Assumptions!$B$20,Assumptions!$B$19*B{rr},0)", 2)
        y.set(f"H{rr}", f"=C{rr}*E{rr}+D{rr}*F{rr}+G{rr}-Assumptions!$B$21", 2, c.get("savings"))
        y.set(f"I{rr}", f"=I{rr-1}+H{rr}", 2, c.get("cumulative"))
        y.set(f"J{rr}", f'=IF(AND(I{rr-1}<0,I{rr}>=0,H{rr}>0),A{rr}-1-I{rr-1}/H{rr},"")', 11)
    end = 4 + years
    y.set("A2", "Estimated payback (years):", 1)
    y.set("D2", f'=IF(COUNT(J5:J{end})=0,"Not within {years} years",ROUND(MIN(J5:J{end}),1))', 11,
          pb.get("payback_years") if pb.get("payback_years") is not None else None)
    y.set("F2", f"Total savings {cur}:", 1)
    y.set("H2", f"=SUM(H5:H{end})", 9, pb.get("total_savings"))
    y.set(f"A{end+2}", pb.get("assumptions_text", "Assumptions: see the Assumptions tab."))
    return [a, z, p, y], quoted["price_inc_tax"], sizing["deposit"]["amount"], pb.get("payback_years")


def main(argv):
    need = ("--job", "--sizing", "--payback-in", "--out")
    if any(k not in argv for k in need):
        print(__doc__, file=sys.stderr)
        return 2
    get = lambda k: argv[argv.index(k) + 1] if k in argv else None  # noqa: E731
    try:
        job = json.load(open(get("--job"), encoding="utf-8"))
        sizing = json.load(open(get("--sizing"), encoding="utf-8"))
        pin = json.load(open(get("--payback-in"), encoding="utf-8"))
        sources = json.load(open(get("--sources"), encoding="utf-8")) if get("--sources") else {}
        if "error" in sizing:
            raise ValueError("sizing.json holds an error: " + sizing["error"])
        sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
        import payback  # same folder; gives the cached values the formulas reproduce
        if not pin.get("annual_use_kwh"):
            pin["annual_use_kwh"] = sizing["sizing"]["annual_use_kwh"]
        pin["_result"] = payback.model({k: v for k, v in pin.items() if not k.startswith("_")})
        sheets, price, deposit, pb = build(job, sizing, pin, sources, get("--customer") or "")
        write_xlsx(get("--out"), sheets)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    out = {"path": get("--out"), "sheets": [s.name for s in sheets],
           "price_inc_tax": price, "deposit": deposit, "payback_years": pb}
    if abs(float(pin["price_inc_tax"]) - float(price)) > 0.01:
        out["warning"] = (f"payback_in price_inc_tax {pin['price_inc_tax']} differs from the quoted "
                          f"price {price}; the workbook uses the quoted price. Re-run payback.py.")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
