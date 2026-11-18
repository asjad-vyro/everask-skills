---
name: Local Web Design Pipeline
description: Finds local businesses with weak or missing websites, builds each one a live demo site and pitches them from your Gmail. When one says yes, it writes the proposal and contract, sets up the Stripe deposit and monthly retainer, and sends a monthly search report. Just name a business type and an area, like "dentists in Leeds".
---

# Local Web Design Pipeline

Runs a web designer's whole sales loop for one business type in one city: find 20
local businesses, score how badly each needs a new site, build demo sites for the
ones the user picks, pitch them from the user's Gmail, and close the ones who say yes
with a proposal, contract, deposit invoice and monthly retainer. It never sends an
email, creates a charge or publishes a client site without the user's say-so, and it
never uses a real business's logo, photos or review text.

## When to Use

- "Find [business type] in [city] with bad or no websites and pitch them."
- "Build demo sites I can send to local [trade] businesses."
- "[Business] said yes, send the proposal and set up their retainer."
- "Send this month's reports to my web design clients."

## Start Here

When this skill is open, treat the user's message as the start of the pipeline, not
as a plain search. "Find futsal courts around me", "dentists Leeds" or just "gyms in
Austin" all mean: run this pipeline for that business type in that area. The user
should not have to spell out the steps or every detail.

- Begin at step 1 straight away. Do not ask "do you want me to find ones with weak
  websites?": that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. Those pauses protect the user's email, money and reputation, so
  never skip them, even if the user says "do everything".
- The only thing needed to start is a business type and an area. If the area is
  missing or only "around me / near me", ask for a city, town or postcode in one short
  `clarify` question, then go. If the business type is missing, ask for that too in
  the same question.
- If the user returns later with "X said yes" or "send the reports", jump to step 6 or
  7 for that client instead of starting over.

## Prerequisites

Connected apps (check with `search_connector_tools`; when a required one is missing,
call `report_missing_connector_access` for it instead of explaining in prose):

| App | For | Needed |
|---|---|---|
| Google Maps | Finding businesses with rating, reviews, phone, website | Step 1 (else `web_search`) |
| Google Sheets | The prospect sheet | Step 2 on |
| Gmail | Pitches, follow-ups, proposals, reports | Step 5 on |
| Stripe | Deposit invoice and monthly subscription | Step 6 |
| Google Search Console | The monthly report | Step 7 |
| Google Docs | Proposal and contract (else `generate_document`) | Optional |
| Netlify | Only if the user asks to host there; otherwise `sites` hosts everything | Optional |
| WhatsApp | Follow-ups only, after a business has messaged the user's WhatsApp Business number | Optional |

Check each app at the step that needs it, not all at the start. Someone finding
prospects for the first time does not need Stripe yet.

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Business type and area (city, town or postcode) | Start | None: ask |
| How many prospects / how many demos | Never ask | 20 prospects, top 5 demos |
| Booking link (Cal.com, Calendly or any URL) | Step 5 | None: ask |
| Sender name, signature, business postal address | Step 5 | None: ask (cold email must carry a real postal address) |
| Portfolio link | Step 5 | Leave out |
| Pricing and terms: build fee, retainer, what it includes, deposit %, payment terms | Step 6 | None: ask |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`
message, then continue.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps below in
order without pausing between them, except at every **Stop**, where you wait for the
user. Name the business type and city in every update so a
long run stays easy to follow. Templates for every email, prompt and document are in
`references/templates.md`: read it before step 3.

## Procedure

### 1. Find

Search Google Maps for "<type> in <city>" through the connector and collect 20
businesses (page through results if needed): name, address, rating, review count,
phone, website, Maps link. For each one with a website, look for a public email on
its contact page with `web_extract`, and note the contact form's URL if it has one.
Never guess an email address; leave it blank.
Skip chains and franchises (several locations under one brand): they buy websites
centrally.

Every business must come from a live source you read in this run: the Maps
connector, or else `web_search` results you can link to. Keep that link in the
"Maps link" column. If neither the Maps connector nor `web_search` is available, stop
here and call `report_missing_connector_access` for Google Maps. Do not list
businesses from memory and do not delegate the search to a subagent that has no web
tools: a made-up business, website or email sent in a pitch is worse than no list.
Do steps 1 and 2 yourself; never hand them to `delegate_task`.

### 2. Score

Write the list to a JSON file (`[{"name": ..., "website": ...}]`, website empty when
there is none) and run the audit:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/audit_sites.py" --file prospects.json
```

It scores 0 to 10 (10 = most in need): no site or a broken one scores 10; otherwise
2 points each for no HTTPS, not mobile friendly, slow, no booking or contact button,
and out of date. A `null` score means the site blocked the check: open it with
`browser_navigate` and `browser_snapshot`, score it by hand on the same five points,
and say so in the reason. Never score a site you have not looked at.

The script's output is the only source of scores. If it says a site does not resolve
(DNS), believe it: either the business has no working site (score 10), or the URL in
your list is wrong. Re-check the URL against the business's listing; never replace
the result with a judgement from memory or from a subagent.

Create a Google Sheet named "Prospects: <type> in <city>" with the columns in
`references/templates.md` (one row per business, sorted by score, highest first), and
share the link.

**Stop.** Show the top of the sheet and ask which to build, offering the top 5 as
the default choice. The user may also remove any business. As soon as they answer, go
straight on through steps 3 and 4.

### 3. Build demos

For each pick, build a one-page site with `sites` (`action: create`), one site per
business, using the demo prompt in `references/templates.md`. The site uses the
business's public facts (services, hours, address, phone) and a summary of what
reviewers praise, written fresh. It uses:

- a made-up logo mark and neutral imagery: never the business's own logo, photos or
  review text, unless the user says they have the owner's permission;
- one clear booking or call button;
- a small footer line: "Demo prepared for <business>. Not their official website."

### 4. Publish demos

Publish each with `sites` (`action: publish`, `name: <business-slug>-demo`) and write
the public link into the sheet's "Demo link" column. If the user asked for Netlify
and it is connected, deploy there instead, one site per business.

**Stop.** List the links and ask the user to open every demo before anything is
sent. Make the changes they ask for with `sites` `action: edit`.

### 5. Pitch

If the booking link or the sender's name, signature or postal address is missing, ask
for them now in one `clarify` message. Then draft one email per business (under 120 words, template in
`references/templates.md`): one specific, true thing about their current site from
the audit, the demo link, the booking link, an opt-out line and the user's postal
address. Show every draft together.

For businesses with **no public email**, prepare the best of these instead, in this
order (templates in `references/templates.md`):

1. **Contact form** (their site has one): the form message, ready for the user to
   paste and submit. Never submit a form yourself.
2. **WhatsApp tap-to-send link** (they have a phone number): a short WhatsApp pitch
   (under 60 words, with the demo link and an opt-out), turned into a link with
   `python3 "${COMPUTER_SKILL_DIR}/scripts/whatsapp_links.py" --country <calling code of
   the area> --file messages.json`. The link opens the user's own WhatsApp with the
   message typed in; nothing is sent until the user taps send. Put it in the sheet's
   "WhatsApp link" column.
3. **Call script** (always, when there is a phone number): 30 seconds, from the audit.

Never send a first message to a business through the WhatsApp connector. A business
number may only start a WhatsApp chat with people who agreed to it (Meta's WhatsApp
Business policy), and numbers found on Google Maps have not. Cold API messages get the
user's number reported and restricted.

**Stop.** Send only the emails the user approves, one at a time from their Gmail, a
minute or more apart. Mark each "Pitched (email)" with the date in the sheet. Give the
user the WhatsApp links, form messages and call scripts as a list to work through,
and ask them to tell you which they sent so you can mark them "Pitched (WhatsApp)",
"Pitched (form)" or "Called".

If a business replies to the user's WhatsApp Business number and the WhatsApp
connector is connected, you may answer it through the connector within WhatsApp's
24-hour reply window, showing each reply to the user before it sends.

UK prospects: sole traders and partnerships count as individuals under PECR, and the
same rules cover WhatsApp and text messages. Flag them in the sheet ("Consent needed")
and do not email them or prepare a WhatsApp link unless the user confirms they have
consent; a call script is fine.

### 6. Close

When the user says a business agreed:

1. Draft the proposal and contract from the user's terms with the templates (Google
   Docs if connected, otherwise `generate_document`). Do not invent terms the user did
   not give; leave a highlighted blank and say which.
2. Prepare in Stripe, but do not create yet: the customer, a deposit invoice
   (build fee × deposit %), and a monthly subscription for the retainer starting on
   the 1st of next month.
3. **Stop.** Show the proposal, the contract and the exact Stripe amounts, currency
   and client email. Create the Stripe objects and send the documents only after the
   user confirms all three.
4. When the client approves the final design: connect their domain with `sites`
   (`action: connect_domain`), give the user the DNS records for the client, and
   publish. Draft an email asking the client to add the user to Google Search Console
   for their domain.

Mark the row "Client" in the sheet.

### 7. Monthly report

For each active client, pull last month from Google Search Console: clicks,
impressions, average position, top 10 queries, top pages. Add booking-button taps
only if a real source tracks them. Build a one-page report (template in
`references/templates.md`) with "What we did this month" from the user's notes; ask
for them if you have none. Show the report and the email, and send from Gmail once
the user approves.

## Automation (offer at the end, never set up unasked)

Offer these three, and create the ones the user accepts with `cronjob`
(`action: create`, `skills` set to this skill's name as you loaded it). Cron runs
have no one to ask, so each prompt must be self-contained and must leave sending for
the user:

- **Weekdays 9:00:** find and score the next 10 prospects for the same type and city
  (skip anyone already in the sheet), build and publish their demos, and save the
  pitches as Gmail drafts. Reply with the list and the draft links for approval.
- **Daily:** for every row "Pitched" 4 or more days ago with no reply in the Gmail
  thread, save one short follow-up as a draft (template in references) and mark it
  "Follow-up drafted". Never a second follow-up. List rows "Pitched (WhatsApp)" or
  "Pitched (form)" 4 or more days ago with no reply, with a fresh follow-up link or
  message for the user to send themselves.
- **1st of each month, 9:00:** build every active client's report from step 7 and
  save each email as a Gmail draft for the user to send.

## Guardrails

- Nothing goes out without approval: emails, Stripe invoices and subscriptions,
  domain changes, publishing a client's final site.
- Never use a real business's logo, photos or verbatim review text in a demo.
- Every pitch has an opt-out line, and every email the user's postal address.
- First contact on WhatsApp is always a tap-to-send link the user sends from their own
  WhatsApp, never a message sent through the connector. Anyone who opts out
  is marked "Opted out" in the sheet and never emailed again.
- No promises of results, rankings, traffic or income in pitches, proposals or reports.
- Report numbers come only from Search Console or another real source. Never estimate
  or round up; write "not tracked" instead.
- Stripe is draft-first: create nothing until the user confirms the amount, currency
  and client.

## Pitfalls

- Scoring a blocked site as broken. A `null` score means "look in the browser", not 10.
- Trusting a "does not load (DNS)" result blindly. Before scoring it 10, confirm that
  website is the one the business's own Maps listing shows; a wrong or invented URL
  also fails DNS.
- Pitching on a weakness the site does not have. Quote only problems the audit or
  your own look confirmed.
- One site for all demos, or one demo per two businesses. Each business gets its own
  site and its own link.
- Asking for every app at the start. Ask for each one at the step that needs it.

## Verification

- The sheet has one row per business, a score and reason for each, sorted by score.
- Every demo link opens and carries the "Demo prepared for" line.
- Every sent email was in a batch the user approved; the sheet shows its status.
- Stripe objects match the amounts the user confirmed.
