#!/usr/bin/env python3
"""Find where viewers drop off in a video and compare it with the channel's average.

Usage:
    python3 retention_report.py --file retention.json

retention.json:
{
  "video_seconds": 612,
  "video": [[0.0, 1.0], [0.01, 0.93], ...],          # [elapsed ratio, audience watch ratio]
  "channel_average": [[0.0, 1.0], [0.01, 0.9], ...]  # optional, same shape
}
The pairs are what YouTube Analytics reports as elapsedVideoTimeRatio and
audienceWatchRatio (also accepted: a list of {"elapsedVideoTimeRatio",
"audienceWatchRatio"} objects). Rewatched parts can go above 1.0.

Prints one JSON object:
    {"points", "kept_at_30s", "kept_at_half", "kept_at_end", "average_kept",
     "drops": [{"at", "at_seconds", "from", "to", "lost"}],   (up to 3 steepest of 2+ points, after the first 5%)
     "spikes": [{"at", "at_seconds", "rise"}],                 (rewatched moments)
     "vs_channel": {"average_kept_diff", "kept_at_30s_diff"} or null,
     "notes": [...]}
"average_kept" is the area under the curve: roughly the average share of the video
watched. Stdlib only.
"""

import json
import sys

WINDOW = 0.03    # compare points 3% of the video apart
MIN_DROP = 0.02  # ignore drops smaller than 2 points of audience


def load(series):
    pts = []
    for p in series or []:
        if isinstance(p, dict):
            pts.append((float(p["elapsedVideoTimeRatio"]), float(p["audienceWatchRatio"])))
        else:
            pts.append((float(p[0]), float(p[1])))
    return sorted(pts)


def at(pts, x):
    if not pts:
        return None
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def area(pts):
    return sum((x1 - x0) * (y0 + y1) / 2 for (x0, y0), (x1, y1) in zip(pts, pts[1:]))


def summary(pts, secs):
    r30 = 30.0 / secs if secs else None
    return {"kept_at_30s": round(at(pts, r30), 3) if r30 and r30 <= 1 else None,
            "kept_at_half": round(at(pts, 0.5), 3),
            "kept_at_end": round(pts[-1][1], 3),
            "average_kept": round(area(pts) / (pts[-1][0] - pts[0][0] or 1), 3)}


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, IndexError) as exc:
        print(json.dumps({"error": f"Could not read the input file: {exc}"}))
        return 1
    secs = float(data.get("video_seconds") or 0)
    pts = load(data.get("video"))
    if len(pts) < 5:
        print(json.dumps({"error": "Need at least 5 retention points for the video"}))
        return 1
    out = {"points": len(pts)}
    out.update(summary(pts, secs))
    notes = []
    if not secs:
        notes.append("No video_seconds given: times are shown as share of the video only.")

    steps = []
    x = 0.05
    while x + WINDOW <= pts[-1][0] + 1e-9:
        # start from the lower of this point and the one before, so falling back
        # after a rewatch spike is not reported as a drop
        a, b = min(at(pts, x), at(pts, x - 0.01)), at(pts, x + WINDOW)
        steps.append((a - b, x, a, b))
        x += 0.01
    drops, used = [], []
    for lost, x, a, b in sorted(steps, reverse=True):
        if lost < MIN_DROP or any(abs(x - u) < WINDOW * 2 for u in used):
            continue
        used.append(x)
        drops.append({"at": round(x, 2), "at_seconds": round(x * secs) if secs else None,
                      "from": round(a, 3), "to": round(b, 3), "lost": round(lost, 3)})
        if len(drops) == 3:
            break
    out["drops"] = sorted(drops, key=lambda d: d["at"])

    spikes = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x1 > 0.05 and y1 - y0 >= 0.03:
            spikes.append({"at": round(x1, 2), "at_seconds": round(x1 * secs) if secs else None,
                           "rise": round(y1 - y0, 3)})
    out["spikes"] = sorted(spikes, key=lambda s: -s["rise"])[:3]

    ch = load(data.get("channel_average"))
    if len(ch) >= 5:
        cs = summary(ch, secs)
        out["vs_channel"] = {"average_kept_diff": round(out["average_kept"] - cs["average_kept"], 3),
                             "kept_at_30s_diff": (round(out["kept_at_30s"] - cs["kept_at_30s"], 3)
                                                  if out["kept_at_30s"] is not None and cs["kept_at_30s"] is not None else None),
                             "channel": cs}
    else:
        out["vs_channel"] = None
        notes.append("No channel average given: no comparison made.")
    out["notes"] = notes
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
