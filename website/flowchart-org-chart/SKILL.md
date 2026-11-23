---
name: Flowchart and Org Chart Maker
description: >
  Draws an org chart, flowchart, process map or timeline from your description as a PNG image, with every box connected correctly.
  Use it for "draw an org chart", "make a flowchart of this process", "who reports to whom diagram", "timeline of these events".
---

# Flowchart and Org Chart Maker

A good result is a clear picture in which every box the user described is present, every line joins the right two boxes, every label is exactly what the user wrote, and the counts of boxes and lines match a table written first. The method is: table first, check it in code, then draw. The picture is published as a PNG with `publish_artifact`.

Hard rules:
- Write labels exactly as the user wrote them (names, job titles, step wording), in the user's language. Do not translate, shorten, correct or add anything. The only text you may add is the branch words of a decision when the user did not write them (the words for "Yes" and "No" in the user's language).
- Do not invent people, steps, dates or reporting lines. If the description is missing something needed to connect the chart (for example who a person reports to), decide the most natural reading, say it in the reply as an assumption, and still deliver.
- Do the counts in code (the script prints them); never count by eye.
- Do not ask questions. Decide, state the assumption in one line, deliver.
- Never install a browser or any package. The script finds Chrome itself; if it prints `PNG NOT BUILT`, publish the `.svg` and say so.

## Step 1: Choose the kind

- `org`: people or units and who reports to whom (a tree, one root).
- `flow`: a process with steps and decisions (start, steps, yes/no decisions, end). Loops back to an earlier step are allowed.
- `timeline`: events in time order, drawn along a horizontal line.
Anything else the user calls a process map or workflow is `flow`. A software architecture or sequence diagram, or any diagram the user wants as an Excalidraw file, is a job for the built-in `diagram` skill: load it with `skill_view` and follow it, including its delivery step, instead of this skill.

## Step 2: Write the table

List every node and connection before drawing anything. Number nodes `n1`, `n2`... in the order the user mentioned them.

- Org: one row per person: `id | name (label) | title (sub) | parent id`. The root has no parent. If the user lists a team without saying who leads it, use the most senior title as root and state that assumption.
- Flow: one row per node: `id | label | type` where type is `start`, `process`, `decision` or `end`; and one row per connection: `from | to | label`. Rules: exactly one start; at least one end; every decision has two or more outgoing branches and each branch has a label; every other node has an outgoing connection; every node is reachable from the start. A step that only happens under a condition ("if the amount is over the limit, escalate") is a decision node with labelled branches, not a process box with the condition in its text. If the user gave no start or end, add nodes with the labels "Start" and "End" in the user's language, and say so.
- Timeline: one row per event in time order: `id | label | date text (sub)`, with dates exactly as the user wrote them. If the user gave no order, keep the order they listed them in.

## Step 3: Check and draw

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Use the full path where the commands below say `SKILL_DIR`. If `skill_view` gives no path, find `draw_chart.py` under `~/.computer/skills` with `search_files`.
2. Use `write_file` to save `/tmp/.scratch/flowchart-org-chart/spec.json` (the table as JSON):

```json
{"kind": "org | flow | timeline", "title": "<optional title in the user's words>", "dir": "ltr",
 "nodes": [{"id": "n1", "label": "<label>", "sub": "<title or date, optional>", "type": "<flow only>", "parent": "<org only: parent id>"}],
 "edges": [{"from": "n1", "to": "n2", "label": "<branch label, decisions only>"}]}
```

   Org: give `parent` on each node; no `edges` needed. Timeline: no `edges` needed. `dir` is `rtl` for Arabic, Hebrew, Persian and Urdu. Leave `title` out unless the user gave one or the chart clearly needs it.
3. Run in `terminal`:
   `python SKILL_DIR/scripts/draw_chart.py /tmp/.scratch/flowchart-org-chart/spec.json /tmp/.scratch/flowchart-org-chart/out <chart-name>`
   with `<chart-name>` a short file name from the topic. The script validates the table (duplicates, unknown ids, orphans, dead ends, unlabelled decision branches, more than one org root, reporting loops), draws the chart, and prints `COUNTS table nodes=N connections=M | drawn nodes=N connections=M`.
4. If it prints `ERRORS`, fix the table (the fix must stay within what the user said) and run again. Fix once or twice; do not loop.
5. Look at the PNG once with `media_analyze` and check: no text cut off, no box overlapping another, every line ends at a box. If something is wrong, adjust only the structure of the table and run again once. Never edit the user's labels to make it fit.

## Step 4: Publish and reply

1. `publish_artifact(path="/tmp/.scratch/flowchart-org-chart/out/<chart-name>.png", kind="file")`. If the script says `PNG NOT BUILT`, publish the `.svg` with `kind: "file"` and say so.
2. If the user asked for an editable version (or mentions Miro, Notion, draw.io, Mermaid), also publish `<chart-name>.mmd` (Mermaid source, org and flow only) with `kind: "file"` and say in one line where it opens (for example mermaid.live). The `.svg` can be opened in a vector editor; publish it too when an editable picture is asked for.
3. The reply, in the user's language, contains:
   - One line: what was drawn and the counts from the script, for example "9 boxes, 8 reporting lines" using the script's numbers, and that they match the table.
   - The table as a short list (org: `name - title -> reports to <name>`; flow: numbered steps with decision branches; timeline: date - event), so the user can check it in text.
   - Assumptions, one line each. If none, say "nothing assumed".

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. Edit `spec.json` (if the file is gone, rebuild it from the table in your previous reply), run the same command with the same `<chart-name>`, publish the same file type again and say in one line what changed (for example "moved Pedro under Laura; 9 boxes, 8 lines").
