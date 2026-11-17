---
name: Test Plan and Test Case Writer
description: >
  Turns a ticket, user story, bug report or set of acceptance criteria into a complete test plan: test cases with exact data, steps and observable expected results, plus a traceability table and a list of criteria that are not testable as written.
  Use it for "write test cases for this story", "make a test plan for this bug fix", "how do I test this", "what should QA check", "is this ticket testable", "build a traceability matrix", "exploratory test charter".
---

# Test Plan and Test Case Writer

A good result is a test plan the QA notes on a ticket can use as they are. Every acceptance criterion has at least one case, every case traces to one criterion or one named risk, expected results can be observed, and vague criteria are named as gaps with a measurable rewrite. It works with any tracker and any test runner.

## Step 1: Read the item and decide the type

Use only what the user gave: the pasted ticket, criteria, repro steps, QA notes, spec text. Do not ask questions first. If something is missing (environments, test levels, regression risks), state an assumption in one line and carry on.

Decide the type: bug, story, task, spike or epic.
- Bug: the repro as a failing case, plus regression.
- Story: all six coverage classes considered.
- Task: happy path plus regression.
- Spike, or a story with real unknowns: exploratory charters instead of scripted cases.
- Epic: no cases of its own. Say its stories carry them, and plan for the stories if the user pasted them.

Number every acceptance criterion `AC-1`, `AC-2` and so on (keep the user's numbering if there is one).

## Step 2: Check testability

For each criterion ask: can two people agree on pass or fail? If not ("works fast", "easy to use", "works on all devices"), do not invent a test for it and do not mark it covered. Mark it GAP and write a measurable rewrite for the ticket author. If a threshold in your rewrite is a number the user did not give, label it "proposed, confirm with the author". Where a criterion is ambiguous at a boundary (for example "up to 24 hours before"), write down which reading you used.

## Step 3: Name the risks

List what else shares the code path, data or screen. Use the ticket's regression-risk field if there is one; otherwise propose risks and mark them as assumptions. Each risk becomes a regression case.

## Step 4: Write the cases

Read `references/test-case-template.md` before writing cases, and `references/coverage-checklist.md` to decide what to cover for the type. Read `references/example-test-plan-story.md` if you want to calibrate the level of detail.

Each case has: ID, title, traces to, class, precondition, test data (exact values, such as `jordan@example.test`, not "a valid email"; fixture or made-up data only), numbered steps with one action each, expected result that is observable (a value, a quoted message, a state, a status code), environment, level, automation status, evidence to attach.

Classes: happy path, boundary and edge, negative and error, regression, accessibility smoke, performance smoke. For a story, every class gets cases or a one-line "not applicable, because".

Level: the lowest that can observe the result. Unit for a return value inside one module, integration when two parts talk, end-to-end when only the full user path shows it, manual when it needs human judgment (write the reason). Do not mark everything manual.

When the expected result depends on a figure the user did not state (a price, a limit, an error text), say it must be confirmed against the spec; never present a made-up value as the product's real behaviour. Test data you choose yourself is fine as long as it is plainly test data.

If the case needs arithmetic (totals, taxes, discounts, date offsets), do the sums in `execute_code` and copy the results into the expected values.

## Step 5: Exploratory charters

For spikes and real unknowns, read `references/exploratory-charter-template.md` and write charters: one question each, 30 to 90 minute timebox, "Explore [target] with [resources] to discover [question]".

## Step 6: Evidence

For each case say what a pass must leave behind: a runner summary line, a screenshot showing X, a log line containing Y, a response body. "Tested" with no artifact is not a result. If someone (or a coding agent) will run the plan, tell them to report each case as pass (with the quoted evidence), fail (with the output) or untestable (with the reason), never to edit assertions or expected values to turn a failure green, and never to count a tool's "command completed" as a pass.

## Step 7: Build the matrix and check it

Read `references/traceability-matrix-template.md` and `references/test-plan-template.md`. Build the criterion-to-case table, then run the reverse check: every case appears once with exactly one trace, every criterion has a case or a GAP with a reason, every risk has a row. Count the cases by level from your own list so the summary numbers are right.

## Output (the whole thing goes in the reply)

Deliver in this order, in full, in the reply itself. If the user asks for a file, also save `test-plan-<ticket-id>.md` with `write_file` and publish it with `publish_artifact` (kind "file"), but still put the plan in the reply.

1. **Assumptions**: one short list (type, environments, levels, anything you inferred).
2. **Test plan summary** for the ticket's QA notes: scope, classes covered (with reasons for any skipped), case count by level, environments, evidence, three to six lines.
3. **Traceability matrix**: table with criterion or risk, short text, cases, levels, status (`covered`, `partial`, `GAP`, `untestable`, `deferred`).
4. **Test cases** in full, in ID order.
5. **Exploratory charters**, if any.
6. **Gaps**: each untestable criterion, why, and a proposed measurable rewrite.

## Hard rules

- Never invent facts about the product: no real error texts, limits, prices, endpoints or behaviours the user did not give. Mark anything inferred as an assumption.
- Never write a case for an untestable criterion as if it were testable, and never mark one covered.
- Every case traces to exactly one criterion or named risk; cut the ones that do not.
- Expected results are observable. "Works correctly" is not a result.
- Test data is made up, using test domains and fixture accounts, never real customer data.
- Any threshold or timing you choose (seconds, limits, TTLs) is labelled "proposed" wherever it appears, including inside rewrites and cases. Do not make unsourced claims about what usually causes a bug or how often.
- Finish in one reply, with no closing offer or question. Do not stop to wait for approval.
