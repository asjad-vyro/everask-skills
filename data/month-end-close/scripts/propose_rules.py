#!/usr/bin/env python3
"""Propose categorisation rules from transactions that are already categorised.

Usage:
    python3 propose_rules.py --file history.json [--min 2]

history.json (past QuickBooks transactions with their category):
    [{"merchant": "UBER *TRIP HELP.UBER.COM", "category": "Travel"}, ...]
    "description" or "payee" is accepted instead of "merchant"; "account" instead of
    "category".

Cleans each merchant name (card-network noise such as "SQ *", "PAYPAL *", store
numbers and ".com" removed) and groups by its first word. Proposes "<word> -> <category>"
when that word was seen at least --min times (default 2) and one category covers at
least 80% of them; otherwise tries the first two words ("uber eats", "amazon web").
Mixed merchants are listed under "conflicts" for the user to decide.

Prints JSON: {"rules": [{"match", "category", "seen", "share"}], "conflicts": [...],
"rules_text": "Uber -> Travel\\n..."}. "rules_text" can be saved and passed to
match_receipts.py --rules once the user approves it. Stdlib only.
"""

import collections
import json
import re
import sys

PREFIX = re.compile(r"^(?:sq|sp|tst|pp|paypal|pos|dd|card|visa|mc|amzn mktp|ext)\s*\*+\s*", re.I)
NOISE = re.compile(r"[*#]|\b\d{3,}\b|\bwww\.|\.com\b|\.co\.uk\b|\b(?:help|trip|pending|purchase)\b", re.I)


def words_for(name):
    text = PREFIX.sub("", (name or "").strip())
    text = NOISE.sub(" ", text)
    out = []
    for w in re.findall(r"[A-Za-z0-9&'.-]+", text):
        w = w.strip(".-'").lower()
        if len(w) > 1 and not re.search(r"\d", w) and w not in out:
            out.append(w)
    return out


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    path = argv[argv.index("--file") + 1]
    minimum = int(argv[argv.index("--min") + 1]) if "--min" in argv else 2
    try:
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"cannot read {path}: {exc}"}))
        return 1
    if not isinstance(rows, list):
        print(json.dumps({"error": "history file must hold a JSON list"}))
        return 1
    groups = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for row in rows:
        merchant = row.get("merchant") or row.get("description") or row.get("payee") or ""
        category = (row.get("category") or row.get("account") or "").strip()
        words = words_for(merchant)
        if words and category and category.lower() not in ("uncategorized expense", "uncategorised expense",
                                                            "ask my accountant"):
            groups[words[0]][" ".join(words[:2])][category] += 1
    rules, conflicts = [], []

    def judge(key, counter, report):
        seen = sum(counter.values())
        category, top = counter.most_common(1)[0]
        if seen < minimum:
            return False
        if top / seen >= 0.8:
            rules.append({"match": key, "category": category, "seen": seen, "share": round(top / seen, 2)})
            return True
        if report:
            conflicts.append({"match": key, "categories": dict(counter), "seen": seen})
        return False

    for first, subs in sorted(groups.items()):
        total = collections.Counter()
        for counter in subs.values():
            total.update(counter)
        only = next(iter(subs)) if len(subs) == 1 else first  # "blue bottle", not just "blue"
        if judge(only, total, report=False):
            continue
        found = False
        for key, counter in sorted(subs.items()):
            found = judge(key, counter, report=True) or found
        if not found and sum(total.values()) >= minimum and len(total) > 1:
            conflicts.append({"match": first, "categories": dict(total), "seen": sum(total.values())})
    rules.sort(key=lambda r: -r["seen"])
    text = "\n".join(f"{r['match']} -> {r['category']}" for r in rules)
    print(json.dumps({"rules": rules, "conflicts": conflicts, "rules_text": text}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
