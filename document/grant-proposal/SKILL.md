---
name: Grant Proposal Writer
description: >
  Writes a complete grant proposal or funding application, tailored to the funder's stated priorities, with need, objectives, methods, impact, budget logic and risks.
  Use it for "write a grant proposal", "draft a funding application", "turn these project notes into a grant application", "write the narrative for this grant".
---

# Grant Proposal Writer

A good grant proposal answers what the funder wants to fund, not only what the applicant wants to do. The result is a full proposal in the reply, with every funder criterion visibly answered, and every gap in the user's facts marked rather than filled in.

## Step 1: Gather what the user gave

From the message, pasted guidance and attachments, list: funder and programme, amount sought, project description, the organisation (type, track record), the funder's priorities or assessment criteria, word or page limits, deadline, currency. Do not ask questions. Whatever is missing, decide, state the assumption in one line, and carry on.

## Step 2: Build the criteria map

If the user pasted funder criteria or guidance, number each criterion or priority exactly as the funder words it. If none were given, say so and use a short list of generic priorities (need, fit with the funder's mission, feasibility, value for money, sustainability), marked as an assumption. Do not invent the funder's priorities from memory. If the user named a funder but gave no criteria, you may do up to two `web_search` or `web_extract` calls for the programme's published guidance and link what you used.

## Step 3: Write the proposal

Use these sections, in this order, with these headings. Where a funder's form has its own sections, use the funder's headings and order instead, and map the content below onto them.

1. **Project title**: informative, says the problem and the approach.
2. **Project summary** (200 to 300 words unless the funder sets a limit): what will be done, why it matters, who benefits, the measurable outcomes. Write it last, place it first.
3. **Need**: the problem, who is affected and how many, what exists now and why it falls short, the cost of doing nothing, why this organisation. Use only evidence the user gave. Where data would go, write `[evidence needed: <what kind of data>]`. Never invent a statistic or cite a study you have not been given or found.
4. **Objectives**: three to five SMART objectives, each with a measure and a date or month.
5. **Approach**: phases with months, activities, who does what, what is produced, and why this approach over alternatives.
6. **Impact and outcomes**: a table with columns Level (output, short-term outcome, medium-term outcome, long-term impact), Description, How measured. State direct beneficiaries and sustainability after the grant ends.
7. **Evaluation plan**: who evaluates, what is measured, when, how findings are shared.
8. **Budget narrative**: a table with columns Budget line, Amount, Justification. Lines: staff, travel, equipment or materials, delivery costs, indirect costs, total. Work out every sum, percentage and per-beneficiary cost in `execute_code` and copy the results; never add in your head. If the user gave no budget, build a draft that totals to the amount sought if one was given, label every figure `assumption` and put placeholders for rates and salaries: `<rate to confirm>`. Add a value-for-money line (cost per beneficiary, what cannot be done without the grant) only when the numbers exist. Check the funder's rules on indirect costs and name the percentage as an assumption if not given.
9. **Organisational capacity**: track record, governance, financial management, using only what the user gave. Otherwise `[organisation to add: past grants and outputs]`.
10. **Risks**: a table with Risk, Likelihood (H/M/L), Impact (H/M/L), Mitigation. Four to six risks that follow from the project described.

## Step 4: Check before replying

Do this in your head or in a short scratch list, then fix the draft:
- Every numbered criterion from Step 2 is addressed in a named section.
- Every number in the text appears in the user's input or a tool result, or is marked as an assumption.
- Budget lines add up to the stated total, and the total matches the amount sought.
- Word or page limits are respected: count the words of each section in `execute_code` when a limit is given, and trim.
- Plain language a reviewer outside the field can follow; no filler or unsupported claims such as "innovative" without saying what is new.

## Step 5: Reply

Put the whole proposal in the reply, in this shape:

1. A short block "Assumptions and gaps": what you assumed, and the list of `[...]` items the user must fill in. Keep it to the real gaps.
2. "Criteria map": a table with Funder criterion and Where answered (section name).
3. The proposal, sections 1 to 10 as above.

Only if the user asks for a file, load the built-in `docx` skill with `skill_view` and follow it, then publish it with `publish_artifact` (`kind: "document"`).

## Hard rules

- Never invent facts: statistics, past grants, partners, quotes, salaries, dates, beneficiary counts, or what the funder prefers. Use the user's figures or mark `[to add: ...]`.
- The proposal is a draft for the user to review; nothing is submitted or sent.
- Funding rules, deadlines and amounts change: for anything about the funder's current rules that the user did not supply, check the funder's own page and link it, or say it is unchecked.
- Never open with a list of questions and never stop to ask for approval: deliver the full proposal in one reply.
