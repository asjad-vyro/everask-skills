---
name: Statistics Reporting Audit
description: >
  Audits the statistics in a paper, thesis or manuscript draft and returns a ranked list of problems plus ready-to-paste corrected text.
  Use it for "check my statistics", "is my n correct?", "audit my methods section", "fix my figure legend statistics", "reviewer says my stats are wrong".
---

# Statistics Reporting Audit

A good result tells the user what a statistical reviewer would object to, ranks it, and gives corrected wording they can paste, without inventing a single number. This is a reporting review, not a reanalysis: compute new statistics only if the user supplies data and asks for it.

## Rules

- Never invent p values, sample sizes, test names, degrees of freedom, confidence intervals, software versions, correction methods, exclusion rules, randomization, blinding or power calculations. Where the user's text lacks a fact, write `AUTHOR_INPUT_NEEDED: <short factual question>` in the revised text.
- Treat the independent experimental unit (animal, patient, culture, donor, batch, plot, device, run) as `n`. Cells, fields of view, images, wells, spectra and repeated readings are not independent unless the design says so.
- Do not recommend a test as final when the unit or design is unclear. Offer the options and say what decides between them.
- Do not turn association into mechanism or cause, and do not rewrite weak results into stronger claims.
- Use neutral wording: "a reviewer may challenge", "not assessable from the supplied text". Never "fake", "wrong" or "manipulated".
- Do the whole job in one reply from what the user gave. Do not open with questions. If a target journal is not named, say you used general reporting practice. If something cannot be assessed, say so in the scope section.
- Any arithmetic (an adjusted p threshold, a count of comparisons, a mean you are asked to check) is done with `execute_code`, never by hand.
- This is reporting guidance, not professional statistical advice; for clinical-trial or regulatory analysis, a statistician should sign off.

## Step 1: Read the input and classify the job

The input may be a Methods or statistical analysis section, Results text with test statistics, figure legends, a reviewer comment, a table of comparisons, or a one-line question such as "is my n right?". Decide which job it is: audit, rewrite, draft a statistics section from design facts, reviewer-response support, or figure-legend alignment. A clean drafting request with enough facts skips the long issue list (see the second output shape).

## Step 2: Extract the design

From the text, list: groups and conditions, endpoints, time points, the unit that was measured and the unit that was analysed, replicates (biological, technical, repeated), pairing or blocking, randomization, blinding, exclusions, missing data, the test or model named for each claim, the multiple-comparison strategy, how data are summarised (mean ± s.d., s.e.m., median and IQR), and software. Mark every item the text does not state as "not given".

## Step 3: Check against the failure modes

Read `references/failure-modes.md` before you list issues. It has the ranked patterns (pseudoreplication, uncorrected multiple comparisons, wrong interaction inference, ignored pairing, significance-only reporting, small-sample overclaims, undefined error bars) with fixes. Work out any counts, such as the number of pairwise comparisons implied by k groups, with `execute_code`.

If the text includes figure legends, panel statistics, stars, error bars or box and violin plots, also read `references/figure-statistics.md` and check each panel.

If the user names Nature as the target journal, also read `references/nature-requirements.md` and add its audit table. Do not call anything a journal requirement unless that file or the user's own journal instructions say so; for other journals, say the user should check the journal's current author instructions, and use `web_search` once if the user asks for them.

Read at most two reference files in one run.

## Step 4: Write the reply

Use this shape for an audit. The whole reply goes in the chat, in full.

```
## Statistics review scope
- Input reviewed: <what the user gave>
- Not assessable from the supplied material: <list>
- Study design readout: <groups, endpoints, tests as stated>
- Independent unit and replication readout: <what n is claimed to be vs what it likely should be>

## Major statistical issues
1. [P0/P1/P2] <issue title>
   - Evidence from the text: <short quote from the user's text>
   - Why it matters: <one sentence>
   - Fix: <concrete action>

## Ready-to-paste revision
<rewritten Statistical analysis / Results / legend text, with AUTHOR_INPUT_NEEDED where a fact is missing>

## AUTHOR_INPUT_NEEDED
- <short factual questions only, one per line>

## Reviewer-risk note
- <what a statistical reviewer may still challenge after the revision>
```

Severity: P0 means a central claim could be undermined (wrong unit, ignored dependence, uncorrected family of tests, wrong interaction inference, undisclosed exclusions). P1 means the claim may stand but reporting is too weak (missing exact n, undefined error bars, no effect sizes or intervals, missing software, star-only p values). P2 is clarity and polish. Order issues P0 first. Quote the user's own words as evidence; do not paraphrase numbers.

For a clean drafting request with enough facts, return instead:

```
## Draft Statistical analysis
<ready-to-paste text>

## Reporting notes
- n definition: ...
- tests/models: ...
- multiple comparisons: ...
- software/version: ...
- unresolved fields: ...
```

For a short question ("is my n right?"), answer it in the first sentence, explain the reason in two or three sentences, then give the corrected wording. Show how the numbers the user gave map to units (for example, measurements per unit and number of units), using only their figures.

For reviewer-response support, give: the reviewer concern (quoted or short paraphrase), the author-side action needed, a draft response, and the replacement manuscript text. Do not claim a new analysis was run unless the user supplied its result or you ran it on their data.

## Statistical analysis paragraph order

When you write a Methods paragraph, use this order and keep only what the user supplied: software and packages (no invented versions); how data are summarised; definition of `n` and replication; tests or models per comparison, including paired or unpaired and parametric or not; the multiplicity strategy; p value reporting rule (exact values where possible, defined thresholds otherwise); exclusion rules, stated or marked missing.

Prefer in Results: effect size with interval and exact p ("<estimate> (95% CI <low> to <high>, p = <exact>)", filled only with the user's numbers). Avoid "highly significant" without an effect size, "proved", "ns" as the only result, and "n = 300 cells" when the experiment has three animals.

If a statistic appears in more than one place (text, table, legend), check the values and precision match, and that "SD" and "SEM", or "confidence interval" and "prediction interval", are used consistently.

## Before you send

Check the reply: the independent unit is defined; biological and technical replicates are separated; no invented value appears anywhere; every central claim maps to a test or is marked descriptive; multiple-comparison status is stated; what could not be assessed is listed; the revised wording does not overclaim.
