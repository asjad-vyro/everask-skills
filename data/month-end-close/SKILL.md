---
name: Month-End Close
description: 'Closes the month''s books: reads the receipts your team sends on WhatsApp, matches and categorises them against QuickBooks, reconciles Stripe payouts to Mercury and builds an Excel close pack with an exceptions tab. After your review it posts the approved entries, chases missing receipts on Slack and drafts the CFO summary in Outlook. Just name the month, like "close October".'
---

# Month-End Close

Runs a small finance team's month-end close for one month: read the receipt photos
staff sent on WhatsApp, match them to the month's uncategorised QuickBooks
transactions and propose categories, tie every Stripe payout to its Mercury deposit,
and build an Excel close pack on live formulas with an Exceptions tab. After the user
has decided every exception, it posts the approved entries to QuickBooks with their
receipts, chases each person missing a receipt in a private Slack message, and drafts
the CFO's summary (and memo, if asked for) in Outlook. It never writes to QuickBooks,
sends a Slack message or emails the CFO without the user's say-so, and it never moves
money or changes a bank or Stripe setting.

## When to Use

- "Close October." / "Run month-end for last month."
- "Match this month's receipts to QuickBooks and reconcile Stripe."
- "I've reviewed the exceptions, push the approved ones to QuickBooks."
- "Chase everyone who's still missing a receipt."
- "Write the CFO's travel allowance memo and draft the close summary."

## Start Here

When this skill is open, treat the user's message as the start of the close, not as a
question about bookkeeping. "Close October", "month-end" or just "do the close" all
mean: run this pipeline for that month. The user should not have to spell out the
steps.

- Begin at step 1 straight away. Do not ask "do you want me to collect the receipts
  first?": that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. They protect the books, the team and the CFO, so never skip them,
  even if the user says "do everything".
- The only thing needed to start is the month. If none is named, close last month
  (say which month in your first update); never ask for it.
- If the user returns with "I've reviewed the exceptions", "push to QuickBooks",
  "chase the missing receipts" or "write the CFO summary", pick up at step 5, 6 or 7
  for that month, using the close pack already built (ask for it in one `clarify` if
  it is not in this chat).

## Prerequisites

Connected apps. Check each one with `search_connector_tools` at the step that needs
it, not all at the start; when a required one is missing, call
`report_missing_connector_access` for it instead of explaining in prose.

| App | For | Needed at step |
|---|---|---|
| WhatsApp | Receipt photos staff sent to the user's WhatsApp Business number | 1 (else photos uploaded in this chat) |
| QuickBooks | Uncategorised transactions, last month's totals, posting entries with receipts | 2, 4, 5 |
| Stripe | Payouts and the balance transactions inside each one (read only) | 3 |
| Mercury | Bank deposits and card holder names (read only) | 2, 3 (else a CSV export the user uploads) |
| Excel / OneDrive | Saving the close pack where the team can edit it | 4 (else a download link) |
| Slack | One private message per person missing a receipt | 6 |
| Outlook | The summary email to the CFO, saved as a draft | 7 |
| Google Docs | The CFO memo | 7 (else `generate_document`) |

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Month to close | Never ask | Last month |
| Categorisation rules or chart of accounts ("Uber -> Travel") | Step 2 | Proposed from the last 3 months of categorised QuickBooks transactions |
| Materiality threshold | Never ask | 75 in the books' currency: anything over it with no receipt is chased |
| Staff list with Slack handles | Step 6 | Match names to Slack users with the connector; ask only for names it cannot find |
| CFO's name and email | Step 7 | None: ask |
| The CFO's memo request (e.g. "travel allowance review with inflation and FX") | Step 7 | No memo |

Use anything the user already gave (an uploaded rules doc, a staff list) and never ask
for it again. When a step needs something missing, ask for all of that step's missing
inputs in one `clarify` message, then continue.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing between them, except at every **Stop**. Name the month (and the
company, once known) in every update. Keep the run's files in one folder,
`close-<YYYY-MM>/`. File shapes, message templates and the memo outline are in
`references/templates.md`: read it before step 1.

## Procedure

### 1. Collect receipts

Through the WhatsApp connector, list the messages with images or PDFs received from
the 1st of the month to 3 days after its end, and download each attachment. Read each
one with `media_analyze` (prompt in `references/templates.md`) and record merchant,
date, total, currency, tax, who sent it and the file name in `receipts.json`. A field
the receipt does not show stays empty; never guess it. Unreadable photos go on a list
for the user, not into the file.

If the WhatsApp connector is missing or cannot fetch media, call
`report_missing_connector_access` for WhatsApp and say the user can also upload the
receipt photos or PDFs in this chat; carry on with whatever is uploaded.

### 2. Match in QuickBooks

Pull the month's uncategorised transactions from QuickBooks (expenses and card lines
posted to "Uncategorized Expense" or with no account): id, date, payee or description,
amount, currency. Fill "spender" from the card holder name on the matching Mercury
card transaction where there is one; otherwise leave it blank. Save `txns.json`.

Rules: use the user's rules or chart of accounts if given (an uploaded doc or typed
lines, saved as `rules.txt`, one "merchant -> category" per line). If none, pull the
last 3 months of categorised QuickBooks expenses into `history.json` and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/propose_rules.py" --file history.json
```

Save its `rules_text` as `rules.txt` and list the proposed rules in your update: the
user approves them with the exceptions at step 4. Then match:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/match_receipts.py" --transactions txns.json \
  --receipts receipts.json --rules rules.txt --month <YYYY-MM> --threshold 75 > match.json
```

Each transaction comes back "matched" (same amount, date within 3 days, merchant
agrees), "likely" (needs a look) or "unmatched", with a proposed category. The script's
output is the only source of matches and categories; never change one from memory.

Every transaction and receipt must come from the connectors or files read in this
run. If QuickBooks is not connected, stop and call `report_missing_connector_access`;
never build the list from memory. Do steps 1 to 4 yourself; never hand them to
`delegate_task`.

### 3. Reconcile Stripe to Mercury

From Stripe, list the payouts whose arrival date falls in the month and, for each, the
balance transactions in it (`payout=<id>`). Save them as returned (amounts in cents)
in `payouts.json`, each with its `balance_transactions`. From Mercury, list the
account's credits from the 1st of the month to 4 days after its end into
`deposits.json`; if Mercury is not connected, ask the user to upload the month's CSV
export from Mercury instead. Then:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/reconcile_payouts.py" --payouts payouts.json \
  --deposits deposits.json > recon.json
```

It ties each payout to a deposit of the same amount within 1 day before to 4 days
after arrival, splits it into gross, refunds and fees, and lists payouts with no
deposit or a different amount, and Stripe deposits with no payout. Only read Stripe
and Mercury; never create, change or retry anything there.

### 4. Build the close pack

Pull last month's totals per expense account from the QuickBooks Profit and Loss
report into `last_month.json` (`{"Travel": 1840.20, ...}`), then:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/build_close_pack.py" --matches match.json \
  --recon recon.json --last-month last_month.json --month <YYYY-MM> \
  --currency <books currency> --company "<company>" --out close-pack-<YYYY-MM>.xlsx
```

Tabs: Summary, Receipts matched, Stripe reconciliation, Category totals, Exceptions.
Every total, difference, status and count is a live formula; never type a total into
the pack or rebuild it by hand. Save it to OneDrive through the Excel connector if
connected, and always deliver it with `publish_artifact`.

**Stop.** Show the Summary numbers and every Exceptions line (missing receipts,
check-match lines, uncategorised lines, payout differences, unusual categories) plus
the proposed rules. Ask the user to decide each line: Approve, Fix (with the change)
or Exclude, in the Decision column or in a reply. Nothing goes to QuickBooks until
every line has a decision. Write the decisions into the pack (rebuild it with the
fixes applied) and publish it again.

### 5. Push to QuickBooks

Post only the approved entries: every "matched" line not on the Exceptions tab, plus
the lines the user approved or fixed. For each, set the category (expense account)
and attach its receipt file. Hold back excluded lines and anything still undecided.
Report what was posted (count and total) and what was held back, line by line.

### 6. Chase missing receipts

From `missing_by_person` in `match.json` (and any missing-receipt lines the user kept
open), draft one Slack message per person: their transactions (date, merchant,
amount) and how to send the receipt (reply on WhatsApp with a photo). Template in
`references/templates.md`. Find each person's Slack user with the connector; ask the
user, in one `clarify`, only for the people you cannot find or who have no card
holder name.

**Stop.** Show every message. Send only the approved ones, each as a private direct
message, never in a channel. Note who was chased and when.

### 7. Report

If the CFO's name and email are missing, ask for them, and for any memo request, in
one `clarify`.

Memo (only when the CFO asked for one): find each external figure on an official
source with `web_search` and read it with `web_extract`: inflation from the national
statistics office (ONS, BLS, Eurostat), exchange rates from the central bank (ECB,
Federal Reserve H.10, Bank of England). Keep each figure's URL and date. Put the
figures in `memo_inputs.json` and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/allowance_review.py" --file memo_inputs.json
```

Write the memo with Google Docs if connected, else `generate_document`, using the
outline in `references/templates.md`. Every external number carries its source and
date; if a figure cannot be found on an official source, say so in the memo instead of
estimating it.

Then save the CFO summary as an Outlook draft (template in `references/templates.md`):
close status, totals from the Summary tab, open exceptions, the close pack and memo
attached. **Draft only; the user sends it.** Give the user the draft link.

## Automation (offer at the end, never set up unasked)

Offer these three, and create the ones the user accepts with `cronjob`
(`action: create`, `skills` set to this skill's name as you loaded it). Cron runs have
no one to ask, so each prompt is self-contained and nothing is posted or sent:

- **Daily, 18:00:** read the day's new receipt photos from WhatsApp and add them to
  the month's receipts log (an Excel file on OneDrive if connected); reply with what
  was filed and which photos could not be read.
- **Last working day of the month, 17:00** (schedule on days 28 to 31; the prompt
  checks it is the last weekday and otherwise stops): run steps 2 to 4 for the month,
  publish the close pack, and reply with the exceptions and the drafted Slack chases
  for the user to approve. Never post to QuickBooks or send a chase.
- **Third working day of the next month, 10:00** (schedule on days 1 to 7; the prompt
  checks the date): list everyone still missing a receipt with one short reminder
  each, drafted for the user to approve and send.

## Guardrails

- Nothing is posted to QuickBooks before the user has decided every line on the
  Exceptions tab, and only approved lines are posted.
- Never move money, pay a bill, issue a refund or change a bank or Stripe setting;
  Stripe and Mercury are read only.
- The close pack stays on live formulas; never hard-code a total.
- Slack chases are polite, private and specific: direct messages only, never a public
  channel, and only after the user approves them.
- The CFO email is a draft the user sends. Every external figure in a memo is cited
  with its source and date.
- Receipts are personal data: keep them in the close pack and QuickBooks only; never
  post them in Slack, email them or share them anywhere else.
- Every transaction, receipt, payout and figure comes from a connector, an uploaded
  file or an official source read in this run. Never fill a gap from memory; leave it
  blank and list it as an exception.

## Pitfalls

- Matching on amount alone. Two £23.40 Uber rides are different receipts; trust the
  script's one-receipt-per-transaction result and send "likely" lines to Exceptions.
- Converting Stripe amounts by hand. Pass payouts as Stripe returns them (cents); the
  script handles zero-decimal currencies such as JPY.
- Looking for deposits only inside the month. A payout arriving on the 31st lands in
  the bank days later: pull deposits to 4 days after month end.
- Typing a total into the pack to "fix" it. Fix the source line and rebuild; the
  formulas recalculate.
- Chasing someone for a transaction they did not make. If the card holder is unknown,
  ask the user who made it before drafting the chase.
- Mixed currencies. The Summary counts the books' currency only; list other-currency
  lines for the user rather than adding them in.

## Verification

- Every uncategorised transaction appears once in Receipts matched with a confidence.
- Every Stripe payout in the month shows Reconciled, Amount differs or No deposit,
  and the Summary close status reads from the formulas.
- QuickBooks shows only the approved entries posted, each with a receipt attached;
  the report lists what was held back.
- Every Slack chase sent was in the batch the user approved, as a direct message.
- The Outlook summary is a draft, not sent, with the pack (and memo) attached.
