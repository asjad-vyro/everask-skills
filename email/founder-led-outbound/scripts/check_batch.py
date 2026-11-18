#!/usr/bin/env python3
"""Check a batch of cold-email drafts before the user approves them, and plan the sends.

Usage:
    python3 check_batch.py --file batch.json [--no-dns]

batch.json:
{
  "booking_link": "https://calendly.com/...",
  "postal_address": "12 High St, Leeds LS1 1AA, UK",
  "daily_cap": 20,                 # optional, default 20
  "spacing_minutes": 4,            # optional, default 4
  "sent_today": 0,                 # optional, emails already sent today
  "opted_out": ["a@b.com", "c.com"],  # optional, emails or whole domains
  "emails": [
    {"to": "jane@acme.com", "company": "Acme", "region": "United Kingdom",
     "entity_type": "company" | "sole_trader" | "partnership" | "",
     "consent": false,
     "subject": "...", "body": "...",
     "personal_source": "https://..."}   # link behind the personal line or signal
  ]
}

Prints JSON: {"summary": {...}, "emails": [...]}. Each email gets:
  "ok"        true when it can go out as written
  "problems"  must be fixed (or the email dropped) before sending
  "warnings"  worth a look, not blocking
  "words"     body word count, not counting the postal address
  "domain_resolves"  true / false / null (null = could not check)
  "send_slot" 1, 2, ... for ok emails within today's cap (null otherwise);
  "send_after_minutes"  minutes after the first send (slot 1 = 0)

Rules checked: under 100 words; an opt-out line; the postal address; the booking
link; no unfilled <placeholders>; a source link for the personal line; a valid
address whose domain resolves; not opted out; no duplicate recipients; consent
needed for UK/EU sole traders and partnerships and for Germany; no promise words.

Stdlib only. Read-only: the only network use is a DNS lookup of each domain.
"""

import json
import re
import socket
import sys

WORD_LIMIT = 100
EMAIL = re.compile(r"^[A-Za-z0-9._%+'-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$")
PLACEHOLDER = re.compile(r"<[^<>\n]{1,60}>|\{\{[^}]*\}\}|\[(?:first name|name|company|link|insert)[^\]]*\]|\bTODO\b|\bTBD\b|XXX", re.I)
OPT_OUT = re.compile(
    r"no thanks|unsubscribe|opt[ -]?out|won'?t (?:email|contact|write)|"
    r"not (?:hear|email)\w* (?:from me )?again|stop (?:emailing|contacting)|"
    r"(?:rather|prefer) not (?:to )?hear", re.I)
PROMISES = re.compile(
    r"\bguarantee[ds]?\b|\brisk[- ]free\b|\b\d+x\b|\bdouble your\b|\btriple your\b|"
    r"\bROI of\b|\bwill (?:increase|boost|grow) your\b", re.I)
UK = {"uk", "united kingdom", "great britain", "gb", "england", "scotland", "wales", "northern ireland"}
EU = {"austria", "belgium", "bulgaria", "croatia", "cyprus", "czechia", "czech republic",
      "denmark", "estonia", "finland", "france", "germany", "greece", "hungary", "ireland",
      "italy", "latvia", "lithuania", "luxembourg", "malta", "netherlands", "poland",
      "portugal", "romania", "slovakia", "slovenia", "spain", "sweden", "de", "fr", "es",
      "it", "nl", "ie", "eu"}
STRICT_B2B = {"germany", "de", "deutschland"}


def squash(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def resolves(domain, use_dns):
    if not use_dns:
        return None
    try:
        socket.setdefaulttimeout(8)
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror as exc:
        if exc.errno in (getattr(socket, "EAI_NONAME", -2), getattr(socket, "EAI_NODATA", -5)):
            return False
        return None
    except OSError:
        return None


def check(item, cfg, seen, use_dns, dns_cache):
    problems, warnings = [], []
    to = (item.get("to") or "").strip()
    body = item.get("body") or ""
    subject = item.get("subject") or ""
    addr = cfg.get("postal_address") or ""
    link = (cfg.get("booking_link") or "").strip()

    domain, dns = "", None
    if not to:
        problems.append("no recipient email: leave this account out, never guess one")
    elif not EMAIL.match(to):
        problems.append(f"'{to}' is not a valid email address")
    else:
        domain = to.split("@", 1)[1].lower()
        if domain not in dns_cache:
            dns_cache[domain] = resolves(domain, use_dns)
        dns = dns_cache[domain]
        if dns is False:
            problems.append(f"domain {domain} does not exist (DNS): the address is wrong")
        elif dns is None and use_dns:
            warnings.append(f"could not check domain {domain}")
    lowered = to.lower()
    if lowered and lowered in seen:
        problems.append("duplicate recipient in this batch")
    seen.add(lowered)
    opted = {o.lower().strip() for o in cfg.get("opted_out") or []}
    if lowered and (lowered in opted or domain in opted):
        problems.append("recipient opted out: never email again")

    text = body.replace(addr, " ") if addr else body
    words = len(re.findall(r"\b[\w'’-]+\b", text))
    if words >= WORD_LIMIT:
        problems.append(f"{words} words: must be under {WORD_LIMIT} (not counting the address)")
    if not OPT_OUT.search(body):
        problems.append("no opt-out line")
    if not addr:
        problems.append("no postal address given for the batch")
    elif squash(addr) not in squash(body):
        problems.append("postal address missing from the email")
    if not link:
        problems.append("no booking link given for the batch")
    elif link.rstrip("/") not in body:
        problems.append("booking link missing from the email")
    ph = PLACEHOLDER.findall(subject + "\n" + body)
    if ph:
        problems.append("unfilled placeholder(s): " + ", ".join(sorted(set(ph))[:5]))
    if not subject.strip():
        problems.append("no subject line")
    if not re.match(r"https?://", (item.get("personal_source") or "").strip()):
        problems.append("no source link for the personal line: rewrite it from a real source or use the sourced company signal")
    promise = PROMISES.findall(subject + " " + body)
    if promise:
        warnings.append("promise words (" + ", ".join(sorted(set(p.lower() for p in promise))) + "): keep only claims the user can back up")

    region = squash(item.get("region"))
    entity = squash(item.get("entity_type")).replace(" ", "_")
    consent = bool(item.get("consent"))
    if not consent:
        if region in STRICT_B2B:
            problems.append("Consent needed: Germany requires prior consent even for B2B cold email")
        elif (region in UK or region in EU) and entity in ("sole_trader", "partnership"):
            problems.append("Consent needed: sole traders and partnerships count as individuals (UK PECR / EU rules)")
        elif region in UK or region in EU:
            if entity not in ("company", "ltd", "limited_company", "corporate"):
                warnings.append("UK/EU recipient: confirm it is a company, not a sole trader or partnership")
        elif not region:
            warnings.append("recipient region unknown: check the rules where they are")
    return {"to": to, "company": item.get("company", ""), "ok": not problems,
            "problems": problems, "warnings": warnings, "words": words,
            "domain_resolves": dns}


def main(argv):
    if "--file" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Could not read input: {exc}"}))
        return 1
    use_dns = "--no-dns" not in argv
    cap = int(cfg.get("daily_cap") or 20)
    spacing = int(cfg.get("spacing_minutes") or 4)
    room = max(cap - int(cfg.get("sent_today") or 0), 0)
    seen, cache, results = set(), {}, []
    for item in cfg.get("emails") or []:
        results.append(check(item, cfg, seen, use_dns, cache))
    slot = 0
    for r in results:
        r["send_slot"], r["send_after_minutes"] = None, None
        if r["ok"]:
            if slot < room:
                slot += 1
                r["send_slot"], r["send_after_minutes"] = slot, (slot - 1) * spacing
            else:
                r["warnings"].append(f"over today's cap of {cap}: send tomorrow")
    summary = {"total": len(results), "ok": sum(r["ok"] for r in results),
               "need_fixes": sum(not r["ok"] for r in results),
               "scheduled_today": slot, "daily_cap": cap, "spacing_minutes": spacing}
    print(json.dumps({"summary": summary, "emails": results}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
