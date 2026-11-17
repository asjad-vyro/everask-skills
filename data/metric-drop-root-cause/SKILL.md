---
name: Metric Drop Root-Cause Finder
description: >
  Finds why a metric fell or jumped: checks the change is real, ranks which segments drove it, and writes a root-cause report with the evidence.
  Use it for "why did revenue drop", "what caused this fall in conversion", "break this decline down by region and channel", "find the driver behind this KPI change".
---

# Metric Drop Root-Cause Finder

A good result tells the user, in one reply, whether the change is real, when it started, which segment drove it (with its share of the change in numbers), which explanations were tested and rejected, and what to do next. Numbers come from the data, never from guesswork.

## Step 1: Take stock of what the user gave

- Data attached (CSV or spreadsheet) or pasted figures: use them. No data at all: do not ask for it. Say that you cannot find the cause without data, then give the investigation plan (which cuts to pull, the likely causes for this metric from `references/hypotheses.md`) and the SQL or spreadsheet steps to run. Never invent figures.
- Pin down: the metric, the two periods being compared (before vs after), and whether it is a sum (revenue, orders) or a ratio (conversion = conversions / sessions). If the periods are not stated, take the latest period against the one just before it of equal length, and say so as an assumption.
- Do not open with questions. Decide, state the assumptions, deliver.

## Step 2: Check the change is real

Read the file with `execute_code` or `terminal` (pandas is available) and look at the columns, date range, missing values and duplicate rows. Then confirm the movement:

- With daily data, run the script's `--validate` (see Step 3). Inside normal daily variation (|z| < 1.5) means: report it as noise or within normal range, name what would change that view, and stop the drill-down.
- Check the data itself first: partial last period, unequal day counts, a column whose definition changed. A partial period is the commonest false alarm.

## Step 3: Drill down with the script

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is `scripts/drilldown.py` in it. Use the full path where the commands below say `SKILL_DIR`. If `skill_view` gives no path, find `drilldown.py` under `~/.computer/skills` with `search_files`.

Sum metric, by date windows (dates inclusive, ISO format):

`python3 SKILL_DIR/scripts/drilldown.py --csv FILE --metric revenue --dimension region channel device --date-col date --a-start YYYY-MM-DD --a-end YYYY-MM-DD --b-start YYYY-MM-DD --b-end YYYY-MM-DD --validate --pairs`

Period label column instead of dates: `--period-col month --period-a LABEL1 --period-b LABEL2`.

Ratio metric: add `--denominator sessions` and use the numerator as `--metric conversions`. The output then splits each segment's effect into a rate effect (its own rate moved) and a mix effect (its share of traffic moved).

Use the columns that exist; the dimensions are whatever categorical columns the file has. If the script errors, fix the arguments from the message; if it still fails, do the same arithmetic in pandas. Pasted figures: do the sums in `execute_code`. Never do arithmetic in your head.

## Step 4: Decide the driver

1. Sum metric: the primary driver is the segment with the largest share of the change. If segments offset each other (net change near zero) use the share of gross movement and say why.
2. Ratio metric: if the mix effect carries most of the change, say the rates did not worsen, the mix changed. If the rate effect carries it, name the segments whose own rate fell.
3. Go one level deeper inside the top segment (pairs output, or filter to the segment and drill by the other columns) to find the narrowest slice that holds most of the change, for example one region on one device.
4. Find the onset: the date the daily series stepped (script's onset line or a daily table for the top segment). A step change points to an event; a gradual slide to a structural shift.
5. Read `references/hypotheses.md` and write three to five hypotheses with the data that supports or refutes each. Use only events the user gave or the data shows. Causes that the data cannot show (a deployment, a campaign) are labelled "to verify", with the question to ask the owner.

## Step 5: Write the report in the reply

The report goes in the reply itself, in full, in this order:

```
# Root cause: <metric> <direction> <size> (<period A> vs <period B>)

**Verdict:** <one or two sentences: real or noise, the primary driver with its share of the change, the most likely cause, confidence High/Medium/Low>

## Is the change real
<size in absolute and percent, z-score or the check used, data-quality checks done>

## Where it came from
<table of the top contributors: segment, before, after, change, share of change. Top 5 to 8 rows; include the narrowest slice>
<one line on volume vs rate vs mix when it applies>

## When it started
<onset date, step or gradual, any user-given events near it>

## Hypotheses
| # | Hypothesis | Evidence for | Evidence against | Verdict |
<three to five rows: Confirmed / Most likely / Refuted / Inconclusive>

## What to do
- Now: <immediate check or fix>
- Next: <short-term follow-up, who to ask, what data to pull>
- Prevent: <alert or check that would catch it earlier>

## Assumptions and limits
<periods assumed, what the data could not show, what was not checked>
```

## Hard rules

- Every figure in the report comes from the script output, the user's data or a calculation you ran. Percent shares are rounded to one decimal; the same number appears the same way everywhere.
- Never invent events, deployments, campaigns, customers or dates. Without a change log, say "no change log was given" and list what to check.
- Correlation is not a confirmed cause. Use "most likely" unless timing, size and affected population all match and alternatives are refuted.
- If the top segment's share is under about 40% and the rest is spread out, say the decline is broad-based and look for a company-wide cause (pricing, seasonality, tracking) instead of naming a single culprit.
- Keep it to the one reply: do not publish a file unless the user asked for one.
