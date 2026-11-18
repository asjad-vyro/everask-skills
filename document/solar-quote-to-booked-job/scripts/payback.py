#!/usr/bin/env python3
"""25-year savings and payback for a solar quote, with an SVG chart.

Usage:
    python3 payback.py --file payback_in.json [--svg payback.svg] > payback.json

payback_in.json:
{
  "price_inc_tax": 9850,          # from size_system.py totals (the option being quoted)
  "upfront_incentive": 0,         # grants/rebates/tax credits that cut the price (sourced, dated)
  "annual_generation_kwh": 4320,  # from size_system.py
  "annual_use_kwh": 3600,         # caps self-used energy at what the home uses
  "self_use_pct": 40,             # share of generation used in the home
  "import_tariff": 0.2450,        # price per kWh on the bill
  "tariff_rise_pct": 3,           # yearly rise in the import price
  "export_rate": 0.15,            # paid per kWh exported (0 if none)
  "export_rise_pct": 0,
  "degradation_pct": 0.5,         # panel output lost per year
  "incentive_per_kwh": 0, "incentive_years": 0,   # per-kWh schemes (e.g. SRECs)
  "annual_upkeep": 0,             # yearly running cost, if any
  "years": 25,
  "currency": "GBP"
}

Prints JSON: {"net_cost", "payback_years" (null if not within the period),
"total_savings", "net_gain", "rows": [{"year", "generation_kwh", "self_used_kwh",
"exported_kwh", "import_tariff", "export_rate", "savings", "cumulative"}],
"chart_rows" (year, cumulative position; ready for render_chart),
"assumptions_text" (one line to print under the chart)}.
These are estimates from the stated assumptions, not a promise of savings.

Stdlib only. No network.
"""

import json
import sys

DEFAULTS = {"upfront_incentive": 0, "self_use_pct": 40, "tariff_rise_pct": 3,
            "export_rate": 0, "export_rise_pct": 0, "degradation_pct": 0.5,
            "incentive_per_kwh": 0, "incentive_years": 0, "annual_upkeep": 0,
            "years": 25, "currency": ""}
REQUIRED = ("price_inc_tax", "annual_generation_kwh", "import_tariff")


def model(p):
    for key in REQUIRED:
        if p.get(key) in (None, ""):
            raise ValueError(f"Missing '{key}'.")
    q = dict(DEFAULTS, **{k: v for k, v in p.items() if v is not None})
    years = int(q["years"])
    if not 1 <= years <= 40:
        raise ValueError("years must be 1-40.")
    if not 0 <= float(q["self_use_pct"]) <= 100:
        raise ValueError("self_use_pct must be 0-100.")
    net_cost = float(q["price_inc_tax"]) - float(q["upfront_incentive"])
    gen0 = float(q["annual_generation_kwh"])
    use = float(q["annual_use_kwh"]) if q.get("annual_use_kwh") else None
    rows, cumulative, payback = [], -net_cost, None
    for y in range(1, years + 1):
        gen = gen0 * (1 - float(q["degradation_pct"]) / 100) ** (y - 1)
        self_used = gen * float(q["self_use_pct"]) / 100
        if use is not None:
            self_used = min(self_used, use)
        exported = gen - self_used
        tariff = float(q["import_tariff"]) * (1 + float(q["tariff_rise_pct"]) / 100) ** (y - 1)
        export = float(q["export_rate"]) * (1 + float(q["export_rise_pct"]) / 100) ** (y - 1)
        incentive = float(q["incentive_per_kwh"]) * gen if y <= int(q["incentive_years"]) else 0
        savings = self_used * tariff + exported * export + incentive - float(q["annual_upkeep"])
        before = cumulative
        cumulative += savings
        if payback is None and cumulative >= 0 and savings > 0:
            payback = round(y - 1 + (-before / savings), 1) if before < 0 else 0.0
        rows.append({"year": y, "generation_kwh": round(gen), "self_used_kwh": round(self_used),
                     "exported_kwh": round(exported), "import_tariff": round(tariff, 4),
                     "export_rate": round(export, 4), "savings": round(savings, 2),
                     "cumulative": round(cumulative, 2)})
    total = sum(r["savings"] for r in rows)
    cur = q["currency"]
    text = (f"Estimate, not a guarantee. Assumes: import price {q['import_tariff']} {cur}/kWh rising "
            f"{q['tariff_rise_pct']}%/yr; export {q['export_rate']} {cur}/kWh"
            f"{' rising ' + str(q['export_rise_pct']) + '%/yr' if float(q['export_rise_pct']) else ''}; "
            f"{q['self_use_pct']}% of generation used at home; panel output falls "
            f"{q['degradation_pct']}%/yr; upfront incentive {q['upfront_incentive']} {cur}"
            f"{'; ' + str(q['incentive_per_kwh']) + ' ' + cur + '/kWh for ' + str(q['incentive_years']) + ' yrs' if float(q['incentive_per_kwh']) else ''}"
            f"{'; upkeep ' + str(q['annual_upkeep']) + ' ' + cur + '/yr' if float(q['annual_upkeep']) else ''}.")
    return {"net_cost": round(net_cost, 2), "payback_years": payback,
            "total_savings": round(total, 2), "net_gain": round(total - net_cost, 2),
            "years": years, "currency": cur, "rows": rows,
            "chart_rows": [[0, round(-net_cost, 2)]] + [[r["year"], r["cumulative"]] for r in rows],
            "assumptions_text": text}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(result, title="Savings and payback"):
    W, H, L, R, T, B = 800, 500, 90, 45, 60, 120
    pts = result["chart_rows"]
    ys = [v for _, v in pts] + [0]
    lo, hi = min(ys), max(ys)
    if hi == lo:
        hi = lo + 1
    pad = (hi - lo) * 0.08
    lo, hi = lo - pad, hi + pad
    n = pts[-1][0]

    def X(x):
        return L + (W - L - R) * x / n

    def Y(v):
        return T + (H - T - B) * (hi - v) / (hi - lo)

    cur = result["currency"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           'font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<text x="{L}" y="32" font-size="20" font-weight="bold" fill="#1a2440">{_esc(title)}</text>']
    step = 10 ** max(0, len(str(int(hi - lo))) - 1)
    if (hi - lo) / step < 4:
        step /= 2
    v = (lo // step) * step
    while v <= hi:
        if v >= lo:
            out.append(f'<line x1="{L}" x2="{W-R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e3e7ef"/>')
            out.append(f'<text x="{L-8}" y="{Y(v)+4:.1f}" font-size="12" text-anchor="end" '
                       f'fill="#555">{v:,.0f}</text>')
        v += step
    out.append(f'<line x1="{L}" x2="{W-R}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#1a2440" stroke-width="1.5"/>')
    for x in range(0, n + 1, 5):
        out.append(f'<text x="{X(x):.1f}" y="{H-B+20}" font-size="12" text-anchor="middle" fill="#555">{x}</text>')
    out.append(f'<text x="{(L+W-R)/2}" y="{H-B+40}" font-size="13" text-anchor="middle" fill="#333">Year</text>')
    out.append(f'<text x="18" y="{(T+H-B)/2}" font-size="13" text-anchor="middle" fill="#333" '
               f'transform="rotate(-90 18 {(T+H-B)/2})">Cumulative position {_esc(cur)}</text>')
    path = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(v):.1f}" for i, (x, v) in enumerate(pts))
    out.append(f'<path d="{path}" fill="none" stroke="#e8a317" stroke-width="3"/>')
    pb = result["payback_years"]
    if pb is not None:
        out.append(f'<circle cx="{X(pb):.1f}" cy="{Y(0):.1f}" r="6" fill="#1a2440"/>')
        out.append(f'<text x="{X(pb)+10:.1f}" y="{Y(0)-10:.1f}" font-size="13" fill="#1a2440">'
                   f'Estimated payback: about {pb} years</text>')
    # assumptions, wrapped
    words, lines, line = result["assumptions_text"].split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > 110:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    for i, ln in enumerate(lines[:4]):
        out.append(f'<text x="{L}" y="{H-B+68+i*16}" font-size="11" fill="#444">{_esc(ln)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            result = model(json.load(fh))
        if "--svg" in argv:
            path = argv[argv.index("--svg") + 1]
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(svg(result))
            result["svg"] = path
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
