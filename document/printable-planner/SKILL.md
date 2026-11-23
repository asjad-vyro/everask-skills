---
name: Printable Planner Maker
description: >
  Makes a one-page printable weekly plan as a PDF: study timetable, class schedule, workout routine, meal plan or chore chart.
  Use it for "make me a study timetable", "weekly schedule to print", "3-day workout plan", "meal plan for the week", "chore chart".
---

# Printable Planner Maker

A good result is one clean A4 page, a grid with days across, that the user can print or pin up, built from their constraints and checked in code (no overlaps, hours per subject right, fixed commitments untouched). The PDF is published with `publish_artifact`, and the plan is also written out in the reply.

Hard rules:
- Write the plan in the language the user wrote in, unless they ask for another. Day names are in that language. Keep the user's subjects, names, foods and figures exactly as given.
- Use weekday names only. Do not put dates on the page unless the user gave them.
- Do not invent commitments. Fixed items (school, work, classes) are only those the user gave, at the times they gave.
- Do all sums and the overlap check with the script (it runs in code); never count hours by hand.
- Meal and workout plans are general wellbeing only: no calorie or macro targets, no weight-loss promises, no medical claims unless the user gave the numbers. Respect every stated allergy or food to avoid strictly. Put one line in the footer, in the plan's language, saying the plan is general and not medical or dietary advice.
- The title, subtitle and footer may only state what the grid itself shows (no progression, weeks or targets that are not in the cells).
- Do not ask questions. Decide, state the assumption in one line, deliver.
- Never install a browser or any PDF package. The script finds Chrome itself; if it prints `PDF NOT BUILT`, publish the html as `html_preview` and say so.

## Step 1: Decide the shape

1. Pick the mode.
   - `time`: a time grid (study timetable, class schedule, daily routine). Days across, times down.
   - `grid`: named rows by days (meal plan: rows are the meals; workout: rows are the warm-up, exercises and cool-down; chore chart: rows are the chores or people).
2. Days: all seven by default, or only the days the user named (for example "3 days a week": choose evenly spaced days such as the first, third and fifth day of the week and say so, unless the user named days). Orientation `landscape` by default, `portrait` for a chore chart or a plan with only 3 days and many rows.
3. If the user gave too little (for example no hours), assume simple defaults, state them in one line, and go on.

## Step 2: Build the plan

Time mode:
1. List the fixed commitments first, one entry per day, `kind: "fixed"`.
2. Add the free-time blocks (`kind: "task"`) the user asked for: each subject or activity gets the weekly hours the user gave, split into sessions of 30 to 120 minutes, spread across different days, with the hardest or the most hours spaced out, not stacked on one day. Respect every limit the user gave (earliest start, latest end, rest day) by putting them in `limits`, and put the weekly hours per subject in `targets` so the script checks them. Add short `rest` blocks only if the user asked for breaks.
3. Times are 24-hour `HH:MM` unless the user clearly uses another clock, in which case keep their style on the page by writing the label text accordingly (the script's time axis stays 24-hour).
4. Entry shape: `{"day": 0, "start": "16:00", "end": "17:30", "label": "<subject>", "kind": "task"}`, where `day` is the 0-based index into `days`. Use the user's subject names as labels.

Grid mode:
1. `rows` are the row names in the user's language; `cells` are `{"day": i, "row": j, "text": "<short text>"}`, 1 to 12 words each.
2. Meals: simple home-style dishes with no word from the user's avoided foods (put those words in `avoid`; the script rejects any cell containing one). Workouts: beginner-safe bodyweight exercises with sets and repeats or minutes, rest days left blank or marked as rest in the user's language. Chores: split fairly across the people or days the user gave.

## Step 3: Check and render

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Use the full path where the command below says `SKILL_DIR`. If `skill_view` gives no path, find `build_planner.py` under `~/.computer/skills` with `search_files`.
2. Use `write_file` to save `/tmp/.scratch/printable-planner/spec.json`:

```json
{"mode": "time", "title": "<title>", "subtitle": "<optional>", "lang": "<code>", "dir": "ltr", "orientation": "landscape",
 "days": ["<day 1>", "<day 2>"], "footer": "<optional line>",
 "limits": {"earliest": "HH:MM", "latest": "HH:MM"}, "targets": {"<label>": 0},
 "entries": [{"day": 0, "start": "HH:MM", "end": "HH:MM", "label": "<text>", "kind": "fixed | task | rest"}]}
```

   For grid mode use `"mode": "grid"`, `"rows": [...]`, `"cells": [...]` and optionally `"avoid": [...]` instead of `limits`, `targets` and `entries`. `dir` is `rtl` for Arabic, Hebrew, Persian and Urdu. `limits`, `targets` and `avoid` are optional and only filled with what the user gave.
3. Run in `terminal`:
   `python SKILL_DIR/scripts/build_planner.py /tmp/.scratch/printable-planner/spec.json /tmp/.scratch/printable-planner/out <plan-name>`
   with `<plan-name>` a short file name from the title. It checks overlaps, limits, targets and avoid-words, prints `TOTAL <label>: N h per week`, renders the PDF with headless Chrome and checks it is one page.
4. If it prints `ERRORS`, fix the entries (never the user's targets or fixed commitments) and run again. If it says the plan spilled onto more than one page, use fewer rows or shorter labels.
5. Look at the PDF once: run `python -c "import fitz;fitz.open('<pdf>')[0].get_pixmap(dpi=70).save('/tmp/.scratch/printable-planner/p.png')"` and then `media_analyze` on that PNG, to check text is not cut off. Fix once if needed.

## Step 4: Publish and reply

1. `publish_artifact(path="/tmp/.scratch/printable-planner/out/<plan-name>.pdf", kind="document")`. If the script says `PDF NOT BUILT`, publish the `.html` with `kind: "html_preview"` and say so.
2. If the user wants to edit the plan in a spreadsheet, load the built-in `xlsx` skill with `skill_view` and follow it, including its delivery step, to build a workbook with one sheet (days across, times or rows down) from the same entries; do not call `publish_artifact` for that workbook yourself.
3. The reply, in the user's language, contains:
   - One line: what was made (one A4 page, landscape or portrait, which days).
   - The plan as a short list per day (`Mon: 16:00-17:30 Math, ...`), taken from the entries.
   - The totals the script printed (hours per subject per week) and whether they match what the user asked.
   - Assumptions, one line each (days chosen, session lengths, anything the user did not give). For meals and workouts, also the not-medical-advice line.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. Edit `spec.json` (if the file is gone, rebuild it from the plan in your previous reply), run the same command with the same `<plan-name>`, publish the PDF again and say in one line what changed (for example "moved Physics on Tuesday to 17:00, totals unchanged").
