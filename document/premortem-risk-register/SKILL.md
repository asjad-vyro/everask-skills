---
name: Pre-Mortem Risk Register
description: >
  Turns a planned decision into a ranked risk register: it assumes the plan has already failed, lists why, and gives each top risk an early-warning signal, a mitigation, an owner and a kill criterion.
  Use it for "run a pre-mortem on this plan", "should I do a pre-mortem on this?", "what could go wrong with this launch", "stress-test my decision", "assume this failed, why?", before a launch, hire, migration, investment or other hard-to-reverse choice. If the decision is trivial it says so instead.
---

# Pre-Mortem Risk Register

A pre-mortem assumes the plan has already failed and reasons backward to why, then turns each cause into a signal to watch, an action to take and a pre-decided point at which to stop. A good result is a register the user can act on, not an essay about risk. Deliver it in full in the reply, in one turn.

## Step 1: Frame the decision

From the user's message and any attached files, write down in one or two sentences the plan and the intended outcome. Pick a concrete horizon (for example "six months after launch"). Judge reversibility: one-way door or two-way door.

If the decision is trivial or fully reversible and cheap to undo (a team lunch spot, a tool you can switch back next week), say so in two or three sentences, explain why a pre-mortem is not worth the effort, optionally give one quick sanity check, and stop. Do not produce a register.

Do not ask the user questions. Where a detail is missing (budget, team size, dates), make a stated assumption and carry on. List the assumptions in one line under "Decision under pre-mortem".

## Step 2: Declare the failure

Read `references/TEMPLATE.md` now: it is the exact output shape. Write the failure in the definite past, as observed fact: "It is six months after launch. This plan has failed." Add two or three concrete sentences of what happened. Write it as a plausible imagined scene, introduced as such ("Imagined scene:"). It must contain no numbers, percentages, counts or named events the user did not give; describe in words ("sign-ups stalled", "stock sat unsold"). Do not state as fact details the user did not give (for example that a supplier's past work was on a different product).

## Step 3: Generate causes, then rank

1. List 8 to 12 causes that explain the declared failure, before judging them. Go beyond the technical: people, incentives, process, timing, dependencies, second-order effects, external events.
2. Always include any risk the user's own text points to (a single supplier, one key person, a tight deadline, an unproven assumption, no budget slack). A risk the user stated plainly must not be missed, and a single point of failure the user named (one supplier, one person, one date) ranks in the top two rows.
3. Cluster duplicates. Rate each cluster Likelihood and Impact as H, M or L. These are judgements: say so once.
4. Keep the top 4 to 6 for the register, ranked most dangerous first (impact first, then likelihood). Put the rest on the watch list.

## Step 4: Convert each top cause into action

For every register row fill all four of these. A row missing any of them is not finished.

- **Leading signal / tripwire**: the earliest observable sign, written so someone would notice it, ideally with a threshold the user can set. Where you suggest a number, mark it as a suggested threshold to calibrate, not a fact.
- **Mitigation**: what reduces likelihood or impact, done now or pre-planned.
- **Owner**: a role the user mentioned (for example "ops lead"), or "Plan owner" if none fits. Do not invent names or new job titles.
- **Kill criterion**: the pre-decided condition under which the team stops, rolls back or changes course. It must be checkable and tied to a date or measure.

## Step 5: Write the reply

Use the layout of `references/TEMPLATE.md` and write the register as a markdown table in the reply. Read `references/EXAMPLE.md` once for the quality bar. The reply, in this order:

1. Decision under pre-mortem (decision, intended outcome, horizon, reversibility, assumptions).
2. The failure, declared (past tense).
3. Top risks and what we will do: 3 to 5 sentences naming the two or three biggest threats and the single most important action against each.
4. Risk register table, with the columns in the template. Cause wording in the past tense, tied to the declared failure.
5. Watch list: lower-ranked causes, one line each.
6. One line: "This is a structured judgement exercise, not a forecast; the ratings are estimates to challenge with the people who know the plan." Add the first action to take this week.

## Hard rules

- Never invent facts about the user's business: figures, customers, quotes, dates, vendors. Anything not given is an assumption and labelled as one.
- Every top cause has a tripwire, a mitigation, an owner and a kill criterion.
- Ranked, not an undifferentiated list. No padding: 4 to 6 rows beat 12.
- Do not promise a better outcome; the aim is better-surfaced and better-handled risk.
- Do not run a pre-mortem on a decision that is already made and irreversible with no way to act on the result, or on an outcome already known (that is a post-mortem): say so briefly and offer the closest useful thing instead.
- The register is the deliverable. If the user asks for a file, write the same content to a .docx by loading the built-in `docx` skill with `skill_view`, and publish it with `publish_artifact`, but still show the register in the reply.
