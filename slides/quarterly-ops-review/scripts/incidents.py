#!/usr/bin/env python3
"""Tally a quarter's incidents (read from a Teams channel or an incident log).

Usage:
    python3 incidents.py incidents.json [--quarter "Q3 2026"] [--fy-start-month 1] [--dayfirst]

incidents.json: a list, one object per incident, each read from its own thread/row:
    {"title": "Carrier no-show, Leeds DC", "date": "2026-07-03", "severity": "Sev 2",
     "root_cause": "Carrier capacity", "resolution": "Rebooked with backup carrier",
     "resolved": "2026-07-04", "link": "https://teams.microsoft.com/l/message/..."}
Leave a field empty when the thread does not say it; never fill it in.

Prints JSON:
    {"quarter": {...}, "total", "outside_quarter", "undated",
     "by_severity": {"Sev 1": n, ..., "Not stated": n},
     "by_root_cause": {"Carrier capacity": n, ..., "Not stated": n},
     "resolved", "open", "days_to_resolve": {"median", "mean", "max", "counted"},
     "incomplete": [{"title", "link", "missing": [fields]}],
     "incidents": [the in-quarter incidents, normalised, sorted by date]}
Severity labels like "S1", "P1", "sev-1", "Severity 1" become "Sev 1"; other words are
kept as written (title case), never mapped to a number.

Stdlib only. No network.
"""

import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quarter_kpis import parse_date, quarter_bounds  # noqa: E402

FIELDS = ("date", "severity", "root_cause", "resolution")


def norm_severity(raw):
    s = str(raw or "").strip()
    if not s:
        return "Not stated"
    m = re.fullmatch(r"(?:sev(?:erity)?|s|p|priority)\s*[-_ ]?\s*([0-5])", s, re.I)
    if m:
        return "Sev %s" % m.group(1)
    return s[:1].upper() + s[1:].lower()


def norm_cause(raw):
    s = re.sub(r"\s+", " ", str(raw or "")).strip().rstrip(".")
    return s[:1].upper() + s[1:] if s else "Not stated"


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) \
        else default


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as fh:
            items = json.load(fh)
        if isinstance(items, dict):
            items = items.get("incidents", [])
        quarter = quarter_bounds(_arg(argv, "--quarter"), int(_arg(argv, "--fy-start-month", "1")))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    dayfirst = "--dayfirst" in argv
    label, start, end, prev = quarter
    kept, outside, undated, incomplete, durations = [], 0, 0, [], []
    sev, cause = {}, {}
    resolved = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        d = parse_date(it.get("date"), dayfirst)
        if d is None:
            undated += 1
        elif not (start <= d <= end):
            outside += 1
            continue
        missing = [f for f in FIELDS if not str(it.get(f) or "").strip()]
        rec = {"title": it.get("title", ""), "date": d.isoformat() if d else None,
               "severity": norm_severity(it.get("severity")),
               "root_cause": norm_cause(it.get("root_cause")),
               "resolution": (it.get("resolution") or "").strip(),
               "resolved": None, "days_to_resolve": None, "link": it.get("link", "")}
        r = parse_date(it.get("resolved"), dayfirst)
        if r:
            rec["resolved"] = r.isoformat()
            resolved += 1
            if d and r >= d:
                rec["days_to_resolve"] = (r - d).days
                durations.append((r - d).days)
        elif rec["resolution"]:
            resolved += 1  # a written resolution without a date still counts as resolved
        if missing:
            incomplete.append({"title": rec["title"], "link": rec["link"], "missing": missing})
        sev[rec["severity"]] = sev.get(rec["severity"], 0) + 1
        cause[rec["root_cause"]] = cause.get(rec["root_cause"], 0) + 1
        kept.append(rec)
    kept.sort(key=lambda x: x["date"] or "9999")
    out = {
        "quarter": {"label": label, "start": start.isoformat(), "end": end.isoformat()},
        "total": len(kept), "outside_quarter": outside, "undated": undated,
        "by_severity": dict(sorted(sev.items(), key=lambda kv: (kv[0] == "Not stated", kv[0]))),
        "by_root_cause": dict(sorted(cause.items(), key=lambda kv: (-kv[1], kv[0]))),
        "resolved": resolved, "open": len(kept) - resolved,
        "days_to_resolve": {
            "median": statistics.median(durations) if durations else None,
            "mean": round(statistics.mean(durations), 1) if durations else None,
            "max": max(durations) if durations else None, "counted": len(durations)},
        "incomplete": incomplete, "incidents": kept,
    }
    if undated:
        out["note"] = ("%d incident(s) have no readable date and are counted in this quarter; "
                       "check their threads." % undated)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
