---
name: 30-60-90 Day Onboarding Plan
description: >
  Builds a 30/60/90-day onboarding plan for a new hire as an Excel workbook with weekly tasks, review checkpoints and resources, plus guidance for the mentor, manager and new hire.
  Use it for "make a 30/60/90 day plan for a new product manager", "onboarding plan for a remote support hire", "new-hire plan with mentor cadence".
---

# 30-60-90 Day Onboarding Plan

A good result is a workbook the manager can hand to the new hire as it is: every item is a checkable task, the dates move when the start date changes, and the first week asks for no business judgement. Work from what the user gave. Do not ask questions; fill gaps with sensible assumptions, label them, and deliver the full result in this one reply.

## Step 1: Read the situation and set assumptions

Pull out of the message: role and level, start date, manager and mentor, team projects, what the new hire should own alone by day 90, mandatory compliance or security training, probation checkpoints, and whether the person is remote.

For anything missing, decide and record it as an assumption (for example "Start date: assumed next Monday", "Mentor time: 30-minute one-on-one weekly"). Put names, systems and documents the user did not give as "[TBD]". Never invent a tool name, policy, project, person or figure as fact.

## Step 2: Set the three phase goals

- Days 1-30: learn and integrate.
- Days 31-60: deliver under guidance.
- Days 61-90: deliver independently.

Map the user's day-90 expectation onto these. The day-90 scope must match the independent ownership the user described, and nothing larger. Deliverables grow from small to large, and there is no independent external delivery in the first 30 days.

If the user gave no day-90 expectation, set a conservative scope that fits the level and record it in Assumptions. Junior or entry level: one small recurring task or one internal-facing project, with the mentor reviewing drafts through day 90. Mid or senior: one owned workstream with manager sign-off. External-facing work, stakeholder-negotiated ownership and running kickoffs appear only when the user asks for them. In weeks 1-4, deliverables are practice or internal drafts reviewed by the mentor, never production or external assets.

## Step 3: Design the rows

Plan 3 to 6 items per week for 13 weeks (weeks 1-4 phase 1, 5-8 phase 2, 9-13 phase 3). Rules:

- Each item starts with a verb and is one task per row. Each has a completion criterion that can be checked: a deliverable, a passed quiz, a demo given, "3 questions written down". Never "understand the business".
- Weeks 1 and 2 include system access, one-on-ones with the team, and required reading. Week 1 is orientation and relationships only, with no task needing business judgement.
- Include the mandatory compliance and security training the user named, early. If none was named, add one row "Complete mandatory compliance and security training [TBD: list from HR]".
- Category is one of exactly five: Business knowledge, Tools and process, Relationships, Deliverables, Compliance training.
- Owner is a role: New hire, Mentor, Manager or HR. State the mentor's time commitment in the plan (default one 30-minute one-on-one a week); do not assume unlimited mentor time.
- If the person is remote or the team is distributed, add an item in week 1 or 2: "Agree asynchronous communication and tool conventions" (channels, response times, meeting norms), and favour video one-on-ones and written check-ins.
- Probation or contract matters follow company policy and local rules. Only flag them in the Milestones sheet; draw no conclusions.

## Step 4: Build the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it. Use `execute_code` to build the file. Title and file name: "<Role> 30-60-90 Day Onboarding Plan.xlsx". Sheets:

1. **Plan**. A1 is the title. A2 is "Start date" and B2 holds the start date as a real date (the cell the user edits). Header row 4 with columns: Phase | Week | Category | Item | Completion criterion | Owner | Target date | Status. Rows from row 5. Target date is a formula, never a typed date: `=$B$2+<days>` where days is the end of that week (week 1 = 4 working days after the start, then 7 per week: `=$B$2+4`, `=$B$2+11`, and so on), formatted as a date. Status is a dropdown (Not started, In progress, Done), default "Not started". Fill colour distinguishes the three phases; freeze the header row; add a filter; wrap text and set readable column widths.
2. **Milestones**. Columns: Checkpoint | Review format | Assessment dimension | Pass criterion | Assessor | Outcome. Checkpoints: end of week 1, day 30, day 60, day 90. Each has 3 to 5 dimensions, and the day-90 pass criteria echo the 90-day goal. Include a row noting probation review conditions follow company policy (if the user mentioned probation). Outcome is left blank.
3. **Resources**. Columns: Type (document / system / person) | Name | Purpose | How to get it. Use what the user gave; everything else reads "[TBD]".

After saving, recalculate or check the formulas with a quick `execute_code` read-back (confirm Plan!G5 is a formula, that the dates differ from B2 sensibly, and that no cell shows an error). Publish with `publish_artifact`, `kind: "document"`.

## Step 5: Write the reply

The reply must contain, in this order:

1. A line stating the file was published, and a short **Assumptions** list (including the day-90 scope default if you set it). Do not open with filler about loading skills or what you are about to do.
2. The three phase goals, one sentence each, tied to the user's day-90 expectation.
3. **Guidance** in three groups, 5 points or fewer each:
   - Mentor: weekly one-on-one cadence and length, feedback style, what to do each phase.
   - Manager: the questions to ask at day 30, day 60 and day 90.
   - New hire: how to update the Status column and the start-date cell.
4. One reminder that this is a living document: review and adjust phases 2 and 3 after the day-30 checkpoint.

## Hard rules

- No questions to the user. The workbook and reply are produced in one pass.
- No invented names, tools, policies, dates or statistics; unknowns are "[TBD]" or a labelled assumption.
- Target dates must be formulas from the start-date cell so changing it re-dates the plan.
- The result is a planning aid, not HR or legal advice; employment and probation decisions follow company policy and local law.
- Do not email or share the plan anywhere; hand over the file only.
