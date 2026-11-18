#!/usr/bin/env python3
"""Build the month-end close pack as an .xlsx with live formulas and an Exceptions tab.

Usage:
    python3 build_close_pack.py --matches match.json --recon recon.json \
        --month 2026-10 --currency GBP --out close-pack-2026-10.xlsx \
        [--company "Acme Ltd"] [--last-month last_month.json]

match.json:  the output of match_receipts.py
recon.json:  the output of reconcile_payouts.py (optional: pass "none" to leave Stripe out)
last_month.json: category totals for the previous month from QuickBooks,
    {"Travel": 1840.20, "Software": 912.00, ...} (optional)

Tabs: Summary, Receipts matched, Stripe reconciliation, Category totals, Exceptions.
Every total, difference, status and count is an Excel formula over the rows, so the
pack recalculates when a line is edited; no total is typed in. Exceptions has a
Decision column (Approve / Fix / Exclude, drop-down) for the user's review.
Exception types: missing receipt (unmatched, over the threshold), check match (likely),
no category, dated outside the month, receipt with no transaction, payout amount
differs, payout with no deposit, Stripe deposit with no payout, unusual category
(new, or moved 50% or more against last month).

Prints JSON: {"path", "sheets", "rows": {...}, "exceptions": n, "exception_types": {...}}.
Stdlib only (writes the .xlsx XML directly); Excel recalculates on open.
"""

import collections
import datetime
import json
import re
import sys
import zipfile
from xml.sax.saxutils import escape

EPOCH = datetime.date(1899, 12, 30)
S_TEXT, S_HEAD, S_DATE, S_MONEY, S_PCT, S_TOTAL, S_TITLE = 0, 1, 2, 3, 4, 5, 6


def die(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def arg(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
        die(f"{name} needs a value")
    return default


def load(path, what, kind):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        die(f"{what} file not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"{what} file is not valid JSON: {exc}")
    if not isinstance(data, kind):
        die(f"{what} file has the wrong shape")
    if isinstance(data, dict) and data.get("error"):
        die(f"{what} file holds an error from the previous script: {data['error']}")
    return data


def col(n):
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


class Sheet:
    def __init__(self, name, widths):
        self.name, self.widths, self.rows = name, widths, []
        self.validations, self.filter = [], None

    def add(self, cells):
        self.rows.append(cells)
        return len(self.rows)

    def ref(self):
        return "'" + self.name.replace("'", "''") + "'"

    def xml(self):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
               'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
               '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
               'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>']
        for i, w in enumerate(self.widths, 1):
            out.append(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>')
        out.append("</cols><sheetData>")
        for r, cells in enumerate(self.rows, 1):
            out.append(f'<row r="{r}">')
            for c, cell in enumerate(cells, 1):
                if cell is None:
                    continue
                value, style = cell if isinstance(cell, tuple) else (cell, S_TEXT)
                at = f'{col(c)}{r}'
                if value is None or value == "":
                    if style:
                        out.append(f'<c r="{at}" s="{style}"/>')
                elif isinstance(value, str) and value.startswith("="):
                    out.append(f'<c r="{at}" s="{style}"><f>{escape(value[1:])}</f></c>')
                elif isinstance(value, bool):
                    out.append(f'<c r="{at}" s="{style}" t="inlineStr"><is><t>{"Yes" if value else "No"}</t></is></c>')
                elif isinstance(value, (int, float)):
                    out.append(f'<c r="{at}" s="{style}"><v>{round(value, 6)}</v></c>')
                elif isinstance(value, datetime.date):
                    out.append(f'<c r="{at}" s="{S_DATE}"><v>{(value - EPOCH).days}</v></c>')
                else:
                    text = escape(str(value))
                    out.append(f'<c r="{at}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>')
            out.append("</row>")
        out.append("</sheetData>")
        if self.filter:
            out.append(f'<autoFilter ref="{self.filter}"/>')
        if self.validations:
            out.append(f'<dataValidations count="{len(self.validations)}">')
            for rng, items in self.validations:
                out.append(f'<dataValidation type="list" allowBlank="1" showErrorMessage="1" sqref="{rng}">'
                           f'<formula1>"{escape(",".join(items))}"</formula1></dataValidation>')
            out.append("</dataValidations>")
        out.append("</worksheet>")
        return "".join(out)


STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="1"><numFmt numFmtId="164" formatCode="yyyy-mm-dd"/></numFmts>
<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="14"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE8EFE6"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left/><right/><top style="thin"/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="7">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="10" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="4" fontId="1" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1"/>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def d(text):
    try:
        return datetime.date.fromisoformat(str(text)[:10]) if text else None
    except ValueError:
        return None


def money(v):
    return (v, S_MONEY) if isinstance(v, (int, float)) else ("", S_MONEY)


def head(sheet, names):
    sheet.add([(n, S_HEAD) for n in names])


def main(argv):
    m_path, r_path, out = arg(argv, "--matches"), arg(argv, "--recon"), arg(argv, "--out")
    month, currency = arg(argv, "--month", ""), (arg(argv, "--currency", "") or "").upper()
    if not m_path or not r_path or not out or not month or not currency:
        print(__doc__, file=sys.stderr)
        return 2
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        die("--month must look like 2026-10")
    company = arg(argv, "--company", "")
    match = load(m_path, "matches", dict)
    recon = {"payouts": [], "unmatched_deposits": []} if r_path.lower() == "none" else load(r_path, "recon", dict)
    last = load(arg(argv, "--last-month"), "last month", dict) if arg(argv, "--last-month") else {}
    rows = match.get("matches") or []
    payouts = recon.get("payouts") or []

    # Receipts matched
    rm = Sheet("Receipts matched", [12, 11, 28, 12, 9, 18, 18, 18, 11, 11, 11, 12, 11, 10, 16, 18, 22])
    head(rm, ["Txn ID", "Date", "Merchant", "Amount", "Currency", "Spender", "Category", "Category source",
              "Confidence", "Receipt ID", "Receipt date", "Receipt amount", "Difference", "Receipt tax",
              "Sent by", "Receipt file", "Note"])
    for x in rows:
        r = len(rm.rows) + 1
        rm.add([x.get("transaction_id", ""), d(x.get("date")), x.get("merchant", ""), money(x.get("amount")),
                x.get("currency", ""), x.get("spender", ""), x.get("category", ""), x.get("category_source", ""),
                x.get("confidence", ""), x.get("receipt_id", ""), d(x.get("receipt_date")),
                money(x.get("receipt_amount")), (f'=IF(L{r}="","",L{r}-D{r})', S_MONEY),
                money(x.get("receipt_tax")), x.get("receipt_sender", ""), x.get("receipt_file", ""),
                x.get("note", "")])
    rm_last = max(len(rm.rows), 2)
    rm.filter = f"A1:Q{rm_last}"

    # Stripe reconciliation
    sr = Sheet("Stripe reconciliation", [26, 12, 9, 12, 12, 12, 12, 13, 13, 11, 24, 12, 13, 12, 15, 30])
    head(sr, ["Payout ID", "Arrival date", "Currency", "Gross", "Refunds", "Fees", "Other", "Net from split",
              "Payout amount", "Split check", "Deposit ID", "Deposit date", "Deposit amount", "Difference",
              "Status", "Note"])
    for p in payouts:
        r = len(sr.rows) + 1
        sr.add([p.get("payout_id", ""), d(p.get("arrival_date")), p.get("currency", ""), money(p.get("gross")),
                money(p.get("refunds")), money(p.get("fees")), money(p.get("other")),
                (f'=IF(D{r}="","",D{r}+E{r}+F{r}+G{r})', S_MONEY), money(p.get("amount")),
                f'=IF(H{r}="","No split",IF(ABS(H{r}-I{r})<0.005,"OK","Differs"))',
                p.get("deposit_id", ""), d(p.get("deposit_date")), money(p.get("deposit_amount")),
                (f'=IF(M{r}="","",M{r}-I{r})', S_MONEY),
                f'=IF(M{r}="","No deposit",IF(ABS(N{r})<0.005,"Reconciled","Amount differs"))', p.get("note", "")])
    sr_first, sr_last = 2, max(len(sr.rows), 2)
    sr.filter = f"A1:P{sr_last}"
    sr.add([])
    sr.add([("Total", S_HEAD), None, None] +
           [(f"=SUM({c}{sr_first}:{c}{sr_last})", S_TOTAL) for c in "DEFGHI"] +
           [None, None, None, (f"=SUM(M{sr_first}:M{sr_last})", S_TOTAL),
            (f"=SUM(N{sr_first}:N{sr_last})", S_TOTAL)])

    # Category totals (this month by formula over Receipts matched)
    this_month = collections.defaultdict(float)
    for x in rows:
        if (x.get("currency") or currency) == currency:
            this_month[x.get("category") or ""] += float(x.get("amount") or 0)
    cats = sorted({c for c in this_month if c} | {c for c in last if c})
    ct = Sheet("Category totals", [26, 14, 14, 14, 11, 18])
    head(ct, ["Category", "This month", "Last month", "Change", "Change %", "Flag"])
    rng = f"'Receipts matched'!$D$2:$D${rm_last}"
    crit_c, crit_cur = f"'Receipts matched'!$G$2:$G${rm_last}", f"'Receipts matched'!$E$2:$E${rm_last}"
    unusual = []
    for c in cats + ["(no category)"]:
        r = len(ct.rows) + 1
        crit = '""' if c == "(no category)" else f"A{r}"
        lm = last.get(c)
        ct.add([c, (f"=SUMIFS({rng},{crit_c},{crit},{crit_cur},Summary!$B$4)", S_MONEY),
                money(lm if lm is not None else (0 if last and c != "(no category)" else None)),
                (f'=IF(C{r}="","",B{r}-C{r})', S_MONEY), (f'=IF(OR(C{r}="",C{r}=0),"",D{r}/C{r})', S_PCT),
                f'=IF(C{r}="","",IF(C{r}=0,IF(B{r}>0,"New this month",""),IF(ABS(E{r})>=0.5,"Moved 50%+","")))'])
        if c != "(no category)" and last:
            now, before = this_month.get(c, 0.0), float(lm or 0)
            if (before == 0 and now > 0) or (before and abs(now - before) / before >= 0.5):
                unusual.append((c, now, before))
    ct_last = len(ct.rows)
    ct.add([])
    ct.add([("Total", S_HEAD), (f"=SUM(B2:B{ct_last})", S_TOTAL), (f"=SUM(C2:C{ct_last})", S_TOTAL),
            (f"=B{ct_last + 2}-C{ct_last + 2}", S_TOTAL)])

    # Exceptions
    ex = Sheet("Exceptions", [5, 26, 26, 11, 30, 12, 9, 18, 46, 11, 30])
    head(ex, ["#", "Type", "Reference", "Date", "Description", "Amount", "Currency", "Person", "Detail",
              "Decision", "Reviewer note"])
    kinds = collections.Counter()

    def exc(kind, ref, date, desc, amount, cur, person, detail):
        n = len(ex.rows)
        kinds[kind] += 1
        ex.add([n, kind, ref, d(date), desc, money(amount), cur, person, detail, "", ""])

    for x in rows:
        if x.get("confidence") == "unmatched" and x.get("over_threshold"):
            exc("Missing receipt", x["transaction_id"], x.get("date"), x.get("merchant"), x.get("amount"),
                x.get("currency"), x.get("spender"), "No receipt fits; over the %s threshold. Chase on Slack."
                % match.get("threshold", ""))
        if x.get("confidence") == "likely":
            exc("Check match", x["transaction_id"], x.get("date"), x.get("merchant"), x.get("amount"),
                x.get("currency"), x.get("spender"), "Receipt %s: %s" % (x.get("receipt_id"), x.get("reason")))
        if not x.get("category"):
            exc("No category", x["transaction_id"], x.get("date"), x.get("merchant"), x.get("amount"),
                x.get("currency"), x.get("spender"), "No rule matched; choose a category.")
        if x.get("note", "").startswith("dated outside"):
            exc("Dated outside the month", x["transaction_id"], x.get("date"), x.get("merchant"), x.get("amount"),
                x.get("currency"), x.get("spender"), x["note"])
    for u in match.get("unused_receipts") or []:
        exc("Receipt with no transaction", u.get("receipt_id"), u.get("date"), u.get("merchant"), u.get("amount"),
            u.get("currency"), u.get("sender"), "No bank or card line fits (personal card? other month?) %s"
            % (u.get("file") or ""))
    for p in payouts:
        if p.get("status") == "amount differs":
            exc("Payout amount differs", p.get("payout_id"), p.get("arrival_date"),
                "Deposit %s" % p.get("deposit_id"), p.get("amount"), p.get("currency"), "",
                "Deposit %.2f vs payout %.2f (difference %.2f)" % (p["deposit_amount"], p["amount"], p["difference"]))
        elif p.get("status") == "no deposit":
            exc("Payout with no deposit", p.get("payout_id"), p.get("arrival_date"), "Stripe payout",
                p.get("amount"), p.get("currency"), "", p.get("note") or "No bank deposit found in the window.")
        if p.get("split_check") not in (None, "ok"):
            exc("Payout split does not add up", p.get("payout_id"), p.get("arrival_date"), "Stripe payout",
                p.get("amount"), p.get("currency"), "", p["split_check"])
    for dep in recon.get("unmatched_deposits") or []:
        exc("Stripe deposit with no payout", dep.get("deposit_id"), dep.get("date"), dep.get("description"),
            dep.get("amount"), dep.get("currency") or "", "", "Bank deposit with no Stripe payout this month.")
    for c, now, before in unusual:
        exc("Unusual category", c, None, "Category total", now, currency, "",
            "Last month %.2f, this month %.2f" % (before, now))
    ex_last = max(len(ex.rows), 2)
    ex.filter = f"A1:K{ex_last}"
    ex.validations.append((f"J2:J{max(ex_last, 200)}", ["Approve", "Fix", "Exclude"]))

    # Summary (formulas only, over the other tabs)
    sm = Sheet("Summary", [38, 22, 50])
    sm.add([("Month-end close" + (f": {company}" if company else ""), S_TITLE)])
    sm.add(["Company", company])
    sm.add(["Month", month])
    sm.add(["Currency", currency, "Totals below count this currency only"])
    rmr = lambda c: f"'Receipts matched'!${c}$2:${c}${rm_last}"
    srr = lambda c: f"'Stripe reconciliation'!${c}${sr_first}:${c}${sr_last}"
    exr = lambda c: f"Exceptions!${c}$2:${c}${ex_last}"
    lines = [
        ("Transactions", f'=COUNTA({rmr("A")})', S_TEXT),
        ("Matched to a receipt", f'=COUNTIF({rmr("I")},"matched")', S_TEXT),
        ("Likely match (check)", f'=COUNTIF({rmr("I")},"likely")', S_TEXT),
        ("No receipt", f'=COUNTIF({rmr("I")},"unmatched")', S_TEXT),
        ("Total spend", f'=SUMIFS({rmr("D")},{rmr("E")},$B$4)', S_MONEY),
        ("Spend with a receipt", f'=SUMIFS({rmr("D")},{rmr("E")},$B$4,{rmr("I")},"<>unmatched")', S_MONEY),
        ("Spend without a receipt", "=B9-B10", S_MONEY),
        ("Stripe payouts", f'=COUNTA({srr("A")})', S_TEXT),
        ("Stripe gross", f'=SUMIFS({srr("D")},{srr("C")},$B$4)', S_MONEY),
        ("Stripe refunds", f'=SUMIFS({srr("E")},{srr("C")},$B$4)', S_MONEY),
        ("Stripe fees", f'=SUMIFS({srr("F")},{srr("C")},$B$4)', S_MONEY),
        ("Paid out", f'=SUMIFS({srr("I")},{srr("C")},$B$4)', S_MONEY),
        ("Deposited in bank (matched)", f'=SUMIFS({srr("M")},{srr("C")},$B$4)', S_MONEY),
        ("Payouts reconciled", f'=COUNTIF({srr("O")},"Reconciled")', S_TEXT),
        ("Payouts not reconciled", "=B12-B18", S_TEXT),
        ("Exceptions", f'=COUNTA({exr("B")})', S_TEXT),
        ("Approved", f'=COUNTIF({exr("J")},"Approve")', S_TEXT),
        ("To fix", f'=COUNTIF({exr("J")},"Fix")', S_TEXT),
        ("Excluded", f'=COUNTIF({exr("J")},"Exclude")', S_TEXT),
        ("Open (no decision yet)", "=B20-B21-B22-B23", S_TEXT),
    ]
    for label, formula, style in lines:
        sm.add([label, (formula, style)])
    sm.add([])
    sm.add([("Close status", S_HEAD),
            ('=IF(AND(B24=0,B19=0),"Ready to post","Open: "&B24&" exception(s) to decide, "&B19&" payout(s) to reconcile")', S_HEAD)])

    sheets = [sm, rm, sr, ct, ex]
    names = "".join(f'<sheet name="{escape(s.name)}" sheetId="{i}" r:id="rId{i}"/>' for i, s in enumerate(sheets, 1))
    defined = "".join(f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">{escape(s.ref())}!'
                      f'${s.filter.split(":")[0][0]}$1:${re.sub(r"[0-9]", "", s.filter.split(":")[1])}$'
                      f'{re.sub(r"[A-Z]", "", s.filter.split(":")[1])}</definedName>'
                      for i, s in enumerate(sheets) if s.filter)
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<sheets>{names}</sheets>' + (f"<definedNames>{defined}</definedNames>" if defined else "") +
                '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
    rels = "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                   f'relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1))
    rels += (f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/'
             '2006/relationships/styles" Target="styles.xml"/>')
    overrides = "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/'
                        'vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                        for i in range(1, len(sheets) + 1))
    try:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                       '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                       '<Default Extension="xml" ContentType="application/xml"/>'
                       '<Override PartName="/xl/workbook.xml" ContentType="application/'
                       'vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                       '<Override PartName="/xl/styles.xml" ContentType="application/'
                       'vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + overrides + '</Types>')
            z.writestr("_rels/.rels",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                       'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            z.writestr("xl/workbook.xml", workbook)
            z.writestr("xl/_rels/workbook.xml.rels",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       + rels + '</Relationships>')
            z.writestr("xl/styles.xml", STYLES)
            for i, s in enumerate(sheets, 1):
                z.writestr(f"xl/worksheets/sheet{i}.xml", s.xml())
    except OSError as exc:
        die(f"cannot write {out}: {exc}")
    print(json.dumps({"path": out, "sheets": [s.name for s in sheets],
                      "rows": {s.name: len(s.rows) - 1 for s in sheets},
                      "exceptions": len(ex.rows) - 1, "exception_types": dict(kinds)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
