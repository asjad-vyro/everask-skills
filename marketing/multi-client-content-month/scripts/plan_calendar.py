#!/usr/bin/env python3
"""Lay out one client's content month: which post goes out on which day, at what time.

Usage:
    python3 plan_calendar.py --file plan.json

plan.json (only "month" and one of "mix" / "last_month_rows" are required):
{
  "client": "Bloom Bakery",
  "month": "2026-12",                       # YYYY-MM
  "timezone": "Europe/London",              # passed through, not converted
  "mix": {"instagram:post": 8, "instagram:carousel": 4,
          "instagram:reel": 4, "linkedin:post": 8},
  "last_month_rows": [{"channel": "instagram", "format": "post"}, ...],
                                            # used for the mix when "mix" is missing
  "pillars": [{"name": "Educate", "weight": 2}, {"name": "Offer", "weight": 1}],
                                            # or plain names; default 4 even pillars
  "days":  {"linkedin": ["Tue", "Wed", "Thu"]},   # posting weekdays per channel
  "times": {"instagram": ["12:00", "18:00"]},     # posting times per channel
  "avoid_dates": ["2026-12-25"],            # no posts on these dates
  "key_dates": [{"date": "2026-12-24", "label": "Christmas Eve"}],
  "promotions": [{"name": "Winter sale", "start": "2026-12-01", "end": "2026-12-07"}]
}

Prints JSON: {"client", "month", "timezone", "rows": [...], "summary": {...},
"warnings": [...]}. Each row: {"n", "date", "weekday", "time", "channel", "format",
"pillar", "key_date", "promotion", "status": "Planned"}. Hooks, captions, hashtags and
calls to action are left for the writer; this script only does the dates and spread.

Rules: each channel's posts are spread evenly over its allowed days (one per day
while there are enough days, then a second time slot); formats are interleaved so
reels and carousels do not bunch up; pillars rotate by weight across the month.
Stdlib only, no network.
"""

import calendar
import datetime
import json
import sys

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DEFAULT_DAYS = {
    "instagram": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    "facebook": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "linkedin": ["Tue", "Wed", "Thu"],
}
DEFAULT_TIMES = {
    "instagram": ["12:00", "18:00"],
    "facebook": ["13:00", "19:00"],
    "linkedin": ["08:30", "12:30"],
}
FALLBACK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
FALLBACK_TIMES = ["12:00", "17:00"]
DEFAULT_PILLARS = ["Educate", "Show the work", "Offer", "Community"]
PUBLISHABLE = {"instagram", "facebook", "linkedin"}


class PlanError(Exception):
    pass


def parse_date(text, what):
    try:
        return datetime.date.fromisoformat(str(text).strip())
    except ValueError:
        raise PlanError(f"{what}: '{text}' is not a date like 2026-12-01")


def parse_time(text, channel):
    try:
        h, m = str(text).strip().split(":")
        return datetime.time(int(h), int(m)).strftime("%H:%M")
    except ValueError:
        raise PlanError(f"times for {channel}: '{text}' is not a time like 18:00")


def parse_mix(plan, warnings):
    mix = plan.get("mix")
    if not mix:
        rows = plan.get("last_month_rows") or []
        if not rows:
            raise PlanError("Give 'mix' (e.g. {\"instagram:post\": 12}) or 'last_month_rows'.")
        mix = {}
        for r in rows:
            key = f"{str(r.get('channel', '')).strip().lower()}:{str(r.get('format', 'post')).strip().lower()}"
            mix[key] = mix.get(key, 0) + 1
        warnings.append("Mix copied from last month's calendar.")
    out = {}
    for key, count in mix.items():
        channel, _, fmt = str(key).partition(":")
        channel, fmt = channel.strip().lower(), (fmt.strip().lower() or "post")
        if not channel:
            raise PlanError(f"mix key '{key}' has no channel; use 'instagram:post'.")
        try:
            count = int(count)
        except (TypeError, ValueError):
            raise PlanError(f"mix '{key}': '{count}' is not a whole number")
        if count < 0:
            raise PlanError(f"mix '{key}': count cannot be negative")
        if count == 0:
            continue
        if channel not in PUBLISHABLE:
            warnings.append(f"'{channel}' is not Instagram, Facebook or LinkedIn: planned, "
                            "but the publishing step does not cover it.")
        out.setdefault(channel, {})
        out[channel][fmt] = out[channel].get(fmt, 0) + count
    if not out:
        raise PlanError("The mix has no posts.")
    return out


def parse_pillars(plan):
    raw = plan.get("pillars") or DEFAULT_PILLARS
    pillars = []
    for p in raw:
        if isinstance(p, dict):
            name, weight = str(p.get("name", "")).strip(), p.get("weight", 1)
        else:
            name, weight = str(p).strip(), 1
        try:
            weight = float(weight)
        except (TypeError, ValueError):
            raise PlanError(f"pillar '{name}': weight must be a number")
        if name and weight > 0:
            pillars.append((name, weight))
    if not pillars:
        raise PlanError("No usable pillars.")
    return pillars


def smooth_pick(targets, done):
    """Pick the item furthest behind its share (deterministic, keeps order on ties)."""
    best, best_ratio = None, None
    for name, target in targets:
        ratio = done[name] / target
        if best_ratio is None or ratio < best_ratio - 1e-9:
            best, best_ratio = name, ratio
    return best


def spread(slots_by_day, count):
    """Choose `count` (date, time) slots spread evenly across the days."""
    days = sorted(slots_by_day)
    if not days:
        return []
    per_day = max(len(t) for t in slots_by_day.values())
    chosen = []
    remaining = count
    for layer in range(per_day):
        usable = [d for d in days if len(slots_by_day[d]) > layer]
        take = min(remaining, len(usable))
        if take <= 0:
            break
        for i in range(take):
            d = usable[int((i + 0.5) * len(usable) / take)]
            chosen.append((d, slots_by_day[d][layer]))
        remaining -= take
    return sorted(chosen)


def plan_month(plan):
    warnings = []
    month = str(plan.get("month", "")).strip()
    try:
        year, mon = (int(x) for x in month.split("-"))
        first = datetime.date(year, mon, 1)
    except ValueError:
        raise PlanError(f"month '{month}' is not like 2026-12")
    last_day = calendar.monthrange(year, mon)[1]
    dates = [first + datetime.timedelta(days=i) for i in range(last_day)]

    avoid = {parse_date(d, "avoid_dates") for d in plan.get("avoid_dates") or []}
    key_dates = {}
    for k in plan.get("key_dates") or []:
        d = parse_date(k.get("date"), "key_dates")
        key_dates.setdefault(d, []).append(str(k.get("label", "")).strip())
    promos = []
    for p in plan.get("promotions") or []:
        start = parse_date(p.get("start"), "promotions start")
        end = parse_date(p.get("end", p.get("start")), "promotions end")
        if end < start:
            raise PlanError(f"promotion '{p.get('name')}' ends before it starts")
        promos.append((str(p.get("name", "")).strip(), start, end))

    mix = parse_mix(plan, warnings)
    pillars = parse_pillars(plan)
    days_cfg = {k.lower(): v for k, v in (plan.get("days") or {}).items()}
    times_cfg = {k.lower(): v for k, v in (plan.get("times") or {}).items()}

    rows = []
    for channel, formats in mix.items():
        wanted_days = days_cfg.get(channel) or DEFAULT_DAYS.get(channel, FALLBACK_DAYS)
        bad = [d for d in wanted_days if str(d)[:3].title() not in WEEKDAYS]
        if bad:
            raise PlanError(f"days for {channel}: {bad} are not weekdays like 'Mon'")
        wanted = {str(d)[:3].title() for d in wanted_days}
        times = sorted({parse_time(t, channel) for t in
                        (times_cfg.get(channel) or DEFAULT_TIMES.get(channel, FALLBACK_TIMES))})
        slots_by_day = {d: times for d in dates
                        if WEEKDAYS[d.weekday()] in wanted and d not in avoid}
        total = sum(formats.values())
        capacity = len(slots_by_day) * len(times)
        if total > capacity:
            warnings.append(f"{channel}: {total} posts asked but only {capacity} slots "
                            f"({len(slots_by_day)} days x {len(times)} times); planned {capacity}. "
                            "Add posting days or times to fit the rest.")
        slots = spread(slots_by_day, min(total, capacity))
        targets = sorted(formats.items(), key=lambda kv: (-kv[1], kv[0]))
        done = {f: 0 for f in formats}
        for d, t in slots:
            fmt = smooth_pick(targets, done)
            done[fmt] += 1
            rows.append({"date": d, "time": t, "channel": channel, "format": fmt})

    rows.sort(key=lambda r: (r["date"], r["time"], r["channel"], r["format"]))
    p_done = {name: 0 for name, _ in pillars}
    for i, r in enumerate(rows, 1):
        pillar = smooth_pick(pillars, p_done)
        p_done[pillar] += 1
        d = r["date"]
        r.update({
            "n": i,
            "date": d.isoformat(),
            "weekday": WEEKDAYS[d.weekday()],
            "pillar": pillar,
            "key_date": "; ".join(key_dates.get(d, [])),
            "promotion": "; ".join(n for n, s, e in promos if s <= d <= e),
            "status": "Planned",
        })
    rows = [{k: r[k] for k in ("n", "date", "weekday", "time", "channel", "format",
                               "pillar", "key_date", "promotion", "status")} for r in rows]

    for d, labels in sorted(key_dates.items()):
        if d.year == year and d.month == mon and d not in avoid and not any(r["date"] == d.isoformat() for r in rows):
            warnings.append(f"No post planned on key date {d.isoformat()} ({'; '.join(labels)}).")
    for name, s, e in promos:
        if not any(s.isoformat() <= r["date"] <= e.isoformat() for r in rows):
            warnings.append(f"No post falls inside promotion '{name}' ({s} to {e}).")

    summary = {"total": len(rows), "by_channel": {}, "by_format": {}, "by_pillar": {}}
    for r in rows:
        for key, field in (("by_channel", "channel"), ("by_format", "format"), ("by_pillar", "pillar")):
            summary[key][r[field]] = summary[key].get(r[field], 0) + 1
    return {"client": plan.get("client", ""), "month": month,
            "timezone": plan.get("timezone", ""), "rows": rows,
            "summary": summary, "warnings": warnings}


def main(argv):
    if "--file" not in argv or argv.index("--file") + 1 >= len(argv):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            plan = json.load(fh)
        if not isinstance(plan, dict):
            raise PlanError("plan.json must be a JSON object")
        result = plan_month(plan)
    except (OSError, json.JSONDecodeError, PlanError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stdout)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
