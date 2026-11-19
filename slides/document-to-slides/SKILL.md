---
name: Document to Slides
description: >
  Turns a report, article, proposal, paper or set of notes into a slide deck in EverAsk's slide maker that keeps the document's argument and exact figures.
  Finds the one-line conclusion, gives each slide one full-sentence headline, and ends on the decision or next step.
  Use it for "turn this document into slides", "make a deck from this report", "summarise this paper as a presentation", "make this into 5 slides".
---

# Document to Slides

Convert an existing document into a deck that carries its argument, not just its headings, built in EverAsk's slide maker.

A good result: someone who sees only the slides can state the document's conclusion, every figure matches the source exactly, and the last slide says what to decide or do next.

**Language (hard rule):** write the deck and your reply in the language the user wrote in, unless they ask for another. Keep their names, figures, units and terms exactly as given.

## Step 1: Get the document

Use the text the user pasted or attached, or a link or file they point you to (for a link, read it with `web_extract`; if a connected app such as Google Drive, Google Docs or Notion holds it and the user named it, use that). If the request refers to a document that is not there ("this report") and nothing is attached, ask one question. Otherwise do not ask: decide, and say your assumptions in the final reply.

Settle:

- **Slide count**: use the number the user gives, exactly ("5 slides" means 5). Otherwise about one slide per page or section, between 6 and 12. Never more than 20: that is the slide maker's limit. If the user asks for more than 20, plan 20 and say so.

Have the document's full text in hand by the end of this step. Once the slide maker is loaded (Step 4), you cannot read files or run code.
- **Audience and purpose**: use what the user said; otherwise infer it from the document (for example decision-makers for a proposal) and state it.

## Step 2: Find the argument

Before planning any slide, write down, from the document only:

1. **The conclusion** in one sentence: what the document wants the reader to believe or do.
2. **The 3 to 6 supporting points** that carry it.
3. **The key figures**: every number that supports a point, copied exactly as written with its unit and period. Do sums, differences and percentage changes in `execute_code`, never by eye, and only when the user wants a derived figure the document does not already state.
4. **The ask or next step**, if the document has one.

If the document has no stated conclusion, say so, and write the conclusion the evidence supports, labelled as yours.

## Step 3: Plan the slides

1. **Title slide**: the document's title (or a headline of the conclusion), and the author, organisation or date only if the document gives them.
2. **The answer first**: slide 2 states the conclusion and the 2 or 3 numbers that matter most.
3. **One idea per slide**, in the document's logic order. Write each slide title as a full-sentence headline that makes the point ("Churn fell after the pricing change"), not a topic label ("Churn"). Give each slide 2 to 4 short bullets or one figure with a line of meaning.
4. **Figures**: keep each exactly as in the source. A table of more than 4 rows becomes a chart slide (when the data suits a chart) or a summary of the 3 rows that matter, and you say what was left out. A chart plots only the document's numbers. Use charts on 3 slides at most.
5. **Closing slide**: the decision, recommendation or next step. If the document gives none, write a placeholder meaning "Next step: not given in the document", in the deck's language, rather than inventing one.
6. **Fit the count**: when the document is longer than the count allows, summarise; do not cut off the end. Merge the weakest points, and move detail, methods and caveats to one slide each at most. When the document states a caveat or limitation that affects the conclusion, keep it on a slide.

Drop what the argument does not need. Do not add slides with facts, statistics, quotes or sources the document does not contain; if general context would help, mark it as an assumption or leave it out.

## Step 4: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck: one `generate_outline` call, then one `generate_design_slides` call, with these arguments.

1. Write `user_prompt`: the user's message, word for word and complete, followed by this brief:

   ```
   DOCUMENT BRIEF
   Audience: <audience>. Slides: <count>.
   Conclusion: <one sentence>
   Figures (copy exactly, the only source for numbers):
   - <figure, unit, period, as written in the document>
   Slide plan (follow exactly):
   1. <full-sentence headline>: <bullets>. Visual: <only for a chart slide: FIGURE: <chart type> of <the exact figures>>
   Left out: <what was summarised or dropped, or none>
   Rules: Use only facts and figures from the document. Do not invent or round figures, quotes, names, dates or sources. Keep every placeholder exactly as written. Write in <the user's language>.
   ```

2. `generate_outline` with `user_prompt`, `title` (the deck's name: the document's title or a short headline), `slug` (a short kebab-case topic) and, only when the user typed a number of slides, `slide_count` (at most 20). The outline appears in the chat for the user to approve or change; don't repeat it in your reply.
3. Do what the result's `next_action` says. On `approved` or `auto_approved`, call `generate_design_slides` at once, in the same reply. On `revise`, change the plan as the user typed and call `generate_outline` again. On `cancelled` or `timeout`, say so in one line and stop.
4. `generate_design_slides` with the same `title`, `slug` and `user_prompt`, plus `source_text` (the document's full text, or for a very long document the sections the plan uses) and `source_name` (its file name or title), so the slides keep the document's facts. Add `language` when the deck is not in English, and `template` only when the user named a look, style or brand. Don't call any image tool: the slide maker makes the deck's pictures itself.
5. If the result lists `slides_not_generated`, call `generate_design_slides` again with `slides` set to those numbers.

## Step 5: Check and hand over

When the deck is ready, call `read_design_deck` once, naming every slide that shows a number (it returns those slides in full), and compare each figure with the source. For each slide with a figure that differs, call `edit_design_slides` with an instruction naming the correct figure and `slides` set to that slide only.

Then reply in a few lines:

- the slide count and the look the slide maker picked;
- the conclusion the deck argues, in one sentence;
- what you summarised or left out, and any assumption you made (audience, a missing conclusion);
- any placeholder still on a slide, by slide number.

The slides carry no speaker notes. If the user asks for notes or a script, write them in the reply as one short section per slide number, using only the document's content. Offer that as the next step.

## What not to do

- Don't use topic labels as slide titles, or put a paragraph of the document on a slide.
- Don't change, round or recompute a figure the document states.
- Don't invent facts, statistics, quotes, names, dates or sources.
- Don't plan more than 20 slides, or, up to 20, a different number from the one the user asked for.
- Don't paste the slides or their code into the chat.
