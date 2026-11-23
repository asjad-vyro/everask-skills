---
name: Thesis Defense Slides
description: >
  Turns your thesis, dissertation or research project into defense slides that fit your time limit, plus 6 to 8 likely committee questions with answer outlines.
  Uses only your own content and marks missing results as placeholders. Use it for "defense slides", "viva presentation", "thesis defence in 15 minutes", "proposal defense deck", "what will the committee ask me".
---

# Thesis Defense Slides

Plan and build the presentation for a thesis, dissertation or research-project defence, sized to the time limit, and prepare the student for the committee's questions. The deck is built in EverAsk's slide maker. It does not write thesis chapters and does not teach a lesson.

**Language (hard rule):** write the deck, the questions and your reply in the language the user wrote in, unless they ask for another. Keep their terms, names, figures and citations exactly as given. Write no text before the tool calls (no "I'll load the skill"): the reply starts with the result, in the user's language.

## Step 1: Gather the thesis content

Use the abstract, chapters, notes or results the user pasted or attached (or a file they name in a connected app such as Google Drive, if connected). Make a **content sheet** in your notes with these fields, each filled only from the user's material, otherwise "not given":

- title, field, degree level, institution (only if given)
- motivation and the gap
- research question or hypotheses; objectives
- method: design, data, sample size, tools
- results: each finding with its exact figures, and the figure or table it comes from
- discussion; contribution; limitations; future work

Settle:

- **Type**: *final defence* (default) or *proposal defence* (no results: use expected outcomes and a timeline instead, only from the material).
- **Minutes**: the user's limit. Slides about one per minute, between 6 and 20, with at most 20 as the slide maker's limit. Without a time, assume 15 minutes and say so.

Never invent results, sample sizes, p-values, effect sizes, citations or names. Do no web search. Do not ask questions unless nothing about the thesis was given at all; if only a topic was given, plan the structure with every result, number and method detail as a visible placeholder. In that case slide headlines come from the topic and the standard sections only ("Result 1: <what the user's topic names>"): do not invent groups, cut-offs ("30 minutes before bed"), variables, mediators, scales, hypotheses, an expected direction or a "preliminary conclusion", and do not write the discussion or contribution as if results existed (use placeholders). Committee questions for a topic-only thesis are about the topic and the standard weak points, phrased "if you used...", never assuming a design or result.

## Step 2: Plan the slides

Plan in this order. Scale the count to the time: for short slots merge slides, never drop the research question, results or contribution.

1. **Title**: title, name, programme, supervisor and date only if given.
2. **Motivation and gap**: why it matters and what was missing.
3. **Research question and objectives**: the question verbatim, objectives as 2 to 4 short lines.
4. **Method**: design, data and sample size as given; a process diagram as the visual.
5. **Results**: 3 to 5 slides (final defence), each with one finding as a full-sentence headline, the exact figures, and the **Visual** line naming the figure or table it needs (chart type and the data from the content sheet). If a figure is missing, the slide shows a placeholder line meaning "Insert result here".
6. **Discussion**: what the results mean for the question.
7. **Contribution**: what is new, 2 or 3 points.
8. **Limitations**: honest, drawn from the material.
9. **Future work**.
10. **Thanks and questions**.

Proposal defence variant: replace results with *expected outcomes* and add a *timeline* slide using only dates the user gave; if none, a placeholder.

Every slide: at most 40 words, a headline that says the point, a Visual line. Put the detail in the questions section, not on slides.

## Step 3: Write the committee questions first

Before loading the slide maker, write for the reply **6 to 8 likely committee questions**, drawn from the thesis itself: the gap, why this method, sample size or data limits, the weakest result, alternative explanations, generalisability, the contribution, and what you would do differently. For each question write a short **answer outline** of 2 to 3 points, using only facts from the content sheet. Where the thesis gives no basis for an answer, write "needs your own answer: <what to cover>". Do not invent facts or citations in the answers. For a topic-only thesis every question and outline stays conditional ("if you used a survey..."): never write "your cross-sectional data", "self-report", a control variable or a finding that contradicts earlier studies as if it were the student's design or result.

Once the slide maker is loaded you cannot run code or read files, so do all of this now and keep it for the final reply.

## Step 4: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck: one `generate_outline` call, then one `generate_design_slides` call, with these arguments.

1. Write `user_prompt`: the user's message, word for word and complete, followed by this brief:

   ```
   DEFENCE BRIEF
   Type: <final or proposal defence>. Minutes: <minutes>. Slides: <count>.
   Content (the only source for findings, numbers and names):
   - <field>: <value as given>
   Slide plan (follow exactly):
   1. <headline>: <the few words on the slide>. Visual: <figure or table, with its exact data>
   Placeholders (keep exactly as written, visible on the slide):
   - Slide <n>: <placeholder text>
   Rules: Use only the thesis content listed. Do not invent results, sample sizes, p-values, citations or names. At most 40 words per slide. Write in <the user's language>.
   ```

2. `generate_outline` with `user_prompt`, `title` (the thesis title or a short version), `slug` (short kebab-case) and `slide_count` set to your planned count (at most 20). The outline appears in the chat for the user to approve or change; do not repeat it in your reply.
3. Do what the result's `next_action` says. On `approved` or `auto_approved`, call `generate_design_slides` at once, in the same reply. On `revise`, change the plan as the user typed and call `generate_outline` again. On `cancelled` or `timeout`, say so in one line, give the questions anyway, and stop.
4. `generate_design_slides` with the same `title`, `slug` and `user_prompt`, plus `source_text` (the content sheet and the user's text) and `source_name`. Add `language` when the deck is not in English, and `template` only when the user named a look or the university's style. Do not call any image tool.
5. If the result lists `slides_not_generated`, call `generate_design_slides` again with `slides` set to those numbers.

## Step 5: Check and hand over

The slide maker adds its own copy (durations such as "fifteen weeks", descriptions of prior studies, causal wording, invented phases) and often exceeds the word limit. Call `read_design_deck` once with `slides` naming every slide (all of them when there are 14 or fewer). Compare each slide with the content sheet: every figure unchanged, and nothing else stated as fact that the content sheet does not hold. Check the word counts in the manifest. For every slide with a wrong figure, an invented item or more than 40 words, call `edit_design_slides` once for all of them, with `slides` set to those numbers, naming what to remove or the correct value and asking to cut to at most 40 words while keeping headlines, visuals and every figure. Remove invented items: never leave one on a slide and only mention it in the reply.

The final reply holds, in this order:

1. Two or three lines: slide count and the minutes it fits, the type, the look picked, each placeholder still on a slide (by slide number), and any assumption.
2. **Likely committee questions**: the 6 to 8 from Step 3, each with its answer outline.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, and say in one line what changed. Call `edit_design_slides` with an instruction naming the change and `slides` set to the affected slide numbers only. Add or revise a committee question only if asked.

## What not to do

- Do not invent results, sample sizes, p-values, citations or names.
- Do not put chapter text on slides.
- Do not plan more than 20 slides.
- Do not paste the slides or their code into the chat.
