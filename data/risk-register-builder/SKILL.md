---
name: Risk Register Builder
description: >
  Builds a scored project risk register: likelihood x impact, RAG status, owners, mitigations, contingencies, a heat map and a top-5 summary.
  Use it for "build a risk register", "score these risks and rank them", "make a risk matrix for our launch", "what risks should we track for this migration".
---

# Risk Register Builder

A good result is a register a steering committee could read as it stands. Every risk is specific, scored with one fixed scale, ranked by exposure, and has a named owner role, an active mitigation and (for High and Critical) a contingency. The whole register goes in the reply itself, in full. Do not ask questions first: work from what the user gave and mark gaps as assumptions.

## Step 1: Gather what you have

From the message and any attached or pasted text, note: project or product name, stage (discovery, delivery, launch, live), objectives, risks already named, dependencies (vendors, teams, systems, approvals), hard dates, and the audience. If something is missing, assume it, tag it *(assumed)*, and list it at the end. Ask nothing unless there is no subject at all to write about.

If the user gave risks with their own likelihood and impact scores, keep those scores exactly. Only score the risks that came without scores, and say which ones you scored.

## Step 2: Build the risk list

1. Start with every risk the user named. Rewrite each so it is specific: cause, event, consequence ("Because <cause>, <event> may happen, leading to <consequence>"). Use only names, vendors and dates the user supplied.
2. If the user named fewer than 8 risks, add risks from the project's own context until there are 8 to 12. Pull prompts from the categories in `references/risk-prompts.md` (read it only when you need to add risks). Label every added risk "suggested" in the Source column so the user can tell them apart from their own.
3. Separate risks from issues. Something that has already happened goes in a short "Issues, not risks" list under the register, not in it.
4. Give each risk one category: Schedule, Technical, Resource, Commercial, Compliance, Stakeholder or External.

## Step 3: Score it all in code

Never do the arithmetic in your head. Use `execute_code` once to:

1. Set L and I (1 to 5 each) for every risk, using the scales in Step 4.
2. Compute Score = L x I.
3. Assign RAG from the score: 12 to 25 is Red, 4 to 11 is Amber, 1 to 3 is Green. Within Red, 20 to 25 is "Critical" and 12 to 19 is "High". Within Amber, 8 to 11 is "Medium" and 4 to 7 is "Low". 1 to 3 is "Negligible". Use this one rule everywhere, including the heat map.
4. Sort by Score descending; break ties by Impact, then Likelihood. Number the risks R01, R02 ... in that ranked order, unless the user's risks already have IDs, in which case keep their IDs.
5. Build the heat map: a 5x5 grid (rows L5 down to L1, columns I1 to I5), each cell listing the IDs of the risks that land there, and the cell's RAG word.
6. Print the final table rows as markdown, and copy them into the reply unchanged.

## Step 4: Scales to use

Likelihood: 5 Almost certain (over 80%), 4 Likely (60 to 80%), 3 Possible (40 to 60%), 2 Unlikely (20 to 40%), 1 Rare (under 20%).

Impact: 5 Critical (programme failure, regulatory breach, major financial loss or safety event), 4 High (delay over 4 weeks, scope cut, reputational damage), 3 Medium (1 to 4 weeks delay, cost overrun, reduced quality), 2 Low (under 1 week, manageable cost), 1 Negligible (easily absorbed).

If the user's project uses a different scale, use theirs and say so.

## Step 5: Write the reply

Use this order and these headings. Values in angle brackets come from the user's input or your marked assumptions.

```
# Risk Register: <project name>

**Stage:** <stage> | **Version:** 1.0 | **Owner:** <role> | **Last reviewed:** <today's date> | **Next review:** <weekly in delivery, monthly in discovery>
**Audience:** <audience>

## Summary
<Two or three sentences: how many risks, how many Red / Amber / Green, the single biggest exposure, and the decision most needed.>

## Risk register
| ID | Risk | Category | L | I | Score | RAG | Owner (role) | Status | Mitigation | Contingency | Review date | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Heat map
<the 5x5 grid from Step 3, as a markdown table>

## Top 5 risks for the steering committee
| Rank | Risk (plain English) | Score | RAG | Owner | Mitigation status |
|---|---|---|---|---|---|
**Decisions needed:** <budget, scope or date decisions the top risks require, or "none identified">

## Issues, not risks
<anything already happened, or "none given">

## Assumptions
<every assumed input, every risk you scored yourself, every added risk, every owner role you chose>

## How to keep this register alive
<three lines: review cadence by RAG, closure criteria, archive closed risks rather than deleting them>
```

Use words in the RAG column ("Red - Critical", "Amber - Medium", "Green - Negligible"), so the table reads without colour. Status is Open, Mitigating or Closed; new risks are Open. In the Top 5 table, Mitigation status is the same Status word (Open, Mitigating or Closed) and nothing else: no claims like "not yet booked", "being sought" or "not started" unless the user said so. Do not add commentary on ties; if you mention order at all, cite only the Step 3 rule (Score, then Impact, then Likelihood). Review dates: Red weekly, Amber fortnightly (Medium) or monthly (Low), Green only if context changes. Work the dates out from today's date in `execute_code`.

Closure criteria to state: the event can no longer occur (milestone passed, contract signed); or the score is 1 to 3 and the team formally accepts it; or it happened and moved to the issues log.

## Hard rules

- Every figure in the reply (L, I, Score, counts, ranks) comes from the `execute_code` output.
- Do not invent facts: no vendor names, people, dates, budgets, percentages or past incidents the user did not give. Where you need a value, write "not given" or mark an assumption.
- Mitigations, contingencies and Decisions needed contain no calendar date, month or deadline the user did not give; use relative wording instead ("before launch", "at least two weeks before <user's date>"). Review dates from Step 5 are the only computed dates.
- Do not state unstated project facts (for example "no float", "handles card data") as context; write them as "if ... *(assumed)*" and list them in Assumptions.
- Owners are role titles (for example "Engineering lead"), not made-up people. Use a person's name only if the user gave it. Never "the team" or "TBD".
- A mitigation is an action being taken to cut likelihood or impact, not "monitor and review". Every Red risk has a contingency: what to do if the mitigation fails. Amber and Green may say "none needed".
- Likelihood and impact for risks you add are judgement calls: say so in the Assumptions section and invite the user to adjust.
- Do not build a file unless the user asks for a spreadsheet; if they do, load the built-in `xlsx` skill with `skill_view` and put the register table in it, then publish it with `publish_artifact` and still show the table in the reply.
- Work from the message and attachments only. If the user wants the risks pulled from an app and it is connected, use it; otherwise carry on without it.
