---
name: Email Subject Line Generator and Tester
description: >
  Gives you angle-distinct email subject lines (with preview text for consumer email), a score for each, and a split-test plan with sample size and decision metric.
  Use it for "write subject lines", "score these subject lines", "nobody opens my emails", "A/B test my subject line", "preview text for my newsletter or promo".
---

# Email Subject Line Generator and Tester

A good result is a short set of subject lines that each take a different angle, each scored against a fixed rubric, plus a test plan the user can run without fooling themselves. The subject line (and preview text for consumer email) is the whole job: do not write the email body, audit deliverability or plan a send cadence.

Hard rules:
- Use only facts the user gave. Never invent a recipient name, company, product detail, offer, date, open rate or result. If something is missing, write "not given" or state an assumption.
- Statistics in the references come from email-tool vendors and are unaudited. Say "vendor-reported, direction only" when you cite one. Never present them as the user's numbers.
- Never ask questions before delivering. Decide, state your assumptions in one line, and deliver everything in the reply itself.
- Do every sum (sample size, split sizes, word and character counts) in `execute_code`. Copy the results; never do the maths in your head.

## Step 1: Read the request and settle the basics

Work out from the message, without asking:
1. **Regime**: B2B cold outbound (a sales email to a stranger) or B2C lifecycle/promotional (customers, subscribers, newsletters, launches, promos). If unclear, pick the likelier one and say so. The two follow different rules.
2. **Recipient and goal**: who gets it and what the email wants them to do. If the body is not given, assume the body delivers exactly what the user described and say so.
3. **Drafts to score**: any subject lines the user pasted.
4. **Test capacity**: list size or sends per day, baseline open or reply rate, what the platform can split-test. Missing values stay "not given".
5. **Constraints**: deadline, brand tone, whether emoji is allowed, research time available. A tight deadline or no research time removes the angles that need per-prospect research (competitor, company initiative, trigger event): delete them and name them as deleted.

## Step 2: Read the rules for the regime

Read `references/pattern-library.md`. Use the B2B section for cold outbound and the B2C section for lifecycle email. Never apply B2B cold rules to B2C or the reverse.

## Step 3: Write the hypothesis

Write one falsifiable sentence before drafting: "Because [observation], we believe [change] will [effect] for [audience]. We'll know when [metric]." If no result could prove it wrong, rewrite it.

## Step 4: Draft the variants

Draft 3 to 5 variants (6 to 10 if the user asked for that many, scoring all and shipping the best). Each uses a different angle from the pattern library; a synonym swap of another variant is a duplicate. For B2C, write a preview text (90 to 140 characters) for every variant that extends the subject and does not repeat it. Hold casing constant across the set, as casing is a test candidate and not a rule.

If the user pasted drafts, score those first, then rewrite the weak ones as new variants.

## Step 5: Score every variant

Read `references/scoring-rubric.md`. Check hard fails first (a hard fail scores 0), then the 10-point scorecard. Count words and characters with `execute_code`. Rewrite any variant under 8/10 or with a hard fail and re-score it. Pasted drafts that fail stay in the table with their real score and the reason; do not quietly drop them.

Self-check the wording: it should read like something a person would type, with no "unlock", "supercharge", "game-changing" or "revolutionary" style phrasing. Any fact a variant leans on (a trigger event, a competitor claim) is flagged "unverified, confirm before sending" unless the user supplied it. Use `web_search` for at most one volatile fact, only if the user asked for it.

## Step 6: Design the test

Read `references/test-design.md`. Fill the test plan: one variable, split, sample per variant, duration, decision metric, guardrails, next test. Run the sample-size calculation in `execute_code` with the user's baseline rate and a stated minimum detectable lift. If no baseline was given, assume one, label it an assumption, and show the sample size for two or three lifts. If the list is too small to power the test, say so plainly, give the best split available, and recommend shipping the default set instead of a queue nobody can run.

## Step 7: Deliver in the reply

Use this order and these headings, all in the reply:

1. **Assumptions**: one or two lines (regime, body promise, anything "not given").
2. **Hypothesis**: the one sentence.
3. **Scorecard**: a table with columns `#`, `Subject`, `Angle`, `Words / chars`, `Score`, `Notes` (add a `Preview text` column for B2C). Rank by score. List any hard-failed draft with the words that triggered it.
4. **Test plan**: the bullets from `references/test-design.md`, with the computed numbers.
5. **Flagged risks**: unverified facts, spam-trigger words found, angles deleted and why, and the next test in queue order or "volume does not support another test".

Keep it tight: a table and short bullets, not an essay. Never put the email body in the deliverable.

## Hard fails in brief

Fake "Re:" or "Fwd:" framing; a subject that promises what the body does not deliver; spam-trigger words in the subject ("free", "guarantee", "act now", "limited time", "click here", all caps, repeated "!!!" or "???"); over the length budget (about 35 characters B2B cold, about 50 B2C); a duplicate angle; a first name in a B2B cold subject. Flag spam-trigger words inside the subject only. A full inbox-placement or domain audit is out of scope: say so in one line if the user's real problem looks like that.

If the user asks "why is my open rate low", diagnose the subject line only, and note that sender reputation, authentication and list quality also matter and need a separate check.
