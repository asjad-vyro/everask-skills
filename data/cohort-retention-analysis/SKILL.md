---
name: Cohort Retention Analysis
description: >
  Turns signup and activity data into a cohort retention matrix, finds which cohorts or channels retain best and where users drop off, and writes up the findings.
  Use it for "build a retention cohort table from this CSV", "which signup cohort retains best", "compare retention by acquisition channel", "why are users churning after month 2".
---

# Cohort Retention Analysis

A good result is a correct cohort x period retention matrix, the headline finding in plain words, a comparison across cohorts or segments, and honest caveats about small or immature cohorts. Every number comes from the user's data and is computed by the script, never by hand.

## Step 1: Find the data and fix the definitions

Work from what the user gave: an attached CSV or Excel file, or pasted rows. You need a user id, a cohort date (signup, first purchase) and an activity date. If the file has them under other names, map them. If cohort date and activity date sit in two files, use `--users` for the one with the cohort date.

Decide and state, do not ask:
- Cohort: month of signup unless the user said otherwise (use weekly if the data spans under about four months).
- Retention event: whatever the activity rows record.
- Metric: bounded retention (active within period N), period 0 included.
- Minimum cohort size: 30 unless the user gave one.

If there is no usable data at all (only a question, nothing attached), do not invent a dataset. Explain in the reply what to supply and give the matrix layout and a SQL starter (see Step 6), then stop.

## Step 2: Prepare the file

Use `read_file` or `execute_code` to look at the columns and first rows. Save pasted rows to `/tmp/.scratch/cohort-retention-analysis/input.csv`.

If the user pasted aggregate counts (users per cohort and active counts per later period) instead of per-user rows, the script cannot run. Do these steps instead:
1. Read `references/retention-patterns.md`.
2. Compute every percentage with `execute_code` and copy the results.
3. List P0 = 100% under Assumptions, unless period 0 counts were given.
4. Treat bounded counts as not nested, since users active in one period need not be active in the next. Never derive "X users didn't come back" or period-to-period churn from them. Never project future periods or cohorts.
5. Then go to Step 4. For an Excel file, convert the right sheet to CSV in the same folder with pandas. Note rows with missing ids or dates, and remove test or internal accounts if the data marks them.

## Step 3: Run the script

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `cohort_matrix.py` under `~/.computer/skills` with `search_files`.

```
mkdir -p /tmp/.scratch/cohort-retention-analysis
python3 SKILL_DIR/scripts/cohort_matrix.py --input <csv> --user-col <id column> --cohort-col <cohort date column> --activity-col <activity date column> --granularity monthly --min-size 30 --out-prefix /tmp/.scratch/cohort-retention-analysis/out
```

Add `--segment-col <column>` to compare channels, plans or regions (cohort matrices are printed per segment). Add `--users <file>` when cohort dates are in a separate users file. Add `--as-of YYYY-MM-DD` when the data is known to be complete only up to a date earlier than its last row. If the user states the data runs through a date (e.g. "through the end of April 2024"), always pass that date (`--as-of 2024-04-30`), even when the last row is earlier. Never take the completeness date from the last row when the user gave one.

The script prints the matrix (percent of the cohort active in each period; blank means the period has not happened yet, which is not 0%), the size-weighted average per period, cohorts under the minimum size, and counts of dropped rows. It also writes CSVs with the `out` prefix. If it exits with a column error, fix the column names and rerun. A cell the script prints as 0.0% is a real zero: report it as 0%, with no footnote. Only blank cells are "not observed yet".

## Step 4: Read the result

Read `references/retention-patterns.md` once before writing the findings: it has the shapes to recognise and the pitfalls to check. Then answer, using only figures printed by the script:
- Which pattern the curves show, and the period where early churn ends (or "no floor").
- Best and worst cohort at the same period number, with the gap in percentage points. Use `execute_code` for any further sum, difference or average and copy the result.
- Whether newer cohorts retain better or worse than older ones at the same period.
- With segments: which segment retains best at the same periods and whether segment sizes are comparable.
- Anything odd: period 0 below 100%, a period where every cohort dips, dropped rows, tiny cohorts.
Causes are hypotheses; label them "possible reason" and never state one as fact.

## Step 5: Deliver in the reply

Put the whole result in the reply. Start directly with the `## Cohort retention` heading, with no narration such as "I'll start by loading...". Do not end with a question or offer.

Check these before sending:
- Every finding matches the printed matrix. Do not say a period is unobserved if the matrix shows a value for it.
- Period words match the granularity (months for monthly, weeks for weekly).
- Data-quality notes go in Caveats, one line each.

If the user asked for a chart, or the matrix is larger than about 8 cohorts, also call `render_chart` with retention curves (one line per cohort, x = period number, y = percent), using values from the script output. Offer the CSVs only if the user asked for files, then publish them with `publish_artifact` (`kind: "file"`).

Reply shape:

```
## Cohort retention: <what was measured>
**Setup:** cohorts by <signup month/week>; active = <event as given>; bounded retention; cohorts under <n> users excluded from averages. Assumptions: <list>.

**Headline:** <one sentence with the main figure from the data>

| Cohort | Size | P0 | P1 | P2 | ... |
|---|---|---|---|---|---|
(matrix from the script, blank cells left blank)

**Weighted average by period:** <from the script>

## Findings
1. <finding, with figures, and the periods compared>
2. ...
3. ...

## Caveats
- <immature cohorts, small cohorts, dropped rows, definition limits>

## Suggested next steps
1. <action tied to a finding>
```

## Step 6: When asked for SQL

If the user has a database rather than a file, give a query that returns one row per user and activity day, then tell them to export it as CSV and rerun:

```
SELECT u.<user id> AS user_id, u.<signup date> AS signup_date, e.<event date> AS activity_date
FROM <users table> u JOIN <events table> e ON e.<user id> = u.<user id>
WHERE e.<event type> = '<retention event>' AND e.<event date> >= u.<signup date>
```

Adjust names to what the user told you.

## Hard rules

- Never invent users, rates, dates, channels or benchmarks. Mark anything not in the data as an assumption, and write "not given" for missing facts. Do not quote industry benchmarks unless the user supplied them.
- All arithmetic is done by the script or `execute_code`, then copied. No mental maths.
- Never derive "users who didn't come back" or period-to-period churn from bounded counts, and never project future periods.
- Blank (immature) cells are never reported as zero, and cohorts are compared only at the same period number.
- Do not open with questions; decide, state the assumption, deliver. Use `clarify` only if no data can be found anywhere in the message or attachments.
