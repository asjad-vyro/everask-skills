#!/usr/bin/env python3
"""Work out the numbers for a CFO memo on allowances: inflation uplift and FX conversion.

Usage:
    python3 allowance_review.py --file memo_inputs.json

memo_inputs.json:
    {
      "allowances": [{"name": "Daily meals, UK", "amount": 40, "currency": "GBP"}, ...],
      "cpi": {"start": {"value": 133.9, "period": "2025-09"},
              "end":   {"value": 138.4, "period": "2026-09"},
              "series": "CPIH index (ONS D7BT)", "source": "<URL>", "retrieved": "2026-11-03"},
      "fx": [{"from": "GBP", "to": "USD", "rate": 1.3342, "date": "2026-10-31",
              "source": "<URL>"}, ...]
    }
Every CPI and FX figure must come from an official source read in this run (national
statistics office, central bank); "source" and the dates are required and are copied
next to each number so the memo can cite them.

Prints JSON: {"inflation": {"rate_pct", "from", "to", "series", "source", "retrieved"},
"allowances": [{"name", "currency", "amount", "uplifted", "change", "converted": [
{"currency", "amount", "uplifted", "rate", "rate_date", "source"}]}], "errors": [...]}.
Uplifted = amount x end CPI / start CPI, rounded to 2 places. A rate given as
from->to also converts to->from (1/rate); two rates against one currency (e.g. the
ECB's EUR->GBP and EUR->USD) give the cross rate GBP->USD. Stdlib only, no network.
"""

import json
import sys


def fail(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError, IndexError) as exc:
        fail(f"cannot read the inputs file: {exc}")
    errors = []
    cpi = data.get("cpi") or {}
    start, end = (cpi.get("start") or {}), (cpi.get("end") or {})
    inflation, factor = None, None
    try:
        s, e = float(start["value"]), float(end["value"])
        if s <= 0:
            raise ValueError("start CPI must be above 0")
        if not cpi.get("source"):
            raise ValueError("CPI source URL missing")
        factor = e / s
        inflation = {"rate_pct": round((factor - 1) * 100, 2), "from": start.get("period"),
                     "to": end.get("period"), "series": cpi.get("series", ""), "source": cpi["source"],
                     "retrieved": cpi.get("retrieved", "")}
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"no inflation figure: {exc}")

    rates = {}
    for fx in data.get("fx") or []:
        try:
            a, b, r = fx["from"].upper(), fx["to"].upper(), float(fx["rate"])
            if r <= 0 or not fx.get("source") or not fx.get("date"):
                raise ValueError("rate, date and source are required")
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            errors.append(f"FX rate {fx} left out: {exc}")
            continue
        meta = {"rate_date": fx["date"], "source": fx["source"]}
        rates.setdefault(a, {})[b] = (r, meta)
        rates.setdefault(b, {}).setdefault(a, (1 / r, meta))

    for via in list(rates):  # cross rates through a shared currency, e.g. GBP->USD via EUR
        for a, (ra, ma) in list(rates[via].items()):
            for b, (rb, mb) in list(rates[via].items()):
                if a != b and b not in rates.get(a, {}):
                    meta = {"rate_date": ma["rate_date"], "source": "cross rate via %s: %s" % (via, ma["source"])
                            + ("" if mb["source"] == ma["source"] else "; " + mb["source"])}
                    rates.setdefault(a, {})[b] = (rb / ra, meta)

    out = []
    for item in data.get("allowances") or []:
        try:
            amount, cur = float(item["amount"]), str(item["currency"]).upper()
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"allowance {item} left out: {exc}")
            continue
        uplifted = round(amount * factor, 2) if factor else None
        row = {"name": item.get("name", ""), "currency": cur, "amount": round(amount, 2), "uplifted": uplifted,
               "change": round(uplifted - amount, 2) if uplifted is not None else None, "converted": []}
        for target, (rate, meta) in sorted(rates.get(cur, {}).items()):
            row["converted"].append({"currency": target, "amount": round(amount * rate, 2),
                                     "uplifted": round(uplifted * rate, 2) if uplifted is not None else None,
                                     "rate": round(rate, 6), **meta})
        out.append(row)
    print(json.dumps({"inflation": inflation, "allowances": out, "errors": errors}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
