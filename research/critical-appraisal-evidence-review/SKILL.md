---
name: Critical Appraisal of Research Evidence
description: >
  Gives a written critical appraisal of a study, abstract or scientific claim: what design it is, whether the conclusion follows, the main biases, confounders and statistical problems, and a certainty verdict.
  Use it for "is this study credible?", "critically appraise this trial", "does this abstract support causation?", "check the stats and bias in this paper", "grade the evidence for this claim".
---

# Critical Appraisal of Research Evidence

A good result is a traceable critique: every concern points to where it appears in the study, says what it does to the conclusion, and is rated by severity. It ends with a plain verdict on what the evidence does and does not support. Be fair: name strengths, separate fatal flaws from minor limitations, and judge the method, not whether you like the result.

## Step 1: Get the material

1. Use what the user gave: pasted abstract or text, an attached paper, a DOI or URL, or just a claim.
2. If there is a URL or DOI, read it with `web_extract`. If there is only a claim with no source (for example "coffee prevents dementia"), run at most two `web_search` calls to find the key study or studies behind it, and say which ones you appraised.
3. If only an abstract is available, appraise the abstract and say plainly that full-text details (protocol, attrition, all outcomes) could not be checked. Do not stop to ask for the full paper: deliver the best appraisal you can and list what would change it.
4. Never invent details of the study. Anything not stated is "not reported" or "not given", which is different from "not done".

## Step 2: Fix the question and the claim

Write down, from the text: population, exposure or intervention, comparator, outcome, follow-up time, effect measure, and setting. Then classify the claim the authors or the user is making as descriptive, predictive or causal, and the design as randomized trial, cohort, case-control, cross-sectional, case series, systematic review or meta-analysis, lab or animal study, or modelling. Note the independent unit (patients, clusters, animals, cell cultures) and whether repeated measures were treated as independent.

## Step 3: Check design and bias

Work through these, citing the section, table or sentence for each concern:

- **Selection and sampling**: who was included, how, and who dropped out (attrition, differential loss).
- **Confounding**: for any non-randomized design, list the plausible confounders that were not measured or adjusted for, and reverse causation. Adjusting for a few covariates does not remove confounding.
- **Measurement**: validated outcomes, self-report, recall, detection and observer bias, blinding of participants and assessors.
- **Randomized trials**: sequence generation, allocation concealment, blinding, deviations from assigned treatment, missing outcome data, selective reporting, and whether the analysis was by intention to treat. Judge each outcome separately, not the paper as a whole.
- **Reporting**: preregistration or protocol, outcome switching, spin (conclusions or title stronger than the results), conflicts of interest and funding.
- **Language**: flag causal words ("prevents", "reduces", "leads to") where the design supports only association.

## Step 4: Check the statistics

Read `references/statistical_pitfalls.md` when the study reports p-values, subgroup or multiple outcomes, small samples, regressions, or effect sizes. Look for: multiple testing without correction or a "significant" result among many subgroups; p just under 0.05 treated as proof; "non-significant" read as "no effect"; no confidence intervals or effect sizes; statistical versus practical importance; underpowered or tiny samples; post-hoc subgroups; relative risk reported without absolute risk; overfitting and data leakage in prediction models.

Do every calculation in `execute_code` and copy the results into the reply, never mental maths. Examples: the chance of at least one false positive across k independent tests at alpha is 1 - (1 - alpha)^k; absolute risk reduction and number needed to treat from event counts the user or paper gave; confidence-interval checks. Only use numbers that appear in the material.

If you give a confounding sensitivity figure (E-value or how strong an unmeasured confounder would need to be), compute it in `execute_code` with the correct formula: for RR < 1 first take RR* = 1/RR; E-value = RR* + sqrt(RR* x (RR* - 1)); for an odds ratio of a common outcome (>15%) first convert with RR ≈ sqrt(OR); also compute it for the CI limit closest to 1. Do not equate 1/RR with the confounder strength needed. If you cannot compute it, leave it out. Do not claim an effect size is "typical of" healthy-user or other bias without a source or a computed figure. If something such as a post-hoc analysis is only a possibility the text does not show, label it "cannot be checked from the material" rather than suggesting it happened.

## Step 5: Grade the certainty of the evidence

Before writing the Verdict or Certainty section, you MUST read `references/evidence_hierarchy.md` (always when giving a certainty rating, comparing several studies, or when the design label alone would mislead). Start randomized evidence at high and observational evidence at low, then move down or up. Use a GRADE-style verdict (high, moderate, low, very low) for one named outcome and comparison, giving a reason for each domain: risk of bias, inconsistency, imprecision, indirectness, publication or missing-evidence bias; for observational evidence also consider large effect or dose-response. Do not downgrade the same problem twice: assign each flaw to one domain only (for example confounding goes under risk of bias; a prevalence-versus-incidence or population mismatch goes under indirectness only if it is not already the reason for the risk-of-bias downgrade), and write which domain carries it. A single study cannot show inconsistency, so say so. If the user asked about several studies, appraise each briefly, then give one synthesis. Read `references/review_sources.md` only if the user wants a formal tool named (RoB 2, ROBINS-I, QUADAS, AMSTAR 2, CASP, reporting checklists) and tell them the tool version to use; this appraisal is not a formal tool assessment unless it was done item by item.

Tools change: if you name a specific current version of a framework, check it with one `web_search` or say "check the current version".

## Step 6: Write the reply

Put the whole appraisal in the reply, in this shape. Use the user's own wording for the claim; never carry over example values from this file.

```
## Appraisal: <short name of the study or claim>

**Claim under test:** <claim, and whether it is descriptive, predictive or causal>
**What was actually studied:** <design, population, exposure/intervention vs comparator, outcome, follow-up, sample size as given>
**Source used:** <full text / abstract only / claim only plus the studies found>

### Verdict
<2-3 sentences: is the conclusion supported, partly supported or not supported, and the certainty rating (high / moderate / low / very low) for which outcome>

### Strengths
- <what was done well>

### Concerns
| # | Severity | Issue | Where it shows up | Effect on the conclusion | Fix or check |
|---|---|---|---|---|---|
| 1 | Critical / Important / Minor | <named bias, confounder or statistical issue> | <section, table or quote, or "not reported"> | <why it matters> | <what would resolve it> |

### Statistics check
<calculations done with execute_code and their results, or "no calculations needed">

### Certainty (GRADE-style)
<each domain, one line with the reason>

### What the evidence does and does not show
- Supported: <...>
- Not supported: <...>
- What would change this view: <...>

### Assumptions and limits
<what was not available, what you assumed>
```

Keep the table to the 4 to 8 concerns that matter most, ordered by severity. Critical means it threatens the main conclusion; Important means it affects interpretation; Minor means it does not change the conclusion.

## Hard rules

- Use only facts from the user's material or tools. Do not invent sample sizes, p-values, authors, citations, journals or quotes. If a number is missing, write "not given".
- Quote or point to the text for each concern; do not make general complaints.
- Separate "not reported" from "not done", and risk of bias from certainty of evidence from applicability.
- Do not assign a numeric quality score or add up checklist items.
- Any E-value or confounder-strength figure must come from `execute_code` with the correct formula, or be left out; each flaw is downgraded in only one GRADE domain.
- Finish in one reply. Do not stop to ask questions; state what you assumed.
- For health or medical topics, add one plain line at the end: this is an evidence appraisal, not medical advice, and it does not replace a clinician's judgment.
