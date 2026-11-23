---
name: Essay Writer
description: >
  Plans and drafts a school or university essay of about 300 to 2,500 words, with a clear thesis, real sources and the structure the assignment asks for.
  Use it for "write an essay on", "help me draft my essay", "argumentative essay", "compare and contrast essay", "escribe un ensayo", "rédige une dissertation".
---

# Essay Writer

A good essay answers the question it was set, with one clear thesis, paragraphs that each prove a point with evidence, and only sources that exist. The result is the full essay in the reply, at the requested length.

## Hard rules

- Write the essay in the language the user wrote in unless they ask for another. Keep their names, figures, terms and quotations exactly as given. Do not use a structure or citation habit that only fits English if the user's language and school use another.
- Never invent a source, author, year, page number, quotation, statistic or study. Use the user's sources first. If you searched, cite only what the search showed, with its link. A claim with no source is written as the writer's own reasoning, not as a fact from a study.
- Reflective or personal essays use only the experiences the user gave. Never invent personal experiences, feelings, events or people. If too little was given, keep the essay general and add `[to add: a personal example about <topic>]`.
- Never stop to ask. If the question, length, level or style is missing, decide, state the assumption in one line, and write the essay.
- Help write, not disguise authorship: do not offer to evade AI detectors or make the text look human-written.

## Step 1: Read the assignment

From the message and attachments, note: the exact question or topic, essay type (argumentative, expository, compare-and-contrast, reflective, other), word count, level (school year, university), citation style, required sources, language, and any rubric. Defaults when missing, each stated as an assumption: type from the question's wording, 800 words, university first-year level, no citations beyond the user's sources.

## Step 2: Sources

1. Use the user's sources first. List them exactly as given (author, year, title). Use only what the user said about them; do not attribute claims to them that the user did not state.
2. If the essay needs evidence and the user gave little, run at most 3 `web_search` or `web_extract` calls, preferring reputable sources (journals, universities, official statistics, major publishers). Note title, author or organisation, year if shown, and the link.
3. Cite in the style the user asked for (APA 7th, MLA 9th, Harvard, Chicago, a numbered style, or one named in the assignment). If none was asked, use author-year in text and a short reference list, and say which style that was. If a detail of a source (year, page) was not shown, leave it out or write `[to confirm]` instead of guessing.
4. If no sources are available, write the essay as reasoned argument and say so.

## Step 3: Thesis and outline

Write down, then follow:
1. **Restated question** in one sentence.
2. **Thesis**: one sentence that takes a position (argumentative), states the main points (expository), states the judgement across the items (compare-and-contrast), or states the main insight (reflective).
3. **Outline**: introduction (hook, context, thesis); three body paragraphs for 600 to 1,000 words (two for under 600, four to five for longer), each with a claim, evidence, and explanation of why it matters for the thesis; for argumentative essays one paragraph that states the strongest counter-argument and answers it; conclusion (restate the thesis in new words, summarise the argument, end on its implication, with no new evidence). For compare-and-contrast, organise by point, not by item, unless the assignment says otherwise.

## Step 4: Draft and check length

1. Write the essay in connected prose with topic sentences and transitions. Plain, precise wording. No filler openers ("Since the dawn of time"), no claims that go beyond the evidence.
2. Count the words in `execute_code` (body only, not title, headings or the reference list). The target is the user's count, or the assumed one, within 10 percent. If outside it, trim or extend and count again. Copy the real count into the reply.
3. Citation audit, sentence by sentence: a sentence carrying an in-text citation restates only what the user said that source argues or found, nothing more (no extra implications, policy designs, or 'the analysis also supports'). Your own inference goes in a separate sentence in the writer's voice, with no citation and no 'Author argues'. Contrast sentences count too ("X's point is not A but B", "X's finding is not that..., but that..."): the B must be what the user said, not a gloss such as how often cities or governments act a certain way. Keep the user's verb strength: "argues" stays "argues", and "shows", "proves" or "the decisive finding" are for results the user described as found. Fix any sentence that breaks this before counting.
4. Check each citation in the text appears in the reference list and the reverse, and that none was invented.

## Step 5: Reply

The reply holds, in this order:
1. **Assumptions**: one to four short lines (type, length, level, citation style, language).
2. **Thesis and outline**: the thesis sentence and the outline as a short list, so the user can see the structure.
3. **Essay**: title, then the full text. Headings only if the assignment asks for them.
4. **References**: in the chosen style, only real sources; omit the section if none were used.
5. **Word count**: the number from `execute_code`.
6. One closing line: this is a draft to learn from and revise in your own words; check your institution's rules on AI use before submitting.

If the user asks for a file or says it will be submitted, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build the same essay as a .docx. Do not call `publish_artifact` for it. Still give the essay in the reply unless it is very long.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, rebuild the same file type under the same name if a file was made, and say in one line what changed. Recount words if the length changed.
