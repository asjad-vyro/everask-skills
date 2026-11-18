#!/usr/bin/env python3
"""Match the month's bank/card transactions to receipts and propose categories.

Usage:
    python3 match_receipts.py --transactions txns.json --receipts receipts.json \
        [--rules rules.txt|rules.json] [--month 2026-10] [--threshold 75] [--days 3]

txns.json (QuickBooks uncategorised transactions, money out, one per line item):
    [{"id": "qb-118", "date": "2026-10-03", "merchant": "UBER *TRIP", "amount": 23.40,
      "currency": "GBP", "spender": "Priya Shah"}, ...]
    "description" is accepted instead of "merchant"; "spender" (card holder) may be blank.
    Amounts may be negative (money out); the size is what is matched.
receipts.json (read from the receipt photos):
    [{"id": "r-07", "merchant": "Uber", "date": "2026-10-03", "amount": 23.40,
      "currency": "GBP", "tax": 3.90, "sender": "Priya Shah", "file": "IMG_2231.jpg"}, ...]
rules: one rule per line, "Uber -> Travel" (also "→", "=", ":"), or JSON
    [{"match": "uber", "category": "Travel"}]. A rule matches when its text appears in
    the merchant name, case-insensitive; the longest matching rule wins.

Matching (one receipt per transaction, best pair first):
    matched   same currency, same amount (to the cent), date within --days, merchant agrees
    likely    same currency, date within --days, and either the amount is the same but the
              merchant name does not agree, or the merchant agrees and the amount is within
              25% (tip, service charge, rounding, FX)
    unmatched no receipt fits

Prints JSON: {"month", "threshold", "matches": [...], "missing_receipts": [...],
"missing_by_person": {...}, "unused_receipts": [...], "out_of_month": [...],
"counts": {...}, "errors": [...]}.
Every transaction appears once in "matches" with its confidence. Missing receipts are
the unmatched transactions over the threshold; those under it are listed in "matches"
only. Stdlib only, read-only.
"""

import datetime
import difflib
import json
import re
import sys

STOP = {"the", "ltd", "limited", "inc", "llc", "plc", "co", "com", "www", "uk", "us",
        "gbp", "usd", "eur", "pos", "card", "payment", "purchase", "debit", "sq", "pp",
        "paypal", "trip", "store", "online", "help", "bv", "gmbh", "sa"}


def die(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def arg(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 >= len(argv):
            die(f"{name} needs a value")
        return argv[i + 1]
    return default


def load_json(path, what):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        die(f"{what} file not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"{what} file is not valid JSON: {exc}")
    if not isinstance(data, list):
        die(f"{what} file must hold a JSON list")
    return data


def parse_date(value):
    if value in (None, ""):
        return None
    text = str(value).strip()
    if re.fullmatch(r"\d{9,11}", text):  # unix seconds
        return datetime.datetime.fromtimestamp(int(text), datetime.timezone.utc).date()
    text = text[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def parse_amount(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return round(abs(float(value)), 2)
    text = re.sub(r"[^\d.,\-]", "", str(value))
    if "," in text and "." in text:
        text = text.replace(",", "") if text.rfind(".") > text.rfind(",") else text.replace(".", "").replace(",", ".")
    elif "," in text and re.search(r",\d{2}$", text):
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return round(abs(float(text)), 2)
    except ValueError:
        return None


def tokens(name):
    words = re.findall(r"[a-z0-9]+", (name or "").lower())
    return {w for w in words if len(w) > 1 and w not in STOP and not w.isdigit()}


def merchant_agrees(a, b):
    ta, tb = tokens(a), tokens(b)
    if ta & tb:
        return True
    ja, jb = "".join(sorted(ta)), "".join(sorted(tb))
    if ja and jb and (ja in jb or jb in ja):
        return True
    return difflib.SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio() >= 0.75


def load_rules(path):
    if not path:
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        die(f"rules file not found: {path}")
    rules = []
    stripped = text.strip()
    if stripped.startswith("["):
        try:
            for item in json.loads(stripped):
                if item.get("match") and item.get("category"):
                    rules.append((str(item["match"]).strip().lower(), str(item["category"]).strip()))
        except (json.JSONDecodeError, AttributeError) as exc:
            die(f"rules file is not valid JSON rules: {exc}")
        return rules
    for line in text.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s*(?:->|→|=>|=|:)\s*", line, maxsplit=1)
        if len(parts) == 2 and parts[0] and parts[1]:
            rules.append((parts[0].strip().strip("\"'").lower(), parts[1].strip().strip("\"'")))
    return rules


def categorise(merchant, rules):
    low = (merchant or "").lower()
    hits = [(len(m), cat, m) for m, cat in rules if m and m in low]
    if not hits:
        return "", ""
    hits.sort(reverse=True)
    return hits[0][1], f"rule: {hits[0][2]}"


def main(argv):
    tx_path, rc_path = arg(argv, "--transactions"), arg(argv, "--receipts")
    if not tx_path or not rc_path:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        threshold = float(arg(argv, "--threshold", "75"))
        days = int(arg(argv, "--days", "3"))
    except ValueError:
        die("--threshold and --days must be numbers")
    month = arg(argv, "--month")
    if month and not re.fullmatch(r"\d{4}-\d{2}", month):
        die("--month must look like 2026-10")
    rules = load_rules(arg(argv, "--rules"))

    errors = []
    txns, receipts = [], []
    for i, t in enumerate(load_json(tx_path, "transactions")):
        d, a = parse_date(t.get("date")), parse_amount(t.get("amount"))
        merchant = t.get("merchant") or t.get("description") or t.get("payee") or ""
        if d is None or a is None:
            errors.append(f"transaction {t.get('id', i)}: unreadable date or amount, left out")
            continue
        txns.append({"id": str(t.get("id", f"t{i + 1}")), "date": d, "merchant": merchant, "amount": a,
                     "currency": (t.get("currency") or "").upper(), "spender": t.get("spender") or ""})
    for i, r in enumerate(load_json(rc_path, "receipts")):
        d, a = parse_date(r.get("date")), parse_amount(r.get("amount"))
        if a is None:
            errors.append(f"receipt {r.get('id', i)}: no readable amount, left out")
            continue
        receipts.append({"id": str(r.get("id", f"r{i + 1}")), "date": d, "merchant": r.get("merchant") or "",
                         "amount": a, "currency": (r.get("currency") or "").upper(),
                         "tax": parse_amount(r.get("tax")), "sender": r.get("sender") or "",
                         "file": r.get("file") or ""})
        if d is None:
            errors.append(f"receipt {r.get('id', i)}: no readable date, matched on amount and merchant only")

    pairs = []
    for t in txns:
        for r in receipts:
            if t["currency"] and r["currency"] and t["currency"] != r["currency"]:
                continue
            gap = abs((t["date"] - r["date"]).days) if r["date"] else None
            if gap is not None and gap > days:
                continue
            agrees = merchant_agrees(t["merchant"], r["merchant"])
            same = abs(t["amount"] - r["amount"]) < 0.005
            close = t["amount"] and abs(t["amount"] - r["amount"]) / t["amount"] <= 0.25
            if same and agrees and gap is not None:
                level, why = "matched", "same amount, date within %d day(s), merchant agrees" % gap
            elif same and agrees:
                level, why = "likely", "same amount and merchant; receipt date unreadable"
            elif same:
                level, why = "likely", "same amount and date, but the merchant name differs"
            elif close and agrees:
                level, why = "likely", "merchant and date agree; amount differs by %.2f" % (r["amount"] - t["amount"])
            else:
                continue
            rank = (0 if level == "matched" else 1, gap if gap is not None else days + 1,
                    abs(t["amount"] - r["amount"]))
            pairs.append((rank, t["id"], r["id"], level, why))
    pairs.sort()
    used_t, used_r, chosen = set(), set(), {}
    for _, tid, rid, level, why in pairs:
        if tid in used_t or rid in used_r:
            continue
        used_t.add(tid)
        used_r.add(rid)
        chosen[tid] = (rid, level, why)

    rmap = {r["id"]: r for r in receipts}
    matches, missing, by_person, out_of_month = [], [], {}, []
    for t in sorted(txns, key=lambda x: (x["date"], x["id"])):
        category, source = categorise(t["merchant"], rules)
        row = {"transaction_id": t["id"], "date": t["date"].isoformat(), "merchant": t["merchant"],
               "amount": t["amount"], "currency": t["currency"], "spender": t["spender"],
               "category": category, "category_source": source or "no rule matched"}
        if month and t["date"].strftime("%Y-%m") != month:
            out_of_month.append(t["id"])
            row["note"] = "dated outside " + month
        if t["id"] in chosen:
            rid, level, why = chosen[t["id"]]
            r = rmap[rid]
            row.update({"confidence": level, "reason": why, "receipt_id": rid,
                        "receipt_date": r["date"].isoformat() if r["date"] else "",
                        "receipt_merchant": r["merchant"], "receipt_amount": r["amount"],
                        "receipt_tax": r["tax"], "receipt_sender": r["sender"], "receipt_file": r["file"]})
        else:
            over = t["amount"] > threshold
            row.update({"confidence": "unmatched", "receipt_id": "", "over_threshold": over,
                        "reason": "no receipt fits" + ("; over threshold, chase it" if over else "; under threshold")})
            if over:
                missing.append(row)
                by_person.setdefault(t["spender"] or "Unknown (ask who made it)", []).append(
                    {"transaction_id": t["id"], "date": row["date"], "merchant": t["merchant"],
                     "amount": t["amount"], "currency": t["currency"]})
        matches.append(row)

    unused = [{"receipt_id": r["id"], "date": r["date"].isoformat() if r["date"] else "",
               "merchant": r["merchant"], "amount": r["amount"], "currency": r["currency"],
               "sender": r["sender"], "file": r["file"]}
              for r in receipts if r["id"] not in used_r]
    counts = {level: sum(1 for m in matches if m["confidence"] == level)
              for level in ("matched", "likely", "unmatched")}
    counts.update({"transactions": len(txns), "receipts": len(receipts), "missing_receipts": len(missing),
                   "uncategorised": sum(1 for m in matches if not m["category"]), "rules": len(rules)})
    print(json.dumps({"month": month or "", "threshold": threshold, "matches": matches,
                      "missing_receipts": missing, "missing_by_person": by_person,
                      "unused_receipts": unused, "out_of_month": out_of_month,
                      "counts": counts, "errors": errors}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
