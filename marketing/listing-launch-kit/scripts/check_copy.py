#!/usr/bin/env python3
"""Check listing copy: fair-housing wording, risky claims, facts against the details, length.

Usage:
    python3 check_copy.py --text description.txt --details details.json [--max-words 300]
        [--max-chars 2000]

details.json (any of these keys; leave out what the user did not give):
    {"price": "£425,000", "beds": 3, "baths": 2, "size": "1,150 sq ft",
     "address": "12 Park Road, Leeds"}

Checks, in order:
- fair_housing: wording that describes who should live there rather than the home
  (family status, age, religion, race or origin, sex, disability). "avoid" = rewrite;
  "review" = often fine in context, have the user decide.
- claims: promises or unverifiable statements (guaranteed, will appreciate, best in...).
- facts: every bed, bath, size and price figure in the text compared with details.json.
  "mismatch" = the text says something different; "not_in_details" = the text states a
  figure the user never gave (confirm or remove); "missing" = a detail not mentioned.
- length: words and characters against --max-words / --max-chars.

Prints JSON {"ok", "counts", "fair_housing", "claims", "facts", "length"}.
"ok" is false when anything is "avoid", a fact mismatches or is not in the details,
or the text is too long. Stdlib only.
"""

import argparse
import json
import re
import sys

# (pattern, severity, why)
FAIR_HOUSING = [
    (r"\b(perfect|ideal|great|suits?|suited|made) (for|to) (a |the )?(young |growing |small |large )?famil(y|ies)\b", "avoid", "describes who should live there (familial status)"),
    (r"\bfamily[- ](home|house|neighbou?rhood|area|street|friendly)\b", "review", "can read as preferring families; describe the rooms and space instead"),
    (r"\b(no|not suitable for) (children|kids|pets and children)\b", "avoid", "excludes families with children"),
    (r"\badults?[- ]only\b", "avoid", "excludes families (allowed only for qualifying senior housing)"),
    (r"\b(young )?professionals?( only| preferred| couple)?\b", "review", "says who should live there; describe the home"),
    (r"\b(singles?|couples?|newlyweds?|bachelor( pad)?|empty[- ]nesters?|retirees?|students?)\b", "avoid", "describes the buyer, not the home (familial status or age)"),
    (r"\b(mature|older|elderly|senior) (buyers?|persons?|people|couples?|residents?)\b", "avoid", "age preference"),
    (r"\b(christian|muslim|jewish|hindu|sikh|catholic)\b", "avoid", "religion"),
    (r"\b(church|mosque|synagogue|temple|gurdwara|chapel|parish)\b", "review", "religious landmark as a selling point; fine as a plain landmark, never as a hint about who belongs"),
    (r"\b(white|black|asian|hispanic|latino|ethnic|integrated|exclusive (community|neighbou?rhood|area)|english[- ]speaking|traditional neighbou?rhood)\b", "avoid", "race, colour, national origin or a coded exclusion"),
    (r"\b(able[- ]bodied|handicap(ped)?|wheelchair[- ]bound|no wheelchairs|mentally ill|physically fit)\b", "avoid", "disability; describe access features instead (step-free entrance, ground-floor bedroom)"),
    (r"\b(man cave|bachelor|his and hers|gentlem[ae]n'?s|ladies'?)\b", "review", "gendered wording; describe the room"),
    (r"\bmaster (bedroom|suite|bath)\b", "review", "many portals and MLSs now prefer 'primary bedroom'"),
    (r"\b(safe|crime[- ]free|low[- ]crime|good) (neighbou?rhood|area|street)\b", "review", "can be read as coded; state facts with a source instead"),
    (r"\b(great|good|top|best|excellent) schools?\b", "review", "school quality claim: name the school, give its distance and cite the official rating"),
]

CLAIMS = [
    (r"\bguarantee(d|s)?\b", "promise"),
    (r"\bwill (appreciate|increase in value|sell fast|not last)\b", "prediction about value or sale"),
    (r"\b(best|cheapest|biggest|finest) (in|on) (the )?(area|street|town|city|market)\b", "unverifiable superlative"),
    (r"\b(investment|rental) (opportunity|yield) of\b", "financial claim: needs a source"),
    (r"\b(no|zero) (flood|flooding|damp|subsidence) (risk|issues|problems)\b", "condition claim: needs a survey or official source"),
    (r"\b(newly|fully|completely) (renovated|refurbished|rewired|replumbed)\b", "condition claim: confirm with the user"),
    (r"\bplanning permission (granted|approved)\b", "legal claim: confirm with the user and cite the reference"),
]

NUM = r"(\d{1,3}(?:[,\s]\d{3})+|\d+(?:\.\d+)?)"
WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
            "eight": 8, "nine": 9, "ten": 10, "single": 1, "double": None}


def to_num(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().lower()
    if s in WORD_NUM:
        return WORD_NUM[s]
    m = re.search(NUM, s)
    if not m:
        return None
    raw = re.sub(r"[,\s]", "", m.group(1))
    val = float(raw)
    if re.search(r"\d\s*k\b", s):
        val *= 1000
    if re.search(r"\d\s*(m|million)\b", s) and not re.search(r"m2|m²|sq", s):
        val *= 1_000_000
    return val


def find_all(pattern, text):
    return [(m.group(0), m) for m in re.finditer(pattern, text, re.I)]


def facts_in_text(text):
    word = r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
    out = {"beds": [], "baths": [], "size": [], "price": []}
    for g, m in find_all(word + r"[- ]?(bed(room)?s?|br)\b", text):
        out["beds"].append((g, to_num(m.group(1))))
    for g, m in find_all(r"(\d+(?:\.\d)?|one|two|three|four|five)[- ]?(full |half )?(bath(room)?s?|ba)\b", text):
        out["baths"].append((g, to_num(m.group(1))))
    for g, m in find_all(NUM + r"\s*(sq\.?\s?ft|sqft|square feet|ft²|ft2|sq\.?\s?m|square met(re|er)s|m²|m2)\b", text):
        out["size"].append((g, to_num(m.group(1)), "m" if re.search(r"m(²|2)|met|sq\.?\s?m\b", m.group(2), re.I) else "ft"))
    for g, m in find_all(r"([£$€])\s?" + NUM + r"\s?(k|m|million)?\b", text):
        out["price"].append((g, to_num(m.group(2) + (m.group(3) or ""))))
    return out


def unit_of(size_str):
    s = str(size_str).lower()
    return "m" if re.search(r"m(²|2)|met|sq\.?\s?m\b", s) else "ft"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--text", required=True)
    ap.add_argument("--details")
    ap.add_argument("--max-words", type=int, default=300)
    ap.add_argument("--max-chars", type=int, default=0)
    a = ap.parse_args()
    try:
        text = open(a.text, encoding="utf-8").read()
        details = json.load(open(a.details, encoding="utf-8")) if a.details else {}
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "Could not read input: %s" % exc}))
        return 2
    if not text.strip():
        print(json.dumps({"error": "The text file is empty."}))
        return 2

    fh = []
    for pat, sev, why in FAIR_HOUSING:
        for g, _ in find_all(pat, text):
            fh.append({"phrase": g, "severity": sev, "why": why})
    claims = [{"phrase": g, "why": why} for pat, why in CLAIMS for g, _ in find_all(pat, text)]

    found = facts_in_text(text)
    facts = []
    for key in ("beds", "baths", "price"):
        want = to_num(details.get(key)) if details.get(key) not in (None, "") else None
        for g, val in found[key]:
            if val is None:
                continue
            if want is None:
                facts.append({"fact": key, "text": g, "status": "not_in_details"})
            elif abs(val - want) > 0.01 and not (key == "price" and abs(val - want) / max(want, 1) < 0.001):
                facts.append({"fact": key, "text": g, "status": "mismatch", "details": details.get(key)})
        if want is not None and not found[key]:
            facts.append({"fact": key, "status": "missing", "details": details.get(key)})
    want_size = to_num(details.get("size")) if details.get("size") else None
    for g, val, unit in found["size"]:
        if want_size is None:
            facts.append({"fact": "size", "text": g, "status": "not_in_details"})
            continue
        wunit = unit_of(details["size"])
        w = want_size if unit == wunit else (want_size * 10.7639 if unit == "ft" else want_size / 10.7639)
        if abs(val - w) / max(w, 1) > 0.02:
            facts.append({"fact": "size", "text": g, "status": "mismatch", "details": details["size"]})
    if want_size is not None and not found["size"]:
        facts.append({"fact": "size", "status": "missing", "details": details.get("size")})

    words = len(re.findall(r"\b[\w'’-]+\b", text))
    chars = len(text.strip())
    length = {"words": words, "chars": chars, "max_words": a.max_words or None,
              "max_chars": a.max_chars or None,
              "too_long": bool((a.max_words and words > a.max_words) or (a.max_chars and chars > a.max_chars))}

    ok = (not any(f["severity"] == "avoid" for f in fh)
          and not any(f["status"] in ("mismatch", "not_in_details") for f in facts)
          and not length["too_long"])
    print(json.dumps({"ok": ok,
                      "counts": {"fair_housing_avoid": sum(f["severity"] == "avoid" for f in fh),
                                 "fair_housing_review": sum(f["severity"] == "review" for f in fh),
                                 "claims": len(claims),
                                 "fact_problems": sum(f["status"] != "missing" for f in facts)},
                      "fair_housing": fh, "claims": claims, "facts": facts, "length": length},
                     indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
