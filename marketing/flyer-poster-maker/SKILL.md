---
name: Flyer and Poster Maker
description: >
  Makes a print-ready flyer, poster or invitation page as PDF and PNG, with your exact title, dates, times, prices and contact details laid out cleanly.
  Use it for "make a flyer", "design a poster for my event", "bake sale flyer", "party invitation", "A4 poster", "Instagram story poster".
---

# Flyer and Poster Maker

A good result is one clean page: a single headline, the key facts (when, where, how much) large and easy to read, one call to action, and every word exactly as the user wrote it. All text is real text, never drawn by an image model, so nothing is garbled.

**Hard rules**
- Write the page in the language the user wrote in, unless they ask for another. Keep their names, figures, dates, prices, phone numbers and addresses exactly as given. Do not translate, round or "fix" them.
- Never invent a date, time, place, price, phone number, URL, sponsor or slogan the user did not give. If an essential is missing (date, time, place, contact), put `[add date]`, `[add time]`, `[add place]`, `[add contact]` (in the user's language) in that field and list the missing items in the reply. The only words you may add yourself are a short headline or call to action built from what the user said (for example "Call 555..." when they gave a phone number). Do NOT add a year, a programme, activities, food, performances, audiences, claims such as "everyone welcome", or a slogan the user did not give. When the request is thin (only a name or topic), leave `kicker`, `subtitle`, `body` and `cta` out entirely: a page with the title and the `[add ...]` placeholders is the right result. Say in the reply which words you wrote.
- No logos or marks of real organisations unless the user supplied the file.

## Step 1: Decide the shape

Pick from the request, and say the choice in the reply:
- `size`: `a4` (default), `a5`, `letter` (US or Canada, or if asked), `a3`, `square` (social post), `story` (1080x1920, Stories). Add `"landscape": true` only if asked.
- `theme` colour: one of red, orange, yellow, green, teal, blue, purple, pink, black. Choose by mood (bake sale orange, school blue, party pink); use the user's colour if they name one.
- `lang`: the ISO code of the page language (`ko`, `es`, `ar`...). Arabic, Hebrew, Persian and Urdu pages are laid out right-to-left automatically.

## Step 2: Write the data file

Use `write_file` to save `/tmp/.scratch/flyer/data.json`:

```json
{
  "filename": "<short-name-with-hyphens>",
  "size": "a4", "theme": "blue", "lang": "<code>",
  "kicker": "<small line above the title, optional>",
  "title": "<the headline, as the user gave it>",
  "subtitle": "<one short line, optional>",
  "details": [{"label": "<Date>", "value": "<as given or [add date]>"}, {"label": "<Time>", "value": "..."}, {"label": "<Place>", "value": "..."}],
  "prices": [{"item": "<as given>", "price": "<as given, with currency>"}],
  "body": "<up to 3 short lines, optional>",
  "cta": "<one call to action>",
  "contact": "<phone, email, address, link as given>",
  "background_image": "<optional path to a PNG or JPG>"
}
```

Rules for the fields: labels are in the page language; at most 4 details and 6 prices (put the rest in `body`, or say it does not fit); leave out any field you have nothing for (do not put filler). Keep the title under 70 characters.

**Invitations** (wedding, birthday, party): `kicker` is "You are invited" in the user's language, `title` the occasion and names as given, `details` date, time, place, `body` dress code or RSVP only if given, `cta` the RSVP line if given.

**Optional picture**: only if the user asks for an image or the page looks plain for a poster. Call `image_generate` with top-level parameters only and a prompt that says "no text, no letters, no logos" and describes a simple background or illustration that fits the theme (portrait for a4/a5/letter/story, square for square). Save the file, put its path in `background_image`. White text on a darkened picture is applied automatically. Skip it for flyers with lots of prices or text.

**QR code**: do not make one. If the user gave a link, print it as text in `contact` and say a QR code can be added with a generator of their choice.

## Step 3: Build

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. If `skill_view` gives no path, find `build.py` under `~/.computer/skills` with `search_files`. The script finds Chrome itself (including the copy in `~/.cache/puppeteer`); do not install anything. Run, with the full path:

`python3 SKILL_DIR/scripts/build.py /tmp/.scratch/flyer/data.json /tmp/.scratch/flyer/out`

It fills `templates/flyer.html`, renders the PDF and PNG with headless Chrome, and prints JSON with `pdf`, `png`, `html` and `pdf_pages`. The design is fixed by the template: do not edit the HTML by hand unless a requested change cannot be made in the data file.

- `pdf_pages` must be 1. If it is not, shorten the text and run again.
- If the JSON has an `error` about Chrome, publish the `.html` with `publish_artifact` (`kind: "html_preview"`) and say that the PDF could not be made.

## Step 4: Look once

Call `media_analyze` on the PNG with the question: "Is any text cut off, overlapping, or hard to read? Is anything empty?" If yes, shorten the text or drop the picture, rebuild once. Then deliver.

## Step 5: Deliver

Publish both files with `publish_artifact`: the PDF with `kind: "document"`, the PNG with `kind: "file"`. Use the same meaningful name for both.

The reply has: one line on size, colour and language chosen; the two files; a list "Still to add" with each placeholder left in the page (or "nothing missing"); any text you wrote yourself (headline or call to action), so the user can change it. Do not paste the HTML.

## When the user asks for a change

Change only what was asked (a field, the colour, the size, the picture) by editing the data file and rebuilding. Keep everything else exactly as it was, produce the same file types under the same name, and say in one line what changed.
