---
name: Deck Redesign
description: >
  Rebuilds a crowded or plain existing presentation (.pptx, PDF or pasted slide text) into a cleaner deck with fewer words per slide, one idea per slide and a visual on each, keeping every fact, number and name.
  Shows a before and after table and lists anything cut. Use it for "make my deck cleaner", "too much text on my slides", "redesign this presentation", "make it more visual".
---

# Deck Redesign

Take an existing deck and rebuild its structure and look in EverAsk's slide maker: same content, fewer words, clearer slides. It does not create a first deck from a document and does not make small exact edits to a file.

**Language (hard rule):** write the new deck and your reply in the language of the existing deck or the user's message, unless they ask for another. Keep every name, figure, unit and term exactly as in the source. Write no text before the tool calls (no "I'll load the skill"): the reply starts with the result.

## Step 1: Read the deck

1. If the user pasted slide text, use it. If they attached a .pptx or .pdf, use the text the file reader gave you. If it is missing or looks incomplete, extract it with `execute_code`:
   - .pptx: `from pptx import Presentation`; loop `Presentation(path).slides`; for each shape with `has_text_frame`, collect `shape.text_frame.text`; also read table cells (`shape.has_table`) and `slide.notes_slide.notes_text_frame.text` when present.
   - .pdf: `import fitz`; `[p.get_text() for p in fitz.open(path)]`.
   Find the path with `search_files` if the user's message does not give it.
2. If a connected app such as Google Drive holds the deck and the user named it, use that. Otherwise work from what they gave you. If no deck or slide text is there at all, ask one question.
3. Images in the source cannot be moved into the new deck. Note any slide whose meaning is mostly an image or chart, and rebuild it from its text, caption or numbers only.

## Step 2: Audit in code

In one `execute_code` call, with slide texts in a list, compute and print:

- slide count; words per slide (split on whitespace; for scripts without spaces, count characters instead and say so); the average and the maximum;
- slides over 60 words;
- slides with no title (first line missing or longer than 12 words);
- every number in the deck (regex for digits, with units and the surrounding 3 words), as a **figure list** you will check against later;
- slides that carry more than one idea (several headings or distinct topics: judge by reading).

Do every count in code and copy the results; never count by eye.

## Step 3: Plan the new deck

Write the plan before building:

1. **Keep the user's order** unless it is clearly broken (conclusion buried, setup after results). Say in one line what moved and why.
2. **One idea per slide.** Split an overloaded slide into several; turn a bullet wall into one full-sentence headline plus at most four short points (at most 35 words in total).
3. **Keep everything**: every fact, number, name, date and quote in the source is on a new slide, worded as it was. You may shorten wording, never change a figure. Anything cut is listed with its slide number and the reason.
4. **Add nothing**: no new facts, statistics, sources or claims, and no derived figures (a remainder such as 100 minus 38, a difference, a computed share or a prior-period value): a chart shows only the source's own numbers, and an unlabelled remainder is drawn without a number. Only section titles and a closing slide echoing the source's own last message may be added.
5. Each slide gets a **Visual** line chosen from its content: a chart of its own numbers, a process diagram for steps, a comparison layout for two options, big-number tiles for key figures, an icon row for lists, or a photo of a named thing. Charts use only the figures from the source.
6. **Cap at 20 slides.** If the plan goes above 20, merge the weakest slides and list what was merged.
7. If the user asked for a style, brand or colours, pass it as the look; otherwise let the slide maker choose.

If a new slide would repeat the title of another, rename it by its point.

## Step 4: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck: one `generate_outline` call, then one `generate_design_slides` call, with these arguments.

1. Write `user_prompt`: the user's message, word for word and complete, followed by this brief:

   ```
   REDESIGN BRIEF
   Slides: <count>. Audience and purpose: <from the source, or not given>.
   Figures (copy exactly, the only source for numbers):
   - <figure with unit and context, as written in the source>
   Slide plan (follow exactly):
   1. <full-sentence headline>: <at most four short points>. Visual: <the picture, diagram or chart of the exact figures>
   Cut or merged: <list, or none>
   Rules: Keep every fact, number and name from the source. Add no new facts, statistics or sources. At most 35 words per slide. Write in <the user's language>.
   ```

2. `generate_outline` with `user_prompt`, `title` (the deck's own title), `slug` (short kebab-case) and `slide_count` set to your planned count (at most 20). The outline appears in the chat for the user to approve or change; do not repeat it in your reply.
3. Do what the result's `next_action` says. On `approved` or `auto_approved`, call `generate_design_slides` at once, in the same reply. On `revise`, change the plan as the user typed and call `generate_outline` again. On `cancelled` or `timeout`, say so in one line and stop.
4. `generate_design_slides` with the same `title`, `slug` and `user_prompt`, plus `source_text` (the full original slide text) and `source_name` (the file name or "pasted slides"). Add `language` when the deck is not in English, and `template` only when the user named a look. Do not call any image tool.
5. If the result lists `slides_not_generated`, call `generate_design_slides` again with `slides` set to those numbers.

## Step 5: Check and hand over

The slide maker pads slides with its own copy: invented figures, causes, badges, captions, derived percentages, labels in another language, and far more words than planned. So check the deck, do not trust it. Call `read_design_deck` with no `slides` argument for the manifest (words per slide), then with `slides` naming every slide that has figures or body copy (all when there are 12 or fewer). Compare with the source and the figure list: every figure present and unchanged; nothing stated that the source does not say; no derived figure; every label in the deck's language. Then call `edit_design_slides` once for all offending slides, with `slides` set to them, naming exactly what to delete or correct and asking for at most 35 words on each. Read the manifest again and repeat once if slides are still over 40 words or still carry an invented item. Remove invented items; never leave one and only mention it in the reply.

The reply holds:

1. A **before and after** table with these rows: slides, average words per slide, maximum words on a slide, slides without a title. For the new deck use the word counts of the final `read_design_deck` manifest (they include chart labels), and say so. Do not report planned counts.
2. What moved or was merged, and anything cut, by old slide number. Write "nothing cut" if so.
3. The look the slide maker picked, and any image or chart from the original that could not be carried over.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, and say in one line what changed. Call `edit_design_slides` with an instruction naming the change and `slides` set to the affected slide numbers only.

## What not to do

- Do not change, round or drop a figure, name or date from the source.
- Do not add facts, statistics, quotes or sources.
- Do not plan more than 20 slides.
- Do not paste the slides or their code into the chat.
