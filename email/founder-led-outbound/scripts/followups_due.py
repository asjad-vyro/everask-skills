#!/usr/bin/env python3
"""List who is due the one follow-up, and who has had theirs and should be left alone.

Usage:
    python3 followups_due.py --file rows.json [--today 2026-11-18] [--days 3]

rows.json: the sheet rows, as a JSON list:
    [{"company": "...", "email": "...", "status": "Emailed",
      "emailed_on": "2026-11-12", "replied": false, "followups_sent": 0}, ...]

Prints JSON: {"today", "days", "due": [...], "finished": [...], "problems": [...]}.
  due       status "Emailed", no reply, no follow-up yet, emailed >= --days days ago
  finished  status "Emailed" or "Followed up", no reply, follow-up already sent
            (never a second follow-up: mark these "No reply")
  problems  rows whose date cannot be read

Rows with any other status (Replied, Booked, Opted out, Not now, ...) are ignored.
Stdlib only. No network access.
"""

import datetime
import json
import sys


def parse(value):
    s = str(value or "").strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def truthy(v):
    return v is True or str(v).strip().lower() in ("yes", "true", "y", "1")


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    today = datetime.date.today()
    if "--today" in argv:
        today = parse(argv[argv.index("--today") + 1]) or today
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 3
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            rows = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read input: {exc}"}))
        return 1
    due, finished, problems = [], [], []
    for row in rows:
        status = str(row.get("status") or "").strip().lower()
        if status not in ("emailed", "followed up") or truthy(row.get("replied")):
            continue
        sent = int(row.get("followups_sent") or 0) or (1 if status == "followed up" else 0)
        if sent >= 1:
            finished.append({"company": row.get("company"), "email": row.get("email"),
                             "action": "mark 'No reply'; no more follow-ups"})
            continue
        d = parse(row.get("emailed_on"))
        if d is None:
            problems.append({"company": row.get("company"),
                             "problem": f"cannot read emailed_on '{row.get('emailed_on')}'"})
            continue
        age = (today - d).days
        if age >= days:
            due.append({"company": row.get("company"), "email": row.get("email"),
                        "emailed_on": d.isoformat(), "days_ago": age})
    print(json.dumps({"today": today.isoformat(), "days": days, "due": due,
                      "finished": finished, "problems": problems}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
