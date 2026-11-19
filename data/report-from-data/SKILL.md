---
name: Report from Data
description: >
  Turns a spreadsheet or CSV into a written weekly, monthly or project report: the numbers worked out, what changed and what it means.
  Use it for "write the weekly report from this data", "monthly report from this sheet", "summarize these numbers for my manager", "what changed this month".
---

# Report from Data

A good result is a short report a manager can read in two minutes: a headline, three to five findings that each carry a number, a small table, and open questions. Every number was computed by code in this turn. Do the whole job in one reply and never stop to ask questions: decide, state the assumption, deliver.

## Hard rules

- Write the report in the language the user wrote in unless they ask for another. Keep their names, column labels, figures and terms exactly as given. Do not assume US date formats or a currency: use the format and symbol that appear in the data or the user's message, and no symbol if neither gives one.
- Every figure in the report was printed by `execute_code` in this turn. Never do arithmetic in your head and never type a number you did not see in the output.
- Do not invent causes. Write "the data shows" for what the file says, and put any explanation in "Open questions" as a question. No benchmarks, targets or industry comparisons unless they are in the file or the user gave them.
- Never change, round or drop a source value silently. Say what you left out: rows excluded (blank or unparsable) with their count, duplicate rows found, columns ignored, and any assumption (which period, which comparison).
- If something is not in the data, write "not given", not a guess.

## Step 1: Load and profile

1. Work in `/tmp/.scratch/report-from-data/`. Read an attached file with pandas (`read_csv` or `read_excel`; for an Excel file with several sheets, list them and use the one the user named, otherwise the first). If the data is pasted in the message, write it to a CSV first. If there is no data at all, use `clarify` once to ask for it.
2. Print the shape, the column names and types, the date range, the null count per column, and the first rows.
3. Identify: the date column (parse it; decide day-first or month-first from the values and say so if ambiguous), the measure columns (numbers, including numbers held as text with a currency symbol, thousands separators or `%`; decide per column from the values whether the decimal mark is a dot or a comma, as in `1,234.56` or `1.234,56`, and say which), and the dimension columns (region, product, team, status).
4. Count rows with a blank or unparsable date or measure and exclude them from the sums; keep the count for the "Scope and caveats" line. Keep exact duplicate rows in the sums (two identical sales can be real), and report how many there are and how much they add, so the user can judge.

## Step 2: Choose the period and the comparison

- Use the period the user named ("this week", "March", "Q2"). If they gave none, use the latest complete period in the data (the last week, month or the whole project to date, matching the report type they asked for) and state it.
- Compare with the previous period of the same length. If the data has a target, budget or plan column, also compare with that. If the data has only one period, skip the comparison and say so.
- A partial last period (fewer days than the one before) is not comparable: say so, and compare per day only if the user would find that useful.

## Step 3: Compute everything in code

In `execute_code`, compute and print:

1. The total (or average, if the measure is a rate or a score: sum a count, average a rate; when the file has the rate's base, such as visits behind a conversion rate, weight by it) for the period and for the comparison period, the absolute change and the percent change. Guard against a zero base: write "n/a" for the percent when the base is 0.
2. The same by each useful dimension, ranked by absolute change. Find the largest rise and the largest fall.
3. For a trend that matters, the values across the last four to eight periods.
4. Any outlier: a value far from the others in its own series.
5. Percent points, not percent, for the change of a rate.

Keep the printed output and build the report table from it. Round only when you write: one decimal for percents, the data's own precision for amounts.

## Step 4: Write the report

If the user described a house format or attached a previous report, follow its headings and tone. Otherwise use this shape, with the user's language for the headings:

```
# <Report type>: <period>

**Headline:** <one sentence: the main result with its number and the comparison>

## Key findings
1. <finding with its number, e.g. "<dimension value> fell by <amount> (<percent>) to <amount>">
2. ...
(three to five, ranked by how much they matter)

## Numbers
| <dimension> | <this period> | <previous period> | Change | Change % |
(one table, at most ten rows, a total row at the bottom; for a rate, the overall rate)

## What changed
<two to four sentences on the biggest movers, using only what the data shows>

## Open questions
- <question for the owner of the data, e.g. why a value moved>

## Scope and caveats
<rows used, rows excluded and why, columns ignored, assumptions>
```

Writing rules: lead with the result, not the method. State direction and size together ("fell by X, from A to B"). Name the dimension values exactly as they appear in the file. Keep the whole report under about 400 words unless the user wants more. A trend that is the point of the report may get one chart with `render_chart`, built from the printed numbers; do not add charts otherwise.

## Step 5: Verify, then deliver

1. In `execute_code`, list every number you wrote in the report and check each against the printed results (totals equal the sum of the rows in the table; changes equal the difference of the two columns). Fix any mismatch before replying.
2. The report goes in the reply itself, in full, starting directly with the headline section. Do not open with a preamble.
3. If the user asks for a file (a document to send, attach or print), build it in the same turn and still put the report in the reply. Word is the default: load the built-in `docx` skill with `skill_view` and follow it, including its delivery step. For a PDF, load the built-in `pdf` skill and build the PDF with it directly, never from a .docx. Those built-ins deliver the file themselves, so do not add your own `publish_artifact` call. Say in one line which format you made.
4. If the user asks to pull the data from Google Sheets, Google Drive, Airtable or Notion and it is connected, use it; otherwise work from what they gave you. Never stall on a connection.
