#!/usr/bin/env python3
"""Compute the numbers a takeaway slide needs from a table.

Usage: python3 figures.py table.csv|table.xlsx [--label COLUMN] [--from COL --to COL] [--sheet NAME]

Reads the table, turns "$1,200", "12%", "1 200,5" style text into numbers,
and prints JSON: per numeric column the total, mean, highest and lowest row,
each row's share of the total and rank; and, with --from and --to, each row's
change (absolute and percent), the total change and which row moved most.
Nothing is estimated: a percent change from zero is reported as null.
"""
import csv
import json
import re
import sys


def num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return None if x != x else float(x)
    s = str(x).strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[^\d,.\-+]", "", s)
    if not re.search(r"\d", s):
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        tail = s.split(",")[-1]
        s = s.replace(",", "") if len(tail) == 3 and s.count(",") >= 1 and len(s.split(",")[0]) <= 3 else s.replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def load(path, sheet):
    if path.lower().endswith((".xlsx", ".xlsm")):
        import pandas as pd
        df = pd.read_excel(path, sheet_name=sheet or 0, dtype=object)
        return [str(c) for c in df.columns], df.values.tolist()
    with open(path, newline="", encoding="utf-8-sig") as f:
        text = f.read()
    try:
        dialect = csv.Sniffer().sniff(text[:2000], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(text.splitlines(), dialect))
    return rows[0], rows[1:]


def r(v, n=2):
    return None if v is None else round(v, n)


def main():
    a = sys.argv[1:]
    if not a:
        print(json.dumps({"error": "usage: figures.py table [--label COL] [--from COL --to COL]"}))
        sys.exit(2)
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    head, rows = load(a[0], opt("--sheet"))
    head = [h.strip() for h in head]
    label = opt("--label") or head[0]
    if label not in head:
        print(json.dumps({"error": "label column not found", "columns": head}))
        sys.exit(2)
    li = head.index(label)
    keep = [x for x in rows if len(x) > li and str(x[li]).strip() and not re.match(r"(?i)^\s*(total|grand total|sum)\b", str(x[li]))]
    dropped = [str(x[li]) for x in rows if x not in keep and len(x) > li and str(x[li]).strip()]
    cols = []
    for j, h in enumerate(head):
        if j == li:
            continue
        vals = [num(x[j]) if j < len(x) else None for x in keep]
        if sum(v is not None for v in vals) >= max(1, len(keep) // 2):
            cols.append((j, h))
    out = {"label_column": label, "rows": len(keep), "ignored_total_rows": dropped, "columns": {}}
    for j, h in cols:
        vals = [(str(x[li]).strip(), num(x[j]) if j < len(x) else None) for x in keep]
        ok = [(n, v) for n, v in vals if v is not None]
        tot = sum(v for _, v in ok)
        order = sorted(ok, key=lambda t: -t[1])
        rank = {n: i + 1 for i, (n, _) in enumerate(order)}
        out["columns"][h] = {
            "total": r(tot), "mean": r(tot / len(ok)) if ok else None, "count": len(ok),
            "highest": order[0] if order else None, "lowest": order[-1] if order else None,
            "missing": [n for n, v in vals if v is None],
            "rows": [{"name": n, "value": v, "share_of_total_pct": r(v / tot * 100) if tot else None,
                      "rank": rank.get(n)} for n, v in vals],
        }
    f, t = opt("--from"), opt("--to")
    if f and t:
        if f not in out["columns"] or t not in out["columns"]:
            print(json.dumps({"error": "--from/--to must be numeric columns", "numeric_columns": list(out["columns"])}))
            sys.exit(2)
        fr = {x["name"]: x["value"] for x in out["columns"][f]["rows"]}
        to = {x["name"]: x["value"] for x in out["columns"][t]["rows"]}
        ch = []
        for n in fr:
            if fr[n] is None or to.get(n) is None:
                ch.append({"name": n, "from": fr[n], "to": to.get(n), "change": None, "change_pct": None})
                continue
            d = to[n] - fr[n]
            ch.append({"name": n, "from": fr[n], "to": to[n], "change": r(d),
                       "change_pct": r(d / fr[n] * 100) if fr[n] else None})
        both = [c for c in ch if c["change"] is not None]
        tf, tt = out["columns"][f]["total"], out["columns"][t]["total"]
        out["change"] = {
            "from_column": f, "to_column": t, "rows": ch,
            "total_from": tf, "total_to": tt, "total_change": r(tt - tf),
            "total_change_pct": r((tt - tf) / tf * 100) if tf else None,
            "largest_rise_by_amount": max(both, key=lambda c: c["change"]) if both else None,
            "largest_fall_by_amount": min(both, key=lambda c: c["change"]) if both else None,
            "largest_change_by_pct": max([c for c in both if c["change_pct"] is not None],
                                         key=lambda c: abs(c["change_pct"]), default=None),
        }
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
