---
name: Project Timeline and Gantt
description: >
  Turns a project's task list into a Gantt chart workbook: start and end dates worked out from durations and
  dependencies, the project end date, the critical path, and a colour-coded timeline sheet that fits on a screen.
  Use it for "make a Gantt chart", "build a project timeline", "schedule these tasks", "when will this project finish",
  "plan this project over 6 weeks".
---

# Project Timeline and Gantt

The user gets an Excel workbook with a Tasks sheet and a Timeline (Gantt) sheet, and a short reply with the end date, the critical path and any conflict. The dates come from a script that does the arithmetic, never from mental maths.

## Hard rules

- Write everything the user will read (sheet names, headers, reply) in the language the user wrote in, unless they ask for another. Keep their task names, owner names and figures exactly as given.
- Use only the tasks, owners, durations, dependencies and dates the user gave. Never invent a start date, a holiday or a deadline. The one exception: when the user gives only a goal and asks for a plan (Step 1, case B), you propose the tasks and mark each as suggested.
- Every date in the workbook comes from the script's output. Never calculate a date yourself.
- Never end the turn without the published workbook.

## Step 1: Get the task list into one shape

Read the message and any attached file (a pasted list, a table, a CSV or a spreadsheet). Build a list with, for each task: `id`, `name`, `owner`, `duration` (whole working days), `depends_on` (a list of ids), `status`.

If the user asks you to pull the task list from Google Sheets, Asana, Trello or Notion and that app is connected, use it. Otherwise work from what they gave you.

Case A, the user gave tasks:
1. Keep the user's task names and owners exactly. Give ids `T1`, `T2`, ... in their order, unless they already have ids.
2. Dependencies written as names ("after design is approved") become the ids of those tasks. Dependencies are finish-to-start: a task begins the working day after the last task it depends on ends.
3. A duration in weeks becomes 5 working days per week (the work week's length, if the user gave another). A task with no duration: assume 1 day and list it under assumptions. A milestone has duration 0.
4. Status: the user's, else "Not started".

Case B, the user gave only a goal (for example "organise a school event in 6 weeks"):
1. Propose 8 to 14 tasks that cover the goal from start to finish, with realistic durations, owners left blank unless given, and dependencies.
2. Set every status to "Suggested" so the user can see these tasks are yours.
3. Fit them inside the time the user stated: after the script runs, `project_weeks` must not exceed it. If it does, shorten durations or remove dependencies you invented, and run again.

Dates and calendar:
- `start_date`: only when the user gave one, as `YYYY-MM-DD`. A date like 03/04 that could be read two ways: pick the reading that matches the user's language and say which one you used. No start date: leave it `null`; the workbook then uses week numbers (Week 1, Week 2...) and the reply says so.
- Working days are Monday to Friday unless the user says otherwise (`work_week` is a list of weekday numbers, Monday = 0). Holidays only if the user listed them. A deadline only if the user gave one.
- Not supported: lags, overlaps, "must not start before" dates. If the user asks for one, schedule without it and say so in the assumptions.

Ask nothing. Decide, state each assumption in the reply, and go on.

## Step 2: Run the scheduling script

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `schedule.py` under `~/.computer/skills` with `search_files`.

1. With `write_file`, save the list as `/tmp/.scratch/project-timeline/in.json`:

```
{"start_date": "<YYYY-MM-DD or null>", "work_week": [0,1,2,3,4], "holidays": [], "deadline": null,
 "tasks": [{"id": "T1", "name": "<task as given>", "owner": "<owner as given>", "duration": <days>,
            "depends_on": [], "status": "<status>"}]}
```

2. Run: `python3 -I SKILL_DIR/scripts/schedule.py /tmp/.scratch/project-timeline/in.json /tmp/.scratch/project-timeline/out.json`
3. The command prints one summary line, then each error or warning. Read `out.json` for the details.
4. If `ok` is false, the message says why: a dependency cycle (it names the tasks in the loop), an unknown task id, a bad duration, a bad date. Do not guess a fix silently. For a cycle, drop the dependency that points from a later step back to an earlier one, run again, and report exactly what you dropped. For anything else, correct the input (a typo in an id, for example) and run again. If it still fails after one correction, deliver no workbook and tell the user the exact conflict and what they need to decide.
5. A warning starting with `CONFLICT` means the schedule ends after the user's deadline. Keep the schedule as computed, deliver it, and report the conflict with the number of days late.

`out.json` fields you use: `end_date`, `project_days`, `project_weeks`, `critical_path` (task ids in order), `timeline.unit` and `timeline.columns` (each with `label`, and `from` and `to` dates when dated), and for each task `start`, `end`, `start_day`, `end_day`, `start_week`, `end_week`, `col_start`, `col_end`, `slack_days`, `critical`.

## Step 3: Build the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it, including its delivery step. Do not call `publish_artifact` for this file. Name the file after the project, for example `<project>-timeline.xlsx`. Fonts: one plain font, size 10 or 11. Build with openpyxl from the values in `out.json`; the dates are values, not formulas.

**Sheet 1, Tasks.** Row 1 is the header, one task per row in the order given, no blank rows. Columns:
`ID | Task | Owner | Start | End | Days | Depends on | Status | Float (days) | Critical`
- Dated mode: Start and End are real Excel dates, number format `dd mmm yyyy`. Undated mode: the columns are `Start week` and `End week` and hold the numbers `start_week` and `end_week`.
- Days = `duration`. Depends on = the ids joined by commas. Float = `slack_days`. Critical = "Yes" for critical tasks (in the user's language), else blank.
- Bold header with a light fill, freeze the top row, turn on the filter, set column widths to fit (Task about 32, Owner 14, others 10 to 12).
- Below the table, after one blank row: `Project end`, the end date (or "Week <project_weeks>"), and `Critical path`, the critical tasks' names joined with " > ". Use the user's language for these labels.

**Sheet 2, Timeline.** The Gantt chart, laid out so it fits on one screen and one landscape page:
- Row 1: the project title. Row 2: the legend: a red cell, "critical path"; a blue cell, "other tasks"; and, in undated mode, the word for "week" (or "day", from `timeline.unit`) in the user's language. Row 3: hidden, holds the numbers 1 to N over the grid columns. Row 4: headers. Tasks start in row 5, in the same order as the Tasks sheet.
- Columns A to H: `ID`, `Task`, `Owner`, `Start`, `End`, then three hidden helper columns: F = `col_start`, G = `col_end`, H = 1 if critical else 0. Hide F, G and H and row 3.
- Grid columns start at column I, one per entry in `timeline.columns`. Row 4 header: dated mode, the column's `from` date as a real date, number format `dd mmm`, so Excel shows the month in the user's own language; undated mode, the label with its leading letter removed (`W3` becomes 3), under the unit word in row 2.
- Widths: A 5, B 30, C 12, D and E 11, grid columns 4 when `timeline.unit` is "day" and 5.5 otherwise. Rotate the row 4 headers 90 degrees when the unit is "day". Never more than 26 grid columns: the script already groups weeks when the project is longer.
- Colour with conditional formatting only, applied to the grid range from I5 to the last grid column and last task row, using two formula rules (first rule, stop if true):
  1. `=AND(I$3>=$F5,I$3<=$G5,$H5=1)` fills red (`C0392B`).
  2. `=AND(I$3>=$F5,I$3<=$G5)` fills blue (`2E75B6`).
  Cells carry no text. Add thin light-grey borders to the grid so empty weeks are visible.
- Freeze panes at `I5` so the task names stay in view. Page setup: landscape, fit to 1 page wide, print titles on rows 4 and columns A:B.
- Milestones (duration 0) fill one cell, like any other task.

Then check, in code, before delivering: the Tasks sheet has one row per task; every Start is on or before its End; the Timeline sheet's last grid column is no further than column AH (26 grid columns); and reopening the file with openpyxl shows both sheets. Fix once if something fails.

## Step 4: Reply

Keep it short, in the user's language. Use this shape:

```
<One line: the workbook is ready, with its name.>
**Project end:** <end date, or "Week N" when undated>  (<project_days> working days)
**Critical path:** <task names in order, joined with " > ">
**Conflicts:** <deadline conflict with days late, cycle you had to break, or "none found">
**Assumptions:** <bullets: start date or "no start date, so weeks", work week, durations you assumed, suggested tasks, anything not supported>
```

If a task has float, you may add one line naming the task with the most float. Do not paste the workbook's rows into the reply.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. For a new duration, owner, task, dependency or start date: edit the task list from Step 1, run the script again on the full list, rebuild the workbook, and keep the same file name. For a formatting change (colours, widths, a column), open the existing workbook and edit it. Say in one line what changed, and, if the end date moved, the new end date.
