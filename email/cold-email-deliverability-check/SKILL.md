---
name: Email Deliverability Check
description: >
  Reviews a cold or bulk email draft and its sending setup (SPF, DKIM, DMARC, domain, volume, links, opt-out, regional law) and returns a spam-risk report with a ranked fix list.
  Use it for "why are my emails going to spam", "check my SPF record", "review this cold email for deliverability", "is my domain going to get blacklisted", "domain warmup plan", "do I need an unsubscribe link".
---

# Email Deliverability Check

A good result is one reply holding a verdict (BLOCKED, AT RISK or CLEARED), findings grouped by layer with a severity and an evidence label on each, a fix list in the right order, and a measurement plan. It covers deliverability hygiene and compliance only. It never helps evade spam filters.

## Hard rules

- Work from what the user gave: the draft, pasted DNS records, bounce codes, volumes, regions. Never open with questions. If something is missing, write "not given", state the assumption you used, and carry on. Use `clarify` only if there is no draft, no records and no description of the setup at all.
- Every fact about the user's setup comes from what they pasted. Do not invent a domain, spam rate, volume, bounce figure or record. Do not invent statistics. The numbers in the reference files are labeled by source: repeat them with their label.
- Do all counting (words, links, images, SPF lookups, dates, percentages) in `execute_code` and copy the results. No mental maths.
- The result is not legal advice. Say so in one line in the report.
- Sending stays a draft. Never send an email.
- Do not build a file unless the user asks for one. The report goes in the reply, in full.

## Evidence labels

Tag each claim: **provider-verified** (mailbox-provider or standards documentation), **vendor** (tool-vendor claim, no independent method), **contested** (credible sources disagree), **practitioner** (expert consensus, uncontrolled). Never present a vendor number as a rule. Where no evidence exists, say so.

## The order that decides placement

Report in this order, because it is what most advice gets backwards:

1. **Authentication is a hard gate.** SPF, DKIM, DMARC alignment, valid PTR, TLS. A failure means rejection or spam-foldering, and no copy edit compensates.
2. **Sender reputation and complaints** are the biggest lever once mail is accepted. Spam-button complaints are the largest negative signal. It is a standing job, not a one-time fix.
3. **Content structure** is a distant tiebreaker: plain-text part, image weight, link domains, tracking, opt-out.
4. **"Spam trigger words" are mostly folklore.** No independent study ties word choice or link count to spam placement. Say that plainly and never make a banned-word list the main fix.

## Step 1: Screen the request

Decline any part that asks to mask or fake the sender identity, use lookalike or deceptive domains, fake `Re:`/`Fwd:` threads, use reply-bot warmup networks or artificial engagement, evade volume limits, or hide or discourage an opt-out. Say so in one sentence and continue with the rest. The line is identity, not count: several owned, honestly identified, correctly authenticated domains are fine; domains meant to disguise who is sending or to restart a burned reputation are not.

## Step 2: Frame the job

In two lines, state: regime (B2B cold, unsolicited, or B2C bulk/opt-in), daily volume, recipient regions, sending-domain setup, and which of these were not given (with your assumption). If the regime is unclear, assume B2B cold. If the regions are unclear, assume US and EU and say the legal answer changes by region.

If the user pasted records, run the arithmetic and checks in `execute_code` where useful. If they gave a domain but no records, you may try `dig TXT <domain> +short` in `terminal`; if `dig` is missing or fails, say so and ask them to paste the lookups (`dig TXT <domain>`, `dig TXT <selector>._domainkey.<domain>`, `dig TXT _dmarc.<domain>`) in a "to verify" line, and carry on.

## Step 3: Authentication layer

Read `references/authentication-and-setup.md` first. Check every record or description the user gave against it:

- SPF: exactly one record; ends in `-all` or `~all`, not `+all` (`+all` authorises every sender on earth: critical, BLOCKER) and not `?all`; count `include:`/`a`/`mx` lookups against the 10-lookup cap; flag a second SPF record.
- DKIM: present for the sending selector, key length, split-string problems.
- DMARC: record exists at `_dmarc.<domain>`; policy `p=none`, `quarantine` or `reject`; `rua=` set; alignment of the From domain with SPF or DKIM.
- Domain architecture: primary corporate domain used for cold volume is a BLOCKER; the default recommendation is one dedicated, honestly identified sending domain, then a subdomain, then a fleet only when volume proves one domain cannot carry it (one suppression list must span every domain).
- Bulk-sender thresholds (5,000/day) versus the Google Workspace 2,000/day account cap: never conflate them.

Any failure here is a BLOCKER. Say that no copy edit compensates and keep the content findings short and labeled.

## Step 4: Reputation layer

Read `references/reputation-and-measurement.md` when the user gave volumes, bounce codes, a spam rate, a blocklisting, a warmup question or a burned domain. Check spam rate against the thresholds (Gmail: below 0.10% target, never 0.30%), bounce codes, dashboard enrollment (Google Postmaster Tools, DMARC aggregate reports, Microsoft SNDS/JMRP, Yahoo complaint feedback loop), and ramp sanity. A burned domain gets the remediation path (identify the listed asset, stop sending, fix the cause, one removal request, retire or rehabilitate), not a copy review. Warmup numbers are vendor conventions: label them and never present "30-50 a day per mailbox" as a provider limit.

## Step 5: Content layer

Read `references/content-review.md` when a draft was given. Run the ten structural checks on the draft. Use `execute_code` to count words, links, images, link domains and any shortener; look for a tracking pixel (1x1 image, tracking-domain links), a missing plain-text part, a missing opt-out, a fake `Re:`/`Fwd:` subject, ALL CAPS and excess punctuation. Give each finding its severity from the reference. Flag the subject line only for deception or placement-damaging structure; do not score it for opens or write variants. Do not hand back a word-list score as the fix. If you suggest a rewritten passage, keep it plain, human and short, and mark it as a suggestion.

## Step 6: Compliance layer

Read `references/compliance-by-region.md` for every recipient region. Check consent or lawful basis, sender identity, postal address where required, honest subject, working opt-out and its deadline. A miss is a BLOCKER for that region's recipients. Penalty figures and national rules change: if you quote one, run one `web_search` to confirm it and link the source, or label it "as listed in the reference, verify before relying on it".

## Step 7: Write the report

Run the gate: any unresolved BLOCKER means BLOCKED; no BLOCKER but unresolved RISKs means AT RISK; zero of both means CLEARED (ADVISORY findings may ship if acknowledged). Never soften a BLOCKER to get a pass. Use this shape, filled only from the user's input:

```
# Deliverability Review: <sender or "sender not given"> to <audience>

Verdict: BLOCKED | AT RISK | CLEARED
Regime: <B2B cold | B2C bulk> · Volume: <the user's figure or "not given"> · Regions: <list> · Assumptions: <list>

## Findings
### 1. Authentication and setup
- [BLOCKER | RISK | ADVISORY | PASS] <finding quoting the user's record or line> (<evidence label>)
### 2. Reputation and measurement
- ...
### 3. Content structure
- ...
### 4. Compliance
- ...

## Fix list (do in this order)
1. <DNS and setup fixes first, then domain, dashboards, compliance, then content edits>

## Measurement plan
- <dashboards to enroll> · <metrics to watch> · <thresholds that trigger action, with their evidence label>

Gate: <n> BLOCKER, <n> RISK, <n> ADVISORY gives <verdict>. Not legal advice.
```

Use real counts for the gate line. Put corrected records or a rewritten opt-out line directly under the relevant fix when the user's input makes that possible (for example a corrected SPF record built from the includes they listed).

## Things to get right

- B2B cold versus B2C bulk differ: consent basis, one-click `List-Unsubscribe` (a bulk/marketing requirement), warmup unit (mailboxes and domains versus dedicated IPs), feedback loops, list hygiene. Split them every time. Authentication, complaint math and structural checks are the same for both.
- Open rate is not a placement KPI: Apple Mail Privacy Protection pre-fetches pixels, and Google states it does not track opens. Use replies, bounces and complaints.
- A seed-list "inbox" result is directional, not proof.
- Gmail has no per-message complaint feedback loop and no delisting process.
- Provider rules have dates (Gmail and Yahoo from February 2024, Microsoft consumer from May 5, 2025). Do not claim one universal deadline.
- A deadline inside a week promotes authentication and demotes anything needing a warmup period. A "keep sending long term" goal promotes reputation work to first.
