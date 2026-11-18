#!/usr/bin/env python3
"""Compute a quarter's KPIs from operations rows (a sheet exported as CSV or JSON).

Usage:
    python3 quarter_kpis.py --bounds [--quarter "Q3 2026"] [--fy-start-month 1]
    python3 quarter_kpis.py --rows shipments.csv --metrics metrics.json \
        [--quarter "Q3 2026"] [--fy-start-month 1] [--dayfirst] \
        [--header-row 1] [--sheet "Shipments"] [--file-name "Ops tracker.xlsx"] [--link URL]

--bounds       only print the quarter's dates (default quarter: the last one that ended).
--rows         CSV (first line = headers) or JSON list of objects, one per sheet row,
               in sheet order, with no rows removed (row numbers are computed from it).
--metrics      JSON list, one object per KPI:
    {"name": "On-time delivery", "unit": "%", "type": "rate",
     "column": "On time", "match": ["yes", "y", "true", "1"]}
    {"name": "Cost per shipment", "unit": "USD", "type": "avg", "column": "Cost"}
    {"name": "Shipments", "type": "count"}
    {"name": "Freight spend", "unit": "USD", "type": "sum", "column": "Cost"}
    {"name": "Claims per 100 shipments", "type": "ratio", "column": "Claims",
     "per": 100}                       # sum(column) / rows * per
  Optional on any metric: "date_column" (else --date-column), "where":
  {"column": "Mode", "in": ["Road"]} to keep only matching rows.
--date-column  column holding each row's date (default: first header containing "date").
--dayfirst     read 03/07/2026 as 3 July (default: 7 March, US order). Without it,
               a date like 13/07/2026 that only works day-first is still read day-first.
--header-row   the sheet row number of the header line (default 1), so data starts on
               the next row; used to report exact sheet rows for the Sources tab.

Prints JSON:
    {"quarter": {"label", "start", "end", "previous_label"},
     "rows_total", "rows_in_quarter", "rows_bad_date": [sheet rows],
     "metrics": [{"name", "unit", "value", "rows_used", "rows_skipped": [sheet rows],
                  "source": {"file", "sheet", "location", "link"}, "error"}]}
"value" is null (never guessed) when no usable rows exist; "error" says why.

Stdlib only. Reads local files; no network.
"""

import csv
import datetime as dt
import json
import re
import sys

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
TRUTHY = {"yes", "y", "true", "1", "on time", "ontime", "x"}


# ---------- quarters ----------

def quarter_bounds(label=None, fy_start=1, today=None):
    """Return (label, start, end, previous_label). Label like 'Q3 2026' (FY quarters
    when fy_start != 1: Q1 starts in fy_start month; the year is the FY's end year)."""
    today = today or dt.date.today()
    if label:
        m = re.match(r"^\s*q([1-4])\s*(?:fy)?\s*'?(\d{2,4})\s*$", label, re.I) or \
            re.match(r"^\s*(?:fy)?\s*'?(\d{2,4})\s*q([1-4])\s*$", label, re.I)
        if not m:
            raise ValueError("Quarter must look like 'Q3 2026' or '2026 Q3', got %r" % label)
        a, b = m.groups()
        q, year = (int(a), int(b)) if len(a) == 1 else (int(b), int(a))
        if year < 100:
            year += 2000
    else:
        # the last quarter that has fully ended
        q, year = _quarter_of(today, fy_start)
        q -= 1
        if q == 0:
            q, year = 4, year - 1
    start = _q_start(q, year, fy_start)
    nq, ny = (1, year + 1) if q == 4 else (q + 1, year)
    end = _q_start(nq, ny, fy_start) - dt.timedelta(days=1)
    pq, py = (4, year - 1) if q == 1 else (q - 1, year)
    prefix = "" if fy_start == 1 else "FY"
    return ("Q%d %s%d" % (q, prefix, year), start, end, "Q%d %s%d" % (pq, prefix, py))


def _q_start(q, year, fy_start):
    # FY year N starts in month fy_start of year N-1 (unless fy_start == 1)
    month0 = (fy_start - 1) + (q - 1) * 3
    y = year if fy_start == 1 else year - 1
    y += month0 // 12
    return dt.date(y, month0 % 12 + 1, 1)


def _quarter_of(day, fy_start):
    shifted = (day.month - fy_start) % 12
    q = shifted // 3 + 1
    year = day.year if fy_start == 1 else (day.year + 1 if day.month >= fy_start else day.year)
    return q, year


# ---------- parsing ----------

def parse_date(value, dayfirst=False):
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _serial(value)
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"\d{5}(\.\d+)?", s):
        return _serial(float(s))
    m = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        return _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})\b", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        if a > 12 and b <= 12:
            return _safe_date(y, b, a)
        if b > 12 and a <= 12:
            return _safe_date(y, a, b)
        return _safe_date(y, b, a) if dayfirst else _safe_date(y, a, b)
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?,?\s+(\d{4})", s)
    if m and m.group(2).lower() in MONTHS:
        return _safe_date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    m = re.match(r"^([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", s)
    if m and m.group(1).lower() in MONTHS:
        return _safe_date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    return None


def _serial(n):
    if 20000 <= n <= 80000:  # Excel serial dates, 1954-2119
        return dt.date(1899, 12, 30) + dt.timedelta(days=int(n))
    return None


def _safe_date(y, m, d):
    try:
        return dt.date(y, m, d)
    except ValueError:
        return None


def parse_number(value):
    """'$1,234.50' -> 1234.5, '(12)' -> -12, '95%' -> 95.0, '' -> None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s.lower() in {"n/a", "na", "-", "--", "none", "null", "tbd"}:
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[^\d.,\-eE]", "", s.strip("()"))
    if s.count(",") and s.count(".") == 0 and re.fullmatch(r"-?\d{1,3}(,\d{3})+", s) is None \
            and re.fullmatch(r"-?\d+,\d{1,2}", s):
        s = s.replace(",", ".")  # decimal comma: '12,5'
    s = s.replace(",", "")
    try:
        n = float(s)
    except ValueError:
        return None
    return -n if neg else n


# ---------- rows ----------

def load_rows(path):
    with open(path, encoding="utf-8-sig") as fh:
        text = fh.read()
    if path.lower().endswith(".json") or text.lstrip().startswith("["):
        rows = json.loads(text)
        if not isinstance(rows, list) or (rows and not isinstance(rows[0], dict)):
            raise ValueError("JSON rows must be a list of objects")
        return rows
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(text.splitlines(), dialect=dialect))


def find_column(headers, wanted):
    if wanted in headers:
        return wanted
    low = {h.strip().lower(): h for h in headers if h is not None}
    return low.get(str(wanted).strip().lower())


def compute(rows, metrics, quarter, dayfirst=False, header_row=1, date_column=None,
            file_name="", sheet="", link=""):
    label, start, end, prev = quarter
    headers = list(rows[0].keys()) if rows else []
    default_date_col = find_column(headers, date_column) if date_column else next(
        (h for h in headers if h and "date" in h.lower()), None)
    out = {"quarter": {"label": label, "start": start.isoformat(), "end": end.isoformat(),
                       "previous_label": prev},
           "rows_total": len(rows), "metrics": []}
    date_cache = {}
    for metric in metrics:
        out["metrics"].append(_one_metric(metric, rows, headers, default_date_col, start, end,
                                          dayfirst, header_row, file_name, sheet, link,
                                          date_cache))
    # quarter-level counts for the default date column
    if default_date_col:
        in_q, bad = 0, []
        for i, row in enumerate(rows):
            d = parse_date(row.get(default_date_col), dayfirst)
            if d is None:
                bad.append(header_row + 1 + i)
            elif start <= d <= end:
                in_q += 1
        out["rows_in_quarter"] = in_q
        out["rows_bad_date"] = bad[:50]
        out["date_column"] = default_date_col
    else:
        out["rows_in_quarter"] = None
        out["rows_bad_date"] = []
        out["date_column"] = None
    return out


def _col_letter(index):
    s = ""
    index += 1
    while index:
        index, r = divmod(index - 1, 26)
        s = chr(65 + r) + s
    return s


def _one_metric(metric, rows, headers, default_date_col, start, end, dayfirst, header_row,
                file_name, sheet, link, date_cache):
    name = metric.get("name") or "Unnamed KPI"
    mtype = (metric.get("type") or "").lower()
    res = {"name": name, "unit": metric.get("unit", ""), "type": mtype, "value": None,
           "rows_used": 0, "rows_skipped": [], "source": None, "error": None}
    if mtype not in {"count", "sum", "avg", "rate", "ratio", "min", "max"}:
        res["error"] = "type must be one of count, sum, avg, rate, ratio, min, max"
        return res
    date_col = find_column(headers, metric["date_column"]) if metric.get("date_column") \
        else default_date_col
    if not date_col:
        res["error"] = "No date column found; pass --date-column or set date_column"
        return res
    col = None
    if mtype != "count":
        col = find_column(headers, metric.get("column", ""))
        if not col:
            res["error"] = "Column %r not in the sheet (columns: %s)" % (
                metric.get("column"), ", ".join(h for h in headers if h))
            return res
    where = metric.get("where")
    where_col = None
    if where:
        where_col = find_column(headers, where.get("column", ""))
        if not where_col:
            res["error"] = "Filter column %r not in the sheet" % where.get("column")
            return res
        allowed = {str(v).strip().lower() for v in where.get("in", [])}

    values, sheet_rows = [], []
    for i, row in enumerate(rows):
        sheet_row = header_row + 1 + i
        key = (date_col, i)
        if key not in date_cache:
            date_cache[key] = parse_date(row.get(date_col), dayfirst)
        d = date_cache[key]
        if d is None or not (start <= d <= end):
            continue
        if where_col and str(row.get(where_col, "")).strip().lower() not in allowed:
            continue
        if mtype == "count":
            values.append(1.0)
            sheet_rows.append(sheet_row)
            continue
        raw = row.get(col)
        if mtype == "rate":
            text = str(raw if raw is not None else "").strip().lower()
            if text == "":
                res["rows_skipped"].append(sheet_row)
                continue
            match = {str(v).strip().lower() for v in metric.get("match", [])} or TRUTHY
            values.append(1.0 if text in match else 0.0)
        else:
            n = parse_number(raw)
            if n is None:
                if mtype == "ratio" and (raw is None or str(raw).strip() == ""):
                    n = 0.0  # a blank claims/incidents cell counts as zero
                else:
                    res["rows_skipped"].append(sheet_row)
                    continue
            values.append(n)
        sheet_rows.append(sheet_row)

    res["rows_used"] = len(values)
    res["rows_skipped"] = res["rows_skipped"][:50]
    if not values:
        res["error"] = "No usable rows in the quarter"
    else:
        if mtype == "count":
            v = float(len(values))
        elif mtype == "sum":
            v = sum(values)
        elif mtype == "avg":
            v = sum(values) / len(values)
        elif mtype == "rate":
            v = 100.0 * sum(values) / len(values)
        elif mtype == "ratio":
            v = sum(values) / len(values) * float(metric.get("per", 1))
        elif mtype == "min":
            v = min(values)
        else:
            v = max(values)
        res["value"] = round(v, 4)
    col_ref = ""
    if col:
        col_ref = "column %s (%s), " % (_col_letter(headers.index(col)), col)
    span = "rows %d-%d" % (min(sheet_rows), max(sheet_rows)) if sheet_rows else "no rows"
    rule = {"count": "count of rows", "sum": "sum", "avg": "average", "min": "minimum",
            "max": "maximum",
            "rate": "share of rows marked %s" % "/".join(metric.get("match", []) or ["yes"]),
            "ratio": "sum / rows x %s" % metric.get("per", 1)}[mtype]
    filt = ""
    if where_col:
        filt = ", where %s in %s" % (where_col, "/".join(map(str, where.get("in", []))))
    res["source"] = {
        "file": file_name, "sheet": sheet, "link": link,
        "location": "%s%s (%d rows dated %s to %s by %s%s); %s" % (
            col_ref, span, len(values), start.isoformat(), end.isoformat(), date_col, filt,
            rule),
    }
    return res


def _arg(argv, flag, default=None):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 >= len(argv):
            raise SystemExit("Missing value after %s" % flag)
        return argv[i + 1]
    return default


def main(argv):
    if not argv or "-h" in argv or "--help" in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        fy = int(_arg(argv, "--fy-start-month", "1"))
        if not 1 <= fy <= 12:
            raise ValueError("--fy-start-month must be 1-12")
        quarter = quarter_bounds(_arg(argv, "--quarter"), fy)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    if "--bounds" in argv:
        label, start, end, prev = quarter
        print(json.dumps({"label": label, "start": start.isoformat(), "end": end.isoformat(),
                          "previous_label": prev}, indent=2))
        return 0
    rows_path, metrics_path = _arg(argv, "--rows"), _arg(argv, "--metrics")
    if not rows_path or not metrics_path:
        print(json.dumps({"error": "--rows and --metrics are required (or use --bounds)"}))
        return 2
    try:
        rows = load_rows(rows_path)
        with open(metrics_path, encoding="utf-8") as fh:
            metrics = json.load(fh)
        if isinstance(metrics, dict):
            metrics = metrics.get("metrics", [])
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read input: %s" % exc}))
        return 1
    if not rows:
        print(json.dumps({"error": "The rows file has no data rows"}))
        return 1
    out = compute(rows, metrics, quarter, dayfirst="--dayfirst" in argv,
                  header_row=int(_arg(argv, "--header-row", "1")),
                  date_column=_arg(argv, "--date-column"),
                  file_name=_arg(argv, "--file-name", rows_path),
                  sheet=_arg(argv, "--sheet", ""), link=_arg(argv, "--link", ""))
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
