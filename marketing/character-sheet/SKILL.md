---
name: Character Reference Sheet
description: >
  Turns a character idea or drawing into a consistent reference sheet: front,
  three-quarter, side and back views, facial expressions, a colour palette with
  hex codes and written traits, plus a text bible you can reuse as a prompt. Use
  it for "make a character sheet", "model sheet for my mascot", "turnaround of
  my OC", "keep my character consistent", "expressions for my game character".
---

# Character Reference Sheet

The user has a character, as a description or a drawing, and wants it fixed in one reference sheet so it stays the same across a comic, game, animation, mascot or book. A good result is one sheet image (turnaround, expressions, palette, traits) and a written character bible whose words are reused unchanged in every image prompt.

Do the whole job in one reply. Never open with questions: decide, mark what you decided, deliver. Write no text before your first tool call or between tool calls: no "I'll load the skill", no "Let me", no progress notes such as "the strip came out wrong, regenerating". The first words the user sees are the result.

## Hard rules

- Write the reply and the text on the sheet in the language the user wrote in, unless they ask for another. Keep their character names, spellings and terms exactly. The image prompts themselves are written in English, because image models follow English best.
- Never invent facts the user did not give: a name, an age, a backstory, a species, a franchise or a personality. Design details you must choose to make the character drawable (hair length, outfit pieces, exact colours) are allowed, but mark each one in the bible as `(my choice)`; what the user gave is unmarked. When the request is short, almost everything is your choice (lining, belt, trim, boots, crest, hair, eyes, skin, age, build): mark every such line, not only the ones that feel big. Only the user's own words are unmarked. If the user gave no name, title the sheet with a plain placeholder such as the role ("Girl knight"), not an invented name.
- Real people, celebrities and existing copyrighted characters (anime, game, film, comic, cartoon characters, brand mascots): do not reproduce them. Say so in one line and make an original character in a similar genre, with different design details, and say which details you changed.
- Never sexualise a character. If the character is a child or looks young, keep clothing, pose and framing fully age-appropriate. If the user gives no age for a "girl" or "boy", do not make the character a child: choose a clearly adult or teenage-neutral design that fits the genre, and mark the age as `(my choice)`.
- No text inside the generated images (no labels, names, captions, signs). All lettering is drawn by the sheet script.
- Do not claim the views match until you have looked at them (Step 5).

Work in `/tmp/.scratch/character-sheet/`. Never install anything.

`SKILL_DIR` below is the `skill_dir` from the `skill_view` result that loaded this skill (the script is in its `scripts/` folder); use the full path in every command. If you do not have it, find `build_sheet.py` under `~/.computer/skills` with `search_files`.

## Step 1: Write the character bible

From the message (and an uploaded drawing, if any), write the bible as plain text. Fixed traits, one line each:

- Style line: the art style in one sentence (for example flat vector, anime, painterly storybook, 3D toy), taken from the user; if none, choose one that fits the use and mark it `(my choice)`.
- Species or type, apparent age group, build and proportions in head-heights.
- Face and hair: hair colour, length and style; eye shape and colour; skin or fur colour.
- Outfit: every piece, in order from top to bottom, with its colour.
- Colours: every colour as a hex code `#RRGGBB`, with a name for where it is used. Use the user's colours when they gave them.
- Distinguishing marks and props.

If the user attached a drawing or photo of the character, download it with `curl -L -o /tmp/.scratch/character-sheet/reference.<ext> "<url>"`, look at it with `media_analyze`, and write the bible from what is actually there; the picture is the truth, not your guess. For a photo of a real person, do not make a lookalike: say so and ask for a drawing or a description (this is the one case where you stop and ask).

Keep the bible compact: it is pasted in full into every prompt, word for word. Write it once and copy that exact text into the turnaround, expressions and any extra prompt: do not shorten, reword or drop pieces for the head-and-shoulders shot (the identity needs the full text). Before each `image_generate` call, check that the CHARACTER line equals the bible.

## Step 2: Turnaround image

Call `image_generate` with top-level parameters `prompt` (and `image_url` if the user supplied a drawing, to keep their design). One wide image, not four calls. Prompt shape, with the bible text copied in unchanged:

```
Character model sheet, turnaround: the same character shown four times in one row, full body from head to feet, in this order: front view, three-quarter view, side view, back view. Neutral standing pose, arms relaxed, same scale and same height in every view, plain white background, even flat lighting, no shadows, no text, no labels, no borders.
CHARACTER: <bible text, word for word>
STYLE: <style line>
```

If the result is not four views in a row, say so and retry once with "exactly four figures side by side, evenly spaced" added. Download the result with `curl -L` as `turnaround.png`.

## Step 3: Expressions image

Call `image_generate` again with `image_url` set to the turnaround image's URL (so the identity carries over) and the same bible text, word for word:

```
Character expression sheet: the head and shoulders of the same character shown <5> times in one row, same size and angle, front view, plain white background, no text. Expressions in order: neutral, happy, sad, angry, surprised.
CHARACTER: <bible text, word for word>
STYLE: <style line>
Keep the face, hair, colours and outfit identical to the reference image.
```

Use the number of expressions the user asked for (4 to 6; five is the default). Download as `expressions.png`.

Optional: an action pose or outfit variants only when the user asked for them, one more `image_generate` call each, with `image_url` set to the turnaround and the same bible text. Do not make more calls than that.

## Step 4: Assemble the sheet

Write a job file and run the script. Every text on the sheet (title, labels, traits) is in the user's language; hex codes are drawn in code from your palette list, so they are exact.

```bash
python3 SKILL_DIR/scripts/build_sheet.py /tmp/.scratch/character-sheet/job.json
```

`job.json`:

```json
{"output": "/tmp/.scratch/character-sheet/<name>-sheet.png",
 "pdf": "/tmp/.scratch/character-sheet/<name>-sheet.pdf",
 "title": "<character name or role>", "subtitle": "<style line>",
 "labels": {"turnaround": "<heading>", "expressions": "<heading>", "palette": "<heading>", "traits": "<heading>"},
 "turnaround": "/tmp/.scratch/character-sheet/turnaround.png",
 "expressions": "/tmp/.scratch/character-sheet/expressions.png",
 "extras": [{"path": "<optional extra image>", "caption": "<heading>"}],
 "palette": [{"name": "<where used>", "hex": "#RRGGBB"}],
 "traits": [{"label": "<trait>", "value": "<text from the bible>"}]}
```

Leave out `pdf` unless the user asked for a PDF. Leave out `extras` when there are none. Read the script's `warnings` (a missing image, a bad hex code, Arabic or Hebrew text, which it cannot draw correctly: then use English labels on the sheet and give the translation in the reply).

## Step 5: Check, then publish

1. Look at the turnaround and the expressions with `media_analyze`, one call each or both together. Ask: do all views and faces have the same hair, eyes, outfit pieces and colours; are the proportions and scale the same; is there any text or stray object; are there four views and the right number of expressions.
2. Compare the colours seen with the palette hex codes. Generated colours drift: say so if a colour is clearly off, and that the hex codes on the sheet are the intended ones.
3. Name any drift honestly (for example a changed hair length, a missing scarf stripe, a different outfit colour in the back view) and offer one regeneration. Do not regenerate more than once yourself unless the turnaround does not show four views.
4. Publish the sheet PNG with `publish_artifact`, `kind: "file"`. If you built a PDF, publish it with `kind: "document"`. Publish the turnaround and expressions images as separate files too, so the user has them at full size.

## The reply

Start with the result, not with what you did. Do not begin with "I'll load the skill" or narrate tool use. Then:

1. The published sheet (and PDF if asked), and the separate images.
2. **The character bible**, in full, in the user's language, with `(my choice)` marks, ready to paste as a prompt: style line, traits, outfit, colours with hex codes, marks, props. Add the English prompt text you used for the images in one block, so the user can reuse it.
3. What the check found (plain words about the pictures; never mention internal tools, models or "drawing paths"): what is consistent, and any drift, named plainly, with an offer of one regeneration.
4. If you replaced a real person or an existing character with an original, say what you changed.

## When the user asks for a change

Change only what was asked (one trait, a colour, an expression, an extra pose). Update that line of the bible, keep every other word of it, regenerate only the image that must change with the previous image as `image_url`, rebuild the sheet under the same name, and say in one line what changed.

## Final self-check

- The bible is in the reply, in full, and the same text was used in every image prompt.
- No name, age, backstory or franchise was invented; every design choice of yours is marked.
- No real person or existing character was copied; nothing is sexualised.
- The sheet has no text from the image model, the hex codes are drawn by the script, and any drift is named.
- The reply is in the user's language and does not start with narration.
