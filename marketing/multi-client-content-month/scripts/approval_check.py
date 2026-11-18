#!/usr/bin/env python3
"""Decide, post by post, what may be scheduled for one client, from their Trello board.

Usage:
    python3 approval_check.py --file approvals.json

approvals.json:
{
  "client": "Bloom Bakery",
  "today": "2026-12-03",                      # the client's local date
  "nudge_days": 2,                            # optional, default 2
  "posts": [                                  # rows of the calendar sheet
    {"id": "12", "date": "2026-12-05", "time": "18:00", "channel": "instagram",
     "caption": "...", "media": ["https://...png"],
     "approved_hash": "",                     # sheet column, blank until approved
     "status": "For approval"}
  ],
  "cards": [                                  # one per post, read from Trello
    {"post_id": "12", "list": "Approved", "card_url": "https://trello.com/c/...",
     "caption": "...", "media": ["https://...png"],
     "date": "2026-12-05", "time": "18:00", "channel": "instagram",
     "new_comments": 0}                       # client comments since the last check
  ]
}

Prints JSON {"client", "today", "posts": [...], "summary": {action: count}}. Each post
gets one "action":
    record_approval     card is in Approved and nothing was recorded yet: write "hash"
                        into the sheet's approved_hash column, then it can be scheduled
    ready_to_schedule   approved, and nothing changed since the approval
    needs_reapproval    changed after approval (card or sheet differs from what was
                        approved): move the card back to "For approval", clear the hash
    out_of_sync         card and sheet differ while the card waits: fix the card first
    changes_requested   client commented or moved the card to a changes list
    nudge               still waiting and due within nudge_days
    overdue             date has passed without approval: never publish it
    waiting             waiting for approval, not due soon
    no_card             no card on the board for this post
    already_done        sheet says Scheduled or Published
A post is only ever schedulable as record_approval or ready_to_schedule.
Stdlib only, no network.
"""

import datetime
import hashlib
import json
import sys

DONE = {"scheduled", "published"}
CHANGE_LISTS = ("change", "revis", "edit", "feedback", "rework")


def norm_text(s):
    return " ".join(str(s or "").replace("\r\n", "\n").split())


def norm_media(m):
    if m is None:
        return []
    if isinstance(m, str):
        m = [m]
    return [str(x).strip() for x in m if str(x).strip()]


def content_hash(item):
    """Hash of what the approver signs off: caption, media, date, time, channel."""
    payload = json.dumps({
        "caption": norm_text(item.get("caption")),
        "media": norm_media(item.get("media")),
        "date": str(item.get("date", "")).strip(),
        "time": str(item.get("time", "")).strip(),
        "channel": str(item.get("channel", "")).strip().lower(),
    }, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def classify(post, card, today, nudge_days):
    status = str(post.get("status", "")).strip().lower()
    if status in DONE:
        return "already_done", f"Sheet status is {post.get('status')}."
    if card is None:
        return "no_card", "No Trello card for this post."
    lst = str(card.get("list", "")).strip().lower()
    card_h, sheet_h = content_hash(card), content_hash(post)
    approved_h = str(post.get("approved_hash", "")).strip()
    try:
        due = datetime.date.fromisoformat(str(post.get("date", "")).strip())
    except ValueError:
        return "out_of_sync", f"Post date '{post.get('date')}' is not a date; fix the sheet."

    if lst == "approved":
        if card_h != sheet_h:
            return "needs_reapproval", "Card and sheet differ; the approved version is unclear."
        if not approved_h:
            if due < today:
                return "overdue", "Approved after its date passed; ask the user for a new date."
            return "record_approval", "Newly approved; record the hash in the sheet."
        if approved_h != card_h:
            return "needs_reapproval", "Content changed after approval."
        if due < today:
            return "overdue", "Approved but its date has passed and it was never scheduled."
        return "ready_to_schedule", "Approved and unchanged."

    if any(w in lst for w in CHANGE_LISTS) or int(card.get("new_comments") or 0) > 0:
        return "changes_requested", "Client asked for changes (comment or list)."
    if card_h != sheet_h:
        return "out_of_sync", "Card does not match the sheet; update the card."
    if due < today:
        return "overdue", "Date passed without approval; do not publish."
    if (due - today).days <= nudge_days:
        return "nudge", f"Due {due.isoformat()} and still waiting for approval."
    return "waiting", "Waiting for approval."


def main(argv):
    if "--file" not in argv or argv.index("--file") + 1 >= len(argv):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            data = json.load(fh)
        today = datetime.date.fromisoformat(str(data.get("today", "")).strip())
        nudge_days = int(data.get("nudge_days", 2))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    except ValueError:
        print(json.dumps({"error": "'today' must be a date like 2026-12-03 and "
                                   "'nudge_days' a whole number"}))
        return 1

    cards = {}
    dupes = set()
    for c in data.get("cards") or []:
        pid = str(c.get("post_id", "")).strip()
        if pid in cards:
            dupes.add(pid)
        cards[pid] = c

    out, summary = [], {}
    for post in data.get("posts") or []:
        pid = str(post.get("id", "")).strip()
        if pid in dupes:
            action, reason = "out_of_sync", "More than one card for this post; keep one."
        else:
            action, reason = classify(post, cards.get(pid), today, nudge_days)
        card = cards.get(pid) or {}
        entry = {"id": pid, "date": post.get("date", ""), "time": post.get("time", ""),
                 "channel": post.get("channel", ""), "action": action, "reason": reason,
                 "card_url": card.get("card_url", "")}
        if action == "record_approval":
            entry["hash"] = content_hash(card)
        out.append(entry)
        summary[action] = summary.get(action, 0) + 1

    post_ids = {str(p.get("id", "")).strip() for p in data.get("posts") or []}
    orphans = [c.get("card_url") or pid for pid, c in cards.items() if pid not in post_ids]
    result = {"client": data.get("client", ""), "today": today.isoformat(),
              "posts": out, "summary": summary}
    if orphans:
        result["cards_without_post"] = orphans
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
