#!/usr/bin/env python3
"""Freelance rate calculator: derives day/hourly rate backwards from target income
and honest utilization. Deterministic, standard library only, no network."""
import argparse, json, math, sys


def calc(target, overhead, tax_pct, weeks_off, billable_pct, hours_week, hours_day):
    need = target * (1 + tax_pct / 100) + overhead
    working_weeks = 52 - weeks_off
    hours = working_weeks * hours_week * billable_pct / 100
    hourly = need / hours
    return need, working_weeks, hours, hourly, hourly * hours_day


def main(argv=None):
    ap = argparse.ArgumentParser(description="Day/hourly rate from target income + honest utilization.")
    ap.add_argument("--target", type=float, required=True, help="Target pre-tax personal income per year")
    ap.add_argument("--overhead", type=float, default=12000, help="Annual business overhead (default 12000)")
    ap.add_argument("--extra-tax-pct", type=float, default=8, help="Self-employment tax premium, pct of target (default 8)")
    ap.add_argument("--weeks-off", type=float, default=6, help="Vacation + sick + admin-only weeks (default 6)")
    ap.add_argument("--billable-pct", type=float, default=60, help="Pct of working time that is billable (default 60)")
    ap.add_argument("--hours-week", type=float, default=40)
    ap.add_argument("--hours-day", type=float, default=8)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.target <= 0 or not 0 < a.billable_pct <= 100 or not 0 <= a.weeks_off < 52 or a.hours_week <= 0 or a.hours_day <= 0:
        print("error: target, hours must be > 0; billable-pct in (0,100]; weeks-off in [0,52)", file=sys.stderr)
        return 2

    need, weeks, hours, hourly, day = calc(a.target, a.overhead, a.extra_tax_pct, a.weeks_off,
                                           a.billable_pct, a.hours_week, a.hours_day)
    naive = a.target / 2000
    quote_hour = math.ceil(hourly / 5) * 5
    quote_day = math.ceil(day / 25) * 25
    sens = {}
    for pct in (50, 60, 70):
        sens[pct] = round(calc(a.target, a.overhead, a.extra_tax_pct, a.weeks_off, pct, a.hours_week, a.hours_day)[3], 2)
    out = {
        "required_revenue": round(need, 2),
        "working_weeks": weeks,
        "billable_hours_year": round(hours, 1),
        "hourly": round(hourly, 2),
        "day_rate": round(day, 2),
        "quote_hourly_rounded_up": quote_hour,
        "quote_day_rounded_up": quote_day,
        "naive_salary_div_2000": round(naive, 2),
        "multiplier_vs_naive": round(hourly / naive, 2),
        "sensitivity_hourly_by_billable_pct": sens,
        "assumptions": {"target": a.target, "overhead": a.overhead, "extra_tax_pct": a.extra_tax_pct,
                        "weeks_off": a.weeks_off, "billable_pct": a.billable_pct,
                        "hours_week": a.hours_week, "hours_day": a.hours_day},
    }
    if a.json:
        print(json.dumps(out, indent=1))
        return 0
    print(f"required revenue: {need:,.2f}  (target {a.target:,.0f} + {a.extra_tax_pct:g}% tax premium + {a.overhead:,.0f} overhead)")
    print(f"billable hours:   {hours:,.0f}  ({weeks:g} weeks x {a.hours_week:g}h x {a.billable_pct:g}% billable)")
    print(f"hourly: {hourly:,.2f}   day rate: {day:,.2f}   (quote {quote_hour}/h, {quote_day}/day rounded up)")
    print(f"naive target/2000 = {naive:,.2f}/h; honest rate is {hourly/naive:.2f}x that")
    print("sensitivity (hourly): " + ", ".join(f"{p}% -> {v:,.2f}" for p, v in sens.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
