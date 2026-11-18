# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## First reply to an inquiry (under 50 words; approved once, then reused)

```
Hi <first name>, thanks for getting in touch about solar! To put a quote together
today, could you fill in this short form? It asks for your last electricity bills,
a few roof photos and your address: <Typeform link>
Any questions, just reply here. <installer first name>, <company>
```

## Typeform intake questions (when creating the form)

1. Full name (short text, required)
2. Email (email, required) and phone (phone number, optional)
3. Installation address with postcode/ZIP (long text, required)
4. Electricity bills, ideally the last 12 months (file upload, required; "a photo or
   PDF of each bill, or one annual statement")
5. Roof photos: each side that gets sun, plus the fuse board and meter (file upload)
6. Which way does the main roof face? (multiple choice: South, South-West, West,
   East, South-East, North, Not sure)
7. Interested in a battery? (Yes / No / Not sure)
8. Rough budget (multiple choice ranges in the installer's currency, "Prefer not to say")
9. Anything else we should know? (shading, planning area, timing) (long text)

File upload questions need a paid Typeform plan. If the user's plan lacks them, ask
the customer to reply to the email with the bills and photos instead.

## Satellite link

`https://www.google.com/maps/@?api=1&map_action=map&center=<lat>,<lon>&zoom=20&basemap=satellite`

## sources.json

```json
{
  "monthly_kwh":      {"source": "Customer bills <first bill date> to <last bill date>", "checked_on": "<date>"},
  "kwh_per_kwp_year": {"source": "<source_url from pvgis_yield.py>", "checked_on": "<checked_on>"},
  "import_tariff":    {"source": "Bill dated <date> (<supplier>, <tariff name>) or <URL>", "checked_on": "<date>"},
  "tariff_rise_pct":  {"source": "<URL of the published forecast, or 'Installer assumption'>", "checked_on": "<date>"},
  "export_rate":      {"source": "<bill or URL of the export tariff>", "checked_on": "<date>"},
  "upfront_incentive":{"source": "<URL of the official scheme page>", "checked_on": "<date>"},
  "self_use_pct":     {"source": "Installer assumption (no battery 30-40%, with battery 60-80%)", "checked_on": "<date>"},
  "degradation_pct":  {"source": "Panel datasheet warranty, or 'Assumed 0.5%/yr'", "checked_on": "<date>"}
}
```

## job.json (for size_system.py)

```json
{
  "monthly_kwh": [<kWh per bill month, from the bills>],
  "kwh_per_kwp_year": <from pvgis_yield.py>,
  "offset_pct": 100,
  "max_panels": <from the roof photos or the installer, else leave out>,
  "battery": <true if the customer is interested>,
  "panel_sku": "<installer's choice, else leave out>",
  "inverter_sku": "<installer's choice, else leave out>",
  "choices": {"mounting": "<sku for this roof type>"},
  "extra_items": [{"sku": "<sku>", "qty": <n>}],
  "labour": {"rate": <per hour, or leave out to use the price list's labour row>,
             "hours_per_kw": <installer's figure>, "fixed_hours": <installer's figure>},
  "margin_pct": <installer's margin>, "margin_basis": "margin",
  "tax_pct": <rate, else 0>,
  "deposit": {"type": "percent", "value": <n>}
}
```

`margin_basis`: "margin" means profit as a share of the selling price (price = cost /
(1 - margin)); "markup" means added on top of cost (price = cost x (1 + markup)). Ask
which the installer means if it is not clear.

## payback_in.json (for payback.py and build_workbook.py)

```json
{
  "price_inc_tax": <sizing.json totals[quoted_option].price_inc_tax>,
  "upfront_incentive": <sourced amount, else 0>,
  "annual_generation_kwh": <sizing.json sizing.expected_generation_kwh_year>,
  "annual_use_kwh": <sizing.json sizing.annual_use_kwh>,
  "self_use_pct": <40 without a battery, 70 with one, unless the installer says otherwise>,
  "import_tariff": <from the bill>, "tariff_rise_pct": <sourced or installer's, default 3>,
  "export_rate": <from the bill or tariff page, else 0>, "export_rise_pct": 0,
  "degradation_pct": 0.5,
  "incentive_per_kwh": 0, "incentive_years": 0, "annual_upkeep": 0,
  "years": 25, "currency": "<GBP / USD / EUR / ...>"
}
```

## Sizing summary (shown at the step 3 Stop)

```
<Customer>, <address>
Yearly use: <annual_use_kwh> kWh (<months_of_bills> months of bills)
Roof: faces <direction>, pitch <tilt>°, <shading notes>. Yield <kwh_per_kwp_year> kWh per kWp (PVGIS, <date>)
System: <panels> x <panel> = <system_kwp> kWp, inverter <inverter> (ratio <dc_ac_ratio>)
Expected generation: <expected_generation_kwh_year> kWh/yr (<share_of_use_covered_pct>% of use)
Battery: <recommended option and added price, or "not requested">
Price: <price_inc_tax> inc. tax (cost <cost>, margin <margin>)
Estimated payback: about <payback_years> years (assumptions below)
Flags: <every flag>
Assumptions: <every assumption>
Workbook: <link>
```

## Proposal outline (branded: logo, colours, company details)

1. Cover: "<Customer>'s solar proposal", address, date, proposal number.
2. Your home: yearly use from the bills, the roof (direction, pitch, satellite image
   link), what we propose and why.
3. The system: panels, inverter, battery (if chosen), size in kWp, expected yearly
   generation, share of use covered.
4. Price: the total including tax, what it includes (from the parts list in plain
   words, not cost prices or margin), the deposit and when the balance is due.
5. Savings estimate: the chart (or the payback table below), with the assumptions
   printed under it word for word from `assumptions_text`.
6. Incentives: each one with its source and the date checked; "subject to the
   scheme's own approval".
7. Warranty: from the installer's terms (panels, inverter, battery, workmanship).
8. Timeline: site visit, final design, install date window, commissioning.
9. "Final price confirmed after the site visit."
10. Next steps: book the site visit (link), pay the deposit (link), sign the contract.

Payback table (when the chart cannot be placed): years 1, 5, 10, 15, 20, 25 with
yearly savings and cumulative position from `payback.json`.

## Contract outline

Parties; the system and site; price, deposit, balance and payment terms; what is
included and excluded (scaffolding, electrical upgrades, structural work found at the
site visit); final price confirmed after the site visit and the customer's right to
cancel if it changes; installation timeline; warranties (from the installer's
terms); customer responsibilities (access, permissions); grid connection and
permits; cancellation and cooling-off period required by the customer's country;
limitation of liability; governing law. Add a note that the installer should have the
contract checked by a lawyer; this skill does not give legal advice.

## QuickBooks estimate lines

| Line | Amount |
|---|---|
| Solar PV system: <panels> x <panel>, <inverter>, mounting and electrical | price ex tax minus battery and labour share, or one line for everything if the installer prefers |
| Battery storage: <battery> (only if quoted) | its price ex tax |
| Installation and commissioning | its price ex tax |

Total ex tax and tax must equal `sizing.json` totals for the quoted option. Memo:
"Final price confirmed after the site visit. Deposit <amount> due to book."
Expiry: 30 days. Never show cost prices or margin on the estimate.

## Stripe deposit payment link

Product: "Solar install deposit - <customer>, <short address>". One-time price: the
deposit amount in the quote's currency. Quantity fixed at 1. After payment: show a
confirmation message with the site visit booking link.

## Proposal email (under 150 words)

```
Subject: Your solar proposal from <company>

Hi <first name>,

Thanks for sending your bills and photos. Here's your proposal for a <system_kwp> kWp
system<, with a <battery kWh> kWh battery> at <address>:
<proposal link>

Price: <price_inc_tax> including tax. Estimated payback is about <payback_years> years
on the assumptions in the proposal (an estimate, not a guarantee).

To go ahead:
1. Book your free site visit: <booking link>
2. Pay the <deposit amount> deposit: <Stripe link>
3. Your estimate: <QuickBooks estimate link>

The final price is confirmed after the site visit. Any questions, just reply.

<sender name>
<company>, <phone>
```

## Follow-up (once, 2 days later, same thread, under 60 words)

```
Hi <first name>, just checking you got the solar proposal for <address>. Happy to
answer any questions, or you can book the site visit here: <booking link>.
<sender name>
```

## Site visit booking email (deposit paid, no visit booked)

```
Hi <first name>, thanks for your deposit, we've received it. Please pick a time for
the site visit here: <booking link>. It takes about <duration> and we'll check the
roof, the fuse board and where the inverter will go. <sender name>
```

## Calendar event

Title "Site visit: <customer>, <short address>"; location the full address; notes:
phone, satellite link, system summary, roof notes, "Deposit paid <date>". Invite the
customer only if the user says so.

## monday.com job card

| Column | Content |
|---|---|
| Item name | <customer>, <short address> |
| Status | Site visit booked |
| Site visit | Date and time |
| Address | Full address and satellite link |
| Contact | Phone and email from the intake form |
| System | <panels> x <panel>, <inverter>, <battery or "no battery">, <system_kwp> kWp |
| Roof | Direction, pitch, roof type, shading and access notes from the photos |
| Parts list (update or long text) | Each part from `sizing.json`: SKU, description, qty (no prices) |
| Work order (update) | Scaffold, mounting type, inverter and battery location (to confirm), isolators, meter, commissioning, grid notification |
| Deposit | Paid <date>, <amount> |
| Quote workbook | Link |
