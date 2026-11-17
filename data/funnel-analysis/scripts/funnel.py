"""Funnel calculator (standard library only).

Two modes:
  Step counts:  python funnel.py --names "A,B,C" --counts "1000,600,300"
  Events CSV:   python funnel.py --events events.csv --steps "signup,activate,purchase"
                  [--user-col user_id] [--event-col event_name] [--time-col timestamp]
                  [--window-days 7] [--segment-col channel] [--value 49.0]

Prints markdown tables. Every number in the report should be copied from this output.
"""
import argparse
import csv
import statistics
import sys
from datetime import datetime


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def parse_time(s):
    s = s.strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass
    for f in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y", "%d/%m/%Y %H:%M:%S", "%Y%m%d"):
        try:
            return datetime.strptime(s, f)
        except ValueError:
            continue
    try:
        return datetime.fromtimestamp(float(s))
    except ValueError:
        raise ValueError(f"Cannot parse timestamp: {s!r}")


def table(names, counts, value=None):
    rows = []
    top = counts[0]
    for i, (n, c) in enumerate(zip(names, counts)):
        prev = counts[i - 1] if i else c
        lost = prev - c if i else 0
        rows.append({
            "step": n, "users": c,
            "step_conv": pct(c, prev) if i else None,
            "overall": pct(c, top),
            "lost": lost,
            "lost_pct": pct(lost, prev) if i else None,
        })
    # recovery value: users lost here x downstream conversion x value
    for i, r in enumerate(rows):
        if i == 0:
            r["recovery_users"] = None
            continue
        downstream = counts[-1] / counts[i] if counts[i] else 0
        r["recovery_users"] = r["lost"] * downstream
        r["recovery_value"] = r["recovery_users"] * value if value is not None else None
    return rows


def print_table(rows, value=None):
    hdr = "| Step | Users | Step conversion | Overall conversion | Lost at this step | Lost % of prior step |"
    print(hdr)
    print("|---|---|---|---|---|---|")
    for r in rows:
        sc = "-" if r["step_conv"] is None else f"{r['step_conv']:.1f}%"
        lp = "-" if r["lost_pct"] is None else f"{r['lost_pct']:.1f}%"
        print(f"| {r['step']} | {r['users']:,} | {sc} | {r['overall']:.1f}% | {r['lost']:,} | {lp} |")
    if len(rows) > 1:
        worst_abs = max(rows[1:], key=lambda r: r["lost"])
        worst_rate = max(rows[1:], key=lambda r: r["lost_pct"])
        print()
        print(f"Overall conversion ({rows[0]['step']} -> {rows[-1]['step']}): {rows[-1]['overall']:.2f}%")
        print(f"Largest absolute loss: {worst_abs['step']} ({worst_abs['lost']:,} users, {worst_abs['lost_pct']:.1f}% of prior step)")
        print(f"Highest drop rate: {worst_rate['step']} ({worst_rate['lost_pct']:.1f}% of prior step)")
        print()
        print("Recovery upper bound (users lost x downstream conversion rate"
              + (" x value per conversion):" if value is not None else "):"))
        for r in rows[1:]:
            line = f"- {r['step']}: ~{r['recovery_users']:.1f} extra final-step users"
            if value is not None:
                line += f", ~{r['recovery_value']:,.2f} value"
            print(line)


def run_events(a):
    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    if len(steps) < 2:
        sys.exit("Give at least two steps.")
    step_idx = {s: i for i, s in enumerate(steps)}
    users = {}  # uid -> {step: [times]}
    seg = {}
    skipped = 0
    with open(a.events, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        cols = rd.fieldnames or []
        for c in (a.user_col, a.event_col):
            if c not in cols:
                sys.exit(f"Column {c!r} not found. Columns are: {cols}")
        if a.segment_col and a.segment_col not in cols:
            sys.exit(f"Segment column {a.segment_col!r} not found. Columns are: {cols}")
        use_time = a.time_col in cols
        for n, row in enumerate(rd):
            ev = (row[a.event_col] or "").strip()
            if ev not in step_idx:
                continue
            uid = (row[a.user_col] or "").strip()
            if not uid:
                skipped += 1
                continue
            try:
                t = parse_time(row[a.time_col]) if use_time else n
            except ValueError:
                skipped += 1
                continue
            users.setdefault(uid, {}).setdefault(ev, []).append(t)
            if a.segment_col and step_idx[ev] == 0 and uid not in seg:
                seg[uid] = (row[a.segment_col] or "").strip() or "(blank)"
    window = a.window_days * 86400 if (a.window_days and use_time) else None

    def reach(evs):
        """Furthest-step walk: each step must occur at/after the previous step."""
        if steps[0] not in evs:
            return None
        t0 = min(evs[steps[0]])
        path = [t0]
        for s in steps[1:]:
            cands = [t for t in evs.get(s, []) if t >= path[-1]]
            if window is not None:
                cands = [t for t in cands if (t - t0).total_seconds() <= window]
            if not cands:
                break
            path.append(min(cands))
        return path

    paths = {u: reach(e) for u, e in users.items()}
    paths = {u: p for u, p in paths.items() if p}
    counts = [sum(1 for p in paths.values() if len(p) > i) for i in range(len(steps))]
    print(f"## Funnel ({len(paths):,} users entered; window: "
          f"{a.window_days} days from step 1)" if window else f"## Funnel ({len(paths):,} users entered; no time window)")
    if skipped:
        print(f"\nNote: {skipped} rows skipped (blank user or unreadable timestamp).")
    print()
    print_table(table(steps, counts, a.value), a.value)

    if use_time:
        print("\n## Time between steps (hours, users who completed both)\n")
        print("| From -> To | Users | Median | P75 | P95 |")
        print("|---|---|---|---|---|")
        for i in range(1, len(steps)):
            d = [(p[i] - p[i - 1]).total_seconds() / 3600 for p in paths.values() if len(p) > i]
            if len(d) >= 2:
                q = statistics.quantiles(d, n=100, method="inclusive")
                print(f"| {steps[i-1]} -> {steps[i]} | {len(d):,} | {statistics.median(d):.2f} | {q[74]:.2f} | {q[94]:.2f} |")
            elif d:
                print(f"| {steps[i-1]} -> {steps[i]} | 1 | {d[0]:.2f} | {d[0]:.2f} | {d[0]:.2f} |")

    if a.segment_col:
        print(f"\n## By {a.segment_col} (value taken at step 1)\n")
        groups = {}
        for u, p in paths.items():
            groups.setdefault(seg.get(u, "(blank)"), []).append(p)
        total_overall = pct(counts[-1], counts[0])
        head = "| Segment | Entered | " + " | ".join(f"Reached {s}" for s in steps[1:]) + " | Overall | vs all (pp) |"
        print(head)
        print("|" + "---|" * (len(steps) + 3))
        for g, ps in sorted(groups.items(), key=lambda kv: -pct(sum(1 for p in kv[1] if len(p) == len(steps)), len(kv[1]))):
            c = [sum(1 for p in ps if len(p) > i) for i in range(len(steps))]
            ov = pct(c[-1], c[0])
            cells = " | ".join(f"{c[i]:,} ({pct(c[i], c[i-1]):.1f}%)" for i in range(1, len(steps)))
            small = " (small n)" if len(ps) < 30 else ""
            print(f"| {g}{small} | {c[0]:,} | {cells} | {ov:.1f}% | {ov - total_overall:+.1f} |")
        print("\nCells show users reaching the step and the step conversion rate.")


def run_counts(a):
    names = [s.strip() for s in a.names.split(",")]
    counts = [int(c.strip().replace("_", "")) for c in a.counts.split(",")]
    if len(names) != len(counts):
        sys.exit("--names and --counts need the same number of items.")
    if any(counts[i] > counts[i - 1] for i in range(1, len(counts))):
        print("WARNING: a later step has more users than the step before it; check the definition.\n")
    print_table(table(names, counts, a.value), a.value)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--names")
    p.add_argument("--counts")
    p.add_argument("--events")
    p.add_argument("--steps")
    p.add_argument("--user-col", default="user_id")
    p.add_argument("--event-col", default="event_name")
    p.add_argument("--time-col", default="timestamp")
    p.add_argument("--segment-col")
    p.add_argument("--window-days", type=float)
    p.add_argument("--value", type=float, help="value of one final-step conversion")
    a = p.parse_args()
    if a.events and a.steps:
        run_events(a)
    elif a.names and a.counts:
        run_counts(a)
    else:
        p.error("Use --names with --counts, or --events with --steps.")


if __name__ == "__main__":
    main()
