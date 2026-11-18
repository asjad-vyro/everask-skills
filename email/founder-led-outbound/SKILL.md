---
name: Founder-Led Outbound
description: Finds companies that fit your ideal customer and show buying signals, scores them in Google Sheets and writes personal cold emails that go out from your Gmail only once you approve them. It drafts every reply, preps each booked call with a brief and a deck tailored from yours, then recaps the call and logs it in HubSpot. Just say who you sell to, like "UK fintechs with 50 to 200 staff that just raised".
---

# Founder-Led Outbound

Runs a founder's outbound loop without a sales team: find companies that match the
ideal customer and show a real buying signal (new funding, hiring, a new leader), score
them in a Google Sheet, write each decision-maker one personal email grounded in
something true and sourced, send the batch the founder approves from their own Gmail,
draft every reply, prep each booked call with a one-page brief and a tailored deck, and
recap the call and log it in HubSpot. It never sends an email, reply or follow-up, and
never writes to HubSpot, without the user's say-so. It only reads LinkedIn.

## When to Use

- "Find [type of company] in [region] that just raised and email their [role]."
- "Fill my pipeline: B2B SaaS, 50 to 200 staff, hiring sales, UK."
- "Check my replies and draft answers."
- "I have a call with [company] tomorrow, prep me."
- "Just finished the call with [company]. Send the recap and update HubSpot."

## Start Here

When this skill is open, treat the user's message as the start of the pipeline, not as
a plain search. "UK fintechs that just raised", "Series A dev-tool startups in Berlin"
or just "logistics companies hiring ops leads" all mean: run this pipeline for that
ideal customer. The user should not have to spell out the steps.

- Begin at step 1 straight away. Do not ask "do you want me to look for buying
  signals?": that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. Those pauses protect the user's inbox, domain and reputation, so
  never skip them, even if the user says "do everything".
- To start you need two things: who they sell to (type of company, and a region) and,
  in one line, what they sell (it decides which buyer and which signals matter). If
  either is missing, ask for both in one short `clarify` question, then go.
- A returning user re-enters where they are: "check replies" → step 5; "prep my call
  with X" → step 6; "the call with X is done" → step 7; "next batch" → step 1 for the
  same profile, skipping everyone already in the sheet.

## Prerequisites

Connected apps (check each with `search_connector_tools` at the step that needs it;
when a required one is missing, call `report_missing_connector_access` for it instead
of explaining in prose):

| App | For | Needed at step |
|---|---|---|
| Vibe Prospecting | Companies matching the profile, with decision-maker contacts | 1 (else another connected prospecting app, else `web_search` with emails left blank) |
| Google Sheets | The scored account list | 2 on |
| LinkedIn | Reading a contact's recent public posts, read only | 3 (else public posts via `web_search`/`web_extract`) |
| Gmail | Emails, replies, follow-ups and recaps from the user's own account | 4 on |
| Google Calendar | Finding booked calls | 6 (else the user names the call) |
| Fathom | Call transcripts | 7 (else another connected recorder, or a pasted transcript or uploaded recording) |
| HubSpot | Contacts, emails, call notes and deal stages | 7 |
| Calendly | Optional: any booking link works | Optional |

Someone finding accounts for the first time does not need HubSpot or Fathom yet.

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Who they sell to (industry or company type, region) and what they sell in one line | Start | None: ask |
| Company size | Never ask | 10–200 staff |
| Buyer role | Never ask | The person who owns the problem the product solves (founder/CEO under 50 staff) |
| Buying signals | Never ask | Funding in the last 12 months, hiring for a related role, a new leader in the buyer's area |
| How many accounts / emails | Never ask | Find 30, email up to 20 per day |
| Booking link (Calendly or any URL) | Step 4 | None: ask |
| Sender name, signature, business postal address | Step 4 | None: ask (cold email must carry a real postal address) |
| Proof they can use (customers they may name, results they can back up) | Step 4 | Leave the proof line out |
| Pitch deck (.pptx preferred, or PDF) | Step 6 | None: ask |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify` message,
then continue. Show the defaults you used in the step 2 summary so the user can
change them at the Stop.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps below in
order without pausing between them, except at every **Stop**, where you wait for the
user. Name the profile (e.g. "UK fintechs, 50–200") or the company in every update.
Templates for the sheet, every email, the brief, the deck changes and the HubSpot
update are in `references/templates.md`: read it before step 2.

## Procedure

### 1. Find

Search Vibe Prospecting through its connector for companies that fit the profile
(industry, size, region) with one decision-maker per company in the buyer role: name,
title, work email, company domain, staff count. Collect about 30. If Vibe Prospecting
is not connected, use another connected prospecting or contact-data app; if there is
none, find companies with `web_search` (funding news, job posts, leadership
announcements) and take the decision-maker's name and title from the company's own
site or a press release. Emails come only from a prospecting connector or a page that
publishes them; otherwise leave the email blank. Never build one from a pattern
(first@company.com).

Then confirm each company's signals yourself with `web_search` and `web_extract`:
the funding announcement, the job post, the leadership news. Record each signal with
its type, a short detail, its date and its source URL. A signal you cannot link to
does not count.

Every company, contact and signal must come from a live source read in this run, with
its link kept next to it. If neither a prospecting connector nor `web_search` is
available, stop here and call `report_missing_connector_access` for Vibe Prospecting.
Do not list companies or people from memory, and do steps 1 to 3 yourself: never hand
sourcing to `delegate_task`.

### 2. Score

Write the accounts and the profile to a JSON file (shape in `references/templates.md`)
and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/score_accounts.py" --file accounts.json
```

It scores 0–10: up to 5 for fit (size, industry, region, a decision-maker in the
target role) and up to 5 for signal strength (recent funding counts most; only sourced
signals count). Pass the sheet's existing domains and anyone opted out as
`exclude_domains`. The script's output is the only source of scores; never change a
score by judgement. Read its `warnings` (unsourced or future-dated signals) and fix the
data, not the score.

Create a Google Sheet named "Outbound: <profile>" with the columns in
`references/templates.md`, one row per account, sorted by score, and share the link.
Accounts with no email get status "No email"; UK or EU sole traders and partnerships,
and anyone in Germany, get "Consent needed".

**Stop.** Show the top of the sheet, the defaults you used and how many have an email,
and ask the user to remove any accounts they do not want. As soon as they answer, go
straight on through steps 3 and 4.

### 3. Personalise

For the top accounts with an email (up to 20), read the contact's recent LinkedIn
posts and the company's latest news. LinkedIn is read only: use the LinkedIn connector
only if it can read that person's public posts; otherwise find public posts with
`web_search` (e.g. `site:linkedin.com/posts "<name>" <company>`) and read them with
`web_extract`. Never send a connection request, message or like, and never log into
LinkedIn in the browser.

Write one personal line per person: true, specific, and about something they said or
did, with the source link in the sheet's "Personal line source" column. If there is
nothing real and recent, write "Nothing personal found" in the sheet and use the
company signal instead (its source link goes in the same column). Never invent a post,
quote, mutual connection, event or result.

### 4. Draft the batch

If the booking link, sender name, signature or postal address is missing, ask for
them (and for proof they can use) in one `clarify` message. Draft one email per
account, up to 20 (template in `references/templates.md`, under 100 words): the
personal line, one sentence on the problem, one proof point from the user's own proof
(leave it out if they gave none), a soft ask, the booking link, the opt-out line and
the postal address. Then write the batch to JSON and check it:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/check_batch.py" --file batch.json
```

It flags anything over 100 words, a missing opt-out, address or booking link, unfilled
placeholders, a personal line with no source, a domain that does not exist, opted-out
or duplicate recipients, consent cases (UK/EU sole traders and partnerships, Germany)
and promise words, and gives each clean email a send slot within today's cap. Fix
every problem or drop that email; never send one the script did not pass.

**Stop.** Show the whole batch with the check summary. Send only the emails the user
approves, one at a time from their Gmail in send-slot order, a few minutes apart, never
more than 20 a day including follow-ups. Mark each "Emailed" with the date in the
sheet.

### 5. Replies

Find replies in the Gmail threads of every "Emailed" or "Followed up" row. Sort each
one and draft a response (templates in `references/templates.md`):

- interested → thank them and give the booking link;
- question → a short, true answer (only facts the user gave; ask the user when unsure);
- not now → a polite close, and the date they suggested in the sheet's notes;
- opt-out → mark "Opted out" in the sheet straight away, and draft a one-line
  confirmation;
- out of office → no reply; note the return date.

Update each row's status.

**Stop.** Show every draft. Send each one only after the user approves it.

### 6. Before each call

Find booked calls in Google Calendar (next 7 days) whose attendees' email domains match
an account in the sheet, or take the call the user names. Mark the row "Booked". If you
do not have their pitch deck yet, ask for it now.

For each call:

1. Refresh the facts with `web_search`/`web_extract` (latest news, the person's role)
   and write a one-page brief with `generate_document` (outline in
   `references/templates.md`): company, person, signals with links, likely pains
   (marked as guesses), questions to ask, the user's most relevant proof.
2. Tailor the deck. A .pptx: inspect it with `import_pptx`, then `edit_pptx` to keep
   their design and change only what the template lists (their company name on the
   title slide, a slide on their likely use case, the most relevant proof first). A
   PDF or other format: read it with `media_analyze` and rebuild a tailored version
   with `generate_design_slides`. Use only the user's own claims and proof. Never put
   the prospect's logo or another customer's name in the deck unless the user says
   they may.

Give the user the brief and the deck. Nothing is sent to the prospect.

### 7. After each call

Get the transcript from Fathom through its connector. If Fathom is not connected, use
another connected meeting recorder, or ask the user to paste the transcript or upload
the recording and transcribe it with `audio_transcribe`. Never write a recap without
a transcript or the user's notes.

1. Draft the recap email (template in `references/templates.md`): what we heard, what
   we agreed, the next step with a date. Use only what the transcript says; if no date
   was agreed, propose one and say so.
2. Prepare the HubSpot update: the contact and company (find before creating, never
   duplicate), the outbound emails and the recap, a call note from the transcript, and a
   deal at the stage that fits. Read the user's real pipeline stages from HubSpot first;
   never invent stage names or deal amounts.

**Stop.** Show the recap and the exact HubSpot changes. Send the recap from Gmail and
write to HubSpot only after the user approves. Aim to have the draft ready within the
hour of the call. Mark the row "Called" (or "Deal") in the sheet.

## Automation (offer at the end, never set up unasked)

Offer these, and create the ones the user accepts with `cronjob` (`action: create`,
`skills` set to this skill's name as you loaded it). Cron runs have no one to ask, so
each prompt must be self-contained (profile, sheet link, booking link, sender details)
and must leave sending and HubSpot writes for the user:

- **Weekdays 8:00:** find and score new accounts for the same profile (skip anyone in
  the sheet or opted out), add them to the sheet, personalise, and save up to 20 emails
  minus today's follow-ups as Gmail drafts, each passed by `check_batch.py`. Also prep
  briefs and decks for today's booked calls. Reply with the list and the draft links
  for approval.
- **Daily 9:00:** run `followups_due.py` on the sheet; for each row due (3 days, no
  reply), save one short follow-up as a draft in the same thread and mark "Follow-up
  drafted"; mark rows that already had their one follow-up "No reply". Also draft
  responses to new replies and mark opt-outs. Never a second follow-up.
- **Weekdays, hourly 10:00–19:00:** for calls that ended since the last run and have a
  transcript, save the recap as a Gmail draft and list the HubSpot changes in the reply
  for the user to approve. Do not write to HubSpot.

```
python3 "${COMPUTER_SKILL_DIR}/scripts/followups_due.py" --file rows.json
```

## Guardrails

- Nothing goes out without approval: batches, replies, follow-ups, recaps. HubSpot is
  written only after the user approves the exact changes.
- Every personal line is true of that person, with its source link; never invent a
  post, quote, mutual connection or result. Every company, contact and signal comes
  from a live source read in this run. Never guess an email address.
- Cold-email rules: every email has an opt-out line and the user's postal address;
  anyone who opts out is marked "Opted out" and never emailed again; respect the rules
  where the recipient is (GDPR and PECR in the UK and EU, where sole traders and
  partnerships count as individuals; Germany needs prior consent even for B2B;
  CAN-SPAM in the US). "Consent needed" rows are not emailed unless the user confirms
  consent.
- LinkedIn is read only: no connection requests, messages, likes or logins.
- No promises of results, ROI or numbers the user cannot back up; proof comes only from
  the user.
- Small volume from the user's own account: at most 20 cold emails a day including
  follow-ups, sent one at a time, a few minutes apart. One follow-up per person, then
  stop.

## Pitfalls

- **Inventing contacts when the prospecting app is missing.** Leave the email blank
  and mark "No email"; a guessed address bounces and hurts the user's domain.
- **A "personal" line that is really a guess** ("Congrats on the growth!"). If there
  is no sourced post or news, say so and use the sourced company signal.
- **Old or unlinked signals.** A 2023 raise is not a buying signal; the score script
  gives it nothing. Do not paper over it in the email.
- **Sending a batch without `check_batch.py`.** It catches the missing address, the
  leftover `<first name>` and the opted-out recipient a tired founder will miss.
- **Duplicates in HubSpot.** Search for the contact and company by email and domain
  before creating either.
- **Recap promises nobody made.** Next steps and dates come from the transcript, or are
  clearly marked as proposed.

## Verification

- Every row in the sheet has a source link for its signal, and every emailed row has a
  "Personal line source".
- Scores in the sheet match `score_accounts.py`'s output exactly.
- Every sent email passed `check_batch.py` and was approved by the user; the sheet
  shows "Emailed" with a date for each.
- No row marked "Opted out" or "Consent needed" received an email.
- HubSpot changes match what the user approved, with no duplicate contacts.
