---
name: SWOT Analysis (Evidence-Checked)
description: >
  Turns a business, plan or decision into a SWOT where every point is labelled evidence or assumption, ranked, and matched into concrete strategic options and next steps.
  Use it for "do a SWOT", "SWOT for my bakery", "SWOT of our company vs competitors", "TOWS matrix", "strengths weaknesses opportunities threats".
---

# SWOT Analysis (Evidence-Checked)

A good result is not a long four-box list. It is a short SWOT in which each point says whether it rests on a fact the user gave (or a source you found) or on an assumption, the few points that matter are marked, and the four lists are crossed into named options (TOWS) with a clear next step. The whole job is done in one reply, from what the user gave you.

## Step 1: Pin down the situation

1. Write one line: what decision or situation this SWOT is about (for example "whether this business should do X"). Take it from the message and any attached text.
2. If the user gave little, do not stop to ask. Decide a sensible reading, and state it in one line as an assumption.
3. Collect every fact the user gave: figures, customers, products, competitors, constraints, dates. Only these count as evidence in Step 3. Never add facts the user did not give.

## Step 2: Check the outside world (optional, at most two searches)

External factors (market trends, regulation, competitors) are the part the user's notes usually lack. If the subject is a real, named company or a market where current facts would change the answer, run at most two `web_search` or `web_extract` calls and keep the source link for each fact you use. If the user supplied enough, or the subject is private or hypothetical, skip this step. Do not search for internal facts: those come only from the user.

## Step 3: Fill the grid, sparingly

- Strengths and Weaknesses are internal (the organisation's own resources, capabilities, habits, position). Opportunities and Threats are external (market, customers, competitors, rules, technology). Sort each point by that test: if the organisation could change it directly, it is internal.
- Three to five points per box. Fewer is fine when the input is thin. Do not pad to reach five.
- Tag every point with one label:
  - `[evidence: user]` the user stated it or it follows directly from what they gave.
  - `[evidence: source]` found by search; add the link.
  - `[assumption]` plausible but not given or found. An unverified point is a hypothesis, not a finding.
- If the user compared themselves with competitors, make the comparison point by point and name only the competitors the user named.
- Never invent numbers, customers, prices, market sizes, quotes or dates. If a number would help and was not given, write the point without it and add "figure not given".
- Mark with a star the one or two points per box that would most change the decision, and drop filler.

## Step 4: Match (TOWS)

Cross the starred and strongest points to produce options, one to two per cell, each a concrete action and not a restated point:

- S-O: use a strength to seize an opportunity.
- S-T: use a strength to counter a threat.
- W-O: fix a weakness so an opportunity can be taken.
- W-T: limit the damage where a weakness meets a threat.

Where a cell has no honest option, write "no clear option from the points above" instead of forcing one.

## Step 5: Recommend and name the checks

Pick the one or two strongest options and say why. Then list the `[assumption]` points those options rest on, each with the cheapest way to verify it (a question to ask, a number to pull, a test to run). If the user's numbers allow a sum (for example a break-even or a share), do it in `execute_code` and copy the result; never calculate in your head.

## Output

Put the full deliverable in the reply, in this order, with no preamble and no promise of a later document:

```
**Situation:** <one line> (Assumed: <anything you assumed about the situation, or "none">)

**A note on method:** A bare SWOT grid is weak analysis (a well-known 1997 study of consultants' SWOT work found long, unprioritised lists that did not amount to analysis). That is why each point below is labelled, ranked and matched into options. <one line only; do not add statistics about how well SWOT works>

| Internal | External |
|---|---|
| **Strengths**<br>- * <point> `[evidence: user]`<br>- <point> `[assumption]` | **Opportunities**<br>- * <point> `[evidence: source]` <link><br>- <point> `[assumption]` |
| **Weaknesses**<br>- * <point> `[evidence: user]`<br>- ... | **Threats**<br>- * <point> `[assumption]`<br>- ... |

(* marks the points that would most change the decision)

**Options (TOWS)**
| Match | Option |
|---|---|
| S-O | <action> |
| S-T | <action> |
| W-O | <action> |
| W-T | <action> |

**What to do first:** <the one or two strongest options and why>

**Check before you commit:** <each assumption those options rest on> : <cheapest way to verify it>
```

## Hard rules

- Every point carries a label. No unlabelled points.
- Facts come only from the user or from a source you link. Everything else is an `[assumption]`, and you say so.
- If the user gave almost nothing, the grid is mostly assumptions: say that plainly in one line under the table and make the "Check before you commit" list the useful part.
- This is a thinking aid, not professional financial or legal advice.
- Never end by asking for more information; finish with what you have.
