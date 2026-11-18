#!/usr/bin/env python3
"""Find winning and fatiguing ads from ad-level weekly results (Meta, TikTok, Google).

Usage:
    python3 ad_report.py --file results.json [--kpi cpp|roas|ctr|hook_rate]
                         [--min-spend 150] [--beat 0.15] [--csv report.csv]

results.json: a JSON list (or a .csv with a header row), one row per ad per week:
    {"platform": "Meta", "ad_id": "...", "ad_name": "...", "campaign": "...",
     "week_start": "2026-11-09", "spend": 412.5, "impressions": 51000,
     "clicks": 640, "video_3s_views": 15200, "purchases": 11,
     "purchase_value": 990.0, "frequency": 1.8}
Common Supermetrics/platform names are accepted too (cost, link_clicks,
video_views_3s, conversions, conversion_value, date, ...). TikTok reports
2-second views (video_watched_2s); they are used as its hook rate. Send three weeks
(last week and the two before) so fatigue can be checked; "last week" is the
newest week in the file. Dates (YYYY-MM-DD) and week labels (2026-W46, 202646)
are bucketed into weeks starting Monday; pull
weekly rows (not daily) so frequency is the real weekly figure.

Prints JSON: {"last_week", "weeks", "kpi", "min_spend", "blended": {...},
"counts": {...}, "ads": [...], "skipped_rows", "warning"}. Each ad: platform, ad_id, ad_name, campaign,
spend, impressions, ctr, hook_rate, cpp, roas, frequency, status, reason,
trend. Status is one of:
    Winner          eligible and beats the blended KPI by at least --beat (15%)
    Fatiguing       CTR or hook rate fell two weeks running while frequency rose
    Winner, fatiguing  both
    Low spend       under --min-spend last week (too little data to judge)
    Steady          everything else
A metric is null when its inputs are missing (e.g. no 3-second views for a
static ad, no frequency from a platform). Fatigue is then "could not check",
never guessed. --min-spend defaults to 2x the blended cost per purchase (or
50 when there were no purchases). --csv also writes the sheet rows.

Stdlib only. Reads a file, writes only the optional CSV.
"""

import csv
import datetime
import json
import re
import sys

ALIASES = {
    "platform": ["platform", "data_source", "source", "network", "channel"],
    "ad_id": ["ad_id", "adid", "ad id", "id", "creative_id"],
    "ad_name": ["ad_name", "ad name", "name", "creative_name"],
    "campaign": ["campaign", "campaign_name", "campaign name"],
    "week_start": ["week_start", "week", "date", "year_week", "date_start"],
    "spend": ["spend", "cost", "amount_spent", "cost_micros_converted"],
    "impressions": ["impressions", "impr"],
    "clicks": ["clicks", "link_clicks", "outbound_clicks", "inline_link_clicks"],
    "video_3s_views": ["video_3s_views", "video_views_3s", "three_second_views",
                       "video_play_actions_3s", "video_watched_2s"],
    "purchases": ["purchases", "conversions", "purchase", "complete_payment"],
    "purchase_value": ["purchase_value", "conversion_value", "conversions_value",
                       "purchase_conversion_value", "revenue", "total_purchase_value"],
    "frequency": ["frequency", "avg_frequency"],
}
SKIPPED = []  # rows with no ad id or no readable week
KPIS = {  # name -> (label, higher is better)
    "cpp": ("cost per purchase", False),
    "roas": ("ROAS", True),
    "ctr": ("CTR", True),
    "hook_rate": ("hook rate", True),
}


def _num(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
    if text in ("", "-", "--", "n/a", "N/A", "null", "None"):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _key(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")


def _pick(row, field):
    lowered = {_key(k): v for k, v in row.items()}
    for alias in ALIASES[field]:
        value = lowered.get(_key(alias))
        if value not in (None, ""):
            return value
    return None


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        if path.lower().endswith(".csv"):
            raw = list(csv.DictReader(fh))
        else:
            raw = json.load(fh)
    if isinstance(raw, dict):
        raw = raw.get("rows") or raw.get("data") or []
    rows = []
    for r in raw:
        row = {f: _pick(r, f) for f in ALIASES}
        for f in ("spend", "impressions", "clicks", "video_3s_views", "purchases",
                  "purchase_value", "frequency"):
            row[f] = _num(row[f])
        row["platform"] = str(row["platform"] or "Unknown").strip()
        row["ad_id"] = str(row["ad_id"] or row["ad_name"] or "").strip()
        row["week_start"] = _monday(row["week_start"])
        if not row["ad_id"] or not row["week_start"]:
            SKIPPED.append({"ad": row["ad_id"], "week": str(_pick(r, "week_start") or "")})
            continue
        rows.append(row)
    return rows


def _monday(value):
    """Bucket a date or ISO week label (2026-W46, 202646) into its Monday; None if unreadable."""
    text = str(value or "").strip()
    try:
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", text) or re.match(r"^(\d{4})(\d{2})(\d{2})$", text)
        if m:
            day = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return (day - datetime.timedelta(days=day.weekday())).isoformat()
        m = re.match(r"^(\d{4})-?W?(\d{2})$", text, re.I)
        if m:
            return datetime.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1).isoformat()
    except ValueError:
        return None
    return None


def _div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def metrics(rows):
    """Sum one ad's rows for one week and derive the ratios."""
    tot = {}
    for f in ("spend", "impressions", "clicks", "video_3s_views", "purchases", "purchase_value"):
        vals = [r[f] for r in rows if r[f] is not None]
        tot[f] = sum(vals) if vals else None
    freqs = [(r["frequency"], r["impressions"] or 0) for r in rows if r["frequency"] is not None]
    if freqs:
        weight = sum(w for _, w in freqs)
        tot["frequency"] = (sum(f * w for f, w in freqs) / weight) if weight else freqs[0][0]
    else:
        tot["frequency"] = None
    tot["ctr"] = _div(tot["clicks"], tot["impressions"])
    video_impr = [r["impressions"] for r in rows
                  if r["video_3s_views"] is not None and r["impressions"] is not None]
    tot["hook_rate"] = _div(tot["video_3s_views"], sum(video_impr) if video_impr else None)
    tot["cpp"] = _div(tot["spend"], tot["purchases"]) if tot["purchases"] else None
    tot["roas"] = _div(tot["purchase_value"], tot["spend"])
    return tot


def _falling_twice(series):
    """series = [w-2, w-1, w0]; True/False, or None if a value is missing."""
    if len(series) < 3 or any(v is None for v in series):
        return None
    return series[2] < series[1] < series[0]


def _rising_twice(series):
    if len(series) < 3 or any(v is None for v in series):
        return None
    return series[2] > series[1] > series[0]


def _pct(v):
    return None if v is None else round(v * 100, 2)


def _round(v, n=2):
    return None if v is None else round(v, n)


def build(rows, kpi, min_spend, beat):
    weeks = sorted({r["week_start"] for r in rows})
    if not weeks:
        return {"error": "No usable rows (each row needs an ad id or name and a week)."}
    last = weeks[-1]
    trend_weeks = weeks[-3:]
    by_ad = {}
    for r in rows:
        by_ad.setdefault((r["platform"], r["ad_id"]), []).append(r)

    seen, daily = set(), False
    for r in rows:
        key = (r["platform"], r["ad_id"], r["week_start"])
        daily = daily or key in seen
        seen.add(key)
    last_rows = [r for r in rows if r["week_start"] == last]
    blended = metrics(last_rows)
    label, higher = KPIS[kpi]
    if min_spend is None:
        min_spend = 2 * blended["cpp"] if blended["cpp"] else 50.0
    target = blended[kpi]

    ads = []
    for (platform, ad_id), ad_rows in by_ad.items():
        now_rows = [r for r in ad_rows if r["week_start"] == last]
        if not now_rows:
            continue  # not running last week
        m = metrics(now_rows)
        series = {w: metrics([r for r in ad_rows if r["week_start"] == w]) for w in trend_weeks}
        trend = {
            "weeks": trend_weeks,
            "ctr_pct": [_pct(series[w]["ctr"]) for w in trend_weeks],
            "hook_rate_pct": [_pct(series[w]["hook_rate"]) for w in trend_weeks],
            "frequency": [_round(series[w]["frequency"]) for w in trend_weeks],
        }
        ctr_fall = _falling_twice([series[w]["ctr"] for w in trend_weeks])
        hook_fall = _falling_twice([series[w]["hook_rate"] for w in trend_weeks])
        freq_rise = _rising_twice([series[w]["frequency"] for w in trend_weeks])

        reasons = []
        spend = m["spend"] or 0.0
        eligible = spend >= min_spend and (kpi not in ("cpp", "roas") or (m["purchases"] or 0) > 0)
        value = m[kpi]
        winner = False
        if eligible and value is not None and target:
            ratio = (value / target - 1) if higher else (1 - value / target)
            winner = ratio >= beat
            if winner:
                reasons.append(f"{label} {_fmt(kpi, value)} vs {_fmt(kpi, target)} blended "
                               f"({round(ratio * 100)}% better) on {spend:,.0f} spend")

        fatigue = None
        ran_weeks = [w for w in trend_weeks if any(r["week_start"] == w for r in ad_rows)]
        if len(trend_weeks) < 3:
            fatigue_note = "fatigue could not check (fewer than 3 weeks of data)"
        elif len(ran_weeks) < 3:
            fatigue_note = "fatigue could not check (ran fewer than 3 weeks)"
        elif freq_rise is None:
            fatigue_note = "fatigue could not check (no frequency for every week)"
        elif ctr_fall is None and hook_fall is None:
            fatigue_note = "fatigue could not check (CTR and hook rate missing)"
        else:
            fatigue = bool(freq_rise and (ctr_fall or hook_fall))
            fatigue_note = None
        if fatigue:
            parts = []
            if ctr_fall:
                parts.append("CTR " + " > ".join(f"{v}%" for v in trend["ctr_pct"]))
            if hook_fall:
                parts.append("hook rate " + " > ".join(f"{v}%" for v in trend["hook_rate_pct"]))
            parts.append("frequency " + " > ".join(str(v) for v in trend["frequency"]))
            reasons.append("; ".join(parts))

        if winner and fatigue:
            status = "Winner, fatiguing"
        elif winner:
            status = "Winner"
        elif fatigue:
            status = "Fatiguing"
        elif spend < min_spend:
            status = "Low spend"
            reasons.append(f"only {spend:,.0f} spend last week (threshold {min_spend:,.0f})")
        else:
            status = "Steady"
            if value is None:
                reasons.append(f"no {label} last week")
            else:
                reasons.append(f"{label} {_fmt(kpi, value)} vs {_fmt(kpi, target)} blended")
        if fatigue_note:
            reasons.append(fatigue_note)

        first = now_rows[0]
        ads.append({
            "platform": platform, "ad_id": ad_id, "ad_name": first["ad_name"] or "",
            "campaign": first["campaign"] or "",
            "spend": _round(m["spend"]), "impressions": _round(m["impressions"], 0),
            "ctr_pct": _pct(m["ctr"]), "hook_rate_pct": _pct(m["hook_rate"]),
            "cpp": _round(m["cpp"]), "roas": _round(m["roas"]),
            "frequency": _round(m["frequency"]), "purchases": _round(m["purchases"], 1),
            "status": status, "reason": "; ".join(reasons), "trend": trend,
        })

    order = {"Winner": 0, "Winner, fatiguing": 1, "Fatiguing": 2, "Steady": 3, "Low spend": 4}
    ads.sort(key=lambda a: (order[a["status"]], -(a["spend"] or 0)))
    counts = {}
    for a in ads:
        counts[a["status"]] = counts.get(a["status"], 0) + 1
    return {
        "last_week": last, "weeks": weeks, "kpi": kpi, "kpi_label": label,
        "min_spend": round(min_spend, 2), "beat_pct": round(beat * 100),
        "blended": {"spend": _round(blended["spend"]), "ctr_pct": _pct(blended["ctr"]),
                    "hook_rate_pct": _pct(blended["hook_rate"]), "cpp": _round(blended["cpp"]),
                    "roas": _round(blended["roas"]), "purchases": _round(blended["purchases"], 1)},
        "counts": counts, "ads": ads,
        "skipped_rows": SKIPPED,
        "warning": ("Several rows per ad per week (daily data?): totals are summed, but "
                    "frequency is an impression-weighted average of the rows, not true "
                    "weekly frequency. Pull weekly rows for exact frequency.") if daily else "",
    }


def _fmt(kpi, v):
    if kpi in ("ctr", "hook_rate"):
        return f"{v * 100:.2f}%"
    if kpi == "roas":
        return f"{v:.2f}x"
    return f"{v:,.2f}"


SHEET_COLUMNS = ["Platform", "Ad", "Ad ID", "Campaign", "Hook", "Angle", "Spend", "Impressions",
                 "CTR %", "Hook rate %", "Cost per purchase", "ROAS", "Frequency",
                 "Status", "Why"]


def write_csv(path, report):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SHEET_COLUMNS)
        for a in report["ads"]:
            w.writerow([a["platform"], a["ad_name"], a["ad_id"], a["campaign"], "", "",
                        a["spend"], a["impressions"], a["ctr_pct"], a["hook_rate_pct"],
                        a["cpp"], a["roas"], a["frequency"], a["status"], a["reason"]])


def main(argv):
    args = {"--kpi": "cpp", "--min-spend": None, "--beat": "0.15", "--csv": None, "--file": None}
    i = 0
    while i < len(argv):
        if argv[i] in args and i + 1 < len(argv):
            args[argv[i]] = argv[i + 1]
            i += 2
        else:
            print(f"Unknown or incomplete argument: {argv[i]}\n\n{__doc__}", file=sys.stderr)
            return 2
    if not args["--file"]:
        print(__doc__, file=sys.stderr)
        return 2
    kpi = args["--kpi"].lower().replace("-", "_")
    kpi = {"cost_per_purchase": "cpp", "cpa": "cpp", "hook": "hook_rate"}.get(kpi, kpi)
    if kpi not in KPIS:
        print(json.dumps({"error": f"Unknown KPI {args['--kpi']}; use cpp, roas, ctr or hook_rate"}))
        return 1
    try:
        rows = load(args["--file"])
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read {args['--file']}: {exc}"}))
        return 1
    min_spend = _num(args["--min-spend"]) if args["--min-spend"] else None
    report = build(rows, kpi, min_spend, float(args["--beat"]))
    if "error" not in report and args["--csv"]:
        write_csv(args["--csv"], report)
        report["csv"] = args["--csv"]
    print(json.dumps(report, indent=2))
    return 1 if "error" in report else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
