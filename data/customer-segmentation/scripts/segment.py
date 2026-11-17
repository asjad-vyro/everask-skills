"""Customer segmentation: RFM scoring or k-means, from an orders CSV or a customer table.
Uses pandas and numpy only. Reads the CSV given on the command line; writes only to --out-dir.

Orders CSV (one row per order):
  python segment.py rfm --csv orders.csv --customer-col customer_id --date-col order_date --amount-col order_total --out-dir out
Customer table (one row per customer, already aggregated):
  python segment.py rfm --csv customers.csv --customer-col id --recency-col days_since_last --frequency-col orders --monetary-col spend --out-dir out
Use `kmeans` instead of `rfm` for clusters; add --k 4 to fix the cluster count.
"""
import argparse, os, sys
import numpy as np
import pandas as pd


def load(a):
    df = pd.read_csv(a.csv)
    for c in [a.customer_col] + [x for x in (a.date_col, a.amount_col, a.recency_col, a.frequency_col, a.monetary_col) if x]:
        if c not in df.columns:
            sys.exit(f"Column '{c}' not found. Columns are: {list(df.columns)}")
    notes = [f"{len(df)} input rows"]
    df = df.dropna(subset=[a.customer_col])
    if a.recency_col:
        cust = df.rename(columns={a.customer_col: "customer", a.recency_col: "recency",
                                  a.frequency_col: "frequency", a.monetary_col: "monetary"})
        cust = cust[["customer", "recency", "frequency", "monetary"]].dropna()
        for c in ("recency", "frequency", "monetary"):
            cust[c] = pd.to_numeric(cust[c], errors="coerce")
        cust = cust.dropna().groupby("customer", as_index=False).first()
        notes.append(f"{len(cust)} customers (customer table used as given)")
        return cust, notes
    df["_d"] = pd.to_datetime(df[a.date_col], errors="coerce")
    df["_a"] = pd.to_numeric(df[a.amount_col], errors="coerce")
    bad = int(df["_d"].isna().sum() + df["_a"].isna().sum())
    df = df.dropna(subset=["_d", "_a"])
    neg = int((df["_a"] <= 0).sum())
    df = df[df["_a"] > 0]
    notes.append(f"dropped {bad} rows with an unreadable date or amount and {neg} rows with an amount of 0 or less (refunds)")
    as_of = pd.to_datetime(a.as_of) if a.as_of else df["_d"].max() + pd.Timedelta(days=1)
    notes.append(f"as-of date {as_of.date()} (recency = days from last order to this date)")
    g = df.groupby(a.customer_col)
    cust = pd.DataFrame({"recency": (as_of - g["_d"].max()).dt.days,
                         "frequency": g[a.customer_col].size(),
                         "monetary": g["_a"].sum()}).reset_index().rename(columns={a.customer_col: "customer"})
    notes.append(f"{len(cust)} customers, {len(df)} orders, date range {df['_d'].min().date()} to {df['_d'].max().date()}")
    return cust, notes


def score(series, high_is_good):
    # Ties share a score (average rank), so one-order customers all get the same F score.
    pct = series.rank(method="average", ascending=high_is_good) / len(series)
    return np.ceil(pct * 5).clip(1, 5).astype(int)


def rfm_name(r, f, m):
    if r >= 4 and f >= 4 and m >= 4: return "Champions"
    if r >= 3 and f >= 4: return "Loyal"
    if r >= 4 and f >= 2: return "Potential Loyalists"
    if r >= 4: return "New Customers"
    if r == 3 and f >= 3: return "Need Attention"
    if r == 3: return "Promising"
    if f >= 3: return "Cant Lose" if (r == 1 and f >= 4 and m >= 4) else "At Risk"
    return "Lost" if (r == 1 and f == 1) else "Hibernating"


def kmeans(X, k, seed=42, iters=100):
    rng = np.random.default_rng(seed)
    c = [X[rng.integers(len(X))]]
    for _ in range(k - 1):
        d = np.min([((X - x) ** 2).sum(1) for x in c], axis=0)
        c.append(X[rng.choice(len(X), p=d / d.sum())] if d.sum() > 0 else X[rng.integers(len(X))])
    c = np.array(c)
    for _ in range(iters):
        lab = np.argmin(((X[:, None, :] - c[None]) ** 2).sum(2), axis=1)
        new = np.array([X[lab == j].mean(0) if (lab == j).any() else c[j] for j in range(k)])
        if np.allclose(new, c): break
        c = new
    return lab


def silhouette(X, lab, seed=42, cap=1500):
    if len(set(lab)) < 2: return float("nan")
    if len(X) > cap:
        idx = np.random.default_rng(seed).choice(len(X), cap, replace=False)
        X, lab = X[idx], lab[idx]
    D = np.sqrt(((X[:, None, :] - X[None]) ** 2).sum(2))
    s = []
    for i in range(len(X)):
        same = lab == lab[i]
        if same.sum() < 2: s.append(0); continue
        a = D[i, same].sum() / (same.sum() - 1)
        b = min(D[i, lab == j].mean() for j in set(lab) if j != lab[i])
        s.append((b - a) / max(a, b))
    return float(np.mean(s))


def table(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join((f"{int(v):,}" if float(v).is_integer() else f"{v:,.2f}") if isinstance(v, (float, int, np.number)) else str(v) for v in r) + " |")
    return "\n".join(out)


def summarise(cust, col):
    tot_m, n = cust["monetary"].sum(), len(cust)
    s = cust.groupby(col).agg(customers=("customer", "size"), avg_recency_days=("recency", "mean"),
                              avg_orders=("frequency", "mean"), avg_spend=("monetary", "mean"),
                              median_spend=("monetary", "median"), total_spend=("monetary", "sum")).reset_index()
    s["pct_customers"] = (s["customers"] / n * 100).round(1)
    s["pct_spend"] = (s["total_spend"] / tot_m * 100).round(1)
    s["spend_index"] = (s["avg_spend"] / cust["monetary"].mean() * 100).round(0)
    return s.sort_values("total_spend", ascending=False).round(2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["rfm", "kmeans"])
    p.add_argument("--csv", required=True)
    p.add_argument("--customer-col", required=True)
    p.add_argument("--date-col"); p.add_argument("--amount-col")
    p.add_argument("--recency-col"); p.add_argument("--frequency-col"); p.add_argument("--monetary-col")
    p.add_argument("--as-of", help="YYYY-MM-DD; default is the day after the last order")
    p.add_argument("--k", type=int, help="k-means cluster count; default picks 3 to 6 by silhouette")
    p.add_argument("--out-dir", default="out")
    a = p.parse_args()
    if not a.recency_col and not (a.date_col and a.amount_col):
        sys.exit("Give --date-col and --amount-col (orders file) or --recency-col, --frequency-col and --monetary-col (customer table).")
    cust, notes = load(a)
    if len(cust) < 10: sys.exit(f"Only {len(cust)} customers: too few to segment.")
    os.makedirs(a.out_dir, exist_ok=True)
    print("DATA\n- " + "\n- ".join(notes))
    if a.mode == "rfm":
        cust["R"] = score(cust["recency"], False); cust["F"] = score(cust["frequency"], True)
        cust["M"] = score(cust["monetary"], True)
        cust["segment"] = [rfm_name(*t) for t in zip(cust.R, cust.F, cust.M)]
        col = "segment"
    else:
        X = np.log1p(cust[["recency", "frequency", "monetary"]].clip(lower=0).to_numpy(float))
        X = (X - X.mean(0)) / np.where(X.std(0) == 0, 1, X.std(0))
        if a.k: ks = [a.k]
        else: ks = list(range(3, min(6, len(cust) // 20) + 1)) or [2]
        res = {k: kmeans(X, k) for k in ks}
        sil = {k: silhouette(X, res[k]) for k in ks}
        print("\nSILHOUETTE BY K (higher is better; above 0.5 is clear structure, 0.25 to 0.5 is weak, below 0.25 is not meaningful)")
        print(", ".join(f"k={k}: {v:.2f}" for k, v in sil.items()))
        k = a.k or max(sil, key=lambda x: (sil[x] if sil[x] == sil[x] else -1))
        print(f"Chosen k = {k}")
        # order clusters by average spend so labels are stable: cluster 1 = highest spend
        cust["cluster"] = res[k]
        order = cust.groupby("cluster")["monetary"].mean().sort_values(ascending=False).index
        cust["cluster"] = cust["cluster"].map({c: i + 1 for i, c in enumerate(order)})
        col = "cluster"
    s = summarise(cust, col)
    cust.to_csv(os.path.join(a.out_dir, "customers_segmented.csv"), index=False)
    s.to_csv(os.path.join(a.out_dir, "segment_summary.csv"), index=False)
    print("\nSEGMENT SUMMARY (sorted by total spend)\n" + table(s))
    print(f"\nOverall: {len(cust)} customers, total spend {cust['monetary'].sum():,.2f}, average {cust['monetary'].mean():,.2f}")
    print("\nSAMPLE CUSTOMER IDS PER SEGMENT")
    for seg, grp in cust.groupby(col):
        ids = sorted(grp["customer"].astype(str))
        print(f"- {seg}: {', '.join(ids[:8])}{' ...' if len(ids) > 8 else ''}")
    print(f"\nFiles written: {a.out_dir}/customers_segmented.csv, {a.out_dir}/segment_summary.csv")


if __name__ == "__main__":
    main()
