---
name: Formal Report Writer
description: >
  Writes a structured report as a Word file from the user's notes: internship, activity, project, lab, field visit or incident report.
  Use it for "write my internship report", "make a report from my notes", "lab report", "incident report", "laporan kegiatan", "informe de prácticas".
---

# Formal Report Writer

A good result is a report an institution can accept: the standard sections for its kind, written in clear formal language, built only from the user's notes, with every gap visibly marked. The deliverable is a .docx file built in the same turn.

## Hard rules

- Write in the language the user wrote in unless they ask for another. Keep their names, places, dates, figures, units and terms exactly as given.
- Only the user's facts. Never invent results, measurements, dates, places, names, participants, quantities, tasks or outcomes. Anything missing is written `[to complete: <what is needed>]`. Do not pad a section with generic text to hide a gap: a short section with a marker is correct.
- Every sentence in a body section must trace to a sentence in the user's notes. Do not narrate how a task was done, what procedure was followed, what the objectives were, what problems arose, how they were solved, what a document contained, what the other people did, or that goals were met, unless the notes say so. "I entered delivery records into the spreadsheet" becomes one sentence saying that, not a paragraph about method. A lesson the user gave is stated as their lesson, not illustrated with invented episodes. Recommendations, challenges and appendices appear only if the notes give them; otherwise the section is one line with a `[to complete: ...]` marker, or is left out if the kind allows. Thin notes give a short report (about 2 to 3 pages), never 8.
- Marker words are written in the report's language (for example `[a completar: ...]`, `[lengkapi: ...]`, `[à compléter : ...]`); the highlighting is the same.
- Generic wording is allowed only for structure (what a section is for) and for the formal tone, never for facts.
- Do every calculation, total, average or percentage in `execute_code` and copy the results. Never calculate in your head. Lab calculations show the formula, the substituted values, the unit and the result.
- Never stop to ask. If the kind of report is not stated, infer it from the notes and say so. Decide, state assumptions, deliver.

## Step 1: Choose the kind and the sections

1. Decide the kind: internship or practice, activity or event, project completion, lab, field visit, or incident. If the user pasted a template or an institution's section list, use that.
2. Read `references/report-types.md` and take the section list for that kind. Translate the headings into the report's language.
3. Note the length asked for (pages or words). Without one, keep each section proportional to the notes: a short notes set gives a short report, not a stretched one.

## Step 2: Sort the notes

In a scratch list, put each fact from the user's notes under the section it belongs to. Mark each section as full, thin or empty. Thin and empty sections get `[to complete: ...]` markers that say exactly what is missing (for example the supervisor's name, the number of participants, the measurement units). Collect all markers for Step 5.

## Step 3: Write the report

1. Formal, plain style: past tense for what happened, third person unless the institution's tradition is first person (student reports often use first person: follow the notes' voice).
2. Front matter by kind: a title page with the fields listed for the kind (marked blanks for fields not given), and a table of contents only if the report will be longer than about five pages.
3. One idea per paragraph. Use tables for data, schedules and budgets. Number tables and figures only if there is more than one.
4. Do not claim anything the notes do not support, for example that goals were fully achieved, that participants were satisfied, or that an error source was present.
5. The summary or conclusion restates only what the body says.
6. Before you build, reread the draft once and delete or mark every sentence that adds a fact, objective, procedure, finding or outcome not in the notes.
7. End with a short signature block for the kinds that use one, with blanks for missing names.

## Step 4: Build the file

1. Load the built-in `docx` skill with `skill_view` and follow it to build the report, including its delivery step. Do not add your own `publish_artifact` call for it.
2. Layout: A4, 12 pt serif or the institution's font if given, 2.5 cm margins, 1.5 line spacing, numbered headings, page numbers. Highlight every marker in yellow. If the user asked for PDF instead, load the built-in `pdf` skill with `skill_view` and build the PDF with it, never a .docx first.
3. Name the file after the kind and the topic, for example `internship-report-<name>.docx`.

## Step 5: Reply

The reply holds:
1. One line saying what kind of report you built, in which language, and the file name.
2. **Assumptions**: only what you decided (kind of report, voice, length).
3. **To complete**: the list of every `[to complete: ...]` marker, so the user knows what to add. If there are none, say "none".
4. For a lab report: the calculated results in a short table.

Do not paste the whole report into the reply; it is in the file.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, rebuild the same file type under the same name, and say in one line what changed.
