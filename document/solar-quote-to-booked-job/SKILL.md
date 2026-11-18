---
name: Solar Quote to Booked Job
description: 'Turns a solar inquiry into a same-day quote: an intake form, a sized system and priced parts list in Excel from your own price list, a 25-year payback chart and a branded proposal. Once you approve, it sends the QuickBooks estimate, Stripe deposit link and proposal from Gmail, then books the site visit and the crew''s job card. Just name the customer or paste the inquiry, like "quote Jane Lee at 4 Elm Road".'
---

# Solar Quote to Booked Job

Runs a small solar installer's quote loop for one customer at a time: reply to the
inquiry with an intake form, research the roof, tariff and incentives, size the system
and price it from the installer's own price list in a workbook with live formulas,
chart 25 years of savings, write the branded proposal and contract, then send the
estimate, deposit link and proposal, book the site visit and brief the crew. Nothing
is quoted until the installer approves the sizing, and no email, estimate, payment
link, calendar invite or job card is created without their say-so. It never promises
savings and never moves money.

## When to Use

- "Quote Jane Lee at 4 Elm Road, her intake form just came in."
- "Reply to the new solar inquiries on Instagram and Facebook."
- "Size a system for this customer: here are their bills and roof photos."
- "Jane approved the sizing, send her the proposal and deposit link."
- "Jane paid the deposit. Book the site visit and make the job card."

## Start Here

When this skill is open, treat the user's message as the start of this pipeline, not
as a general question. "Quote the Lees", "new inquiry from Sam on Instagram" or just a
pasted customer message all mean: run this pipeline for that customer.

- Begin at the right step straight away. Do not ask "do you want me to size a
  system?": that is what this skill is for.
- A new inquiry (a message, a name with no intake yet) starts at step 1. A Typeform
  response, or bills and roof photos the user attached, start at step 2.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. They protect the installer's prices, money and reputation, so never
  skip them, even if the user says "do everything".
- The only thing needed to start is which customer (a name, a message or an
  address). If it is missing, ask for it in one short `clarify` question, then go.
- Returning users jump in: "approved the sizing" → step 4; "send the proposal" →
  step 6; "deposit paid" → step 7. Re-read that customer's files from earlier steps
  first; never rebuild them from memory.

## Prerequisites

Check each app with `search_connector_tools` at the step that needs it, not all at
the start. When a required one is missing, call `report_missing_connector_access` for
it instead of explaining in prose.

| App | For | Needed at step |
|---|---|---|
| Facebook / Instagram | Reading and answering inquiries (one is enough) | 1 (else the user pastes the inquiry and sends the reply) |
| Typeform | The intake form and its responses | 1-2 (else bills and photos attached in chat) |
| Google Maps | Address to coordinates, satellite view of the roof | 2 (else `web_search` for the coordinates) |
| Excel (OneDrive) or Google Drive | Storing the quote workbook | 3 (else `publish_artifact` delivers the .xlsx) |
| Google Docs | Proposal and contract | 5 (else `generate_document` / `generate_contract`) |
| QuickBooks | The estimate | 6 |
| Stripe | The deposit payment link | 6 |
| Gmail | Proposal email and follow-up | 6 |
| Calendly | Site visit booking (any booking link works) | 6-7, optional |
| Google Calendar | The site visit on the installer's calendar | 7 |
| monday.com | The crew's job card | 7 |

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Which customer (name, inquiry or address) | Start | None: ask |
| Typeform intake form link | Step 1 | Create one with the Typeform connector from the template |
| Supplier price list (sheet upload) with labour rate and hours, margin % | Step 3 | None: ask (never price from memory) |
| Tax rate on the quote | Step 3 | 0%, stated on the sizing as an assumption to check |
| Proposal branding: logo, colours, company details, warranty, terms | Step 5 | None: ask once, then offer to remember it with `memory` |
| Deposit rule (percent or fixed amount) and site visit booking link | Step 6 | None: ask |
| Crew board on monday.com | Step 7 | The board named like "Jobs" or "Installs"; ask if several |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`
message, then continue. Remember the price list, branding, deposit rule and booking
link with `memory` only if the user agrees, so the next quote starts faster.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing between them, except at every **Stop**. Name the customer in every
update. Keep each customer's files in one folder named after them (`job.json`,
`sources.json`, `sizing.json`, `payback_in.json`, the workbook and chart). Templates
for every message, form, document and record are in `references/templates.md`: read
it before step 1.

## Procedure

### 1. Reply with intake

Find the new inquiry through the Facebook or Instagram connector (or use the message
the user pasted). Draft the short reply from the template with the customer's first
name and the Typeform intake link. No form yet: create one with the Typeform connector
using the intake questions in the templates, and show the user its link.

**Stop (first time only).** Show the reply template and the form. Once the user
approves the template, save it with `memory` (if they agree) and from then on send it
to each new inquiry without asking again, changing only the first name. Reply only
inside Meta's 24-hour window after the customer's last message; for older inquiries,
give the user the reply to send themselves. Never message anyone who did not write in.

### 2. Research the site

Read the Typeform response (or the files in chat). From the bills, with
`media_analyze`: each month's kWh, the import price per kWh, the export rate, the
supplier and tariff name, and the bill dates. From the roof photos: which way the roof
faces, rough pitch, shading, obstacles and a rough count of panels that fit (say it is
an estimate from photos).

Get the coordinates from the address with the Google Maps connector and record a
satellite link (template). Then run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/pvgis_yield.py" --lat <lat> --lon <lon> --facing <S|SW|...> --tilt <pitch>
```

Leave out `--facing`/`--tilt` when unknown; the script then uses the best angle and
says so. Its yield is the only source for sunlight figures.

Tariff: take it from the bill. If the bill does not show it, find the supplier's
published rate with `web_search`/`web_extract`. Incentives: search official sources
(government, energy regulator, utility) for grants, rebates, tax credits and export
payments that apply at that address. Write every figure into `sources.json` with its
source (the bill, or a URL) and the date checked (template). Refresh any figure older
than 30 days.

Every figure must come from the bills, a script, or a page you read in this run.
If you cannot read a bill or reach a source, leave the figure out and say so; never
fill in a tariff, rebate or sunlight figure from memory. Do this research yourself,
never through `delegate_task`.

### 3. Size and price

Ask for the price list, labour and margin now if they are missing. Read the
uploaded sheet:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/price_list.py" <price list .xlsx or .csv> > price_list.json
```

Show any `skipped` rows (no readable price) and `warnings`. Write `job.json` (fields in
the templates) from the bills, the yield, the roof limit and the customer's battery
interest, then:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/size_system.py" --job job.json --prices price_list.json > sizing.json
python3 "${COMPUTER_SKILL_DIR}/scripts/payback.py" --file payback_in.json --svg payback.svg > payback.json
python3 "${COMPUTER_SKILL_DIR}/scripts/build_workbook.py" --job job.json --sizing sizing.json \
  --payback-in payback_in.json --sources sources.json --customer "<name, address>" \
  --out "Solar quote - <customer> - <date>.xlsx"
```

`payback_in.json` takes the quoted price and generation from `sizing.json` and the
dated figures from step 2 (template). The workbook has Assumptions (yellow input
cells with sources and dates), Sizing, Parts and Payback tabs, all live formulas.
Upload it to the user's OneDrive (Excel) or Google Drive through the connector, else
deliver it with `publish_artifact`.

Every price comes from the price list. Show every line of `flags` (parts not on the
list, roof limit hit, several mounting options, missing labour hours) and the
`assumptions`. Never add a price that is not on the list.

**Stop.** Show the sizing summary (template) and the workbook link. The installer
checks panel count, inverter, battery, quantities and price. Make the changes they ask
for by editing `job.json` and re-running the three scripts. Nothing goes further until
they approve the sizing.

### 4. Payback

Show the chart in the chat with `render_chart` (`chart_type: line`, columns
`["Year", "Cumulative position <currency>"]`, rows from `chart_rows` in
`payback.json`), with `assumptions_text` written under it. Deliver `payback.svg` with
`publish_artifact` for the proposal. The script's numbers are the only source: do not
round them up, and call the payback an estimate.

### 5. Proposal

Ask for the branding now if it is missing. Write the proposal (outline in the
templates) with the Google Docs connector, or `generate_document` if Docs is not
connected, passing the chart link in `image_urls`. If the chart cannot be placed, use
the payback table from the template instead. Write the contract with
`generate_contract` from the installer's own warranty and terms. Both say "Final price
confirmed after the site visit". Leave a highlighted blank for any term the installer
did not give; never invent warranty, finance or legal terms.

### 6. Send

Ask for the deposit rule and booking link now if missing, and re-run `size_system.py`
with the `deposit` rule so the amount comes from the script. Prepare, without creating:

1. The QuickBooks estimate: the customer and the lines from the template, matching
   the workbook total exactly.
2. The Stripe payment link for the deposit amount, in the quote's currency.
3. The proposal email (template) with the proposal, contract, estimate, deposit link
   and booking link.

**Stop.** Show the email, the estimate lines and total, and the deposit amount,
currency and recipient. Only after the user confirms: create the QuickBooks estimate,
create the Stripe payment link, put both links in the email and send it from Gmail.
Report what was sent, to whom, with the links.

### 7. Book the visit and brief the crew

When the deposit is paid (check the payment link's payments in Stripe; never take the
user's or customer's word as proof of payment without saying so):

1. Site visit: if the customer booked through the booking link (Calendly connector),
   use that slot. Otherwise draft a short email offering the booking link (template).
2. Prepare the Google Calendar event and the monday.com job card (template): customer,
   address, satellite link, roof notes, the approved system, the parts list with
   quantities from `sizing.json`, the visit date, and "Deposit paid <date>".

**Stop.** Show the event, the job card and any email. Create them and send the email
only after the user confirms.

## Automation (offer at the end, never set up unasked)

Offer these, and create the ones the user accepts with `cronjob` (`action: create`,
`skills` set to this skill's name as you loaded it). Cron runs have no one to ask, so
each prompt must be self-contained and must leave every send and record for the user:

- **Every 2 hours, 8:00-20:00:** check Typeform for responses since the last run; for
  each, run steps 2-3 (research, sizing, workbook) and reply with the sizing summaries
  queued for approval. List new Facebook/Instagram inquiries with the approved reply
  ready for the user to send (or to say "send them").
- **Daily 9:00:** for each proposal email sent 2 or more days ago with no reply in the
  Gmail thread, save one short follow-up as a Gmail draft (template). Never a second.
- **Daily 9:00:** find deposits paid since the last run in Stripe and prepare step 7
  for each (event, job card, booking email), listed for the user to confirm. Create
  nothing.

## Guardrails

- A person approves the sizing before any proposal, estimate or deposit link exists.
- Every savings figure states its assumptions. Never promise or guarantee savings,
  payback, bill cuts or incentive approval.
- Tariff and incentive figures carry their source and date; refresh any older than 30
  days. Sunlight figures come only from `pvgis_yield.py`.
- Prices come only from the user's price list; flag any part not on it, never price it.
- Money is draft-first: the deposit follows the user's rule and the script; the
  estimate and payment link are created only after the user confirms amount, currency
  and customer. The skill never takes, moves or refunds money.
- The customer's bills, address and photos stay in the quote files and the documents
  sent to that customer; never post them anywhere public or in a shared channel.
- Meta messaging: answer only people who wrote in, within 24 hours of their last
  message; no promotional follow-ups through Messenger or Instagram DMs.
- Never guess contact details, tariffs or incentives; leave them blank and say so.

## Pitfalls

- Estimating yearly use from one or two bills without saying so. `size_system.py`
  flags it; repeat the flag at the Stop and in the proposal's assumptions.
- Taking the optimal-angle yield as the real roof. When pitch or direction were
  unknown, say the yield is an upper estimate and confirm at the site visit.
- Quoting a price that differs from the workbook. The estimate, proposal and email
  all use `sizing.json` totals; re-run the scripts after any change.
- Rounding payback down or calling it a guarantee. Quote the script's figure as
  "about N years, estimated".
- Creating the Stripe link before the user confirms the deposit. Show it first.

## Verification

- `sources.json` has a source and a date within 30 days for every tariff, incentive
  and yield figure used.
- The workbook total, the proposal price, the QuickBooks estimate total and the
  email match `sizing.json` to the penny; the deposit matches the user's rule.
- The sizing was approved in chat before the proposal was written.
- Every email sent, estimate, payment link, event and job card was shown and
  confirmed first; the run reports each with its link.
