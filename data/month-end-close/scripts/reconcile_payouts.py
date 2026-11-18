#!/usr/bin/env python3
"""Tie each Stripe payout to its bank deposit and split it into gross, fees and refunds.

Usage:
    python3 reconcile_payouts.py --payouts payouts.json --deposits deposits.json|.csv [--days 4]

payouts.json: Stripe payouts for the month, either as the Stripe API returns them
    ({"object": "payout", "id": "po_...", "amount": 152340, "arrival_date": 1759708800,
      "currency": "usd", "status": "paid"}; amounts in the smallest unit, e.g. cents)
    or plain ({"id", "arrival_date": "2026-10-06", "amount": 1523.40, "currency"}).
    Optional per payout: "balance_transactions" (the Stripe balance transactions in that
    payout, each {"type", "amount", "fee"}), or ready-made "gross", "fees", "refunds".
deposits: bank credits for the month (Mercury or any bank). JSON list of
    {"id", "date" | "postedAt", "amount", "description" | "counterpartyName" | "bankDescription"}
    or a CSV export with columns such as "Date (UTC)", "Description", "Amount".
    Only money in is used. When some deposits mention Stripe, only those are matched.

A payout is "reconciled" when a deposit of exactly the same amount and currency
arrives from 1 day before to --days days after its arrival date (default 4: weekends).
"amount differs" when the only deposit in that window (or the only one within 5% of
the payout) has a different amount;
"no deposit" when nothing arrives. Stripe deposits left over are listed too.
Gross = charges and payments; refunds = refunds and payment refunds (negative);
fees = Stripe fees on those lines plus separate fee lines (negative); other =
adjustments, disputes and anything else. gross + refunds + fees + other = net, which
is checked against the payout amount ("split_check").

Prints JSON: {"payouts": [...], "unmatched_deposits": [...], "totals": {...},
"errors": [...]}. Stdlib only, read-only: it never calls Stripe or the bank.
"""

import csv
import datetime
import json
import re
import sys

ZERO_DECIMAL = {"bif", "clp", "djf", "gnf", "jpy", "kmf", "krw", "mga", "pyg", "rwf", "ugx",
                "vnd", "vuv", "xaf", "xof", "xpf"}
GROSS = {"charge", "payment"}
REFUND = {"refund", "payment_refund"}
FEE = {"stripe_fee", "application_fee", "tax_fee"}
SKIP = {"payout", "payout_cancel", "payout_failure", "transfer"}


def die(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def to_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) or re.fullmatch(r"\d{9,11}", str(value).strip()):
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc).date()
    text = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def to_number(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    negative = text.startswith("(") or text.startswith("-")
    text = re.sub(r"[^\d.]", "", text)
    try:
        number = float(text)
    except ValueError:
        return None
    return -number if negative else number


def load(path, what):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            if path.lower().endswith(".csv"):
                return list(csv.DictReader(fh))
            data = json.load(fh)
    except FileNotFoundError:
        die(f"{what} file not found: {path}")
    except (json.JSONDecodeError, csv.Error) as exc:
        die(f"{what} file cannot be read: {exc}")
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        data = data["data"]
    if not isinstance(data, list):
        die(f"{what} file must hold a list")
    return data


def pick(row, *names):
    lower = {str(k).strip().lower(): v for k, v in row.items()}
    for name in names:
        if lower.get(name.lower()) not in (None, ""):
            return lower[name.lower()]
    return None


def main(argv):
    if "--payouts" not in argv or "--deposits" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 4
    errors = []

    payouts = []
    for i, p in enumerate(load(argv[argv.index("--payouts") + 1], "payouts")):
        currency = (p.get("currency") or "").lower()
        minor = p.get("object") == "payout" or isinstance(p.get("arrival_date"), int)
        unit = 1 if (not minor or currency in ZERO_DECIMAL) else 100
        amount, arrival = to_number(p.get("amount")), to_date(p.get("arrival_date") or p.get("date"))
        pid = p.get("id") or f"payout-{i + 1}"
        if amount is None or arrival is None:
            errors.append(f"{pid}: unreadable amount or arrival date, left out")
            continue
        if p.get("status") in ("failed", "canceled"):
            errors.append(f"{pid}: status {p.get('status')}, left out")
            continue
        split = {"gross": None, "fees": None, "refunds": None, "other": None}
        lines = p.get("balance_transactions")
        if isinstance(lines, list) and lines:
            g = f = r = o = 0.0
            for bt in lines:
                kind = (bt.get("type") or "").lower()
                if kind in SKIP:
                    continue
                amt, fee = (to_number(bt.get("amount")) or 0.0) / unit, (to_number(bt.get("fee")) or 0.0) / unit
                if kind in GROSS:
                    g += amt
                elif kind in REFUND:
                    r += amt
                elif kind in FEE:
                    f += amt
                else:
                    o += amt
                f -= fee
            split = {"gross": round(g, 2), "fees": round(f, 2), "refunds": round(r, 2), "other": round(o, 2)}
        else:
            for key, src in (("gross", "gross"), ("fees", "fees"), ("refunds", "refunds"), ("other", "other")):
                val = to_number(p.get(src))
                if val is not None:
                    split[key] = round(val / unit if minor else val, 2)
            if split["fees"] is not None and split["fees"] > 0:
                split["fees"] = -split["fees"]
            if split["refunds"] is not None and split["refunds"] > 0:
                split["refunds"] = -split["refunds"]
        net = round(amount / unit, 2)
        parts = [v for v in split.values() if v is not None]
        check = None
        if split["gross"] is not None:
            check = "ok" if abs(sum(parts) - net) < 0.005 else "split %.2f does not equal payout %.2f" % (sum(parts), net)
        payouts.append({"payout_id": pid, "arrival_date": arrival, "currency": currency.upper(),
                        "amount": net, **split, "split_check": check})

    deposits = []
    for i, d in enumerate(load(argv[argv.index("--deposits") + 1], "deposits")):
        amount = to_number(pick(d, "amount", "Amount"))
        date = to_date(pick(d, "postedAt", "date", "Date (UTC)", "Date", "createdAt", "Timestamp"))
        parts = []
        for k in ("counterpartyName", "description", "bankDescription", "Bank Description", "Reference"):
            v = str(pick(d, k) or "").strip()
            if v and v not in parts:
                parts.append(v)
        text = " | ".join(parts)
        status = str(pick(d, "status", "Status") or "").lower()
        if amount is None or date is None:
            errors.append(f"deposit {pick(d, 'id') or i + 1}: unreadable amount or date, left out")
            continue
        if amount <= 0 or status in ("failed", "cancelled", "canceled"):
            continue
        deposits.append({"deposit_id": str(pick(d, "id", "Reference", "bankDescription", "Bank Description") or f"deposit-{i + 1}"), "date": date,
                         "amount": round(amount, 2), "description": text.strip(),
                         "currency": str(pick(d, "currency", "Original Currency") or "").upper(),
                         "stripe": "stripe" in text.lower()})
    if any(d["stripe"] for d in deposits):
        deposits = [d for d in deposits if d["stripe"]]

    used = set()
    window = lambda p, d: -1 <= (d["date"] - p["arrival_date"]).days <= days
    same_ccy = lambda p, d: not d["currency"] or not p["currency"] or d["currency"] == p["currency"]
    for p in sorted(payouts, key=lambda x: x["arrival_date"]):
        exact = [d for d in deposits if d["deposit_id"] not in used and same_ccy(p, d) and window(p, d)
                 and abs(d["amount"] - p["amount"]) < 0.005]
        exact.sort(key=lambda d: abs((d["date"] - p["arrival_date"]).days))
        if exact:
            d = exact[0]
            p.update(status="reconciled", deposit_id=d["deposit_id"], deposit_date=d["date"].isoformat(),
                     deposit_amount=d["amount"], difference=0.0)
            used.add(d["deposit_id"])
            continue
        p.update(status="no deposit", deposit_id="", deposit_date="", deposit_amount=None, difference=None)
    for p in payouts:
        if p["status"] != "no deposit":
            continue
        near = [d for d in deposits if d["deposit_id"] not in used and same_ccy(p, d) and window(p, d)]
        if len(near) > 1:
            close = [d for d in near if p["amount"] and abs(d["amount"] - p["amount"]) / abs(p["amount"]) <= 0.05]
            near = close if len(close) == 1 else near
        if len(near) == 1:
            d = near[0]
            p.update(status="amount differs", deposit_id=d["deposit_id"], deposit_date=d["date"].isoformat(),
                     deposit_amount=d["amount"], difference=round(d["amount"] - p["amount"], 2))
            used.add(d["deposit_id"])
        elif len(near) > 1:
            p["note"] = "%d deposits in the window, none the same amount; pick by hand" % len(near)

    for p in payouts:
        p["arrival_date"] = p["arrival_date"].isoformat()
    leftovers = [{**d, "date": d["date"].isoformat()} for d in deposits if d["deposit_id"] not in used]
    total = lambda key: round(sum(p[key] or 0 for p in payouts), 2)
    totals = {"payouts": len(payouts), "reconciled": sum(p["status"] == "reconciled" for p in payouts),
              "amount_differs": sum(p["status"] == "amount differs" for p in payouts),
              "no_deposit": sum(p["status"] == "no deposit" for p in payouts),
              "unmatched_deposits": len(leftovers), "payout_total": total("amount"),
              "gross": total("gross"), "fees": total("fees"), "refunds": total("refunds"), "other": total("other"),
              "currencies": sorted({p["currency"] for p in payouts})}
    print(json.dumps({"payouts": payouts, "unmatched_deposits": leftovers, "totals": totals, "errors": errors},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
