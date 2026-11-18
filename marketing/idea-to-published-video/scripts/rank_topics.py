#!/usr/bin/env python3
"""Score and rank candidate video topics from sourced evidence.

Usage:
    python3 rank_topics.py --file topics.json [--top 10]

topics.json:
{
  "channel_median_views": 12000,          # median views of the channel's recent videos
  "topics": [
    {"topic": "...", "working_title": "...", "covered_recently": false,
     "evidence": [
       {"type": "past_video", "title": "...", "views": 41000, "url": "https://youtu.be/..."},
       {"type": "question", "text": "...", "url": "https://www.reddit.com/r/.../comments/..."},
       {"type": "search_term", "term": "...", "views": 900, "source": "YouTube Analytics"}
     ]}
  ]
}

Every evidence item needs a "url" or a "source"; items without one are dropped and
reported, because an unsourced claim is not evidence.

Score 0-10 (higher = make it sooner):
    proven      0-4  best related past video's views / channel median:
                     >=3x -> 4, >=2x -> 3, >=1.5x -> 2, >=1x -> 1
    demand      0-3  distinct audience questions (different URLs): 5+ -> 3, 3-4 -> 2, 1-2 -> 1
    search      0-2  related YouTube search terms bringing views: 2+ -> 2, 1 -> 1
    fresh       0-1  1 if not covered in the channel's recent videos
A topic with no sourced evidence gets score null and goes to the bottom.

Prints a JSON list, best first: {"rank", "topic", "working_title", "score",
"parts": {...}, "evidence": [...], "why": "..."} plus {"dropped": [...]} at the end.
Stdlib only.
"""

import json
import sys


def proven_points(ratio):
    for limit, pts in ((3, 4), (2, 3), (1.5, 2), (1, 1)):
        if ratio >= limit:
            return pts
    return 0


def score(topic, median):
    ev = topic.get("evidence") or []
    vids = [e for e in ev if e.get("type") == "past_video"]
    qs = {e.get("url") for e in ev if e.get("type") == "question"}
    terms = [e for e in ev if e.get("type") == "search_term"]
    parts, why = {}, []
    best = max((float(v.get("views") or 0) for v in vids), default=0)
    if vids and median:
        ratio = best / median
        parts["proven"] = proven_points(ratio)
        why.append(f"related video at {ratio:.1f}x the channel median")
    else:
        parts["proven"] = 0
        if vids and not median:
            why.append("past video found but no channel median given, not scored")
    parts["demand"] = 3 if len(qs) >= 5 else 2 if len(qs) >= 3 else 1 if qs else 0
    if qs:
        why.append(f"{len(qs)} audience question(s)")
    parts["search"] = 2 if len(terms) >= 2 else 1 if terms else 0
    if terms:
        why.append(f"{len(terms)} search term(s) already bringing views")
    parts["fresh"] = 0 if topic.get("covered_recently") else 1
    if not ev:
        return None, parts, "no sourced evidence"
    return sum(parts.values()), parts, "; ".join(why)


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 10
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, IndexError) as exc:
        print(json.dumps({"error": f"Could not read the input file: {exc}"}))
        return 1
    median = float(data.get("channel_median_views") or 0)
    rows, dropped = [], []
    for t in data.get("topics", []):
        kept = []
        for e in t.get("evidence") or []:
            if e.get("url") or e.get("source"):
                kept.append(e)
            else:
                dropped.append({"topic": t.get("topic"), "evidence": e,
                                "reason": "no url or source"})
        t = dict(t, evidence=kept)
        s, parts, why = score(t, median)
        rows.append({"topic": t.get("topic", ""), "working_title": t.get("working_title", ""),
                     "score": s, "parts": parts, "evidence": kept, "why": why})
    rows.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0)))
    rows = rows[:top]
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    print(json.dumps(rows + [{"dropped": dropped}], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
