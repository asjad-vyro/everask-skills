#!/usr/bin/env python3
"""Work out the status of action items from evidence, and group open items by owner.

Usage:
    python3 action_items.py status items.json [--as-of 2026-09-30] [--dayfirst]
    python3 action_items.py by-owner items.json [--as-of 2026-11-23] [--dayfirst]

items.json: a list, one object per action item:
    {"item": "Add a backup carrier for the Leeds lane", "owner": "Sam Patel",
     "due": "2026-08-15",
     "evidence": [{"status": "done", "source": "Ops tracker.xlsx, Carriers!B14",
                   "link": "https://...", "date": "2026-08-09"}],
     "user_status": null,
     "link": "https://... (Read AI notes or monday.com item)"}
evidence[].status is one of: done, in progress, dropped (what the source shows).
user_status is what the user confirmed in chat (same values, or slipped).

status mode, one rule per item, in order:
    user_status given             -> that status, basis "Confirmed by the user"
    evidence given                -> the newest evidence's status; "in progress" past its
                                     due date (vs --as-of) becomes "slipped"
    nothing                       -> "unknown", needs_confirmation = true
Never guesses "done" from silence. Prints JSON:
    {"as_of", "counts": {status: n}, "needs_confirmation": [items],
     "items": [{"item", "owner", "due", "status", "basis", "source", "link",
                "overdue_days", "needs_confirmation"}]}

by-owner mode (for the weekly status): items as read from monday.com, each with
"item", "owner", "due", "status" (monday labels like "Working on it", "Stuck", "Done"
are understood) and "link". Open items (status not done/dropped) are grouped by
owner, each with due date and days overdue or days left. Prints JSON:
    {"as_of", "owners": [{"owner", "open", "overdue", "items": [...]}], "no_owner": [...]}

--as-of defaults to today. Stdlib only. No network.
"""

import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quarter_kpis import parse_date  # noqa: E402

VALID = {"done", "in progress", "slipped", "dropped"}
ALIASES = {"complete": "done", "completed": "done", "closed": "done", "finished": "done",
           "in-progress": "in progress", "ongoing": "in progress", "working on it": "in progress",
           "started": "in progress", "open": "in progress", "stuck": "in progress",
           "late": "slipped", "overdue": "slipped", "delayed": "slipped",
           "cancelled": "dropped", "canceled": "dropped", "won't do": "dropped",
           "wont do": "dropped", "descoped": "dropped"}


def norm_status(raw):
    s = str(raw or "").strip().lower()
    if not s:
        return None
    s = ALIASES.get(s, s)
    return s if s in VALID else None


def judge(item, as_of, dayfirst):
    due = parse_date(item.get("due"), dayfirst)
    overdue = (as_of - due).days if due and as_of > due else 0
    out = {"item": item.get("item", ""), "owner": (item.get("owner") or "").strip() or None,
           "due": due.isoformat() if due else None, "status": "unknown",
           "basis": "No evidence and not confirmed", "source": None,
           "link": item.get("link", ""), "overdue_days": overdue,
           "needs_confirmation": True}
    user = norm_status(item.get("user_status"))
    if user:
        out.update(status=user, basis="Confirmed by the user", needs_confirmation=False)
        if user in ("done", "dropped"):
            out["overdue_days"] = 0
        return out
    ev = [e for e in item.get("evidence") or [] if isinstance(e, dict) and norm_status(e.get("status"))]
    if ev:
        ev.sort(key=lambda e: parse_date(e.get("date"), dayfirst) or dt.date.min)
        newest = ev[-1]
        status = norm_status(newest.get("status"))
        if status == "in progress" and overdue > 0:
            status = "slipped"
        out.update(status=status, needs_confirmation=False,
                   basis="Evidence" + (" dated %s" % newest["date"] if newest.get("date") else ""),
                   source=newest.get("source"), link=newest.get("link") or out["link"])
        if not newest.get("source"):
            out["needs_confirmation"] = True
            out["basis"] += " with no source named"
    if out["status"] in ("done", "dropped"):
        out["overdue_days"] = 0
    if out["status"] == "unknown" and overdue > 0:
        out["basis"] += "; past its due date"
    return out


def by_owner(items, as_of, dayfirst):
    owners, no_owner = {}, []
    for it in items:
        status = norm_status(it.get("status") or it.get("user_status"))
        if status in ("done", "dropped"):
            continue
        raw_status = str(it.get("status") or "").strip()
        due = parse_date(it.get("due"), dayfirst)
        rec = {"item": it.get("item", ""), "due": due.isoformat() if due else None,
               "status": raw_status or status or "unknown", "link": it.get("link", ""),
               "days_overdue": (as_of - due).days if due and as_of > due else 0,
               "days_left": (due - as_of).days if due and due >= as_of else None}
        owner = (it.get("owner") or "").strip()
        if not owner:
            no_owner.append(rec)
            continue
        owners.setdefault(owner, []).append(rec)
    result = []
    for owner, recs in sorted(owners.items(), key=lambda kv: kv[0].lower()):
        recs.sort(key=lambda r: r["due"] or "9999")
        result.append({"owner": owner, "open": len(recs),
                       "overdue": sum(1 for r in recs if r["days_overdue"] > 0), "items": recs})
    return {"owners": result, "no_owner": no_owner}


def main(argv):
    if len(argv) < 2 or argv[0] not in ("status", "by-owner"):
        print(__doc__, file=sys.stderr)
        return 2
    mode, path = argv[0], argv[1]
    dayfirst = "--dayfirst" in argv
    as_of = dt.date.today()
    if "--as-of" in argv:
        as_of = parse_date(argv[argv.index("--as-of") + 1]) if argv.index("--as-of") + 1 < len(argv) else None
        if not as_of:
            print(json.dumps({"error": "--as-of must be a date like 2026-09-30"}))
            return 1
    try:
        with open(path, encoding="utf-8") as fh:
            items = json.load(fh)
        if isinstance(items, dict):
            items = items.get("items", [])
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read %s: %s" % (path, exc)}))
        return 1
    items = [i for i in items if isinstance(i, dict) and (i.get("item") or "").strip()]
    if mode == "by-owner":
        out = {"as_of": as_of.isoformat()}
        out.update(by_owner(items, as_of, dayfirst))
    else:
        judged = [judge(i, as_of, dayfirst) for i in items]
        counts = {}
        for j in judged:
            counts[j["status"]] = counts.get(j["status"], 0) + 1
        out = {"as_of": as_of.isoformat(), "counts": counts,
               "needs_confirmation": [j for j in judged if j["needs_confirmation"]],
               "items": judged}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
