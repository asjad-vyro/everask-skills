---
name: Quarterly Ops Review
description: 'Builds your quarterly operations review from SharePoint, OneDrive and Teams: a KPI workbook where every number links to its source, a deck on your company template, a one-pager, a board memo and an Outlook draft to your VP. Reports on last quarter''s action items and, after the meeting, tracks the new ones on monday.com. Just name your KPIs, like "on-time %, cost per shipment, incidents".'
---

# Quarterly Ops Review

Prepares an ops or project manager's quarterly review for leadership: pull the quarter's
numbers from the operations sheet on SharePoint, the carrier or partner report in
OneDrive and the incident thread in Teams; merge them into one Excel workbook with live
formulas and a Sources tab; report on last quarter's action items; build the deck on the
company's own PowerPoint template; write a one-pager and a board memo; and leave an
Outlook draft for the VP. After the meeting it turns the decisions into monday.com items
and a Teams post. It never estimates a missing number, never restyles the template,
never sends the Outlook email, and never creates monday.com items or posts in Teams
until the user confirms the list.

## When to Use

- "Do our Q3 ops review: on-time %, cost per shipment, incidents, claims."
- "Build the quarterly review deck on our template from the ops tracker and carrier report."
- "Write the board memo and one-pager for this quarter's ops numbers."
- "The leadership review is done. Pull the actions from Read AI and put them on monday.com."
- "Send the owners their open action items."

## Start Here

When this skill is open, treat the user's message as the start of the review, not as a
question about reviews. "Q3 ops review", "do the quarterly review" or just a list of
KPIs means: run this pipeline for the quarter that just ended.

- Begin at step 1 straight away. Do not ask "do you want me to pull the data?": that
  is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. Those pauses keep wrong numbers out of a board pack and keep
  anything from going to leadership without the user, so never skip them, even if the
  user says "do everything".
- To start you need the KPIs, and where the data lives. If the KPIs are missing, ask
  in one short `clarify`: "Which KPIs does leadership expect (e.g. on-time %, cost per
  shipment, incidents)? Or upload last quarter's deck." If the user did not name the
  files or channel, search for them (step 1) and offer the best matches in that same
  question instead of asking for links.
- The quarter defaults to the one that just ended; never ask for it.
- A returning user re-enters where they are: "the review meeting is done" → step 7;
  "send the owners their items" → the weekly status in Automation; "fix the cost
  number" → edit the Sources tab and rebuild from step 2.

## Prerequisites

Connected apps (check each with `search_connector_tools` at the step that needs it; when
a required one is missing, call `report_missing_connector_access` for it instead of
explaining in prose):

| App | For | Needed at step |
|---|---|---|
| SharePoint / Microsoft Excel | Reading the operations sheet; saving the workbook | 1, 2 |
| OneDrive | The carrier or partner report PDF; saving the files | 1, 6 |
| Microsoft Teams | The incident thread; the decisions post | 1, 7 |
| Read AI | Last quarter's action items; this quarter's transcript (else the Read AI recap email in Outlook, a Teams meeting transcript, or notes the user uploads) | 3, 7 |
| Outlook | The draft to the VP | 6 |
| monday.com | This quarter's action items | 7 |

Someone building the deck for the first time does not need monday.com yet; check it
at step 7.

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| KPIs leadership expects, with which way is better, and targets | Start | From last quarter's deck if uploaded; targets: ask in step 1 only if not in the deck |
| Where the data lives (sheet, PDF, Teams channel) | Start | Search SharePoint, OneDrive and Teams; offer the matches |
| Quarter | Never ask | The last quarter that ended (calendar; use the fiscal year if the user names one) |
| Last quarter's numbers | Never ask | Last quarter's deck or workbook if given, else computed from the same sheet |
| Company PowerPoint template (.pptx built on it) | Step 4 | None: ask |
| VP's name and email | Step 6 | None: ask |
| Date of the leadership review meeting | End (Automation) | None: ask only if the user accepts the follow-up |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify` message,
then continue.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing between them, except at every **Stop**. Name the quarter and company in
every update ("Q3 2026, Acme Logistics: pulled 812 shipment rows"). Keep one working
folder for the run: `rows.csv`, `metrics.json`, `kpis.json`, `merged.json`,
`incidents.json`, `actions.json`. Shapes, outlines and messages are in
`references/templates.md`: read it before step 1.

## Procedure

### 1. Pull

Get the quarter's dates: `python3 "${COMPUTER_SKILL_DIR}/scripts/quarter_kpis.py" --bounds`
(add `--quarter "Q2 2026"` or `--fy-start-month 4` when the user says so).

Every number must come from a file or thread you read in this run through a connector
(or a file the user uploaded), with its location kept next to it. If a source app is
not connected, call `report_missing_connector_access` for it and go on with the
others; never fill a number from memory, from an earlier quarter, or from a subagent.
Do the reading yourself; never hand it to `delegate_task`.

- **Operations sheet** (SharePoint / Excel connector): read the used range of the
  sheet with every column and all rows, in sheet order, and save it as `rows.csv`.
  Write `metrics.json` (one entry per KPI the sheet can answer; shapes in
  `references/templates.md`) and run:

  ```
  python3 "${COMPUTER_SKILL_DIR}/scripts/quarter_kpis.py" --rows rows.csv --metrics metrics.json \
    --quarter "<quarter>" --sheet "<sheet name>" --file-name "<file name>" --link "<file URL>"
  ```

  Run it again with `--quarter "<previous quarter>"` for last quarter's values when
  last quarter's deck is not available. Its output is the only source for these
  values; check `rows_bad_date` and `rows_skipped` and report them.
- **Carrier or partner PDF** (OneDrive connector): download it and read it with
  `media_analyze`. Record each KPI with its page and the exact label printed there. If
  a KPI is not in the PDF, it is missing, not zero.
- **Incidents** (Teams connector): read the channel's messages for the quarter. One
  incident per root post or incident thread (replies are not new incidents). Write
  `incidents.json` with date, severity, root cause, resolution, resolved date and the
  message link, leaving any field the thread does not state empty, then run
  `python3 "${COMPUTER_SKILL_DIR}/scripts/incidents.py" incidents.json --quarter "<quarter>"`.
- **Last quarter and targets**: from last quarter's deck (`import_pptx`, note the slide
  number) or workbook. Targets the user typed are sourced as "User, in chat, <date>".

Reply with a short list: what was found (file, rows or pages, count), and every KPI
or period still missing. Ask for missing targets in one `clarify`, then go on.

### 2. Merge in Excel

Write `kpis.json` (shape in `references/templates.md`): for each KPI, last quarter,
this quarter and target, each with its file, location (sheet and cells, page or slide)
and link. Add the incident list and any rows the deck will quote as `tables`. Run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/merge_kpis.py" kpis.json \
  --xlsx "<Quarter> ops review KPIs.xlsx" > merged.json
```

The workbook has a KPIs tab (values pulled from the Sources tab by formula; change,
change %, vs target, trend and status as live formulas), a Charts tab (one native chart
per KPI) and a Sources tab linking every number to its file and cell or page. Missing
values stay blank and highlighted. Deliver it with `publish_artifact`.

**Stop.** Show the KPI table from `merged.json` (the `summary` lines), the missing and
unsourced list, and the workbook. Ask the user to check the numbers against the
sources. Fix what they correct in `kpis.json` and run the script again; nothing is
built on the numbers until they say they are right. When they confirm, offer to save
the workbook next to the operations sheet in SharePoint, and save it only if they say yes.

### 3. Last quarter's actions

Find last quarter's leadership review notes: Read AI through its connector if
connected; else the Read AI recap email in Outlook (search for the meeting title in the
last quarter); else the Teams meeting recap or transcript; else ask the user to upload
the notes. List each action item exactly as recorded, with owner and due date.

For each item, look for evidence in what you already read (the workbook, the Teams
channel, monday.com items if they were tracked there) and record it with its source.
Write `actions.json` and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/action_items.py" status actions.json --as-of <quarter end>
```

Its statuses are final unless the user changes them. An item with no evidence is
"unknown", never "done". Add the items as an "Action items" table in `kpis.json` and
run `merge_kpis.py` again, so the workbook carries them.

**Stop** (only if `needs_confirmation` is not empty). Ask the user, in one `clarify`, to
give the status of each unproven item (done, in progress, slipped, dropped). Put their
answers in `user_status`, run the script again and go on.

### 4. Build the deck

If the template is missing, ask for it now: the company .pptx (a .potx must be saved
as a .pptx first, e.g. a deck built on the template, which works best). Read it with
`import_pptx` to learn its layouts, palette and fonts. Then build the deck with
`edit_pptx` only, so every slide comes from the template's own masters and layouts.
Never rebuild or restyle it with `generate_design_slides`, and never change fonts,
colours or layouts.

Slides, in order (outline in `references/templates.md`): title, summary, one slide per
KPI with its chart, incidents, last quarter's action items, risks, asks of leadership.
Add slides with `add_slide` (`clone_of` a matching content slide of the template, or
`layout` naming its title-and-content layout), then remove the template's sample
slides. Every slide's `notes` say where each number came from (Sources tab ref, file,
cell or page).

Charts: run
`python3 "${COMPUTER_SKILL_DIR}/scripts/kpi_chart_png.py" merged.json --out charts --colors "<3 hex colours from the template palette>" --bg <slide background hex> --data-url`
and pass each `data_url` to `add_image` on its KPI slide. A KPI with this quarter
missing gets no chart; its slide says "Not available: <reason>".

Risks and asks come from the data (missed targets, open incidents, slipped actions)
and from what the user said; write "To confirm with <user>" for any you are unsure of.

### 5. One-pager and board memo

With `generate_document`, write both from `merged.json`, `incidents.py` output and the
action-item statuses only (outlines in `references/templates.md`). The one-pager is the
summary on a page; the memo is board-ready prose: performance, issues, decisions
needed. Copy numbers exactly as `merged.json` formats them, so the deck, one-pager
and memo agree. Before moving on, check that every number in both documents appears
in `merged.json` or the Sources tab.

### 6. Draft to the VP

Ask for the VP's name and email if missing. With the Outlook connector, create a
**draft** (never send) to the VP: subject, a three-line summary from the template, and
the deck, one-pager and memo attached. If the connector cannot attach files, save the
three files to the user's OneDrive (ask which folder) and put their links in the draft;
say which you did.

**Stop.** Show the draft and the three files. The user sends it from Outlook. Then
offer the automations.

### 7. After the leadership meeting

When the user says the meeting happened (or the follow-up automation brings the
transcript): read this meeting's transcript or notes the same way as step 3. List
every decision and every new action item with owner and due date as stated; leave the
owner or date blank when the transcript does not say it, never guess.

**Stop.** Show the list and the Teams decisions post (template in references). Ask the
user to confirm or fix the actions, owners and dates, and which board and Teams channel
to use. Only then create each item on monday.com (item name, owner, due date, a link to
the transcript), and post the decisions summary in the channel. Report each created
item's link.

## Automation (offer at the end, never set up unasked)

Offer these two, and create the ones the user accepts with `cronjob` (`action: create`,
`skills` set to this skill's name as you loaded it). Cron runs have no one to ask, so
each prompt must be self-contained and must leave creating and posting for the user:

- **The morning after the leadership review** (one-off, ISO time from the meeting date
  the user gives): pull the meeting's Read AI transcript (or recap email), list the
  decisions and new action items with owners and due dates, and draft the Teams post.
  Reply with the list for the user to confirm; create nothing on monday.com and post
  nothing in Teams. The user's "confirm" re-enters step 7.
- **Every Monday, 9:00:** read the open items on the monday.com board, run
  `action_items.py by-owner`, and draft one short Teams message per owner (template in
  references) in the reply, with overdue items first. The user posts them or says
  "send them", after which you post each one through the Teams connector.

## Guardrails

- Every number in the deck, one-pager and memo traces to the Sources tab. Never
  estimate, round up, carry over or fill a missing figure; write "Not available" and
  flag it.
- Build on the template's own masters and layouts; never change fonts, colours or
  layouts, and never rebuild the deck with a new design.
- Never send the Outlook email; it stays a draft for the user.
- No monday.com items and no Teams posts until the user confirms the list of actions,
  owners and dates.
- An action item's status is "unknown" unless the data or the user confirms it.
- Never guess names, owners, emails or dates; leave them blank and ask.
- Do the data reading yourself; scripts' outputs are the only source for what they
  compute, never a judgement from memory or a subagent.

## Pitfalls

- Mixing units: a sheet with on-time as 0.942 and a PDF with 94.2%. Put every
  percentage on the same scale (94.2 with unit "%") before `merge_kpis.py`.
- Counting Teams replies as incidents. One incident per root post or thread.
- Reading a carrier PDF figure without its page. If you cannot name the page, the
  number is not sourced; recheck it with `media_analyze`.
- Using `generate_design_slides` "to make it look better". It restyles the deck; use
  `edit_pptx` on the user's template.
- US vs UK dates in the sheet (03/07/2026). Check `rows_bad_date` and pass `--dayfirst`
  when the sheet writes day first.
- A fiscal quarter treated as a calendar one. Ask once if the user says "FY" and use
  `--fy-start-month`.

## Verification

- The workbook opens with KPIs, Charts and Sources tabs; every KPI value is a formula
  pointing at a Sources row with a file and location.
- The deck uses only the template's layouts, has one slide per KPI plus incidents,
  actions, risks and asks, and every slide's notes name its sources.
- The deck, one-pager and memo show the same numbers as `merged.json`.
- The Outlook message is in Drafts, not Sent.
- monday.com items and the Teams post exist only for actions the user confirmed.
