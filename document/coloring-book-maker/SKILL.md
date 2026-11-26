---
name: Coloring Book Maker
description: >
  Makes a printable coloring book on any theme as one PDF: a cover and clean black-and-white line-art pages, for children or adults.
  Use it for "make a coloring book", "coloring pages of animals", "printable colouring book for my kid", "mandala coloring pages", "libro para colorear", "كتاب تلوين".
---

# Coloring Book Maker

A good coloring book has pictures that are easy to color: crisp black outlines on pure white, one clear subject per page, no repeats, and line weight that fits the age. The result is a print-ready PDF with a cover, and the page list in the reply.

**Hard rules**
- Write the cover and the reply in the language the user wrote in, unless they ask for another (Arabic: clear standard language, not a dialect). Keep the title, names and words the user gave exactly.
- Never put text in the pictures: the title and every word on the cover are typed by the script, not drawn.
- Nothing branded or trademarked: if the user names a character, brand or film (a cartoon mouse, a superhero), turn it into a generic description (a cheerful cartoon mouse in red shorts) and say so in the reply. Never draw a real person or a real child's likeness.
- Keep content age-appropriate. Never invent facts (animal facts, dates, claims) on pages; pages are pictures only.
- Limit: at most 12 pages plus one cover picture per reply (13 `image_generate` calls). If the user asks for more, say the limit up front in the reply, deliver the first 12, and tell them to ask for "the next set" (the same style line is then repeated so the book matches).
- Never ask questions first: decide, state assumptions, deliver. The first words of the reply must be what you made, never "I'll load the skill" or any narration of tool use (do not write it before the tool calls either).
- Generate exactly the planned number of pictures, no spares: the planned count is the page count in Step 1 (8 when the user gave none, not 12). Twelve is a ceiling, not a default.
- Never install a browser or a PDF package. If no Chrome is found, publish the .html as `html_preview` and say so.

## Step 1: Plan the pages

Decide and keep for the reply's assumptions line:
1. **Theme and audience**: from the message. Age missing: assume ages 4 to 8 (children). Adults or "relaxing", "mindfulness", "mandala": adult style.
2. **Page count**: the user's number (up to 12). Missing: 8.
3. **Style line** (written once, copied word for word into every prompt):
   - Young children (up to about 6): `bold thick black outlines, very simple large shapes, minimal detail, cute friendly style`
   - Older children (7 to 12): `clear medium black outlines, moderate detail, playful style`
   - Adults: `fine black line art, intricate detailed patterns, zentangle style`
4. **Numbered page list**: one subject per page, no two alike (three different kinds of fish count as repeats: vary the animal or object, not just its pose), each a single centred subject with a simple setting (for example: `1. a cow standing in a meadow`). Fit the theme and the age.
5. **Size**: `a4` default, `letter` for US/Canada or if asked. Title: the one given; if none, write a plain title in the user's language from the theme and say it is an assumption. Set `belongs_label` ("This book belongs to", translated) when the user wants a name page; for a gift or kids' book it is a nice default. Set `blank_backs` to true if the user mentions markers, paint or single-sided printing, or asks for it: a blank page follows every picture so ink cannot bleed through.

## Step 2: Make the pictures

Make `/tmp/.scratch/coloring-book-maker/` with `terminal`. Call `image_generate` once per page and once for the cover picture, top-level parameters only, with a portrait orientation if the tool has a size, aspect-ratio or orientation parameter. Every prompt has exactly this shape:

`Coloring book page, <style line>. Black outlines on a pure white background, no shading, no grey, no color, no filled black areas. Subject: <this page's subject>, centred, with space around it. No text, no letters, no words, no border.`

The cover picture's subject is the theme's most recognisable subject, smiling or in a simple pose. Copy or download each result to `/tmp/.scratch/coloring-book-maker/page-1.png`, `page-2.png`, ... and `cover.png` (`cp`, or `curl -L -o` for a URL). If a call fails, retry it once; if it fails again, leave that page out and say which in the reply.

## Step 3: Build the PDF

Write `/tmp/.scratch/coloring-book-maker/data.json` with `write_file`:

```json
{
  "filename": "<title-slug>", "title": "<title>", "subtitle": "<optional, e.g. the age range as given>",
  "author": "<only if given>", "lang": "<ISO code>", "size": "a4", "theme": "blue",
  "cover_image": "/tmp/.scratch/coloring-book-maker/cover.png",
  "belongs_label": "<translated, or leave the key out>", "blank_backs": false,
  "pages": ["/tmp/.scratch/coloring-book-maker/page-1.png", "..."]
}
```

`theme` (cover colour): blue, green, orange, purple, red, teal, chosen to suit the theme. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Use the full path where it says `SKILL_DIR`. If `skill_view` gives no path, find `build_coloring.py` under `~/.computer/skills` with `search_files`. Run:

`python3 SKILL_DIR/scripts/build_coloring.py /tmp/.scratch/coloring-book-maker/data.json /tmp/.scratch/coloring-book-maker/out`

The script turns every picture into pure black and white (greys print clean), whitens the edges, measures how much of each page is dark, builds the PDF with headless Chrome and prints JSON. Check it:
- `rejected` lists pages that are over 40 percent dark or nearly blank. Regenerate those pages once with the same prompt plus "much simpler, fewer lines", replace the files and run again. A page still rejected after that is kept out; say so.
- `pdf_pages` equals `expected_pdf_pages`, and `pages_match_plan` is `true`. The expected count is the cover, the optional name page, and each picture (twice if blank backs).
- If `error` says Chrome was not found, publish the `.html` with `kind: "html_preview"` and say the PDF could not be made.

Look once at one page: call `media_analyze` on `/tmp/.scratch/coloring-book-maker/out/bw/page-01.png` asking whether it is clean black outlines on white, whether the subject matches `<subject>`, and whether any text or letters appear. If text appears, regenerate that page once.

## Step 4: Deliver

Publish `/tmp/.scratch/coloring-book-maker/out/<filename>.pdf` with `publish_artifact`, `kind: "document"`.

The reply has, in order:
1. One line: title, number of pages (with the cover), paper size, age style.
2. The numbered page list (subject per page), exactly as in the book.
3. Assumptions: age, page count, style, title if you made it, size, and any generic replacement of a named character; any page left out and why.
4. Printing tip: print at 100 percent, single-sided on plain white paper (a blank back page was added if markers were mentioned).
5. If more than 12 pages were asked for: the limit and how to ask for the next set.
6. If they plan to sell it: check the platform's rules on AI-made content before publishing; compliance is not promised.

## When the user asks for a change

Change only what was asked: regenerate only the page named, with the same style line and the new subject, replace only that file, and rebuild. Keep every other page exactly as it was, rebuild the same file under the same name, publish again, and say in one line what changed.

## Final check

No text inside pictures; no trademarked character; every page present and on the list; the PDF page count matches; the reply is in the user's language.
