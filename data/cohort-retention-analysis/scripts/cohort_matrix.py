"""Build a cohort retention matrix from a CSV of user activity.

Input CSV needs a user id, a cohort date (e.g. signup date) and an activity date.
One row per activity is fine; duplicates are collapsed to one signal per user per period.
Optionally pass a separate users CSV so cohort size counts users with no activity at all.

Usage:
  python cohort_matrix.py --input events.csv --user-col user_id --cohort-col signup_date \
      --activity-col activity_date --granularity monthly --out-prefix /tmp/.scratch/cohort-retention-analysis/out
  Optional: --users users.csv  --segment-col channel  --min-size 30  --as-of 2024-06-30
"""
import argparse
import sys

import pandas as pd


def period_index(s, gran):
    if gran == "monthly":
        return s.dt.year * 12 + s.dt.month
    if gran == "weekly":
        return (s.dt.normalize() - pd.Timestamp("1970-01-05")).dt.days // 7  # Monday-based weeks
    return (s.dt.normalize() - pd.Timestamp("1970-01-01")).dt.days


def label(idx, gran):
    if gran == "monthly":
        return f"{(idx - 1) // 12}-{(idx - 1) % 12 + 1:02d}"
    if gran == "weekly":
        return (pd.Timestamp("1970-01-05") + pd.Timedelta(days=int(idx) * 7)).strftime("%Y-%m-%d")
    return (pd.Timestamp("1970-01-01") + pd.Timedelta(days=int(idx))).strftime("%Y-%m-%d")


def build(users, act, gran, as_of):
    users = users.copy()
    users["cp"] = period_index(users["cohort"], gran)
    act = act.merge(users[["user", "cp"]], on="user", how="inner")
    act["ap"] = period_index(act["activity"], gran)
    act["n"] = act["ap"] - act["cp"]
    before = int((act["n"] < 0).sum())
    act = act[act["n"] >= 0]
    last = int(period_index(pd.Series([as_of]), gran).iloc[0])
    sizes = users.groupby("cp")["user"].nunique().rename("size")
    ret = act.groupby(["cp", "n"])["user"].nunique().unstack(fill_value=0)
    max_n = max(int(ret.columns.max()) if len(ret.columns) else 0, int((last - sizes.index).max()))
    ret = ret.reindex(index=sizes.index, columns=range(0, max_n + 1), fill_value=0)
    counts = ret.astype(float)
    for cp in counts.index:  # periods not yet observable are blank, not zero
        for n in counts.columns:
            if cp + n > last:
                counts.loc[cp, n] = float("nan")
    pct = counts.div(sizes, axis=0) * 100
    return sizes, counts, pct, before


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--users", help="optional users CSV (one row per user) holding the cohort column")
    p.add_argument("--user-col", default="user_id")
    p.add_argument("--cohort-col", default="signup_date")
    p.add_argument("--activity-col", default="activity_date")
    p.add_argument("--segment-col")
    p.add_argument("--granularity", choices=["daily", "weekly", "monthly"], default="monthly")
    p.add_argument("--min-size", type=int, default=0)
    p.add_argument("--as-of", help="last date with complete data (default: latest activity date)")
    p.add_argument("--out-prefix", default="cohort")
    a = p.parse_args()

    ev = pd.read_csv(a.input)
    for c in (a.user_col, a.activity_col):
        if c not in ev.columns:
            sys.exit(f"Column {c!r} not found. Columns: {list(ev.columns)}")
    src = pd.read_csv(a.users) if a.users else ev
    if a.cohort_col not in src.columns:
        sys.exit(f"Column {a.cohort_col!r} not found. Columns: {list(src.columns)}")
    cols = {a.user_col: "user", a.cohort_col: "cohort"}
    if a.segment_col:
        cols[a.segment_col] = "segment"
    users = src[list(cols)].rename(columns=cols)
    users["cohort"] = pd.to_datetime(users["cohort"], errors="coerce")
    bad = int(users["cohort"].isna().sum())
    users = users.dropna(subset=["cohort"]).sort_values("cohort").drop_duplicates("user")
    act = ev[[a.user_col, a.activity_col]].rename(columns={a.user_col: "user", a.activity_col: "activity"})
    act["activity"] = pd.to_datetime(act["activity"], errors="coerce")
    act = act.dropna()
    as_of = pd.Timestamp(a.as_of) if a.as_of else act["activity"].max()

    def run(u, tag):
        sizes, counts, pct, before = build(u, act, a.granularity, as_of)
        sizes.index = [label(i, a.granularity) for i in sizes.index]
        pct.index = counts.index = sizes.index
        pct.columns = counts.columns = [f"P{c}" for c in pct.columns]
        out = pct.round(1)
        out.insert(0, "size", sizes)
        small = out["size"] < a.min_size
        print(f"\n=== Retention % {tag}(bounded: active in exactly that period; blank = not yet observable) ===")
        print(out.to_string(na_rep=""))
        if small.any():
            print(f"Cohorts below min size {a.min_size}: {list(out.index[small])}")
        # size-weighted average per period over cohorts that have reached it, min-size cohorts excluded
        keep = ~small
        w = {}
        for c in counts.columns:
            ok = keep & counts[c].notna()
            w[c] = round(float(counts.loc[ok, c].sum() / sizes[ok].sum() * 100), 1) if ok.any() else None
        print("Weighted average by period:", w)
        return out, counts, before

    out, counts, before = run(users, "")
    out.to_csv(f"{a.out_prefix}_retention_pct.csv")
    counts.to_csv(f"{a.out_prefix}_retained_users.csv")
    print(f"\nUsers in scope: {users['user'].nunique()}; unparseable cohort dates dropped: {bad}; "
          f"activity rows before the cohort period ignored: {before}; data complete through: {as_of.date()}")
    if a.segment_col:
        for seg, u in users.groupby("segment"):
            o, c, _ = run(u, f"[{a.segment_col}={seg}] ")
            o.to_csv(f"{a.out_prefix}_retention_pct_{str(seg).replace('/', '_')}.csv")
    print(f"Saved CSVs with prefix {a.out_prefix}")


if __name__ == "__main__":
    main()
