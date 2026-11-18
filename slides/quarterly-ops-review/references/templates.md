# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## metrics.json (for quarter_kpis.py)

One entry per KPI the operations sheet can answer. Use the sheet's own column names.

```json
[
  {"name": "On-time delivery", "unit": "%", "type": "rate", "column": "<On time column>",
   "match": ["yes", "y", "true", "on time"]},
  {"name": "Cost per shipment", "unit": "USD", "type": "avg", "column": "<Cost column>"},
  {"name": "Shipments", "type": "count"},
  {"name": "Claims per 100 shipments", "type": "ratio", "column": "<Claims column>", "per": 100},
  {"name": "Road shipments", "type": "count", "where": {"column": "<Mode>", "in": ["Road"]}}
]
```

Types: `count`, `sum`, `avg`, `rate` (share of rows whose column matches, as %),
`ratio` (sum of column / rows × per), `min`, `max`. Add `"date_column"` when the KPI is
dated by a different column than the first one with "date" in its name.

## kpis.json (for merge_kpis.py)

```json
{"company": "<company>", "quarter": "<Q3 2026>", "previous_quarter": "<Q2 2026>",
 "kpis": [
   {"name": "<KPI>", "unit": "<% | USD | GBP | blank>", "better": "<higher | lower>",
    "this_quarter": {"value": <n>, "file": "<file name>",
                     "location": "<sheet, column, rows / page / slide>", "link": "<URL>"},
    "last_quarter": {"value": <n>, "file": "<file>", "location": "<...>", "link": "<URL>"},
    "target":       {"value": <n>, "file": "<file, or User, in chat>", "location": "<...>"}}
 ],
 "tables": [
   {"sheet": "Incidents", "columns": ["Date", "Severity", "Root cause", "Resolution", "Thread"],
    "rows": [["<date>", "<sev>", "<cause>", "<resolution>", "<Teams link>"]]},
   {"sheet": "Action items", "columns": ["Item", "Owner", "Due", "Status", "Basis", "Source"],
    "rows": [["<item>", "<owner>", "<due>", "<status>", "<basis>", "<source>"]]}
 ]}
```

A value the sources do not have is `null`. For quarter_kpis.py values, copy its
`source.location` into `location`. Add the incident totals as KPIs ("Incidents",
"Sev 1 incidents", better: lower) with the Teams channel as file and the date range
and thread count as location.

## Sources tab (built by merge_kpis.py)

| Column | Content |
|---|---|
| Ref | S1, S2… (quote it in speaker notes) |
| KPI | KPI name |
| Period | Last quarter / this quarter / Target |
| Value | The number (blank and yellow when missing) |
| Unit | %, currency code or blank |
| File | File, channel or "User, in chat" |
| Sheet, cell or page | Exact location |
| Link | Clickable link to the file or message |
| Note | MISSING / No source given / anything to check |

## Deck outline (edit_pptx on the template)

One `add_slide` per slide, `clone_of` the template slide that matches, then
`delete_slide` the template's sample slides. Notes on every slide.

1. **Title**: "<Quarter> Operations Review", "<company>", "<presenter>, <meeting date>".
2. **Summary**: 3–5 bullets, each a `summary` line from merged.json, worst miss first;
   one bullet on incidents; one on action items (e.g. "4 of 6 actions done, 1 slipped").
3. **One slide per KPI**: title "<KPI>: <this quarter value>"; bullets: vs last
   quarter, vs target (status), one line of cause only if the data shows it; chart from
   `kpi_chart_png.py` (region right half). Missing: "Not available: <reason>", no chart.
4. **Incidents**: total, by severity, top 3 root causes, open vs resolved, median days
   to resolve; Sev 1 incidents named one per bullet with resolution.
5. **Last quarter's action items**: one bullet per item: "<item>: <owner>, due <date>:
   <status>" (status unknown items say "Status unknown").
6. **Risks**: missed targets, open incidents, slipped actions, each with its number.
7. **Asks of leadership**: decisions or resources the user named; "To confirm with
   <user>" for any you inferred.

Speaker notes, every slide:

```
Sources: <Ref> <file>, <sheet/cell/page>; <Ref> <file>, <location>. Workbook: <workbook name>, Sources tab.
```

## One-pager (generate_document, one page)

```
<Company>: <Quarter> operations at a glance
Prepared by <user> on <date>. All figures from <workbook name>, Sources tab.

Headline: <one sentence: the biggest change or miss, with its number>

KPIs
| KPI | <previous quarter> | <quarter> | Target | Status |
<one row per KPI from merged.json; "Not available" where missing>

Incidents: <total>, <by severity>; top cause: <cause> (<n>).
Last quarter's actions: <done> done, <in progress> in progress, <slipped> slipped, <dropped> dropped, <unknown> unknown.
Decisions needed: <1–3, from the deck's asks>
```

## Board memo (generate_document, 1–2 pages of prose)

```
To: <board / leadership>   From: <user>   Date: <date>
Subject: <Quarter> operations review

1. Summary: three or four sentences: overall performance, the main miss and the main
   improvement, with numbers.
2. Performance: one short paragraph per KPI group (service, cost, safety/quality),
   every figure as in merged.json, compared with last quarter and target.
3. Issues: incidents (count, severity, causes, what was fixed) and slipped actions,
   with what is being done, only as stated in the sources or by the user.
4. Decisions needed: numbered, each with the choice, the cost or impact if known, and
   who owns it.
Appendix: Sources: <workbook name>, Sources tab.
```

No forecasts, guarantees or causes the data does not show.

## Outlook draft to the VP (draft only)

```
To: <VP email>
Subject: <Quarter> ops review: deck, one-pager and board memo

Hi <VP first name>,

<Line 1: headline result with its number>
<Line 2: the biggest risk or miss with its number>
<Line 3: the decision needed from leadership>

Deck, one-pager and memo attached; every figure traces to the Sources tab of the KPI workbook.

<user name>
```

## Status check (clarify, step 3)

```
I couldn't prove the status of these <n> action items from last quarter. For each,
reply done, in progress, slipped or dropped:
1. <item> (<owner>, due <date>)
2. ...
```

## Teams decisions post (after the user confirms, step 7)

```
<Quarter> ops review: decisions and actions (<meeting date>)

Decisions
- <decision>

Actions
- <action>: <owner>, due <date>  (<monday.com link>)

Notes: <Read AI or transcript link>
```

## monday.com item

| Field | Content |
|---|---|
| Name | The action as worded in the transcript |
| Owner / Person | The confirmed owner |
| Due date | The confirmed date |
| Status | "Not started" (or the board's first status) |
| Update / note | "From <Quarter> ops review, <meeting date>: <transcript link>" |

## Weekly owner status (Teams, drafted by the Monday automation)

```
Hi <owner first name>, your open actions from the <Quarter> ops review:
- <item>: due <date> (<n> days overdue / <n> days left), <status>
Reply here if any date needs to move.
```

Overdue first. Under 80 words per owner.
