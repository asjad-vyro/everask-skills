---
name: Class Presentation Maker
description: >
  Makes a school or university presentation on any topic: few words per slide, a picture on every slide and the number of slides sized to your time slot.
  Facts come from the user or a quick web search, with sources on the last slide. Use it for "make a presentation on the water cycle", "slides for my class talk", "I have 8 minutes to present", "PowerPoint for my school project".
---

# Class Presentation Maker

Build the slides a student presents in class on a topic: one idea per slide, very few words, a picture or diagram on each, and a length that fits the time slot. The deck is built in EverAsk's slide maker.

**Language (hard rule):** write the deck and your reply in the language the user wrote in, unless they ask for another. Keep their names, facts, figures and terms exactly as given. Write no text before the tool calls (no "I'll load the skill"): the reply starts with the result, in the user's language.

## Step 1: Pin down the talk

From the message and any attached notes or assignment text (or a file the user names in a connected app such as Google Drive, if it is connected), settle:

- **Topic** and, if given, the assignment's required points.
- **Level**: the grade, course or age the user states. If none, assume a general school-age audience and say so in the reply.
- **Minutes**: the user's time slot. Content slides = minutes minus 2, rounded, plus the title, summary, sources and questions slides: so the deck has about as many slides as minutes, up to 2 more (8 minutes = 8 to 10 slides). Never fewer than 6 and never more than 20 (the slide maker's limit). If no time is given, assume 8 minutes and say so.
- **Facts the user supplied**: list them. Every one must appear on a slide, worded as given.

Do not ask questions unless there is no topic at all. Decide, and state assumptions in the reply.

## Step 2: Get the facts

1. Use the user's facts and attached text first.
2. If more facts are needed, run `web_search` at most three times in total. Keep only facts you saw in a result, and note the page title and link of the result that showed each one. Where results disagree on a figure, leave it out or use the most careful source. Never name an organisation or author that did not appear in a result.
3. Do not invent statistics, dates, quotes, names or sources. If you are not sure of a figure, leave it out. A fact from your own general knowledge is allowed only if it is basic and well established; do not put a source name on it.
4. Write numbers exactly as the source gives them.

## Step 3: Plan the slides

Write this plan before building. Use this order:

1. **Title**: the topic, plus the presenter's name, class or date only if the user gave them (otherwise leave those out).
2. **Agenda**: 3 to 5 words per item, only if there are 8 or more slides.
3. **Content slides** (5 to 12, fewer for short talks): one idea each.
   - A headline that says the point in at most 8 words.
   - At most 30 words in total on the slide, in 2 to 4 short lines. Count them. Over the limit means cut or split.
   - A **Visual** line that says exactly what picture it carries: a diagram, a labelled map, a photo of a named thing, a chart of the given figures, an icon row. Every content slide has one.
   - A visual may only show the listed facts. Do not plan size comparisons ("bigger than N countries"), equivalents or any ratio that needs a figure you do not have: use a plain labelled map, a proportion diagram of a given fraction, or a photo of a named thing.
   - Pitch the words to the stated level: everyday words for young students, the field's terms (defined once) for university.
4. **Summary**: 3 takeaways in at most 12 words each.
5. **Sources**: always its own slide, never folded into the closing slide. The real sources used, one per line, with links. If only the user's facts were used, the slide says, in the deck's language, that the facts come from the presenter's own notes (do not write the words "the user's notes" on a slide, the presenter is the user).
6. **Questions**: a closing slide with a short question or thank-you.

Each content slide that has a number gets a chart or a big-number visual, using only the supplied or found figures.

If the user asked for a script or speaker notes, write one or two sentences per slide in the reply after the build, about 130 words spoken per minute at most, using only the slide's facts. Otherwise write none.

## Step 4: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck: one `generate_outline` call, then one `generate_design_slides` call, with these arguments.

1. Write `user_prompt`: the user's message, word for word and complete, followed by this brief:

   ```
   CLASS PRESENTATION BRIEF
   Level: <level>. Slides: <count>. Time: <minutes>.
   Facts to keep exactly (the only source for numbers):
   - <fact, as the user or source gave it>
   Slide plan (follow exactly):
   1. <headline>: <the few words on the slide>. Visual: <the picture or diagram>
   Rules: At most 30 words per slide. Every content slide carries a picture, diagram or chart. Use only the facts listed. Do not invent figures, quotes, names, dates or sources. Write in <the user's language>.
   ```

2. `generate_outline` with `user_prompt`, `title`, `slug` (short kebab-case topic) and, only when the user typed a number of slides, `slide_count` (at most 20). The outline appears in the chat for the user to approve or change; do not repeat it in your reply.
3. Do what the result's `next_action` says. On `approved` or `auto_approved`, call `generate_design_slides` at once, in the same reply. On `revise`, change the plan as the user typed and call `generate_outline` again. On `cancelled` or `timeout`, say so in one line and stop.
4. `generate_design_slides` with the same `title`, `slug` and `user_prompt`, plus `source_text` (the user's facts and the facts and links you found) and `source_name`. Add `language` when the deck is not in English, and `template` only when the user named a look. Do not call any image tool: the slide maker makes the pictures itself.
5. If the result lists `slides_not_generated`, call `generate_design_slides` again with `slides` set to those numbers.
6. Call `read_design_deck` once, naming the slides with figures, and read the word counts in its manifest. Check the slides against the fact list: if the slide maker added a figure, comparison or name that is not in your list (for example "8 times the size of a country"), fix that slide with `edit_design_slides` and `slides` set to it, and say so in the reply.

## Step 5: Hand over

Reply in a few lines: the slide count and the minutes it fits, the level you pitched it at, the look the slide maker picked, any assumption (level, minutes), what picture each kind of slide carries, and the sources used (title and link, as found; do not call them "official" unless they are government or institutional pages). Offer a speaker script as the next step if none was asked for.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, and say in one line what changed. For a deck already built, call `edit_design_slides` with an instruction naming the change and `slides` set to the affected slide numbers only.

## What not to do

- Do not put more than 30 words on a slide or leave a content slide without a picture plan.
- Do not invent facts, statistics, quotes or sources.
- Do not plan more than 20 slides.
- Do not paste the slides or their code into the chat.
