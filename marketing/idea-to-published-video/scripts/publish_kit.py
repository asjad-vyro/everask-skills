#!/usr/bin/env python3
"""Check YouTube metadata against YouTube's limits, format chapters, and work out the
exact publish times for the video and its Shorts.

Usage:
    python3 publish_kit.py --file kit.json

kit.json:
{
  "titles": ["...", "...", "..."],
  "description": "...",                       # without chapters; they are appended
  "tags": ["...", "..."],
  "chapters": [{"start": 0, "title": "Intro"}, {"start": 74.5, "title": "..."}],
  "video_seconds": 612,
  "publish": {"date": "2026-11-24", "time": "17:00", "timezone": "Europe/London"},
  "shorts": {"count": 3, "every_days": 2, "time": "12:00"}   # optional
}

Prints one JSON object:
    {"titles": [{"text", "chars", "ok", "problems"}],
     "chapters_text": "0:00 Intro\n1:14 ...", "chapters_ok", "chapter_problems",
     "description_full", "description_chars", "description_ok",
     "tags_chars", "tags_ok",
     "publish_at_utc": "2026-11-24T17:00:00Z", "publish_local": "...",
     "shorts_publish_at_utc": [...], "problems": [...]}

YouTube rules checked: title 1-100 characters, no < or >; description up to 5000
characters, no < or >; tags up to 500 characters in total; chapters start at 0:00,
at least 3, each at least 10 seconds long, in order. Publish time must be in the
future. Stdlib only (zoneinfo needs Python 3.9+ with time zone data).
"""

import datetime
import json
import sys

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None


def stamp(sec, long_form):
    sec = int(sec)
    h, m, s = sec // 3600, sec // 60 % 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if long_form else f"{m}:{s:02d}"


def check_text(text, limit, label):
    problems = []
    if not text.strip():
        problems.append(f"{label} is empty")
    if len(text) > limit:
        problems.append(f"{label} is {len(text)} characters; YouTube allows {limit}")
    if "<" in text or ">" in text:
        problems.append(f"{label} contains < or >, which YouTube rejects")
    return problems


def chapters(items, video_seconds):
    problems = []
    items = sorted(items or [], key=lambda c: float(c["start"]))
    if not items:
        return "", False, ["no chapters"]
    if float(items[0]["start"]) != 0:
        problems.append("first chapter must start at 0:00")
    if len(items) < 3:
        problems.append("YouTube needs at least 3 chapters")
    ends = [float(c["start"]) for c in items[1:]] + [float(video_seconds or 0)]
    for c, end in zip(items, ends):
        if end and end - float(c["start"]) < 10:
            problems.append(f"chapter '{c['title']}' is under 10 seconds")
    long_form = float(video_seconds or 0) >= 3600
    text = "\n".join(f"{stamp(c['start'], long_form)} {c['title'].strip()}" for c in items)
    return text, not problems, problems


def to_utc(date, time, tz):
    if ZoneInfo is None:
        raise ValueError("zoneinfo not available; give the time in UTC")
    local = datetime.datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=ZoneInfo(tz))
    return local, local.astimezone(datetime.timezone.utc)


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            kit = json.load(fh)
    except (OSError, ValueError, IndexError) as exc:
        print(json.dumps({"error": f"Could not read the input file: {exc}"}))
        return 1
    out, problems = {}, []
    out["titles"] = []
    for t in kit.get("titles", []):
        p = check_text(t, 100, "title")
        out["titles"].append({"text": t, "chars": len(t), "ok": not p, "problems": p})
    text, ok, cp = chapters(kit.get("chapters"), kit.get("video_seconds"))
    out.update(chapters_text=text, chapters_ok=ok, chapter_problems=cp)
    desc = (kit.get("description") or "").rstrip()
    full = desc + ("\n\nChapters\n" + text if text else "")
    dp = check_text(full, 5000, "description")
    out.update(description_full=full, description_chars=len(full), description_ok=not dp)
    problems += dp
    tags = kit.get("tags") or []
    # YouTube counts a tag with spaces as if quoted, plus a comma between tags
    tag_chars = sum(len(t) + (2 if " " in t else 0) for t in tags) + max(0, len(tags) - 1)
    out.update(tags_chars=tag_chars, tags_ok=tag_chars <= 500)
    if tag_chars > 500:
        problems.append(f"tags are {tag_chars} characters; YouTube allows 500")

    pub = kit.get("publish")
    if pub:
        try:
            local, utc = to_utc(pub["date"], pub["time"], pub["timezone"])
            now = datetime.datetime.now(datetime.timezone.utc)
            out["publish_local"] = local.isoformat()
            out["publish_at_utc"] = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            if utc <= now:
                problems.append("publish time is in the past")
            sh = kit.get("shorts")
            if sh:
                times = []
                for i in range(int(sh.get("count", 0))):
                    d = (local + datetime.timedelta(days=int(sh.get("every_days", 2)) * (i + 1))).date()
                    _, u = to_utc(d.isoformat(), sh.get("time", pub["time"]), pub["timezone"])
                    times.append(u.strftime("%Y-%m-%dT%H:%M:%SZ"))
                out["shorts_publish_at_utc"] = times
        except (KeyError, ValueError) as exc:
            problems.append(f"could not read publish time: {exc}")
        except Exception as exc:  # unknown time zone
            problems.append(f"could not read time zone: {exc}")
    out["problems"] = problems + [p for t in out["titles"] for p in t["problems"]] + cp
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
