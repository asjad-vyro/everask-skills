#!/usr/bin/env python3
"""Clean a contact list for the just-listed email and split it into send batches.

Usage:
    python3 contact_batches.py --csv contacts.csv [--batch-size 50]
        [--suppress unsubscribed.txt] [--all-opted-in]
    python3 contact_batches.py --json contacts.json ...   (list of objects, e.g. a HubSpot export)

Columns are matched by name, case-insensitive:
    email:        email, e-mail, email address
    name:         first name / firstname / name / full name
    consent:      consent, opt in, opted in, opt-in, subscribed, marketing, marketing consent,
                  email consent, gdpr  (yes/true/1/y/subscribed/opted in = agreed)
    unsubscribed: unsubscribed, opted out, opt out, do not email, unsubscribe, hs_email_optout
--suppress: a file of addresses (one per line) who opted out earlier; always removed.
--all-opted-in: the user confirmed in chat that everyone on this list agreed to hear from
    them. Only then are rows with no consent column kept. A "no" in a consent column
    is never overridden.

Prints JSON:
    {"summary": {"rows", "kept", "excluded", "batches", "batch_size"},
     "batches": [[{"email", "first_name"}, ...], ...],
     "excluded": [{"row", "email", "reason"}, ...]}
Removes: no or invalid email, duplicates, unsubscribed or suppressed, no consent.
Stdlib only.
"""

import argparse
import csv
import io
import json
import re
import sys

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9-]{1,63})*\.[A-Za-z]{2,}$")
YES = {"yes", "y", "true", "1", "subscribed", "opted in", "opt in", "opt-in", "agreed",
       "granted", "consented", "x", "✓"}
NO = {"no", "n", "false", "0", "unsubscribed", "opted out", "opt out", "declined",
      "not subscribed", "non-subscribed", "withdrawn"}

COLS = {
    "email": ["email", "e-mail", "email address", "e-mail address", "emailaddress", "mail"],
    "first": ["first name", "firstname", "first_name", "given name"],
    "name": ["name", "full name", "fullname", "contact name", "contact"],
    "consent": ["consent", "opt in", "opted in", "opt-in", "optin", "subscribed",
                "marketing", "marketing consent", "email consent", "gdpr",
                "marketing email consent", "email opt in", "marketing opt in"],
    "unsub": ["unsubscribed", "opted out", "opt out", "opt-out", "do not email",
              "unsubscribe", "email opt out", "unsubscribed from all email",
              "hs email optout"],
}


def norm(h):
    return re.sub(r"[\s_]+", " ", (h or "").strip().lower())


def pick(headers, key):
    want = COLS[key]
    by_norm = {norm(h): h for h in headers}
    for w in want:
        if w in by_norm:
            return by_norm[w]
    return None


def load(a):
    if a.csv:
        raw = open(a.csv, "rb").read()
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(io.StringIO(text), dialect=dialect))
    data = json.load(open(a.json, encoding="utf-8"))
    if isinstance(data, dict):  # e.g. {"results": [{"properties": {...}}]}
        data = data.get("results") or data.get("contacts") or []
    rows = []
    for d in data:
        rows.append(d.get("properties", d) if isinstance(d, dict) else {})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv")
    ap.add_argument("--json")
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--suppress")
    ap.add_argument("--all-opted-in", action="store_true")
    a = ap.parse_args()
    if not a.csv and not a.json:
        print(json.dumps({"error": "Give --csv <file> or --json <file>."}))
        return 2
    try:
        rows = load(a)
        suppressed = set()
        if a.suppress:
            suppressed = {l.strip().lower() for l in open(a.suppress, encoding="utf-8") if l.strip()}
    except (OSError, ValueError, csv.Error) as exc:
        print(json.dumps({"error": "Could not read the list: %s" % exc}))
        return 2
    if not rows:
        print(json.dumps({"error": "The list has no rows."}))
        return 2

    headers = list({k for r in rows for k in r.keys() if k})
    c_email, c_first, c_name = pick(headers, "email"), pick(headers, "first"), pick(headers, "name")
    c_consent, c_unsub = pick(headers, "consent"), pick(headers, "unsub")
    if not c_email:
        print(json.dumps({"error": "No email column found. Columns: %s" % ", ".join(sorted(headers))}))
        return 2

    seen, kept, excluded = set(), [], []
    for i, r in enumerate(rows, start=2 if a.csv else 1):
        email = (r.get(c_email) or "").strip().strip("<>").strip()
        low = email.lower()

        def out(reason):
            excluded.append({"row": i, "email": email, "reason": reason})

        if not email:
            out("No email"); continue
        if not EMAIL_RE.match(email):
            out("Invalid email"); continue
        if low in seen:
            out("Duplicate"); continue
        seen.add(low)
        if low in suppressed:
            out("Opted out earlier (suppression list)"); continue
        if c_unsub and norm(str(r.get(c_unsub, ""))) in YES:
            out("Unsubscribed"); continue
        if c_consent:
            v = norm(str(r.get(c_consent, "")))
            if v in NO:
                out("Said no to marketing"); continue
            if v not in YES and not a.all_opted_in:
                out("Consent not recorded"); continue
        elif not a.all_opted_in:
            out("No consent column: ask the user to confirm everyone opted in"); continue
        first = (r.get(c_first) or "").strip() if c_first else ""
        if not first and c_name:
            first = ((r.get(c_name) or "").strip().split(" ") or [""])[0]
        kept.append({"email": email, "first_name": first.title() if first.isupper() or first.islower() else first})

    size = max(1, a.batch_size)
    batches = [kept[i:i + size] for i in range(0, len(kept), size)]
    print(json.dumps({"summary": {"rows": len(rows), "kept": len(kept), "excluded": len(excluded),
                                  "batches": len(batches), "batch_size": size,
                                  "consent_column": c_consent, "unsubscribed_column": c_unsub},
                      "batches": batches, "excluded": excluded}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
