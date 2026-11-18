#!/usr/bin/env python3
"""Size a solar system and price the parts list from the installer's own price list.

Usage:
    python3 size_system.py --job job.json --prices price_list.json > sizing.json

price_list.json: the output of price_list.py ({"items": [...]}).
job.json (only the first two keys are required):
{
  "monthly_kwh": [310, 290, ...],        # from the bills, 1-12 months; or "annual_kwh": 3600
  "kwh_per_kwp_year": 864,               # from pvgis_yield.py (or "peak_sun_hours": 3.0)
  "performance_ratio": 0.8,              # only used with peak_sun_hours
  "offset_pct": 100,                     # share of yearly use to cover, default 100
  "max_panels": 14,                      # roof limit, if known
  "battery": true,                       # customer is interested in a battery
  "battery_target_kwh": 5,               # default: half a day's average use
  "panel_sku": "...", "inverter_sku": "...", "battery_sku": "...",   # installer's choices
  "choices": {"mounting": "<sku>"},      # pick one item where a category has several
  "extra_items": [{"sku": "...", "qty": 1}, {"description": "Bird mesh", "qty": 1}],
  "labour": {"rate": 45, "hours_per_kw": 6, "fixed_hours": 4},   # or a labour row in the list
  "margin_pct": 25, "margin_basis": "margin",   # "margin" (on the selling price) or "markup"
  "tax_pct": 0,
  "deposit": {"type": "percent", "value": 10}   # or {"type": "fixed", "value": 500}
}

Prints JSON: inputs used, "sizing" (annual use, kWp, panels, inverter, generation),
"parts" (base system lines with qty, unit cost, line cost), "battery_options",
"totals" (cost, margin, price ex tax, tax, price inc tax, for "base" and
"with_battery"), "deposit", "flags" (anything not on the price list, assumptions,
limits hit) and "assumptions". Every price comes from price_list.json; a part that is
not on it is flagged and left out of the totals, never priced from memory.

Stdlib only. No network.
"""

import json
import math
import sys

DC_AC_MAX = 1.33  # largest panel kWp per inverter kW accepted when picking an inverter


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def money(x):
    return round(x + 1e-9, 2)


def qty_for(item, panels, kwp):
    unit = item.get("unit", "each")
    if unit == "per_panel":
        return panels
    if unit == "per_kw":
        return round(kwp, 3)
    return 1


def pick(items, sku, key, flags, label):
    """Return the item with this sku, else None (flagged)."""
    if not sku:
        return None
    for it in items:
        if it["sku"].lower() == str(sku).lower() or it["description"].lower() == str(sku).lower():
            return it
    flags.append(f"{label} '{sku}' is not on the price list; chose automatically instead.")
    return None


def size(job, prices):
    items = prices["items"] if isinstance(prices, dict) else prices
    flags, assumptions = [], []
    by_cat = {}
    for it in items:
        by_cat.setdefault(it["category"], []).append(it)

    # Annual use
    if job.get("monthly_kwh"):
        months = [float(x) for x in job["monthly_kwh"] if x is not None]
        if not 1 <= len(months) <= 12:
            raise ValueError("monthly_kwh needs 1 to 12 values.")
        annual = sum(months) * 12 / len(months)
        if len(months) < 12:
            flags.append(f"Yearly use estimated from {len(months)} month(s) of bills "
                         f"(x12/{len(months)}); seasonal swings are not captured.")
    elif job.get("annual_kwh"):
        annual, months = float(job["annual_kwh"]), []
    else:
        raise ValueError("Give monthly_kwh (from the bills) or annual_kwh.")
    if annual <= 0:
        raise ValueError("Yearly use must be above zero.")

    # Yield
    if job.get("kwh_per_kwp_year"):
        yield_kwp = float(job["kwh_per_kwp_year"])
        yield_source = "kwh_per_kwp_year (PVGIS)"
    elif job.get("peak_sun_hours"):
        pr = float(job.get("performance_ratio", 0.8))
        yield_kwp = float(job["peak_sun_hours"]) * 365 * pr
        yield_source = f"peak_sun_hours x 365 x performance ratio {pr}"
        assumptions.append(f"Performance ratio {pr} (losses from heat, cables, inverter, dirt).")
    else:
        raise ValueError("Give kwh_per_kwp_year (from pvgis_yield.py) or peak_sun_hours.")
    if yield_kwp <= 0:
        raise ValueError("Yield must be above zero.")

    offset = float(job.get("offset_pct", 100)) / 100
    target_kwp = annual * offset / yield_kwp

    # Panel
    panels_list = [p for p in by_cat.get("panel", []) if p.get("watts")]
    if not panels_list:
        raise ValueError("The price list has no panel with a wattage.")
    panel = pick(panels_list, job.get("panel_sku"), "watts", flags, "Panel") or \
        min(panels_list, key=lambda p: (p["unit_cost"] / p["watts"], -p["watts"]))
    if not job.get("panel_sku"):
        assumptions.append(f"Panel: {panel['description']} (lowest cost per watt on your list).")
    panel_w = float(panel["watts"])
    panels = max(1, math.ceil(target_kwp * 1000 / panel_w - 1e-9))
    if job.get("max_panels") and panels > int(job["max_panels"]):
        flags.append(f"Roof limit: {panels} panels needed for {offset*100:.0f}% of use, "
                     f"capped at {int(job['max_panels'])}.")
        panels = int(job["max_panels"])
    kwp = panels * panel_w / 1000
    generation = kwp * yield_kwp

    # Inverter
    inverters = [i for i in by_cat.get("inverter", []) if i.get("kw")]
    inverter = pick(inverters, job.get("inverter_sku"), "kw", flags, "Inverter")
    if inverter is None:
        fits = [i for i in inverters if i["kw"] * DC_AC_MAX >= kwp]
        if fits:
            inverter = min(fits, key=lambda i: (i["kw"], i["unit_cost"]))
            assumptions.append(f"Inverter: smallest on your list that fits {kwp:.2f} kWp "
                               f"(panel kWp up to {DC_AC_MAX}x inverter kW).")
        else:
            flags.append(f"No inverter on the price list is large enough for {kwp:.2f} kWp; "
                         "add one or split the array. Inverter left out of the price.")

    parts = [dict(panel, qty=panels)]
    if inverter:
        parts.append(dict(inverter, qty=1))

    # Other categories: one item each (installer's choice, else the only one, else first + flag)
    choices = {k.lower(): v for k, v in (job.get("choices") or {}).items()}
    for cat in ("mounting", "electrical", "other"):
        options = by_cat.get(cat, [])
        if not options:
            if cat == "mounting":
                flags.append("No mounting items on the price list; mounting not priced.")
            continue
        if cat in choices:
            chosen = choices[cat] if isinstance(choices[cat], list) else [choices[cat]]
            for sku in chosen:
                it = pick(options, sku, None, flags, cat.title())
                if it:
                    parts.append(dict(it, qty=qty_for(it, panels, kwp)))
            continue
        if cat == "mounting" and len(options) > 1:
            it = options[0]
            parts.append(dict(it, qty=qty_for(it, panels, kwp)))
            flags.append(f"Several mounting options on the list; used '{it['description']}'. "
                         f"Others: {', '.join(o['description'] for o in options[1:])}.")
        elif cat == "mounting":
            parts.append(dict(options[0], qty=qty_for(options[0], panels, kwp)))
        else:
            for it in options:  # electrical and other rows are usually all needed
                parts.append(dict(it, qty=qty_for(it, panels, kwp)))
            if cat == "other":
                flags.append("Included every 'other' row on the price list: "
                             + ", ".join(o["description"] for o in options) + ". Remove any not needed.")

    for extra in job.get("extra_items") or []:
        key = extra.get("sku") or extra.get("description")
        found = next((it for it in items if key and (it["sku"].lower() == key.lower()
                                                     or it["description"].lower() == key.lower())), None)
        if found:
            parts.append(dict(found, qty=float(extra.get("qty", 1))))
        else:
            flags.append(f"'{key}' is not on the price list: not priced. Add a price before quoting.")

    # Labour
    labour = dict(job.get("labour") or {})
    hourly_rows = [it for it in by_cat.get("labour", []) if it["unit"] == "per_hour"]
    if labour.get("rate") is None and hourly_rows and (labour.get("hours_per_kw") or labour.get("fixed_hours")):
        labour["rate"] = hourly_rows[0]["unit_cost"]
    if labour.get("rate") is not None:
        hours = float(labour.get("fixed_hours", 0)) + float(labour.get("hours_per_kw", 0)) * kwp
        if hours <= 0:
            flags.append("Labour rate given but no hours (hours_per_kw / fixed_hours); labour not priced.")
        else:
            parts.append({"sku": "LABOUR", "category": "labour", "description": "Installation labour",
                          "unit": "per_hour", "unit_cost": float(labour["rate"]), "qty": round(hours, 2)})
    elif by_cat.get("labour"):
        for it in by_cat["labour"]:
            if it["unit"] == "per_hour":
                flags.append(f"Labour row '{it['description']}' is per hour but no hours were given; "
                             "not priced.")
            else:
                parts.append(dict(it, qty=qty_for(it, panels, kwp)))
    else:
        flags.append("No labour rate or labour row: labour not priced.")

    for p in parts:
        p["line_cost"] = money(p["qty"] * p["unit_cost"])

    # Batteries
    batteries = [b for b in by_cat.get("battery", []) if b.get("kwh")]
    target_batt = float(job.get("battery_target_kwh") or round(annual / 365 / 2, 1))
    recommended = pick(batteries, job.get("battery_sku"), "kwh", flags, "Battery")
    if recommended is None and batteries:
        fits = [b for b in batteries if b["kwh"] >= target_batt]
        recommended = min(fits, key=lambda b: (b["kwh"], b["unit_cost"])) if fits else \
            max(batteries, key=lambda b: b["kwh"])
    if job.get("battery") and not batteries:
        flags.append("Customer asked about a battery but the price list has none with a kWh size.")
    if job.get("battery") and not job.get("battery_target_kwh"):
        assumptions.append(f"Battery size target {target_batt} kWh = half an average day's use.")

    # Price
    m = float(job.get("margin_pct", 0)) / 100
    basis = job.get("margin_basis", "margin")
    if basis == "margin" and m >= 1:
        raise ValueError("A margin on the selling price must be under 100%.")
    tax = float(job.get("tax_pct", 0)) / 100

    def sell(cost):
        return cost / (1 - m) if basis == "margin" else cost * (1 + m)

    def totals(cost):
        ex = money(sell(cost))
        t = money(ex * tax)
        return {"cost": money(cost), "margin": money(ex - cost), "price_ex_tax": ex,
                "tax": t, "price_inc_tax": money(ex + t)}

    base_cost = sum(p["line_cost"] for p in parts)
    battery_options = []
    for b in sorted(batteries, key=lambda b: b["kwh"]):
        battery_options.append({"sku": b["sku"], "description": b["description"], "kwh": b["kwh"],
                                "unit_cost": b["unit_cost"],
                                "added_price_inc_tax": money(sell(b["unit_cost"]) * (1 + tax)),
                                "recommended": recommended is not None and b["sku"] == recommended["sku"]})
    result_totals = {"base": totals(base_cost)}
    if recommended:
        result_totals["with_battery"] = dict(totals(base_cost + recommended["unit_cost"]),
                                             battery_sku=recommended["sku"])
    quoted = "with_battery" if (job.get("battery") and recommended) else "base"

    dep = job.get("deposit") or {}
    total = result_totals[quoted]["price_inc_tax"]
    if dep.get("type") == "percent":
        deposit = money(total * float(dep["value"]) / 100)
    elif dep.get("type") == "fixed":
        deposit = money(min(float(dep["value"]), total))
    else:
        deposit = None
        flags.append("No deposit rule given: deposit not calculated.")

    if not job.get("tax_pct"):
        assumptions.append("No tax added (tax_pct 0). Check the rate that applies to this install.")

    return {
        "inputs": {"annual_kwh_basis": "monthly_kwh" if months else "annual_kwh",
                   "months_of_bills": len(months), "yield_source": yield_source,
                   "offset_pct": offset * 100, "margin_pct": m * 100, "margin_basis": basis,
                   "tax_pct": tax * 100, "deposit_rule": dep or None},
        "sizing": {"annual_use_kwh": round(annual, 1), "kwh_per_kwp_year": round(yield_kwp, 1),
                   "target_kwp": round(target_kwp, 3), "panel": panel["description"],
                   "panel_watts": panel_w, "panels": panels, "system_kwp": round(kwp, 3),
                   "inverter": inverter["description"] if inverter else None,
                   "inverter_kw": inverter["kw"] if inverter else None,
                   "dc_ac_ratio": round(kwp / inverter["kw"], 2) if inverter else None,
                   "expected_generation_kwh_year": round(generation, 0),
                   "share_of_use_covered_pct": round(generation / annual * 100, 1),
                   "battery_target_kwh": target_batt},
        "parts": [{k: p.get(k) for k in ("sku", "category", "description", "unit", "qty",
                                          "unit_cost", "line_cost")} for p in parts],
        "battery_options": battery_options,
        "totals": result_totals,
        "quoted_option": quoted,
        "deposit": {"amount": deposit, "of_total": total},
        "flags": flags,
        "assumptions": assumptions,
    }


def main(argv):
    if "--job" not in argv or "--prices" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        job = load(argv[argv.index("--job") + 1])
        prices = load(argv[argv.index("--prices") + 1])
        print(json.dumps(size(job, prices), indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
