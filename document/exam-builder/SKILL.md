---
name: Exam and Quiz Paper Builder
description: >
  Builds a ready-to-print exam or quiz paper with a separate answer key and marking scheme, from a topic, a syllabus or the teacher's own material.
  Use it for "make an exam on...", "write a quiz for my class", "test paper with answer key", "create a 20-mark test from this chapter", "multiple choice questions with marks or points". Not for practice worksheets, study guides or lesson plans.
---

# Exam and Quiz Paper Builder

This skill is for the person setting the paper (teacher, trainer, tutor), not for a learner studying. A good result is a paper whose marks add up to the stated total, whose questions fit the level, and whose answer key is correct and marks every question so another person can grade it.

## Hard rules

- **Language**: write the paper, the key, every label on them and everything around them in the language the user wrote in, unless they ask for another. Keep their names, figures, terms and spelling exactly as given. Use the user's own word for marks (marks, points), their grade or level names, units and number format (for example a decimal comma).
- **Never invent facts.** If the user gave material (a passage, chapter, notes), every question must be answerable from that material alone, and every key answer must be traceable to it. If they gave only a topic, use well-established facts only and leave out any date, figure, name or claim you are not sure of. Do not make up quotations, sources, school names, teacher names, dates or exam board rules. Write original questions; do not copy questions from published exam papers or textbooks unless the user supplied them.
- **Do not open with questions.** Decide, state your assumptions in one line (level, duration, marks split), and deliver in this reply.
- **Every number is computed in code.** Marks totals, per-section subtotals, and any numerical answer (maths, physics, finance) are computed with `execute_code`, and the results copied. Never add or solve in your head.
- **Size**: at most about 40 questions in one turn. If the user asks for more, build the first 40 and end with one line saying how to ask for the next set ("ask for set 2 on <the remaining topics>").
- **The question paper file never contains answers.** The key goes in its own file. If the user asks for a single file, put the key after a page break and tell them to print or share only the pages before it.

Work in `/tmp/.scratch/exam-builder/` (create it). Files saved there persist between `execute_code` calls; an `execute_code` call's own working folder does not.

## Step 1: Pin down the paper

From the message, note (do not ask):

1. Subject and topics, and the source material if any.
2. Audience: age or level, as the user gave it.
3. Total marks and duration. If a total is given, use it exactly. If none is given, choose a sensible total and say so in the assumptions line. If no duration is given, leave it off the paper and say so.
4. Question types and counts (multiple choice, true/false, short answer, calculation, essay). If the user gave a split, follow it exactly. If not, choose a mix that suits the level and state it.
5. Difficulty: if not given, about half easy recall, a third application, the rest higher-order, and say so.

## Step 2: Build the blueprint

Before writing any question, make the blueprint in `execute_code` as a Python list: one row per question number, with topic, type, difficulty (easy, medium, hard), marks, and for each multiple-choice question its planned answer letter. Check in the same call that:

- the marks sum to the stated total, and each section's marks sum to its subtotal;
- every topic the user named has at least one question; with three or more topics, no topic has more than about a third of the marks unless the user asked for that;
- with four or more multiple-choice questions, the planned letters use each of the four options, no letter takes more than about 40 percent, and no letter repeats more than three times in a row.

Fix and re-run at most twice. Do not write questions that are not in the blueprint.

## Step 3: Write the questions to the blueprint

Write the whole paper once, with `write_file`, to `/tmp/.scratch/exam-builder/paper.json`: title, header details, sections, and for each question its number, topic, type, difficulty, marks, wording, and the answer and marking points. For a multiple-choice question store the correct option's text, the three wrong options and the planned letter; do not order the options yourself.

- One idea per question. Clear wording, no trick wording, no double negatives.
- **Multiple choice**: four options, exactly one correct, three plausible wrong options built from common mistakes. No "all of the above" or "none of the above". Options of similar length; the correct one must not be the longest by habit. Label options A to D, or with the labels the user's language normally uses.
- **True/false**: state something that is clearly true or clearly false; no half-true statements.
- **Short answer and essay**: say what is asked (name, explain, compare, give two reasons) and show the marks in brackets at the end, in the form `(<n> <the user's word for marks>)`.
- **Calculations**: choose the numbers, compute the answer and each marking step in `execute_code`, and use the printed results in the key.
- **Material given**: before keeping a question, find the sentence in the material that answers it; drop the question if there is none.
- No two questions test the same fact.

## Step 4: The answer key and marking scheme

These are fields of each question in the same single `paper.json` write as Step 3, not a second write:

- Multiple choice: the planned letter (code writes the final key letter in Step 5), plus a one-line reason. True/false: the correct word, plus a one-line reason.
- Short answer: the model answer, then how the marks are split (for example one mark per correct point, with the points listed), and what to accept as an alternative answer.
- Calculation: the worked steps with the marks for method and for the final answer, using the code results.
- Essay: the content points expected and a simple band guide (full, partial, minimal), with marks per band that add up to the question's marks.

## Step 5: Verify in code, then fix

Run one `execute_code` call that reads `paper.json` and:

1. places each multiple-choice question's correct option at its planned letter and the wrong options in the other places, and writes the options and the key letter back;
2. checks that the marks add up to the total and to each section subtotal, that every multiple-choice question has four distinct options and exactly one keyed answer, that the letters are spread as planned, and that no two question texts are the same;
3. saves `paper.json` and prints the check results, then the final paper: each question with its options in their placed order, and its key answer.

If anything fails, fix `paper.json` and run the check again, at most twice. If the user gave material, re-read each key answer against it.

## Step 6: Build the files

A paper is meant to be printed, so build files in this same turn. The user usually does not name a format: choose Word.

- **Word** (default): load the built-in `docx` skill with `skill_view` and follow it, including its delivery step. Write one build script that reads `/tmp/.scratch/exam-builder/paper.json` and writes both files in one run: `<subject>-<paper>-questions.docx` and `<subject>-<paper>-answer-key.docx`. Use A4 paper unless the user names US Letter or says they are in the US or Canada. Do not call `publish_artifact` for these files.
- **PDF** (only if the user asks): load the built-in `pdf` skill and build both PDFs with it directly from `paper.json`. Never build a .docx and convert it.
- If the user asked only for the questions in the chat, skip the files and give the full paper and key in the reply.

Question paper layout, all labels in the paper's language: title (subject and paper name); a header with blank lines for the student's name and class, a date line (blank unless the user gave the date), the duration if given, and the total marks; short instructions (answer all questions, marks shown in brackets); then sections by question type with each section's marks, questions numbered in order, space to write after short-answer and calculation questions, and the total at the end.

Answer key layout: a title meaning "Answer key and marking scheme" in the paper's language, the paper's name and total marks, the answers as in Step 4, a table of question number against keyed answer for the multiple-choice items, and the blueprint table at the end so the setter can see topic coverage.

## Step 7: Reply shape

In the language the user wrote in:

1. One line of assumptions: level, total marks, duration, question mix.
2. One line naming the two files and the format chosen.
3. If the paper has 20 questions or fewer: the full question paper text, then, after a line saying it is for the setter only, the answer key and marking scheme. If it has more: the answer list only, one line per question with its number and keyed answer. Copy questions, option order and key letters from the Step 5 printout, never from memory, so the reply matches the files.
4. The check result in one line: what was checked and whether it passed.
5. If the paper was capped at 40 questions, the line on how to ask for the next set.

If the files could not be built, give the full paper and key in the reply and say so.

## Optional sources

If the user asks to save the paper to Google Docs or Google Drive, or to add it to Google Classroom, and that app is connected, do it; in Google Classroom save it as a draft only, never post or assign it to students. Otherwise work from what the user gave you, deliver the files and the reply here, and send nothing anywhere.
