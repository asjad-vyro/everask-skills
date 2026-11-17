"""Budget maths. Usage: python3 budget.py <file.csv> [income]
CSV columns: category,type,amount. type is income, needs, wants or savings.
Multiple rows may share a category. If no income row exists, pass income as 2nd argument.
Prints a JSON summary: totals, shares, 50/30/20 targets and gaps, savings rate, unallocated money."""
import csv, json, sys
from collections import defaultdict

def main():
    path = sys.argv[1]
    income = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    by_type = defaultdict(float)
    by_cat = defaultdict(lambda: defaultdict(float))
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            t = r["type"].strip().lower()
            amt = float(str(r["amount"]).replace("$", "").replace(",", ""))
            if t == "income":
                income += amt
            else:
                by_type[t] += amt
                by_cat[t][r["category"].strip()] += amt
    if income <= 0:
        sys.exit("No income found")
    out = {"income": round(income, 2)}
    targets = {"needs": 0.5, "wants": 0.3, "savings": 0.2}
    for t, share in targets.items():
        a = by_type.get(t, 0.0)
        out[t] = {"actual": round(a, 2), "pct_of_income": round(a / income * 100, 1),
                  "target": round(income * share, 2), "gap": round(a - income * share, 2),
                  "categories": {k: round(v, 2) for k, v in sorted(by_cat[t].items(), key=lambda x: -x[1])}}
    spent = sum(by_type.values())
    out["total_outgoings_incl_savings"] = round(spent, 2)
    out["unallocated"] = round(income - spent, 2)
    out["savings_rate_pct"] = round(by_type.get("savings", 0.0) / income * 100, 1)
    out["savings_shortfall_to_20pct"] = round(max(0.0, income * 0.2 - by_type.get("savings", 0.0)), 2)
    print(json.dumps(out, indent=2))

main()
