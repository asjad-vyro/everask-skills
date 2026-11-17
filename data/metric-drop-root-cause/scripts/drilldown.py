"""Drill-down for a metric change. Standard library only.

Compares two periods of a CSV, ranks which segments drove the change, and for
ratio metrics (e.g. conversions / sessions) splits each segment's effect into a
rate effect and a mix effect.

Periods are chosen either by a label column:
    --period-col month --period-a 2025-01 --period-b 2025-02
or by date windows (ISO dates, inclusive):
    --date-col date --a-start 2025-02-01 --a-end 2025-02-28 --b-start 2025-03-01 --b-end 2025-03-28

Examples:
    python drilldown.py --csv data.csv --metric revenue --dimension region channel device \
        --date-col date --a-start 2025-02-01 --a-end 2025-02-28 --b-start 2025-03-01 --b-end 2025-03-28
    python drilldown.py --csv data.csv --metric conversions --denominator sessions \
        --dimension channel --period-col week --period-a W1 --period-b W2
    python drilldown.py --csv data.csv --metric revenue --date-col date --validate \
        --a-start 2025-02-01 --a-end 2025-02-28 --b-start 2025-03-01 --b-end 2025-03-28
"""

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from datetime import date


def num(row, col):
    raw = (row.get(col) or "").strip().replace(",", "")
    if raw == "":
        return 0.0
    try:
        return float(raw)
    except ValueError:
        sys.exit(f"Column '{col}' has a non-numeric value: {raw!r}")


def day(row, col):
    try:
        return date.fromisoformat((row.get(col) or "").strip()[:10])
    except ValueError:
        sys.exit(f"Column '{col}' has a value that is not an ISO date (YYYY-MM-DD): {row.get(col)!r}")


def pick(rows, args, which):
    if args.period_col:
        label = args.period_a if which == "a" else args.period_b
        return [r for r in rows if (r.get(args.period_col) or "").strip() == label]
    start = date.fromisoformat(args.a_start if which == "a" else args.b_start)
    end = date.fromisoformat(args.a_end if which == "a" else args.b_end)
    return [r for r in rows if start <= day(r, args.date_col) <= end]


def value(rows, args):
    """Return (numerator, denominator) sums."""
    n = sum(num(r, args.metric) for r in rows)
    d = sum(num(r, args.denominator) for r in rows) if args.denominator else None
    return n, d


def ratio(n, d):
    return n / d if d else 0.0


def validate(rows, args):
    if not args.date_col:
        sys.exit("--validate needs --date-col and the a/b date windows")
    daily = defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        k = day(r, args.date_col)
        daily[k][0] += num(r, args.metric)
        if args.denominator:
            daily[k][1] += num(r, args.denominator)

    def series(start, end):
        s, e = date.fromisoformat(start), date.fromisoformat(end)
        return [ratio(*v) if args.denominator else v[0] for k, v in sorted(daily.items()) if s <= k <= e]

    base, after = series(args.a_start, args.a_end), series(args.b_start, args.b_end)
    if len(base) < 7 or not after:
        print("VALIDATE: need at least 7 baseline days and some days in period B.")
        return
    mu, sd = statistics.mean(base), statistics.pstdev(base)
    mb = statistics.mean(after)
    se = sd / (len(after) ** 0.5)
    z = (mb - mu) / se if se else float("inf")
    print("VALIDATE (daily values)")
    print(f"  baseline days={len(base)} mean={mu:,.4g} sd={sd:,.4g}")
    print(f"  period B days={len(after)} mean={mb:,.4g} change={(mb - mu) / mu * 100 if mu else 0:+.1f}%")
    print(f"  z-score of period B mean vs baseline mean (standard error = sd / sqrt(days in B)): {z:+.2f}")
    print("  Reading: |z| < 1.5 = inside normal variation, report as noise unless other evidence;"
          " larger = real movement. Weekday patterns inflate sd, so compare equal weekday mixes.")
    # onset: first day in B window after which values stay beyond 1.5 sd below/above the baseline mean
    sign = -1 if mb < mu else 1
    days_b = [(k, ratio(*v) if args.denominator else v[0]) for k, v in sorted(daily.items())
              if date.fromisoformat(args.b_start) <= k <= date.fromisoformat(args.b_end)]
    onset = None
    for i, (k, v) in enumerate(days_b):
        if all(sign * (x - mu) > 1.5 * sd for _, x in days_b[i:]):
            onset = k
            break
    print(f"  Onset (first day from which every later day is >1.5 sd {'below' if sign < 0 else 'above'} baseline): "
          f"{onset if onset else 'none found - change is gradual or noisy'}")


def drill(rows_a, rows_b, dim, args):
    agg = {}
    for tag, rows in (("a", rows_a), ("b", rows_b)):
        g = defaultdict(lambda: [0.0, 0.0])
        for r in rows:
            key = (r.get(dim) or "").strip() or "(blank)"
            g[key][0] += num(r, args.metric)
            if args.denominator:
                g[key][1] += num(r, args.denominator)
        agg[tag] = g
    keys = sorted(set(agg["a"]) | set(agg["b"]))
    ta_n = sum(v[0] for v in agg["a"].values())
    tb_n = sum(v[0] for v in agg["b"].values())
    ta_d = sum(v[1] for v in agg["a"].values())
    tb_d = sum(v[1] for v in agg["b"].values())
    out = []
    if not args.denominator:
        net = tb_n - ta_n
        gross = sum(abs(agg["b"][k][0] - agg["a"][k][0]) for k in keys)
        for k in keys:
            a, b = agg["a"][k][0], agg["b"][k][0]
            ch = b - a
            out.append({"segment": k, "a": a, "b": b, "change": ch,
                        "pct": (ch / a * 100) if a else None,
                        "share_of_net": (ch / net * 100) if net else None,
                        "share_of_gross": (ch / gross * 100) if gross else 0.0,
                        "share_a": a / ta_n * 100 if ta_n else 0.0,
                        "share_b": b / tb_n * 100 if tb_n else 0.0})
        out.sort(key=lambda r: abs(r["change"]), reverse=True)
        return out, {"a": ta_n, "b": tb_n, "net": net, "gross": gross}
    ra, rb = ratio(ta_n, ta_d), ratio(tb_n, tb_d)
    for k in keys:
        na, da = agg["a"][k]
        nb, db = agg["b"][k]
        r_a, r_b = ratio(na, da), ratio(nb, db)
        w_a, w_b = ratio(da, ta_d), ratio(db, tb_d)
        rate_eff = w_b * (r_b - r_a)           # segment's own rate moved
        mix_eff = (w_b - w_a) * (r_a - ra)     # segment's weight moved
        out.append({"segment": k, "rate_a": r_a, "rate_b": r_b, "weight_a": w_a * 100, "weight_b": w_b * 100,
                    "rate_effect": rate_eff, "mix_effect": mix_eff, "total_effect": rate_eff + mix_eff})
    out.sort(key=lambda r: abs(r["total_effect"]), reverse=True)
    return out, {"a": ra, "b": rb, "net": rb - ra,
                 "rate_total": sum(r["rate_effect"] for r in out), "mix_total": sum(r["mix_effect"] for r in out)}


def show(dim, table, tot, args):
    print(f"\nDIMENSION: {dim}")
    if not args.denominator:
        print(f"  total A={tot['a']:,.2f}  B={tot['b']:,.2f}  net change={tot['net']:+,.2f}"
              f"  ({tot['net'] / tot['a'] * 100 if tot['a'] else 0:+.1f}%)")
        print(f"  {'segment':<22}{'A':>14}{'B':>14}{'change':>14}{'%chg':>9}{'%net':>9}{'%gross':>9}{'shareA':>8}{'shareB':>8}")
        for r in table:
            pct = f"{r['pct']:+.1f}" if r["pct"] is not None else "new"
            sn = f"{r['share_of_net']:+.1f}" if r["share_of_net"] is not None else "n/a"
            print(f"  {r['segment'][:21]:<22}{r['a']:>14,.2f}{r['b']:>14,.2f}{r['change']:>+14,.2f}{pct:>9}{sn:>9}"
                  f"{r['share_of_gross']:>+9.1f}{r['share_a']:>8.1f}{r['share_b']:>8.1f}")
        print("  %net = share of the net change (misleading when the net change is near zero or segments offset);"
              " %gross = share of total absolute movement.")
    else:
        print(f"  overall rate A={tot['a']:.4%}  B={tot['b']:.4%}  change={tot['net'] * 100:+.3f} pts")
        print(f"  of which rate effect={tot['rate_total'] * 100:+.3f} pts, mix effect={tot['mix_total'] * 100:+.3f} pts")
        print(f"  {'segment':<22}{'rateA':>9}{'rateB':>9}{'wtA%':>8}{'wtB%':>8}{'rate fx':>10}{'mix fx':>10}{'total fx':>10}")
        for r in table:
            print(f"  {r['segment'][:21]:<22}{r['rate_a']:>9.2%}{r['rate_b']:>9.2%}{r['weight_a']:>8.1f}{r['weight_b']:>8.1f}"
                  f"{r['rate_effect'] * 100:>+10.3f}{r['mix_effect'] * 100:>+10.3f}{r['total_effect'] * 100:>+10.3f}")
        print("  effects are in percentage points of the overall rate; rate fx = segment's own rate changed,"
              " mix fx = segment's share of the denominator changed.")


def main():
    p = argparse.ArgumentParser(description="Drill down into a metric change by dimension.")
    p.add_argument("--csv", required=True)
    p.add_argument("--metric", required=True, help="numeric column (the numerator for a ratio metric)")
    p.add_argument("--denominator", help="numeric column; makes the metric a ratio (numerator / denominator)")
    p.add_argument("--dimension", nargs="*", default=[])
    p.add_argument("--period-col")
    p.add_argument("--period-a")
    p.add_argument("--period-b")
    p.add_argument("--date-col")
    p.add_argument("--a-start")
    p.add_argument("--a-end")
    p.add_argument("--b-start")
    p.add_argument("--b-end")
    p.add_argument("--validate", action="store_true", help="check the change against daily variation")
    p.add_argument("--pairs", action="store_true", help="also drill into every pair of dimensions")
    args = p.parse_args()

    if args.period_col and not (args.period_a and args.period_b):
        p.error("--period-col needs --period-a and --period-b")
    if not args.period_col and not (args.date_col and args.a_start and args.a_end and args.b_start and args.b_end):
        p.error("give --period-col/--period-a/--period-b or --date-col with --a-start/--a-end/--b-start/--b-end")

    with open(args.csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("CSV is empty")
    cols = set(rows[0])
    for c in [args.metric, args.denominator, args.period_col, args.date_col, *args.dimension]:
        if c and c not in cols:
            sys.exit(f"Column '{c}' not in CSV. Columns: {sorted(cols)}")

    if args.validate:
        validate(rows, args)
    rows_a, rows_b = pick(rows, args, "a"), pick(rows, args, "b")
    if not rows_a or not rows_b:
        sys.exit(f"No rows in period A ({len(rows_a)}) or period B ({len(rows_b)}); check the labels or dates")
    print(f"rows: period A={len(rows_a)}, period B={len(rows_b)}")
    for dim in args.dimension:
        table, tot = drill(rows_a, rows_b, dim, args)
        show(dim, table, tot, args)
    if args.pairs and len(args.dimension) > 1:
        for i, d1 in enumerate(args.dimension):
            for d2 in args.dimension[i + 1:]:
                name = f"{d1}+{d2}"
                for rr in rows_a + rows_b:
                    rr[name] = f"{rr.get(d1)} / {rr.get(d2)}"
                table, tot = drill(rows_a, rows_b, name, args)
                show(name, table[:8], tot, args)


if __name__ == "__main__":
    main()
