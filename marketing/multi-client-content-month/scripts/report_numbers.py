#!/usr/bin/env python3
"""Turn one client's Supermetrics numbers into the exact figures for the monthly report.

Usage:
    python3 report_numbers.py --file metrics.json

metrics.json (copy the numbers from Supermetrics results as they are):
{
  "client": "Bloom Bakery",
  "month": "2026-11",
  "channels": [
    {"channel": "instagram",
     "this": {"reach": 18234, "impressions": 40211, "engagements": 1532,
              "followers_start": 5120, "followers_end": 5301},
     "last": {"reach": 16010, "impressions": 35870, "engagements": 1490,
              "followers_start": 5002, "followers_end": 5120}}
  ],
  "posts": [{"channel": "instagram", "date": "2026-11-04", "link": "https://...",
             "caption": "...", "reach": 4100, "engagements": 388}]
}
Any metric may be missing or null: it is reported as "not tracked", never guessed.
Numbers may be written with thousands separators ("18,234").

Prints JSON {"client", "month", "channels": [...], "totals": {...}, "top_posts": [...],
"notes": [...]}. Per channel and metric: value, last month, change and change_pct.
engagement_rate = engagements / reach x 100. follower_growth = followers_end -
followers_start. Percentages are cut (not rounded) to one decimal place, so a
figure is never shown higher than it is. Reach is not added up across channels
(the same person can be reached on two). Stdlib only, no network.
"""

import json
import math
import sys

METRICS = ("reach", "impressions", "engagements", "followers_end", "follower_growth",
           "engagement_rate")
NT = "not tracked"


class DataError(Exception):
    pass


def num(value, where):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise DataError(f"{where}: '{value}' is not a number")
    if isinstance(value, (int, float)):
        if math.isnan(value):
            return None
        return value
    text = str(value).strip().replace(",", "").replace(" ", "")
    if text.lower() in ("", "-", "n/a", "na", "null", "none"):
        return None
    try:
        f = float(text)
    except ValueError:
        raise DataError(f"{where}: '{value}' is not a number")
    return int(f) if f.is_integer() else f


def cut(x, places):
    """Truncate toward zero; never shows a figure higher than it is."""
    factor = 10 ** places
    return math.trunc(round(x * factor, 6)) / factor  # round(…, 6) drops float noise like 28.999999


def derived(block, where):
    block = block or {}
    vals = {k: num(block.get(k), f"{where}.{k}") for k in
            ("reach", "impressions", "engagements", "followers_start", "followers_end")}
    s, e = vals["followers_start"], vals["followers_end"]
    vals["follower_growth"] = (e - s) if s is not None and e is not None else None
    r, g = vals["reach"], vals["engagements"]
    vals["engagement_rate"] = cut(g / r * 100, 2) if r and g is not None else None
    return vals


def compare(now, before, metric):
    out = {"value": NT if now is None else now, "last_month": NT if before is None else before}
    if now is None or before is None:
        out["change"], out["change_pct"] = NT, NT
        return out
    change = now - before
    if metric == "engagement_rate":
        change = cut(change, 2)
        out["change"] = change
        out["change_pct"] = "n/a (already a rate; change is in points)"
        return out
    out["change"] = change
    if before == 0:
        out["change_pct"] = "n/a (last month was 0)"
    else:
        pct = cut(change / abs(before) * 100, 1)
        out["change_pct"] = f"{'+' if pct > 0 else ''}{pct}%"
    return out


def main(argv):
    if "--file" not in argv or argv.index("--file") + 1 >= len(argv):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            data = json.load(fh)
        notes, channels = [], []
        totals = {"engagements": 0, "follower_growth": 0}
        missing_total = set()
        for i, ch in enumerate(data.get("channels") or []):
            name = str(ch.get("channel", f"channel {i + 1}")).strip().lower()
            now = derived(ch.get("this"), f"{name}.this")
            before = derived(ch.get("last"), f"{name}.last")
            row = {"channel": name}
            for m in METRICS:
                row[m] = compare(now[m], before[m], m)
            channels.append(row)
            for m in totals:
                if now[m] is None:
                    missing_total.add(m)
                else:
                    totals[m] += now[m]
            if now["reach"] is None:
                notes.append(f"{name}: reach not tracked, so no engagement rate.")
        for m in missing_total:
            totals[m] = NT + " for at least one channel"
        if not channels:
            raise DataError("No channels in the file; nothing to report.")

        posts = []
        for j, p in enumerate(data.get("posts") or []):
            eng = num(p.get("engagements"), f"posts[{j}].engagements")
            reach = num(p.get("reach"), f"posts[{j}].reach")
            if eng is None:
                continue
            posts.append({"channel": str(p.get("channel", "")).lower(), "date": p.get("date", ""),
                          "link": p.get("link", ""), "caption": str(p.get("caption", ""))[:120],
                          "engagements": eng, "reach": NT if reach is None else reach,
                          "engagement_rate": cut(eng / reach * 100, 2) if reach else NT})
        posts.sort(key=lambda p: (-p["engagements"],
                                  -(p["reach"] if isinstance(p["reach"], (int, float)) else 0)))
        if not posts:
            notes.append("No post-level engagements: top posts not tracked.")
        no_link = [p for p in posts[:5] if not p["link"]]
        if no_link:
            notes.append(f"{len(no_link)} of the top posts have no link; add it from Supermetrics.")
    except (OSError, json.JSONDecodeError, DataError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    print(json.dumps({"client": data.get("client", ""), "month": data.get("month", ""),
                      "channels": channels, "totals": totals, "top_posts": posts[:5],
                      "notes": notes}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
