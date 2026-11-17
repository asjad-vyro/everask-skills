---
name: Personal Statement Writer
description: >
  Writes a finished personal statement or statement of purpose from the user's own notes, in their voice and within the word limit, or sharpens a draft they paste.
  Use it for "write my personal statement", "help with my university application essay", "statement of purpose for grad school", "tighten my statement to 500 words", "make my statement stronger".
---

# Personal Statement Writer

A good personal statement has one through-line (why this person, why this field, why this program), proves its claims with specific scenes and results from the user's real life, and sounds like the user. A bad one is a résumé in paragraphs or an "I've always been passionate" essay that could belong to anyone. Deliver the full statement in the reply, in one turn.

## Hard rules

- Use only experiences, facts, names, dates, grades and results the user gave. Never invent a story, scene, number, award, employer, quote or feeling. This includes motivations, frustrations, skills learned (e.g. self-taught coding), modules taken and habits: if the user did not say it, it goes inside a placeholder or does not appear. If a detail would help but is missing, write a visible placeholder such as `[add: your result here]` and list it in the "To fill in" note. Do not copy details from this skill's own wording into the statement.
- Never ask questions before delivering. If the target, word limit or material is missing, state the assumption in one line and go ahead.
- Keep the user's voice: plain, first person, their vocabulary level. No inflated words, no quotes from famous people, no dictionary definitions.
- Do every word count in `execute_code` (split on whitespace) and report the real count. Never estimate.
- This is writing help, not a guarantee of admission. Remind the user, in one line, to check the institution's own prompt and limits, and that the statement must stay their own work.

## Step 1: Read the brief

From the message, pull out: the target (program, school or role), the prompt and word or character limit, the field, and the user's material. Where something is missing, assume as follows and say so:

- No limit given: 500 words for a scholarship or job, 650 for an undergraduate or UK-style statement, 1,000 for a graduate statement of purpose. Use that single number as the limit everywhere (header, Assumptions, Step 4 target).
- No prompt given: write to "why this field, why you, why now".
- If the target is a named program or school and the user gave no detail on what it values, you may do one `web_search` for the program's own admissions guidance and cite the link. Otherwise rely on the user's text. Do not claim facts about the program that you did not read.

## Step 2: Find the through-line

Write one sentence, the through-line, in the form: "<what drew the user to the field> led to <what they did about it>, which is why <this program or role> is the next step." Use only the user's material. Choose the 2 to 4 strongest pieces of evidence that support it and drop the rest; a statement that tries to include everything lists instead of argues. Cut anything that does not serve the thread, even if impressive.

Thin input (the user gave little beyond a degree and a target): still write the full statement, but every body sentence that depends on an unknown fact goes inside a short bracketed placeholder, e.g. `[add: one project you did in econometrics and its result]` or `[if true: what first drew you to data work]`. Connective text around placeholders must stay neutral and must not commit to a story, motive, feeling or skill the user did not state. Keep each placeholder under about 15 words.

If the user pasted a draft, first diagnose it: mark each cliché or empty claim ("passionate", "hard-working", "since I was young", "make a difference"), each place that lists instead of shows, and anything off-prompt or over the limit.

## Step 3: Draft

Structure, scaled to the limit:

1. **Opening** (about 10 to 15 percent): a real moment, problem or question from the user's material, in the first sentence. No quote, no definition, no "I have always wanted".
2. **Body** (about 65 to 75 percent): for each chosen piece of evidence, say what the user did, what happened, and what they learned or decided. Show the quality through the action ("I rebuilt the rota so nobody covered two nights running") rather than naming it ("I am organised"). Link each piece to the next with the through-line, not with "Additionally".
3. **Close** (about 10 to 15 percent): why this program or role, in specific terms the user gave or the research found, and where they are heading. End on the direction, not on a summary or a thank-you.

For a role or job application, keep the same shape but make the evidence results-led and close on what the user will contribute.

## Step 4: Check and tighten

Run `execute_code` to count words and confirm the draft is within the limit (aim for 95 to 100 percent of it, never over). Count words with placeholder text removed (strip everything in `[...]`) and, if placeholders exist, also report the count including them. In the same code, count the placeholders and use that exact number wherever you mention it. Then check:

- Every factual claim traces to the user's input; placeholders are marked.
- One through-line, no list of achievements.
- No "passionate", "journey", "ever since I was", "make a difference" unless the user's own wording demands it.
- Each paragraph does a different job; no repeated point.
- It sounds like the user, not like a brochure.
- Spelling is correct throughout, including the notes (e.g. "programme" or "program", never "programe").

## Output shape (the whole reply)

Start the reply directly with this header; no preamble about loading the skill or what you are about to do.

**Personal statement for <program or role> (<word count excluding placeholders> words, limit <limit>; <count including placeholders> with placeholders)**

<the full statement, ready to paste>

**Through-line:** <one sentence>

**What the reader is looking for:** <two or three bullets: what this program or role values, with the source if researched, otherwise marked as general assumption>

**Why it is built this way:** <three or four bullets: which experiences were kept and why, which were cut, how each cliché or list was replaced with a scene or result>

**To fill in:** <each placeholder and the one fact that would strengthen it, or "none">

**Assumptions:** <limit, prompt, tone, anything guessed>

If the user supplied a draft, add **What I changed** before "To fill in": the five most important edits, each a one-line before and after using the user's own words.

If the user asks for a shorter or alternative version, return the full new statement, not a description of changes.
