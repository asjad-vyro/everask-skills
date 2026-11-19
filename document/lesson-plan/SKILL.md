---
name: Lesson Plan Builder
description: >
  Builds a complete, printable lesson plan a teacher can teach from: objectives, timed activities, checks for understanding, differentiation and a student handout.
  Use it for "lesson plan", "plan a lesson on", "I need to teach <topic> tomorrow", "daily plan", "mini-lesson". Any subject, any country. Not for slides, stand-alone worksheets, quizzes, exams or grading.
---

# Lesson Plan Builder

A good lesson plan lets a teacher walk in and teach: one clear objective, a timed sequence that adds up to the period, a way to see whether students got it, specific help for the students who need it, and the handout ready to print. This skill writes the plan for the teacher (not slides, not a study guide for students).

## Hard rules

- **Language**: write the plan, the handout and every label in them in the language the user wrote in, unless they ask for another. Keep their names, figures, class details and terms exactly as given. Use the user's own system for grades, ages and terms; do not assume US grade levels, US spelling or US-only conventions. Write numbers the way the user's language does (for example a decimal comma where that is the norm).
- **No questions.** Decide from the message, state your assumptions in one line, and deliver in this reply. Never open with questions.
- **No invented standards.** Cite a curriculum standard or code only if the user gave it, word for word as given. If none was given, write the objectives in plain words and put a line meaning "Curriculum standard: not given" in the plan's language. Never make up or recall a code from memory, and do not name a curriculum the user did not name.
- **No invented facts about the class.** Class size, students' prior learning, school resources and the date are not given unless the user said so; mark anything you assume as an assumption. Do not name real students.
- **Content must be correct.** Every worked example, answer key and number is checked. Do the arithmetic in `execute_code` and copy the results. Quote a text or source word for word only if the user gave it or you opened it with `web_extract`; never reproduce a text from memory.
- Student-facing text must be readable by the students' age (and reading level, if the user gave one): short sentences, everyday words, one instruction at a time.
- The plan stays a draft for the teacher to adapt.

## Step 1: Read the request

From the message, note (do not ask):

1. **Learner group**: grade or age, class size if given, and anything said about them (new to the language of instruction, mixed ability, a reading level, special needs). If no grade or age is given, assume one that fits the topic and say so.
2. **Subject and topic**, and the **one thing** students should be able to do by the end.
3. **Lesson length** in minutes. If not given, assume 45 and say so.
4. **Curriculum or standard** if named (see the rule above) and the **country or language context**.
5. **Resources**: assume only a board and paper unless the user listed more. Do not rely on a projector, devices or the internet unless the user said they have them.
6. **Prior content**: what students already know, only as the user gave it; otherwise state a prerequisite as an assumption.

Read `references/subject-notes.md` once, the section for the lesson's subject (maths, language and reading, science, humanities), before you design. Its notes override the general order below where they differ. If the subject is something else (arts, foreign languages, PE, computing), skip the file and use the general structure below.

## Step 2: Design the lesson

1. **Objective**: one or two "students will be able to <do something observable>" statements in the plan's language, using verbs such as explain, solve, compare, write, sort, identify. No "understand" or "know". Everything below must serve these.
2. **Sequence**, each phase with minutes. The general order, with rough shares of the period that add up to 100 percent (a starting point, not a rule):
   - **Launch / hook** (about 10 percent): a short task or question that starts thinking and reveals what students already know.
   - **Modelling** (about 20 percent): the teacher shows one worked example while thinking aloud.
   - **Guided practice** (about 25 percent): students try items in pairs or groups with the teacher circulating.
   - **Independent practice** (about 25 percent): the handout, done alone.
   - **Exit ticket** (about 10 percent).
   - **Closure** (about 10 percent): students say or write what they learned and link it back to the objective.
   Use the subject note's order where it gives one (science: students observe or investigate before the teacher explains; humanities: background, then source work, then discussion). Keep transitions inside the phase minutes.
3. **Timing**: list every phase's minutes in `execute_code`, sum them, and confirm the total equals the lesson length exactly. Fix and re-sum until it does.
4. **Checks for understanding**: at least two during the lesson (what the teacher asks or looks for, and what to do if many students miss it) and one exit ticket.
   - The exit ticket is a new item, not a copy of a practice item, targets the hardest case the lesson teaches, and fits in its minutes.
   - Give a three-way sort, with labels in the plan's language meaning got it / almost there / needs re-teaching, each with what a response in that group looks like. Every possible response fits exactly one group, and equivalent forms of the same answer sit in the same group.
5. **Likely mistakes**: two or three specific wrong answers or ideas students at this age commonly show on this topic, each with what the teacher does. Name the actual wrong answer.
6. **Differentiation**: concrete changes, not "provide support". Include:
   - **Extra support**: a scaffold such as a sentence starter, a partly worked example, a picture or a manipulative made from paper.
   - **Stretch**: a harder or open version of the task.
   - **Any group the user named** (for example students new to the language of instruction): the specific adaptation for them, such as a key-word list the teacher explains with quick board sketches or gestures (no generated images needed), a partner, a sentence frame on every task that asks for sentences, and an oral or pointing way to show the answer. For home-language support, give the key-word list a blank home-language column for the student, a family member or a bilingual colleague to fill in. Print translations only into a language the user named, only single key words, and mark them for a speaker of that language to check.
7. **Materials**: only what the lesson uses, and every item listed is used in a phase. Anything students need to hold is the handout or a household or classroom item.
8. **Student handout**: the tasks students do, worded exactly as in the plan; a labelled answer space under each task (lines for sentences, open space for maths working); a sentence starter on the task where writing is hardest; the exit ticket at the end. It must print well in black and white: never let colour or position alone carry meaning. Size it so a typical student finishes in its phase minutes. If the lesson is oral and needs no handout, say so and skip it.

## Step 3: Build the document

The teacher prints this, so make a Word file. Load the built-in `docx` skill with `skill_view` and follow it, including its delivery step; do not call `publish_artifact` for this file. Use A4 paper unless the user names US Letter or says they teach in the US or Canada. If the user asked for the plan in the chat only, give it in the reply instead; if they named another format, use it (for PDF, load the built-in `pdf` skill and build the PDF with it directly, never by converting a .docx).

Name the file after the topic, for example `lesson-plan-<topic>.docx`. Build one document with these parts, in this order, headings in the user's language:

**Part 1: Teacher plan**
1. **At a glance**: topic, learner group, length in minutes, the curriculum standard line, a one-line timeline of every phase with its minutes in the form "<phase> <minutes>", materials list, assumptions.
2. **Objectives**.
3. **Prior knowledge** (assumed) and **key vocabulary** (three to six terms with short definitions the students can understand).
4. **Lesson sequence**: a table with columns Time (minutes), Phase, What the teacher does and says, What students do, Check. Put the exact words the teacher says for the launch and the worked example.
5. **Checks for understanding and exit ticket**, with the sort criteria and the answer key.
6. **Likely mistakes** and what to do.
7. **Differentiation**.
8. **Closure** line and a one-sentence cut to use if time runs short (which activity to shorten).

**Part 2: Student handout** (start on a new page): name and date lines (blank), a short title, the tasks, labelled answer spaces, the exit ticket. No answers on it.

**Answer key**: after the handout, on its own page marked for the teacher only, give every answer, worked.

Keep it skimmable: paragraphs of at most three sentences, bullets as fragments, each instruction in exactly one place.

## Step 4: Reply

In the user's language:

1. One line: what you built (grade or age, topic, minutes), the file's format and the assumptions you made.
2. A short summary of at most six bullets: objective, the timeline with minutes, the check for understanding, the key adaptation, and the one thing to prepare beforehand.
3. The file, delivered as the `docx` skill instructs.

If the file could not be built, put the full plan in the reply instead and say so. Do not end with a list of questions.

## Check before you reply

- Phase minutes add up to the lesson length (the sum was done in `execute_code`).
- Every practice item, worked example and answer was worked and is correct.
- Handout tasks match the plan's wording, and the exit ticket is identical in plan and handout.
- No standard code appears unless the user gave it.
- The group the user mentioned has its own adaptation.
- Everything, labels included, is in the user's language.

## Optional sources

If the user asks you to save the plan to Google Docs, Google Drive or Notion, or to add it to Google Classroom, and that app is connected, do it; in Google Classroom save it as a draft only, never post or assign it to students. Otherwise work from what the user gave you and deliver the file here.
