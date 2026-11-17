"""Trend, seasonality, anomaly and forecast for one metric over time. Standard library only.

Usage:
  python ts_forecast.py --csv data.csv --date-col date --value-col sales --horizon 6 [--freq M] [--season 12] [--out-dir DIR]
Prints one JSON report. Writes DIR/forecast.csv and DIR/decomposition.csv (DIR defaults to the current folder).
"""
import argparse, csv, json, math, os, statistics as st
from datetime import date, datetime, timedelta

FMTS = ["%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%b %Y", "%B %Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d-%b-%Y", "%Y"]
Z95 = 1.96


def parse_date(s):
    s = s.strip()
    for f in FMTS:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise SystemExit(f"Cannot parse date: {s!r}")


def num(s):
    s = (s or "").strip().replace(",", "").replace("$", "").replace("%", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def infer_freq(dates):
    gaps = [(b - a).days for a, b in zip(dates, dates[1:]) if b > a]
    g = st.median(gaps)
    if g <= 1.5: return "D"
    if 5 <= g <= 9: return "W"
    if 25 <= g <= 35: return "M"
    if 80 <= g <= 100: return "Q"
    raise SystemExit(f"Cannot infer frequency (median gap {g} days). Pass --freq D, W, M or Q.")


def key(d, freq, d0):
    if freq == "D": return (d - d0).days
    if freq == "W": return (d - d0).days // 7
    if freq == "M": return d.year * 12 + d.month - 1
    return d.year * 4 + (d.month - 1) // 3


def label(k, freq, d0):
    if freq == "D": return d0 + timedelta(days=k)
    if freq == "W": return d0 + timedelta(days=7 * k)
    if freq == "M": return date(k // 12, k % 12 + 1, 1)
    return date(k // 4, (k % 4) * 3 + 1, 1)


def ols(y):
    n = len(y); xm = (n - 1) / 2; ym = sum(y) / n
    sxx = sum((i - xm) ** 2 for i in range(n))
    b = sum((i - xm) * (v - ym) for i, v in enumerate(y)) / sxx if sxx else 0.0
    return ym - b * xm, b, xm, sxx


def seasonal_index(y, m):
    """Additive seasonal index (sums to 0). Alternates a linear trend fit and per-position medians, using every cycle."""
    n = len(y)
    s = [0.0] * m
    for _ in range(6):
        a, b, _, _ = ols([v - s[i % m] for i, v in enumerate(y)])
        buckets = [[] for _ in range(m)]
        for i in range(n):
            buckets[i % m].append(y[i] - (a + b * i))
        s = [st.median(bk) for bk in buckets]
        c = sum(s) / m
        s = [v - c for v in s]
    return s, None


def fit_ls(y, m):
    """Linear trend + seasonal index. Returns predict(t), fitted list, resid sd, params."""
    s = [0.0] * (m or 1)
    if m:
        s, _ = seasonal_index(y, m)
    ds = [v - (s[i % m] if m else 0) for i, v in enumerate(y)]
    a, b, xm, sxx = ols(ds)
    n = len(y)
    fitted = [a + b * i + (s[i % m] if m else 0) for i in range(n)]
    res = [v - f for v, f in zip(y, fitted)]
    sd = math.sqrt(sum(r * r for r in res) / max(1, n - 2 - (m - 1 if m else 0)))

    def pred(t):
        h = t - n + 1
        w = Z95 * sd * math.sqrt(1 + 1 / n + (t - xm) ** 2 / sxx) if sxx else Z95 * sd
        return a + b * t + (s[t % m] if m else 0), w
    return pred, fitted, res, sd, (a, b, s)


def fit_naive(y, m):
    n = len(y)
    per = m or 1
    diffs = [y[i] - y[i - per] for i in range(per, n)]
    sd = st.pstdev(diffs) if len(diffs) > 1 else 0.0

    def pred(t):
        back = t - per * (((t - n) // per) + 1)
        return y[back], Z95 * sd * math.sqrt(((t - n) // per) + 1)
    return pred


def metrics(actual, fc):
    ae = [abs(a - f) for a, f in zip(actual, fc)]
    pe = [abs(a - f) / abs(a) for a, f in zip(actual, fc) if a != 0]
    return {"mae": round(sum(ae) / len(ae), 4), "mape_pct": round(100 * sum(pe) / len(pe), 2) if pe else None}


def r(x, k=4):
    return None if x is None else round(x, k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--date-col", required=True)
    ap.add_argument("--value-col", required=True)
    ap.add_argument("--horizon", type=int, default=6)
    ap.add_argument("--freq", choices=["D", "W", "M", "Q"])
    ap.add_argument("--season", type=int, help="season length in periods; 0 = none")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()

    raw = {}
    skipped = 0
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            v = num(row.get(a.value_col))
            if v is None or not (row.get(a.date_col) or "").strip():
                skipped += 1
                continue
            d = parse_date(row[a.date_col])
            raw.setdefault(d, []).append(v)
    dates = sorted(raw)
    if len(dates) < 8:
        raise SystemExit("Need at least 8 data points.")
    freq = a.freq or infer_freq(dates)
    d0 = dates[0]
    agg = {}
    dup = 0
    for d in dates:
        k = key(d, freq, d0)
        agg.setdefault(k, []).extend(raw[d])
    dup = sum(len(v) - 1 for v in agg.values())
    ks = sorted(agg)
    k0, k1 = ks[0], ks[-1]
    y, filled = [], []
    for k in range(k0, k1 + 1):
        if k in agg:
            y.append(sum(agg[k])); filled.append(False)
        else:
            y.append(None); filled.append(True)
    for i, v in enumerate(y):  # linear interpolation of gaps
        if v is None:
            lo = max(j for j in range(i) if y[j] is not None)
            hi = min(j for j in range(i + 1, len(y)) if y[j] is not None)
            y[i] = y[lo] + (y[hi] - y[lo]) * (i - lo) / (hi - lo)
    n = len(y)
    labels = [label(k0 + i, freq, d0) for i in range(n)]

    default_m = {"D": 7, "W": 52, "M": 12, "Q": 4}[freq]
    m = default_m if a.season is None else a.season
    notes = []
    if m and n < 2 * m:
        notes.append(f"Only {n} periods for a season of {m}: fewer than 2 full cycles, so seasonality is not estimated.")
        m = 0
    if m == 1: m = 0

    # Decomposition and anomalies
    # Pass 1 finds outliers; they are replaced by their fitted value so they do not bend the trend or seasonal index.
    _, f1, r1, _, _ = fit_ls(y, m)
    med1 = st.median(r1)
    mad1 = st.median([abs(e - med1) for e in r1]) or 1e-9
    y_all = y
    y = [f1[i] if abs(0.6745 * (r1[i] - med1) / mad1) > 3.5 else y_all[i] for i in range(n)]
    pred, fitted, res, sd, (ia, ib, sidx) = fit_ls(y, m)
    res_all = [y_all[i] - fitted[i] for i in range(n)]
    ds_var = st.pvariance([v - (sidx[i % m] if m else 0) for i, v in enumerate(y)])
    trend_part = [ia + ib * i for i in range(n)]
    seas_part = [sidx[i % m] if m else 0.0 for i in range(n)]
    var_r = st.pvariance(res)
    var_tr = st.pvariance([t + e for t, e in zip(trend_part, res)])
    var_se = st.pvariance([s_ + e for s_, e in zip(seas_part, res)]) if m else 0
    trend_strength = max(0.0, 1 - var_r / var_tr) if var_tr else 0.0
    seas_strength = max(0.0, 1 - var_r / var_se) if m and var_se else 0.0
    med = st.median(res)
    mad = st.median([abs(e - med) for e in res]) or 1e-9
    anomalies = []
    for i, e in enumerate(res_all):
        mz = 0.6745 * (e - med) / mad
        if abs(mz) > 3.5 and not filled[i]:
            anomalies.append({"period": labels[i].isoformat(), "actual": r(y_all[i], 2), "expected": r(fitted[i], 2),
                              "gap": r(y_all[i] - fitted[i], 2), "gap_pct": r(100 * (y_all[i] - fitted[i]) / fitted[i], 1) if fitted[i] else None,
                              "robust_z": r(mz, 1), "kind": "spike" if mz > 0 else "dip", "interpolated_gap_fill": filled[i]})
    anomalies.sort(key=lambda x: -abs(x["robust_z"]))

    # Backtest: hold out the last periods, compare two methods
    hb = max(1, min(a.horizon, n // 4))
    per = m or 1
    if m and n - hb < 2 * m:
        hb = n - 2 * m
    backtest = None
    chosen = "linear_trend_plus_seasonal"
    if hb >= 2 and n - hb >= 8:
        tr, te = y[:-hb], y[-hb:]
        p_ls = fit_ls(tr, m)[0]
        p_nv = fit_naive(tr, m)
        ls = metrics(te, [p_ls(len(tr) + i)[0] for i in range(hb)])
        nv = metrics(te, [p_nv(len(tr) + i)[0] for i in range(hb)])
        backtest = {"holdout_periods": hb, "linear_trend_plus_seasonal": ls, "seasonal_naive" if m else "last_value": nv}
        if nv["mae"] < ls["mae"]:
            chosen = "seasonal_naive" if m else "last_value"
    if backtest is None:
        notes.append("Series too short for a hold-out test; forecast uses linear trend plus seasonal index without a back-test.")

    pf = pred if chosen == "linear_trend_plus_seasonal" else fit_naive(y, m)
    rows = []
    for h in range(1, a.horizon + 1):
        t = n - 1 + h
        p, w = pf(t)
        rows.append({"period": label(k0 + t, freq, d0).isoformat(), "forecast": r(p, 2), "lower_95": r(p - w, 2), "upper_95": r(p + w, 2)})

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "forecast.csv"), "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=["period", "forecast", "lower_95", "upper_95"]); w_.writeheader(); w_.writerows(rows)
    with open(os.path.join(a.out_dir, "decomposition.csv"), "w", newline="") as f:
        w_ = csv.writer(f); w_.writerow(["period", "actual", "trend", "seasonal", "residual", "gap_filled"])
        for i in range(n):
            w_.writerow([labels[i].isoformat(), r(y_all[i], 2), r(trend_part[i], 2), r(seas_part[i], 2), r(res_all[i], 2), filled[i]])

    season_out = None
    if m:
        names = None
        if freq == "M":
            mons = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            names = [mons[(labels[0].month - 1 + i) % 12] for i in range(m)]
        elif freq == "D" and m == 7:
            dn = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            names = [dn[(labels[0].weekday() + i) % 7] for i in range(m)]
        season_out = [{"position": names[i] if names else i + 1, "effect_vs_trend": r(sidx[i], 2)} for i in range(m)]

    mean_y = sum(y) / n
    out = {
        "data": {"periods": n, "first": labels[0].isoformat(), "last": labels[-1].isoformat(), "frequency": freq, "season_length": m or None,
                 "rows_skipped_blank_or_non_numeric": skipped, "duplicate_rows_summed": dup, "gaps_interpolated": sum(filled),
                 "mean": r(mean_y, 2), "min": r(min(y), 2), "max": r(max(y), 2), "last_value": r(y[-1], 2)},
        "trend": {"slope_per_period": r(ib, 3), "slope_pct_of_mean_per_period": r(100 * ib / mean_y, 2) if mean_y else None,
                  "direction": "up" if ib > 0 else "down" if ib < 0 else "flat", "strength_0_to_1": r(trend_strength, 2)},
        "seasonality": {"strength_0_to_1": r(seas_strength, 2), "index_additive": season_out},
        "anomalies_robust_z_gt_3.5": anomalies,
        "backtest": backtest, "method_used": chosen,
        "residual_sd": r(sd, 2),
        "forecast": rows, "notes": notes,
        "files": {"forecast": os.path.join(a.out_dir, "forecast.csv"), "decomposition": os.path.join(a.out_dir, "decomposition.csv")},
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
