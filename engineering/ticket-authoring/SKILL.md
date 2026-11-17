---
name: Bug Report and Ticket Writer
description: >
  Turns messy notes, a bug description, a feature idea or a spec into ready-to-paste tickets: bug reports, user stories, tasks, spikes and epics.
  Use it for "write a bug report", "turn these notes into a ticket", "write a user story with acceptance criteria", "break this into tickets", "scope a spike", "write a Jira / Linear / GitHub issue".
---

# Bug Report and Ticket Writer

A good ticket lets the person who pulls it start work without asking a question. Deliver the finished tickets in the reply, in Markdown ready to paste into Jira, Linear or GitHub Issues. Never open with questions: decide, state your assumptions, deliver.

## Step 1: Read the source and pick the type

Read everything the user gave (notes, logs, spec, thread). List each distinct defect, outcome, open question and unit of build work in it. Then pick a type for each:

- One defect: **Bug**.
- One user-visible outcome: **Story**.
- Build work with no user-visible outcome of its own: **Task** (usually under a story).
- One open question that needs research before a decision: **Spike**.
- A group of stories aimed at one metric: **Epic**.

If the user asked for a type, use it. If they pasted a spec or idea and said "break this down", produce one epic, its stories, and tasks or spikes under them.

## Step 2: Fill the template

- Bug and story templates are below. For task, spike and epic, read `references/templates.md` first (also holds the severity and priority scales).
- Fill every field. Where the user did not give a fact, write `not given` or mark it `(assumed)`. Never invent build numbers, versions, error text, users, dates, metrics, file paths, ticket ids or names. If the notes lack repro steps, write the steps the notes support, mark gaps, and put "confirm exact steps" in QA notes.
- Quote error text exactly as given.
- Link a spec; do not paste it. Write `none` for a field that is truly empty so the reader knows it was considered.
- Estimates, owners and parent links the user did not give stay `unassigned` or `not given`.

### Bug template

```
TITLE: [area] [symptom] when [trigger]
TYPE: Bug | OWNER: <unassigned> | PARENT: <link or none> | LABELS: <labels>

ENVIRONMENT
- Build or version: <from the user, or not given>
- Browser or device: <...>
- Account type: <...>
- Data state: <...>

REPRO STEPS (from a known starting state, one action per step, include the data typed)
1. <action>
2. <action>
3. <observe the result>
Reproduces: <every time / N of M / once / not given>

OBSERVED
<what happens, exact error text>

EXPECTED
<what should happen, and why (spec, prior behaviour)>

CURRENT TEST RESULT
<failing test name, or "no test covers this path" if unknown>

SEVERITY: <S1-S4>   PRIORITY: <P0-P3>   Reason: <one line>

REGRESSION RISK
<what else shares this code path; what a fix could break>

QA NOTES
- <edge cases beyond the repro>

FIX VERIFICATION
<a named test to add, or numbered manual steps; two people must agree on pass or fail>

EXPECTED RESULT AFTER FIX
<what passing looks like, observable>

ATTACHMENTS
- <screenshot, recording or log the user should attach>
```

Title pattern: `[area] [symptom] when [trigger]`, for example "Checkout: wrong total when a promo is removed" in shape only. Observed and expected are separate lines. If no repro can be written at all, make it a spike: "Find the repro for <symptom>", timeboxed.

### Story template

```
TITLE: <user-facing outcome in a few words>
TYPE: Story | OWNER: <unassigned> | PARENT EPIC: <link or none> | ESTIMATE: <not given>

USER STORY
As a <specific user>, I want <action>, so that <outcome>.

SPEC
<link, or "none given">

ACCEPTANCE CRITERIA
- [ ] Given <context>, when <action>, then <observable outcome>
(cover the happy path, the empty state, the error state and the permission boundary)

NON-GOALS
- <what a reviewer might assume is included but is not>

DESIGNS: <link or none>
ANALYTICS EVENTS: <object_action name, trigger, properties; or none>
FEATURE FLAG: <name and default, or none>

QA NOTES
- <states, roles, platforms, regression areas>

DEFINITION OF DONE
- [ ] Every acceptance criterion checked by someone other than the author
```

Acceptance criteria must be checkable by two people who agree on the result. "Fast" is not checkable; give a threshold with its condition. If the user gave no threshold, propose one and mark it `(assumed, confirm)`. Always include at least one non-goal.

## Step 3: Severity is not priority

Set both on bugs. Severity is how bad the defect is; priority is when to fix it. Use the scales in `references/templates.md`. State the reason for the priority in one line. When they differ, say why.

## Step 4: Check readiness

For each ticket check: title searchable; no field left blank; criteria or verification steps checkable; nothing pasted from a spec; a spike has a timebox in days and ends in a decision memo; an epic has a metric with baseline and target and kill criteria (use `not given` and flag it if the user gave none). Mark each ticket Ready or Not ready, and for Not ready list the exact missing facts.

## Step 5: Output

Put all of this in the reply:

1. For more than one ticket, a summary table first: `| # | Type | Title | Parent | Estimate | Ready |`.
2. Each ticket in full in its own Markdown block, order: epic, stories, tasks and spikes under each story, then bugs.
3. A short "Assumptions and open questions" list: what you assumed and what the user should confirm.

If the user asked to post tickets to Jira, Linear or GitHub and that app is connected, you may offer to; otherwise just return the Markdown. Tickets stay drafts until the user says to file them.

If the team capitalizes software development costs and the user asks for a capitalization stage, add a line `CAPITALIZATION STAGE: preliminary | application development | post-implementation` (spikes that evaluate options are preliminary; build work is application development; fixes on shipped features are post-implementation) and say finance owns the final call. This is not accounting advice. Otherwise leave the field out.

## Hard rules

- Everything is in the reply itself, in full.
- Only facts from the user's material; the rest is `not given` or marked assumed.
- Each bug has numbered repro steps, observed and expected on separate lines, and a named verification.
- Each story has Given/When/Then criteria and a non-goal.
- Each spike has a timebox in days and a decision memo as its output.
- Each epic has kill criteria.
