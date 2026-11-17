---
name: OKR Writer and Reviewer
description: >
  Drafts a complete OKR set (objective, outcome-based key results, initiatives, guardrails), or reviews and rewrites OKRs you already have, with missing baselines flagged instead of invented.
  Use it for "write Q1 OKRs for my team", "fix these OKRs, they read like a task list", "convert this roadmap into OKRs", "review my OKRs".
---

# OKR Writer and Reviewer

A good result is a ready-to-use OKR set for one team and one cycle: a clear objective, key results that measure change (not work), initiatives listed as bets, guardrails, and an honest audit. Missing numbers are marked, never made up. The whole job finishes in one reply, in the reply itself.

## Step 1: Pick the mode and state it

Read the request and choose one. Say which in the first line ("Mode: Rewrite").

- **Draft**: the user gives goals, strategy, a problem or a team description and wants OKRs.
- **Review**: the user pastes OKRs and wants them assessed. Score them (Step 6) and list fixes. Also give a corrected version unless they said not to.
- **Rewrite**: the user pastes a roadmap, feature list or flawed OKRs and wants outcome-shaped OKRs. Do the full rewrite.

If it is really a project plan, KPI dashboard or status report, say so in one line, then still give the closest useful OKR version.

## Step 2: Set the frame, from what the user gave

Decide these and list them under Context. Where the user did not say, pick a default and label it "assumed".

- Scope: company, department, product, team or initiative. Default: team.
- Cycle: default one quarter. Do not invent calendar dates; use the cycle name the user gave, or "next quarter" if none.
- OKR type: committed (aim for 100%), aspirational (a stretch; 60 to 70% is a good score), learning, operational health, or compliance or safety (aim for 100%).
- Empowerment signal: `empowered` if the team chooses what to build and can change course mid-cycle; `feature-team` if features, projects or dates are already committed; `mixed`; or `unknown`. Infer it from the input. Never stop to ask. Treat `unknown` like `empowered` but add one open question.
- Strategic input: the parent goal, customer problem or business pressure behind this. If none was given, write "not given" and use the user's own goals as the intent.

## Step 3: Separate outcomes from work

Sort every item the user gave into one of two piles. Test: "if it can go in a backlog, it is not an outcome." Features, launches, tasks, hires and activity counts go to Initiatives. What changes for customers or the business becomes the objective and the key results.

## Step 4: Write the objective and key results

Read `references/rubric.md` now, before you write, for the anti-patterns and rubric.

- **Objective**: one qualitative sentence stating the desired change. No numbers in it. Aim for 1 to 3 objectives; 1 is the default for a small request.
- **Key results**: 2 to 4 per objective. Each one is a metric that moves from a baseline to a target by a deadline, and each has the fields shown in Step 7.
- Include at least one leading KR (behaviour the team can move) next to any lagging one (revenue, retention).
- Any KR that pushes growth, speed or volume needs a paired guardrail (quality, retention, reliability, cost).

**No invented numbers.** Use only baselines, targets and benchmarks the user gave. For anything missing write `baseline needed` (and in Open Questions say how to measure it), `target: set after baseline` or `target: proposed, assumption`. If you propose a target to make the draft concrete, give it as a clearly labelled assumption, for example "target: <proposed>, assumption", and never state a baseline you were not given. Do not quote benchmarks or industry averages unless the user supplied them.

When the user did give figures, do all arithmetic (percentage changes, gaps, implied rates) in `execute_code` and copy the results.

## Step 5: Map initiatives as bets

For each initiative: which KR it should move, the hypothesis ("we expect X because Y"), and its dependency. Initiatives are experiments, not promises. Never list one as a KR.

## Step 6: Audit

Rate the set against the rubric in `references/rubric.md`: pass, risk or fail per criterion, one line of reason each, and a specific fix for every risk or fail. In Review mode, audit the user's original OKRs first and then your corrected version.

Hard rules:
- Never tie OKR scores to pay, bonuses or individual performance ratings. If the user asks, refuse in one or two sentences and explain: people sandbag targets and hide bad news.
- Default to team OKRs. If individual OKRs are requested, warn once about sandbagging and false precision, then write them if still wanted.
- If the signal is `feature-team` or `mixed`, include the Disclosure section; otherwise leave it out.

## Step 7: Write the reply in this shape

Put the full deliverable in the reply. Use markdown, no JSON, no placeholders left unresolved except the marked ones.

```
Mode: <Draft | Review | Rewrite>

## Context
- Scope / Cycle / OKR type / Empowerment signal: <each value, "assumed" where it was>
- Strategic input: <from the user, or "not given">
- Assumptions: <list>

## Objective
<one sentence, no numbers>

## Key Results
- KR1: <metric verb and noun, baseline to target by deadline, or the marked gap>
  - Metric: <precise definition>
  - Baseline: <the user's figure with its date, or "baseline needed">
  - Target: <the user's figure, or "set after baseline", or "<proposed>, assumption">
  - Evidence source: <where the number comes from, or "source not identified">
  - Owner: <team>
  - Type: <leading | lagging | guardrail | health | evidence-generation>
  - Confidence: <high | medium | low | unknown>
- KR2: ...

## Initiatives as Bets
- <initiative>: moves KR<n>; hypothesis: <...>; depends on: <...>

## Guardrails
- <metric and threshold, or "threshold needed">: prevents <failure>

## Alignment Notes
- Parent or strategy link / Peer dependencies / Out of scope this cycle

## Disclosure   (only for feature-team or mixed)
This set frames pre-committed work as outcome bets. If the metrics do not move when the work ships, that is a learning, not a delivery failure. The team keeps shipping; the OKRs inform next cycle's planning.

## Quality Audit
- <criterion>: <pass | risk | fail> - <reason; fix if risk or fail>

## Open Questions
1. <specific, answerable>

## Suggested Next Step
<one concrete action>
```

In Review mode, put a short "What was wrong" list (each original item, the anti-pattern it hit, and why) before the Context section, and map each flawed item to its new place (KR or initiative).

Add a line under Alignment Notes: "Source of truth: this is a planning draft; keep the live version in your OKR tracker."

## Hard rules

- Facts come only from the user's message and attachments. Never invent a baseline, target, benchmark, owner name, team size, date or customer. Write "not given" or mark an assumption.
- Key results measure outcomes, never tasks, launches or counts of activity.
- Do not ask questions before delivering. Decide, label assumptions, deliver, and put anything unresolved in Open Questions.
- The reply is the deliverable; do not build a file unless the user asks for one.
