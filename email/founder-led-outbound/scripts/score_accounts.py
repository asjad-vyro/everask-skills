#!/usr/bin/env python3
"""Score B2B accounts 0-10 on fit with the ideal customer and strength of buying signals.

Usage:
    python3 score_accounts.py --file accounts.json [--today 2026-11-18]

accounts.json:
{
  "icp": {
    "min_staff": 50, "max_staff": 200,                 # optional
    "industries": ["fintech", "payments"],             # optional, [] = any
    "regions": ["United Kingdom", "UK", "Ireland"],    # optional, [] = any
    "roles": ["CTO", "VP Engineering", "Head of Data"],# optional, [] = any decision-maker
    "signals": ["funding", "hiring", "new_leader", "tool"]  # optional, [] = all count
  },
  "exclude_domains": ["already-in-sheet.com"],          # optional (in sheet, opted out)
  "accounts": [
    {"company": "...", "domain": "acme.com", "staff": 120 | "51-200" | null,
     "industry": "...", "region": "...",
     "contact_name": "...", "contact_role": "...", "contact_email": "...",
     "signals": [{"type": "funding" | "hiring" | "new_leader" | "tool" | "other",
                  "detail": "Series A, $12M", "date": "2026-05-02",
                  "source": "https://..."}]}
  ]
}

Prints JSON: {"accounts": [...sorted, highest score first...], "skipped": [...],
"warnings": [...]}. Each account gets "score" (0-10), "fit" (0-5), "signal" (0-5),
"best_signal", "best_source", "reasons" (list of short strings).

Fit (0-5): staff in range 2 (within 25% of the range 1, unknown 0); industry 1;
region 1; a named contact whose role matches 1.
Signal (0-5, capped): only signals with an http(s) source link count.
  funding     <= 6 months 3, <= 12 months 2, older 0
  hiring      <= 60 days 2, <= 120 days 1, older 0
  new_leader  <= 6 months 2, <= 12 months 1, older 0
  tool        1 (no date needed)
  other       <= 6 months 1
  An undated funding/hiring/new_leader/other signal scores 1 and is marked "undated".
A signal without a source link scores 0 and is reported in "warnings": never trust
an unsourced signal.

Stdlib only. No network access.
"""

import datetime
import json
import re
import sys

WEIGHTS = {
    # type: [(max_age_days, points), ...] checked in order
    "funding": [(183, 3), (366, 2)],
    "hiring": [(60, 2), (120, 1)],
    "new_leader": [(183, 2), (366, 1)],
    "other": [(183, 1)],
}
ALIASES = {
    "funded": "funding", "raise": "funding", "raised": "funding", "fundraise": "funding",
    "job": "hiring", "jobs": "hiring", "job_post": "hiring", "hire": "hiring",
    "new_hire": "new_leader", "leader": "new_leader", "new_exec": "new_leader",
    "leadership": "new_leader", "technology": "tool", "tech": "tool", "stack": "tool",
}


def norm_type(t):
    t = re.sub(r"[^a-z_]", "_", (t or "other").strip().lower()).strip("_")
    t = ALIASES.get(t, t)
    return t if t in ("funding", "hiring", "new_leader", "tool", "other") else "other"


def parse_staff(value):
    """Return (low, high) or None. Accepts 120, "120", "51-200", "200+", "1,000"."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return (int(value), int(value))
    s = str(value).replace(",", "").strip()
    nums = [int(n) for n in re.findall(r"\d+", s)]
    if not nums:
        return None
    if len(nums) >= 2:
        return (min(nums[0], nums[1]), max(nums[0], nums[1]))
    if s.endswith("+"):
        return (nums[0], nums[0] * 2)
    return (nums[0], nums[0])


def parse_date(value):
    if not value:
        return None
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%d %B %Y", "%d %b %Y", "%B %Y", "%b %Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return datetime.date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            return None
    return None


def matches(value, options):
    v = (value or "").lower()
    if not v:
        return False
    for o in options:
        o = (o or "").lower().strip()
        if not o:
            continue
        # whole words only, so "CTO" does not match "Director"
        if re.search(r"(?<![a-z0-9])" + re.escape(o) + r"(?![a-z0-9])", v) or \
                re.search(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", o):
            return True
    return False


def size_points(staff, lo, hi):
    if lo is None and hi is None:
        return 2, "size: no limit set"
    rng = parse_staff(staff)
    if rng is None:
        return 0, "size unknown"
    lo = lo or 0
    hi = hi or 10 ** 9
    a, b = rng
    if a >= lo and b <= hi:
        return 2, f"size {staff} in range"
    if b >= lo * 0.75 and a <= hi * 1.25:
        return 1, f"size {staff} near range"
    return 0, f"size {staff} out of range"


def signal_points(sig, today, wanted):
    t = norm_type(sig.get("type"))
    src = (sig.get("source") or "").strip()
    label = (sig.get("detail") or t).strip()
    if wanted and t not in wanted:
        return 0, label, "", f"signal '{label}' is not one the user asked for"
    if not re.match(r"https?://", src):
        return 0, label, "", f"signal '{label}' has no source link: not counted"
    if t == "tool":
        return 1, label, src, ""
    d = parse_date(sig.get("date"))
    if d is None:
        return 1, label + " (undated)", src, ""
    age = (today - d).days
    if age < 0:
        return 0, label, src, f"signal '{label}' is dated in the future ({d}): check it"
    for max_age, pts in WEIGHTS[t]:
        if age <= max_age:
            return pts, f"{label} ({d})", src, ""
    return 0, f"{label} ({d}, too old)", src, ""


def score(acc, icp, today):
    reasons, warnings = [], []
    wanted = {norm_type(s) for s in icp.get("signals") or []}
    sp, why = size_points(acc.get("staff"), icp.get("min_staff"), icp.get("max_staff"))
    fit = sp
    reasons.append(why)
    inds = icp.get("industries") or []
    if not inds or matches(acc.get("industry"), inds):
        fit += 1
    else:
        reasons.append(f"industry '{acc.get('industry') or 'unknown'}' not in profile")
    regs = icp.get("regions") or []
    if not regs or matches(acc.get("region"), regs):
        fit += 1
    else:
        reasons.append(f"region '{acc.get('region') or 'unknown'}' not in profile")
    roles = icp.get("roles") or []
    if not (acc.get("contact_name") or "").strip():
        reasons.append("no decision-maker found")
    elif not roles or matches(acc.get("contact_role"), roles):
        fit += 1
    else:
        reasons.append(f"contact role '{acc.get('contact_role') or 'unknown'}' not a target role")

    sig_total, best = 0, (0, "", "")
    for sig in acc.get("signals") or []:
        pts, label, src, warn = signal_points(sig, today, wanted)
        if warn:
            warnings.append(f"{acc.get('company')}: {warn}")
        sig_total += pts
        if pts > best[0]:
            best = (pts, label, src)
        if pts:
            reasons.append(f"+{pts} {label}")
    signal = min(sig_total, 5)
    if signal == 0:
        reasons.append("no sourced recent signal")
    out = dict(acc)
    out.update({"score": fit + signal, "fit": fit, "signal": signal,
                "best_signal": best[1], "best_source": best[2], "reasons": reasons})
    return out, warnings


def domain_of(acc):
    d = (acc.get("domain") or "").lower().strip()
    d = re.sub(r"^https?://", "", d).split("/")[0]
    return d[4:] if d.startswith("www.") else d


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    today = datetime.date.today()
    if "--today" in argv:
        today = parse_date(argv[argv.index("--today") + 1]) or today
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read input: {exc}"}))
        return 1
    if isinstance(data, list):
        data = {"accounts": data}
    icp = data.get("icp") or {}
    exclude = {e.lower().strip() for e in data.get("exclude_domains") or []}
    scored, skipped, warnings, seen = [], [], [], set()
    for acc in data.get("accounts") or []:
        if not (acc.get("company") or "").strip():
            warnings.append("an account with no company name was skipped")
            continue
        dom = domain_of(acc)
        if dom and dom in exclude:
            skipped.append({"company": acc["company"], "reason": "already in sheet or opted out"})
            continue
        key = dom or acc["company"].lower().strip()
        if key in seen:
            skipped.append({"company": acc["company"], "reason": "duplicate"})
            continue
        seen.add(key)
        out, warn = score(acc, icp, today)
        scored.append(out)
        warnings.extend(warn)
    scored.sort(key=lambda a: (-a["score"], -a["signal"], a["company"].lower()))
    print(json.dumps({"today": today.isoformat(), "accounts": scored,
                      "skipped": skipped, "warnings": warnings}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
