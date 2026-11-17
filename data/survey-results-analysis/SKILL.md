---
name: Survey Results Analysis
description: >
  Turns survey responses into an honest findings report: results per question, segment differences, open-text themes with counts, confidence labels and what the data does not show.
  Use it for "analyse this survey", "what do these responses tell us", "cluster these open-text answers", "is this difference real with n=47?", "analyse our NPS or CSAT results".
---

# Survey Results Analysis

A good result tells the user what the survey clearly shows, how sure to be, and what not to conclude. Honesty about weak data matters more than confident conclusions: a firm claim from 47 responses and a leading question is worse than no claim. Finish the whole analysis in one reply.

## Step 1: Read the data

1. If the user attached a file (CSV, XLSX), load it with pandas in `execute_code`. Print the columns, row count, dtypes, missing values per column and the first rows. If the data is pasted in the message, parse it from there. If only aggregated results are given (counts or percentages per option), work from those and say that cross-tabs and bias checks on raw rows were not possible.
2. Classify each column: closed question (single choice, multi-choice, rating or scale, NPS 0-10), segment attribute (role, plan, company size, region, tenure) or open text. Remove obvious test rows or duplicates only if clearly marked, and state how many.
3. Note the survey context the user gave: the question it was meant to answer, hypotheses, audience, recruitment, response rate, decision to inform. Anything not given is "not stated". Do not ask questions; state assumptions instead.

## Step 2: Audit the survey itself

Before reading results, judge these and carry them into the report:
- **Sample size**: N overall and per segment. Under about 100 responses is direction only. Any segment under 30 is too small for a segment claim.
- **Recruitment and selection bias**: who could answer and who is likely missing (for example only active users, only people who opened an email, only people with a complaint).
- **Question design**: name any question that is leading or loaded, double-barrelled ("fast and reliable"), has unbalanced scale options, or has no neutral or "does not apply" option. Report such results but label them **Biased** and say which way they likely lean. Do not give a numeric size of the bias unless the user gave one.
- **Non-response**: share of blanks per question, when large.

## Step 3: Compute everything in code

Do all counting in `execute_code`; never estimate in your head. Read `references/stats-helpers.py.md` and paste the functions you need. For each closed question compute counts and percentages (of those who answered), and a 95% interval for the headline figures with the Wilson function. For NPS compute promoters (9-10), passives (7-8), detractors (0-6) and NPS = %promoters minus %detractors, with n.

For each segment comparison that matters, compute the group sizes, the two results, the difference in percentage points with an interval, and a p-value (two-proportion z-test, or Fisher exact when any cell is under 5). For ratings compare means with SD and n. Then label each comparison:
- **Likely real**: p under 0.05 and both groups at least 30, and the interval does not include zero.
- **Possible but unproven**: a visible gap that does not clear that bar, or a group of 30 to 99 with a borderline p.
- **Noise or too small to say**: p of 0.10 or more, or either group under 30.
When you test many segment cuts, say that some will look significant by chance and that the unplanned ones are leads, not findings.

Print the results as a table in the tool output and copy the numbers from it into the report. Do not retype from memory or change figures.

## Step 4: Group the open text

Skip this step if there is no open text. Otherwise:
1. Read every open-text response (use code to print them in batches if there are many).
2. Choose 3 to 7 themes that cover the responses. Assign each response to its main theme, with an "Other" bucket, and a note when a response clearly has two themes.
3. Count in code: build a dict response id to theme and count it. Report counts and the share of open-text responses. Say the grouping is done by you, not hand-coded, so borderline responses could move.
4. Take 2 to 3 quotes per theme verbatim from the data. Never invent, trim to change meaning or paraphrase inside quote marks.
5. Mark each theme positive, negative, conditional or mixed, and flag any theme that contradicts the closed-question numbers. That is often the most useful finding.
6. If the file also has segment columns, check whether any theme is concentrated in one segment, with counts.

## Step 4b: Test hypotheses

For each hypothesis the user gave, give a status: SUPPORTED, CONTRADICTED, INCONCLUSIVE or NOT TESTED BY THIS SURVEY (the question was not asked or was asked badly), with the evidence and a High, Medium or Low confidence. If the user gave none, state the one or two questions the survey most plausibly answers and treat those as the hypotheses, marked as assumed.

## Step 5: Write the report

Read `references/report-template.md` and fill it in as the reply itself, in full, in this order. Do not publish a file unless the user asked for one (then use `publish_artifact` and still give the full report in the reply, or load the built-in `docx` skill with `skill_view` for a Word file). If the user asked for a chart, use `render_chart`.

Rules for the content:
- The executive summary comes first: 3 to 5 sentences with the findings, one confidence label and the single biggest caveat.
- Every number comes from your Step 3 output or the user's data. Show n next to every percentage.
- Confidence labels (High, Medium, Low, Direction only, Biased) always follow from sample size, method and effect size, and the reason is stated. Intervals are approximate and apply to random samples; for a self-selected sample say the interval understates the real uncertainty.
- "What the data does NOT show" must be specific to this survey: who is missing, what was not asked, what could distort the reading, and the one follow-up that would close the biggest gap.
- Give 3 to 5 recommendations ranked by impact and confidence, each with evidence, a confidence label, counter-evidence and what would strengthen it. If the data supports no recommendation, say that and give the research to do instead.

## Hard rules

1. Never overstate significance. With a small N say plainly: the data shows direction, not proof, and should not drive a large spend. Do not use words like "proves", "significant" or "confirms" for anything that did not clear Step 3's bar.
2. Never claim cause from survey data. A survey shows that X goes with Y. For cause, say a controlled test is needed: one decision metric, a control and a treatment group, a sample size set for the smallest effect worth detecting, and a win-or-lose rule fixed before the test.
3. NPS is a tracking number, not a diagnosis. Analyse the distribution and the open-text reasons, and do not turn the score alone into a feature recommendation.
4. If asked "what percent want X?", give the percentage with its n, who was asked, the interval and the question wording, not a bare number.
5. Do not invent data: no extra respondents, benchmarks, industry norms, quotes, or percentages. If a comparison to a benchmark would help, say what to look up. Stated intent ("would you use...") is not behaviour; say so when it matters.
6. If the data is too large to print, work on it in code in chunks and sample only for reading; never truncate silently. If a column is unreadable or missing, say so and carry on with the rest.
7. Keep the report to what the data supports. Do not pad with generic survey advice.
