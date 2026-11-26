---
name: Ebook and Booklet Maker
description: >
  Turns a topic, an outline or your own draft into a designed short ebook or booklet as a PDF: cover, contents page, chapters and a closing page.
  Use it for "make an ebook", "create a booklet", "turn this draft into a PDF guide", "lead magnet", "write and design a short guide", "buat ebook".
---

# Ebook and Booklet Maker

A good short ebook has a clear promise on the cover, a contents page whose page numbers are right, four to eight chapters that each do one job, and a calm, readable layout. The result is a PDF of roughly 8 to 30 pages, published in the same reply.

**Hard rules**
- Write the book in the language the user wrote in, unless they ask for another. Keep their names, figures, terms and the exact title they gave. Right-to-left languages (Arabic, Hebrew, Persian, Urdu) are handled by `lang`.
- Never invent statistics, studies, quotes, testimonials, case histories, prices, author credentials, contact details, dates or a copyright year. A claim that needs a source gets a real source (Step 2) or is left out. Where something is missing, write a visible placeholder such as `[to add: author bio]` and list it in the reply.
- If the user gave a draft, keep their words: only lay them out (split into chapters, add headings the structure needs). Do not rewrite, shorten or "improve" their text unless asked.
- Never put text inside a generated picture: the title and every word are typed in the layout.
- Never speak as the author or shop about things the user did not tell you: no "in our experience", "the plants we hand to customers", "our customers", no claimed years in business. Write in a neutral guide voice.
- Safety, health, toxicity and legal statements (for example "this plant is unsafe for pets") are facts too: include one only if the user gave it or a search (Step 2) shows it; otherwise leave it out.
- Never ask questions first: decide, state the assumptions, deliver. The first words of the reply must be what you built, never "I'll load the skill" or any narration of tool use (do not write it before the tool calls either).
- Never install a browser or a PDF package (no `pip install playwright`, `weasyprint`, `apt`). If no Chrome is found, publish the .html as `html_preview` and say so.

## Step 1: Plan

Work out, and write down in the reply's assumptions line:
1. **Topic, audience, goal** from the message. Missing audience: "beginners". Missing goal: "inform and give practical steps".
2. **Size**: `a5` for a booklet or if unsure for a print booklet, `a4` default, `letter` for US/Canada or if asked, `6x9` for a trade-style ebook. **Theme**: `navy` default; also `green`, `burgundy`, `terracotta`, `charcoal`, `teal`, `purple`, `gold`, or a `#rrggbb` the user named.
3. **Chapters**: 4 to 8, each with a title that says what the reader gets. With an outline from the user, one chapter per item, titles exactly as given. With a draft, split at its own headings or topic changes; keep the order.
4. **Source of the draft**: if the user asks you to take their text from Google Drive or Notion and it is connected, use it; otherwise work from what they gave you.
5. **Length**: with a topic only, write about 2,000 to 5,000 words in total in this one reply (a typical chapter is 300 to 700 words) and say that this is the limit per reply; offer to extend a chapter at a time. With a draft, the length is the draft's.

## Step 2: Write the chapter text

For each chapter write `lead` (one sentence promise, optional) and `body` in this small format (blank line = new paragraph):

```
Plain paragraph text with **bold** and *italic*.

## A sub-heading
- bullet
- bullet

1. numbered step
2. numbered step

> A call-out box: a tip, a checklist note or a warning.
```

- Use a call-out or list in most chapters so pages are not walls of text. Call-outs hold the writer's own advice, never a made-up quote.
- Practical advice you give is general and hedged ("often", "many people"); no numbers you cannot source.
- A fact that needs support (a figure, a health or legal claim, a date): run at most 3 `web_search` or `web_extract` calls in the whole run, use only what the pages show, and list each as a line in `sources` (title, organisation or author, link). If you did not search, leave the claim out and have no `sources` page.
- Health, money and legal topics: add one plain line in the closing page that this is general information, not professional advice.
- The user's draft text goes into `body` unchanged (convert their headings to `## ` and their lists to `- `).

## Step 3: Cover picture (optional)

Only if the user wants a picture or the cover would be plain without one. Call `image_generate` once with top-level parameters only: a prompt for a simple portrait illustration or abstract background that fits the topic, ending with "No text, no letters, no logos, no words." Save it to `/tmp/.scratch/ebook-maker/cover.png` (copy it, or `curl -L -o` for a URL). Skip it for a first draft the user did not ask pictures for; a solid theme colour cover is fine.

## Step 4: Write the data file and build

Make `/tmp/.scratch/ebook-maker/` and save `/tmp/.scratch/ebook-maker/data.json` with `write_file`:

```json
{
  "filename": "<title-slug>", "title": "<title>", "subtitle": "<optional>", "author": "<only if given>",
  "lang": "<ISO code>", "size": "a5", "theme": "navy",
  "cover_image": "/tmp/.scratch/ebook-maker/cover.png",
  "labels": {"contents": "<Contents, in the book's language>", "chapter": "<Chapter>", "sources": "<Sources>"},
  "front_lines": ["© <year given, or [year]> <author given, or [author name]>", "<disclaimer or rights line if the user gave one>"],
  "copyright_page": true,
  "chapters": [{"title": "<chapter title>", "lead": "<optional>", "body": "<text in the small format>"}],
  "sources": ["<only real sources found>"],
  "closing": {"title": "<e.g. Thank you, in the book's language>", "body": "<short closing, next step, a contact only if given>"}
}
```

The file must be valid JSON: inside `body` write line breaks as `\n` escapes (a raw line break inside a string breaks it); the write result's `lint` must not show an error.

Leave out `cover_image` if there is none, and `sources` if there are none. Translate `labels` into the book's language. The `front_lines` copyright line uses only the author and year the user gave; otherwise the placeholders stay visible.

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Use the full path where it says `SKILL_DIR`. If `skill_view` gives no path, find `build_ebook.py` under `~/.computer/skills` with `search_files`. Run:

`python3 SKILL_DIR/scripts/build_ebook.py /tmp/.scratch/ebook-maker/data.json /tmp/.scratch/ebook-maker/out`

It renders the PDF with headless Chrome, fills the contents page and footer page numbers from the real pages, and prints JSON. Check it:
- `contents_match` is `true`, and `contents` lists every chapter with the same page in both fields. If not, run it once more.
- `pdf_pages` is between 8 and 30 for a normal ebook (a short booklet may be fewer). Say the number.
- `words_per_chapter` and `words_total` are the real counts; copy them, never estimate.
- `placeholders_in_text` lists what the user still has to fill; name each in the reply.
- If `error` says Chrome was not found, publish the `.html` with `kind: "html_preview"` and say the PDF could not be made.

Look once at the cover and one chapter page: use `terminal` to render them (`python3 -c "import fitz; d=fitz.open('<pdf>'); d[0].get_pixmap(dpi=60).save('/tmp/.scratch/ebook-maker/p1.png'); d[3].get_pixmap(dpi=60).save('/tmp/.scratch/ebook-maker/p4.png')"`) and call `media_analyze` on each, asking if text is cut off, overlapping or unreadable. Fix once and rebuild.

## Step 5: Deliver

Publish `/tmp/.scratch/ebook-maker/out/<filename>.pdf` with `publish_artifact`, `kind: "document"`.

- **Word version**: if the user wants to keep editing, or asks for .docx, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build the same text in a .docx; do not call `publish_artifact` for that file. Say that the layout is simpler than the PDF.
- **EPUB**: if asked, say EPUB is not produced; the PDF (and a Word file) are.
- **Print booklet**: pages are in reading order. Folding and stapling (saddle-stitch) needs the pages re-ordered, which the printer or the print dialog's booklet option does; page count should be a multiple of 4 for that, and the reply says how many pages there are.

The reply has, in order:
1. One line: what you built (title, size, page count, language).
2. The contents: chapter titles with page numbers, as in the PDF.
3. Word counts: total and per chapter, from the script.
4. Assumptions: audience, size, theme, anything you decided; the length limit and the offer to extend a chapter at a time (topic-only books).
5. What the user must still fill in or check: placeholders, sources used (or "no outside facts used, so no sources page").

## When the user asks for a change

Change only what was asked by editing `/tmp/.scratch/ebook-maker/data.json` (a chapter's text, the title, the colour, the size, a new chapter) and rebuilding. Keep everything else exactly as it was, rebuild the same file type under the same name, publish it again and say in one line what changed.

## Final check

No invented statistic, quote, testimonial, credential, year or contact; every gap is a visible placeholder named in the reply; the user's own text is unchanged; contents numbers match; the reply starts with what was built.
