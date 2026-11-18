#!/usr/bin/env python3
"""Check ad copy against platform length limits, the brand's words to avoid and risky claims.

Usage:
    python3 check_copy.py --file copy.json [--rules rules.json]

copy.json: [{"name": "20261116_..._v1", "platform": "meta",
             "fields": {"primary_text": "...", "headline": "...", "description": "..."}}, ...]
    Fields per platform:
      meta:   primary_text, headline, description
      tiktok: ad_text, display_name
      google: headline (each <= 30), long_headline, description, business_name
              (a list of strings is allowed for headline/description)
rules.json (from the brand guidelines, all optional):
    {"avoid_words": ["cheap", "miracle"], "banned_claims": ["cures acne"],
     "competitors": ["Brand X"], "allow": ["best-selling"]}

Prints a JSON list, one per ad: {"name", "platform", "ok", "errors": [...], "warnings": [...]}.
errors   = will be rejected or breaks a brand rule (fix before upload);
warnings = gets cut off on screen, or a phrase ad reviewers often flag (read it again).
The risky-phrase list is a prompt to check, not a policy ruling.

Stdlib only. No network.
"""

import json
import re
import sys

# (hard limit -> error, display limit -> warning), in characters
LIMITS = {
    "meta": {"primary_text": (None, 125), "headline": (None, 40), "description": (None, 30)},
    "tiktok": {"ad_text": (100, None), "display_name": (40, None)},
    "google": {"headline": (30, None), "long_headline": (90, None),
               "description": (90, None), "business_name": (25, None)},
}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
RISKY = [
    (r"\bguarantee[ds]?\b", "a guarantee"),
    (r"\b(cure[sd]?|heal[s]?|treat[s]?)\b", "a medical claim"),
    (r"\bclinically (proven|tested)\b", "a clinical claim (needs proof)"),
    (r"\b(doctor|dermatologist)[- ]?(recommended|approved)\b", "an endorsement claim"),
    (r"\blose \d+\s*(lbs?|kg|pounds|kilos)\b", "a weight-loss result"),
    (r"\bbefore (and|&) after\b", "before-and-after"),
    (r"(#1|\bnumber one\b|\bbest\b)", "a superlative (needs proof)"),
    (r"\brisk[- ]free\b", "risk-free"),
    (r"\b(get rich|make \$?\d+|passive income)\b", "an income claim"),
    (r"\bare you (fat|overweight|depressed|anxious|in debt|single|diabetic)\b",
     "a personal-attribute question (Meta rejects these)"),
    (r"\b(free)\b", "\"free\" (state the terms)"),
]


def _texts(value):
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    return [] if value is None else [str(value)]


def check(ad, rules):
    platform = str(ad.get("platform", "")).strip().lower()
    fields = ad.get("fields") or {}
    errors, warnings = [], []
    limits = LIMITS.get(platform)
    if limits is None:
        errors.append(f"unknown platform '{platform}' (use meta, tiktok or google)")
        limits = {}
    for field, value in fields.items():
        hard, soft = limits.get(field, (None, None))
        if limits and field not in limits:
            warnings.append(f"{field}: not a {platform} field this script knows")
        for text in _texts(value):
            n = len(text)
            if hard and n > hard:
                errors.append(f"{field}: {n} characters, limit {hard}: \"{text[:50]}\"")
            elif soft and n > soft:
                warnings.append(f"{field}: {n} characters, cut off after about {soft}")
            if not text.strip():
                warnings.append(f"{field}: empty (leave the field out if it is not used)")
            if platform == "tiktok" and field == "ad_text" and EMOJI.search(text):
                warnings.append("ad_text: has emoji; TikTok may reject it")

    all_text = " ".join(t for v in fields.values() for t in _texts(v))
    low = all_text.lower()
    allow = [a.lower() for a in rules.get("allow", [])]
    for word in rules.get("avoid_words", []):
        if word and re.search(r"\b" + re.escape(word.lower()) + r"\b", low):
            errors.append(f"uses a word the brand avoids: \"{word}\"")
    for claim in rules.get("banned_claims", []):
        if claim and claim.lower() in low:
            errors.append(f"makes a claim the brand may not make: \"{claim}\"")
    for comp in rules.get("competitors", []):
        if comp and re.search(r"\b" + re.escape(comp.lower()) + r"\b", low):
            errors.append(f"names a competitor: \"{comp}\"")
    for pattern, label in RISKY:
        m = re.search(pattern, low)
        if m and not any(a in low for a in allow if m.group(0) in a):
            warnings.append(f"check {label}: \"{m.group(0)}\"")
    return {"name": ad.get("name", ""), "platform": platform, "ok": not errors,
            "errors": errors, "warnings": warnings}


def main(argv):
    opts = {"--file": None, "--rules": None}
    i = 0
    while i < len(argv):
        if argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            print(f"Unknown or incomplete argument: {argv[i]}\n\n{__doc__}", file=sys.stderr)
            return 2
    if not opts["--file"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(opts["--file"], encoding="utf-8") as fh:
            ads = json.load(fh)
        rules = {}
        if opts["--rules"]:
            with open(opts["--rules"], encoding="utf-8") as fh:
                rules = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read input: {exc}"}))
        return 1
    if not isinstance(ads, list):
        print(json.dumps({"error": "copy.json must be a JSON list"}))
        return 1
    print(json.dumps([check(ad, rules) for ad in ads], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
