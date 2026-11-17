#!/usr/bin/env python3
"""Simulate avalanche / snowball debt payoff. Standard library only.
Usage: python3 payoff.py debts.json EXTRA [--csv-dir DIR]
debts.json: [{"name": str, "balance": number, "apr": percent, "min": number}]
Prints JSON: per strategy months, total_interest, total_paid, payoff_order, yearly balances.
With --csv-dir, writes schedule_<strategy>.csv (month, debt, payment, principal, interest, remaining)."""
import csv, json, os, sys

def simulate(debts, extra, strategy, cap=1200):
    ds = [dict(d, bal=round(float(d["balance"]), 2)) for d in debts]
    key = (lambda d: -float(d["apr"])) if strategy == "avalanche" else (lambda d: d["bal"])
    order0 = sorted(ds, key=key)
    rows, total_int, month, order, yearly = [], 0.0, 0, [], []
    budget = sum(float(d["min"]) for d in ds) + float(extra)
    while any(d["bal"] > 0.005 for d in ds) and month < cap:
        month += 1
        live = [d for d in ds if d["bal"] > 0.005]
        interest = {d["name"]: round(d["bal"] * float(d["apr"]) / 1200, 2) for d in live}
        for d in live:
            d["bal"] = round(d["bal"] + interest[d["name"]], 2)
        total_int += sum(interest.values())
        pay = {d["name"]: 0.0 for d in live}
        left = budget
        for d in live:  # minimums first
            p = min(float(d["min"]), d["bal"])
            pay[d["name"]] += p; left -= p
        for d in sorted(live, key=key):  # surplus to target, rolling down the order
            if left <= 0.005: break
            room = d["bal"] - pay[d["name"]]
            p = min(left, room)
            if p > 0: pay[d["name"]] += p; left -= p
        for d in live:
            p = round(pay[d["name"]], 2)
            d["bal"] = round(d["bal"] - p, 2)
            rows.append([month, d["name"], p, round(p - interest[d["name"]], 2), interest[d["name"]], max(d["bal"], 0)])
            if d["bal"] <= 0.005 and d["name"] not in order: order.append(d["name"])
        if month % 12 == 0: yearly.append([month, round(sum(d["bal"] for d in ds), 2)])
    ok = all(d["bal"] <= 0.005 for d in ds)
    paid = round(sum(r[2] for r in rows), 2)
    return {"strategy": strategy, "paid_off": ok, "months": month, "total_interest": round(total_int, 2),
            "total_paid": paid, "target_order": [d["name"] for d in order0], "payoff_order": order,
            "balance_at_year_ends": yearly}, rows

if __name__ == "__main__":
    debts = json.load(open(sys.argv[1])); extra = float(sys.argv[2])
    out_dir = sys.argv[sys.argv.index("--csv-dir") + 1] if "--csv-dir" in sys.argv else None
    res = {}
    for s in ("avalanche", "snowball"):
        r, rows = simulate(debts, extra, s); res[s] = r
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, f"schedule_{s}.csv"), "w", newline="") as f:
                w = csv.writer(f); w.writerow(["month", "debt", "payment", "principal", "interest", "remaining_balance"]); w.writerows(rows)
    print(json.dumps(res, indent=1))
