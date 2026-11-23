---
name: Quiz Game Builder
description: >
  Builds a playable quiz game as one web page: your questions, instant feedback, scoring, optional timer and team mode.
  Use it for "make a quiz game", "build a classroom quiz", "turn these questions into a game", "quiz for a party".
---

# Quiz Game Builder

A good result is one self-contained page that opens in a browser, works on a phone and a projector, and has exactly the questions the user gave (or well-checked ones the agent wrote), with the right answer marked on each. The page is published with `publish_artifact`; the reply also lists every question with its answer so the teacher can check them.

Hard rules:
- Write the quiz (questions, options, interface texts) in the language the user wrote in, unless they ask for another. Keep their names, figures and terms exactly as given.
- If the user gave questions, use them word for word. Do not add, drop or "improve" them. If they gave no answer for a question, work it out; if you cannot be sure, say so in the reply.
- If the user gave only a topic, write 10 questions (or the number asked) with one clearly correct answer each, at the level they named (age, grade, exam). Use only well-established facts. Do not invent statistics, dates or quotes. If you are unsure of a fact, replace the question.
- Any maths answer is computed in `execute_code`, never in your head.
- Do not ask questions. Decide, state the assumption in one line, deliver.

## Step 1: Plan the questions

1. Decide the language, the level, the number of questions and the title (short, from the user's words).
2. Write each question as: text, 2 to 6 options, the index of the correct option (0 is the first), and an optional one-line `explain` shown after answering (only for questions you wrote yourself; for questions the user gave, leave `explain` out). True/false questions have two options in the user's language. Put the correct answer in different positions across the quiz, not always first.
3. Keep options short enough to read on a projector. Wrong options must be plausible but clearly wrong.
4. Decide settings: `teams` (1 by default; use 2 to 4 only if the user wants teams or a class game), `timerSeconds` (0 = off, else 10, 15, 20, 30 or 60; only if the user asked for a timer), `shuffleOptions` (true only if the user wants shuffled answers), `shuffleQuestions` (true only if asked).
5. `dir` is `rtl` for Arabic, Hebrew, Persian and Urdu, otherwise `ltr`. `lang` is the language code (`pt`, `es`, `ko`, `ar`...).

## Step 2: Build the page

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Use the full path where the commands below say `SKILL_DIR`. If `skill_view` gives no path, find `build_quiz.py` under `~/.computer/skills` with `search_files`.
2. Use `write_file` to save `/tmp/.scratch/quiz-game-builder/spec.json`:

```json
{"config": {"title": "<title>", "subtitle": "<optional>", "lang": "<code>", "dir": "ltr",
            "timerSeconds": 0, "teams": 1, "shuffleQuestions": false, "shuffleOptions": false,
            "ui": {"start": "...", "next": "...", "finish": "...", "correct": "...", "wrong": "...",
                   "timeUp": "...", "answerWas": "...", "score": "...", "question": "...", "of": "...",
                   "teams": "...", "team": "...", "timer": "...", "replay": "...", "results": "...",
                   "count": "{n} ...", "outOf": "...", "turn": "...", "winner": "...", "tie": "...", "seconds": "s"}},
 "questions": [{"q": "...", "options": ["...", "..."], "answer": 0, "explain": "..."}]}
```

   The `ui` block holds the page's button and label texts. Translate every key into the quiz language (`count` keeps `{n}` for the number of questions; `timer` means "Timer (seconds per question, 0 = off)"; `outOf` joins "3 out of 10"; `of` joins "Question 2 of 10"). In English, use these defaults: Start, Next, See results, Correct!, Not quite., Time is up., Answer:, Score, Question, of, Teams, Team, "Timer (seconds per question, 0 = off)", Play again, Results, "{n} questions", out of, Turn, Winner, It is a tie, s.
3. Run in `terminal`:
   `python SKILL_DIR/scripts/build_quiz.py SKILL_DIR/templates/quiz.html /tmp/.scratch/quiz-game-builder/spec.json /tmp/.scratch/quiz-game-builder/<quiz-name>.html`
   It checks the questions and prints each question with its correct answer. Fix any `ERROR` and run again. A `WARNING` lists interface texts still in English: translate them and run again (ignore it only for words that really are the same in the language).
4. Compare the printed answer list with your plan: same count, same correct answers. If a maths question is involved, confirm its answer from `execute_code` output.
5. Confirm the script printed `OK` (it has validated the data: option counts, answer indexes, no duplicate options).
6. Publish with `publish_artifact(path=".../<quiz-name>.html", kind="html_preview")`. Use a meaningful file name from the title.

## Step 3: Reply

The reply contains, in the quiz language:
1. One line saying what was built: number of questions, settings (teams, timer) and that it plays in the chat preview and works offline once saved as an .html file.
2. How to play, in two lines: click or tap an answer (keys 1 to 4 also work), Enter or Space for the next question; pick teams and timer on the start screen.
3. The answer key: a numbered list, each line `N. <question> -> <correct answer>`, so the teacher can check it. Mark any question you wrote yourself as "written by me, please check" when the user gave only a topic.
4. One line on assumptions (level, language, anything you chose).

Do not paste the page's code in the reply.

## How to edit the quiz yourself

If the user wants to change questions without you: the questions sit in one list near the top of the .html file, between `QUESTIONS_START` and `QUESTIONS_END`; each has `q`, `options` and `answer` (0 is the first option). Say this in one line only if they ask how to edit by hand.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. Edit the saved `spec.json` (rewrite it with the change; if the file is gone, rebuild the spec from the previous answer key and your earlier questions), rebuild the same file with the same name using the same command, publish it again and say in one line what changed (for example "question 4 reworded, timer set to 20 seconds").
