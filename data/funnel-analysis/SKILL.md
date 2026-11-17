---
name: Funnel Drop-Off Analysis
description: >
  Turns an events CSV or a list of step counts into a funnel report: step and overall conversion, where users drop off, segment gaps and ranked fixes.
  Use it for "where do users drop off", "analyse my conversion funnel", "compare funnel conversion by channel", "which step loses the most users".
---

# Funnel Drop-Off Analysis

A good result is a funnel table with correct numbers, the step that matters most named plainly, a segment comparison when the data allows it, and a short ranked list of fixes with a hypothesis for each. The whole report goes in the reply.

## Step 1: Identify the input

Decide which of these the user gave and go straight on. Do not ask questions; state assumptions in the report.

- **Step counts** (typed or pasted, such as "1000, 600, 300, 90" with step names): use the counts mode in Step 2.
- **An events file** (one row per event, with a user id, an event name and usually a timestamp): use the events mode. Open the file with `read_file` or `execute_code` just far enough to see the column names and the distinct event names.
- **A table that already has one row per step** (a step column and a users column): treat it as step counts.
- **Nothing attached or typed**: say what you need (step names with user counts, or an events file) and show the command shape from Step 2 with placeholder values. Do not invent a funnel.

Funnel steps: use the order the user gave. For an events file with no stated order, infer the order from the event names (for example signup before purchase), say you inferred it, and keep only the events that fit one journey. If the user gave a time window, use it; otherwise run with no window and say so.

## Step 2: Run the calculator

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is `scripts/funnel.py`. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `funnel.py` under `~/.computer/skills` with `search_files`. Run it with `terminal`. Copy an attached file into `/tmp/.scratch/funnel-analysis/` first if you need a path.

Step counts:

```
python3 SKILL_DIR/scripts/funnel.py --names "<step 1>,<step 2>,<step 3>" --counts "<n1>,<n2>,<n3>" [--value <value of one final conversion>]
```

Events file:

```
python3 SKILL_DIR/scripts/funnel.py --events <file.csv> --steps "<event 1>,<event 2>,<event 3>" [--user-col <col>] [--event-col <col>] [--time-col <col>] [--segment-col <col>] [--window-days <n>] [--value <n>]
```

Defaults are `user_id`, `event_name` and `timestamp`; pass the real column names when they differ. A user counts for a step only if the step happens after the previous one (and within the window, if given). Run it once per segment column the user cares about; if they named none and the file has obvious ones (channel, device, plan, country), run it with one or two of them. Do not do any arithmetic yourself: every number in the report comes from the script output. For anything the script does not cover (period-over-period comparison, a revenue figure per step), calculate it in `execute_code` and copy the result.

If the script reports a missing column, read the column names it prints and rerun. If a later step has more users than the one before, say the step order or definition looks wrong and flag it.

## Step 3: Write the report

Read `references/funnel_design_guide.md` once before you write the hypotheses and the prioritisation. While writing:

1. Every rate you restate in a sentence must be copied from the script's table and must name its denominator. For example, write "30% of the 300 who added a card". Do not turn a rate into "N in 100" or "about half" phrasing; give the exact figure from the output, such as "320 of 680 lost (47%)".
2. Judge severity only against the user's own other steps or segments, for example "the largest loss of any step". Never call a rate extreme, unusual, normal, typical, healthy or within range. Never say what "usually" happens.
3. Do not state facts about the user's product, site or UI that the data does not show. Phrase each such hypothesis as a condition, for example "if the plan screen is where price first appears, ...".
4. Recommendations may name only steps, segments and columns that exist in the data. Do not mention ad sets, pages or campaigns unless they are in the data.
5. Do not add numbers that the script did not print, such as your own recovery estimates "at current downstream rate". Write "value not given" instead.
6. Start the reply with the report heading, with no narration about loading the skill or running tools.

Reply with this shape, in full:

```
# <Funnel name> - funnel analysis

**Scope:** <what the funnel is, number of users entering, time window or "no window", date range if the data has one>
**Assumptions:** <step order inferred or given, window, any rows skipped, value per conversion if used or "not given">

## Summary
- Overall conversion: <first step> to <last step> is <x%> (<n> of <n> users).
- Biggest leak: <step> loses <n> users (<x%> of the step before).
- <One line on the most important segment gap, or "no segment data given".>

## Funnel table
<the table from the script>

## Where users drop off
For each of the two or three worst steps, ranked by users lost:
### <Step>
- Lost: <n> users (<x%> of the prior step); recovery ceiling <from the script, or "value not given">
- Hypotheses: <one to three, drawn from the guide; mark each as a hypothesis, not a finding>
- How to check: <the data or test that would confirm it>

## Segments
<segment table from the script; say which segment is worst and at which step it diverges from the best. Flag any segment under 30 entering users as too small to rank.>

## Time between steps
<only if the data had timestamps: the median and P95 table, and which gap is long>

## Recommendations
| Priority | Action | Step | Why (with the number) |
|---|---|---|---|
| 1 | <action> | <step> | <users lost or segment gap> |

## Caveats
<tracking gaps that could fake a drop, cohorts too recent to have converted, small samples, anything assumed>
```

If the user gave no segments, no timestamps or no value per conversion, leave out that section and say why in one line instead of padding it.

## Rules

- Every figure comes from the user's data or the script output. Never invent a rate, a benchmark ("typical SaaS conversion is...") or a revenue number. If asked how the funnel compares with others, say no benchmark was given and offer to search the web.
- Hypotheses are labelled as hypotheses. The data shows where users leave, not why.
- Never describe a rate as normal, typical, healthy, extreme, unusual or "within range", and never make general claims such as "X usually leaks most". Compare only within the user's own data.
- Rank by users lost as well as by rate; name both when they differ.
- Recovery value is an upper bound, never a forecast.
- Finish in one reply. Do not stop to ask for approval or more detail.
- Only build a file (a spreadsheet, a deck) if the user asks for one; then load the built-in `xlsx` skill with `skill_view` and follow it.
