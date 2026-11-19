---
name: Worksheet and Answer Key Maker
description: >
  Makes a printable practice worksheet with a worked example, exercises that get harder step by step and a separate answer key, pitched at the class's level.
  Use it for "make a worksheet on...", "practice sheet for my class", "homework sheet with answers", "exercises on fractions with an answer key". Not for marked exams, quizzes or lesson plans.
---

# Worksheet and Answer Key Maker

A good worksheet practises one skill and nothing else. It shows one worked example, then exercises that get steadily harder, with room to write, and an answer key the teacher can trust. It is for practice: no marks, no grade. A marked test or exam paper is a different job.

## Hard rules

- **Language**: write the worksheet, the instructions, every label and the key in the language the user wrote in, unless they ask for another. Keep their names, figures and terms exactly as given. Do not use conventions that only work in English (date formats, currency, grade names), and write numbers the way the worksheet's language does (for example a decimal comma where that is the norm). The date line is a blank line labelled in the worksheet's language.
- **Never invent facts.** Do not make up school names, teacher names, class names, dates, textbook references or curriculum codes. Use only what the user gave. Mark any assumption (age, level, number of exercises) in one line.
- **Every answer must be right.** Do every calculation in `execute_code` and copy the results into the key; never work sums out in your head. For language, history or science exercises, write only questions with one defensible answer, and keep to facts and grammar rules you are sure of. If you are not sure, leave the question out.
- **Do not open with questions.** Decide, state assumptions in one line, and deliver the full worksheet and key in this turn.
- Stay on the one skill the user named. Do not drift into neighbouring topics.

## Step 1: Pin down the job

From the message, note (do not ask):

1. **The single skill** being practised, as one sentence ("add fractions with unlike denominators"). If the topic is broad, pick the most useful single skill inside it and say so.
2. **The learners**: age or level. If not given, assume a typical level for the topic and say so.
3. **Number of exercises**: use the user's number. If none, use 12.
4. **Mixed class?** If the user says the class is mixed, or gives two levels, make two versions of the core band (see Step 3).
5. **Format**: if the user names one (Word, PDF), use it. Otherwise build a .docx, because worksheets are printed.

## Step 2: Write the worked example

Before the exercises, one worked example of the skill, with every step written out in plain words and a short note on the usual mistake. Choose numbers or sentences that are different from every exercise. For numerical content, compute the example in `execute_code`.

## Step 3: Write the exercises in three bands

Split the exercises across three bands, in this order, numbered 1 to N without restarting: starter about a third, core the largest share, stretch the rest (for 12 exercises: 4 starter, 5 core, 3 stretch). Give each band a short label in the worksheet's language.

- **Starter**: one step, small friendly numbers or short simple sentences, same pattern as the worked example.
- **Core**: the full skill, as the class would meet it in a normal lesson. Vary the form a little (a gap to fill, a short problem in words, spot-the-error).
- **Stretch**: needs two steps, an unfamiliar context or an explanation ("Why is this wrong?"). Still the same skill.

Rules for the exercises:

1. Each exercise has one correct answer, or a short list of acceptable answers noted in the key.
2. Each gets harder than the one before it, within its band.
3. Word problems use ordinary names and objects. Do not use real people, schools or brands.
4. Leave room to write: a blank answer line or a few ruled lines after each exercise (more for stretch and for working).
5. For a mixed class: give the core band in two versions with the same exercise numbers and the same count, one with more support (smaller numbers, a hint, a partly done step) and one with more challenge. On the worksheet, label them neutrally (for example "Path A" and "Path B" in the worksheet's language), never "easy" or "hard"; say which is which only in the key and the reply. The key covers both.

For numerical exercises, generate the numbers and compute every answer and every step of working in `execute_code` first (use Python's `fractions` module for fractions), print the results, and copy them to the key. Give answers in lowest terms unless the skill asks for another form. Check that no answer is negative, zero or a messy decimal unless the skill calls for it.

## Step 4: Write the answer key

A separate page after the worksheet, headed "Answer key" in the worksheet's language. For each exercise: the answer, and for anything numerical, the working in short steps. For explanation questions, give the accepted answer in one or two lines. End with one line listing the most likely mistakes and which exercises show them.

## Step 5: Layout

1. Page 1 onwards: the title (the skill in plain words), a name line and a date line (blank, labelled in the worksheet's language), a one-line instruction, the worked example in a box or shaded block, then the exercises by band with the band labels.
2. Answer key on its own page (a page break before it).
3. Fit the worksheet on as few pages as is comfortable: two sides for 12 exercises. It must print well in black and white, so never let colour alone carry meaning.

## Step 6: Deliver

The worksheet is meant to be printed, so build the file in this same turn:

- **Word** (default): load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build the .docx with the layout above, on A4 paper unless the user names US Letter or says they are in the US or Canada. Do not call `publish_artifact` for it.
- **PDF** (only if the user asks): load the built-in `pdf` skill and build the PDF directly with it. Never build a .docx and convert it.
- Right-to-left languages (Arabic, Hebrew, Persian, Urdu): build the .docx with the document direction set right-to-left and text aligned right. If the user insists on PDF, check the rendered page; if the text comes out broken or reversed, say so and deliver the .docx instead.

Then reply with:

1. One line: the skill practised, the level assumed, the number of exercises, the format chosen.
2. The full text of the worksheet and the answer key, so the user can read it without opening the file.
3. One line: how to ask for a harder or easier version, or a different number of exercises.

## Optional sources

If the user asks you to save the worksheet to Google Docs or Google Drive, or to add it to Google Classroom, and that app is connected, do it; in Google Classroom save it as a draft only, never post or assign it to students. Otherwise work from what the user gave you and deliver the file here.
