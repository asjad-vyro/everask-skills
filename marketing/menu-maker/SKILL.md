---
name: Menu Maker
description: >
  Turns your list of dishes and prices into a clean, print-ready restaurant, cafe or event menu as a PDF, with sections, optional descriptions and dietary marks.
  Use it for "make a menu", "design a cafe menu", "turn this price list into a printable menu", "bilingual menu", "wedding dinner menu".
---

# Menu Maker

A good menu is easy to scan: sections in the order the owner wants, every dish and price exactly as given, one consistent price format, and room to breathe. The result is a one or two page PDF ready to print.

**Hard rules**
- Write the menu in the language the user wrote in, unless they ask for another. Keep dish names, prices and currency symbols exactly as given.
- Never invent a dish, price, description, ingredient, allergen or dietary mark. Write a description only when the user asks for descriptions, and then only from ingredients they gave. A missing price stays blank (no dots, no price); list those dishes in the reply.
- Allergen and dietary marks (V, GF, spicy...) only where the user supplied them.
- Copy every dish name, section name and price character for character, including capital letters ("Tomato soup" stays "Tomato soup"; do not title-case). Do not invent section names: if the user gave none, use ONE section with an empty `name`, even if the dishes could be grouped. `title` and `tagline` are only what the user gave; with no venue name use a plain word in the menu language (the word for "Menu") as the title and no tagline.
- Never change a price when tidying the format. Only unify the look (for example `4.5` to `4.50`) if the user's own prices already use two decimals elsewhere; otherwise copy each price as written.

## Step 1: Get the items

- Pasted text or a message: read the dishes, prices and sections from it.
- A photo or scan of an old menu: call `media_analyze` on it asking for the full text with prices, then work from that text. In the reply, say that it was read from the image and list anything unclear.
- A spreadsheet (.xlsx or .csv): read it with pandas; use columns for section, name, price, description, notes if present.

Keep the user's section order and item order. If there are no sections, make one section with no name. If the user gave a section name in one language and wants a bilingual menu, see Step 2.

## Step 2: Write the data file

Use `write_file` to save `/tmp/.scratch/menu/data.json`:

```json
{
  "filename": "<venue-name-menu>",
  "title": "<venue or event name, as given>", "tagline": "<optional, as given>",
  "lang": "<ISO code of the menu language>",
  "size": "a4", "theme": "burgundy", "columns": 1,
  "png": false,
  "legend": {"<mark>": "<meaning as the user gave it>"},
  "note": "<footer line>",
  "sections": [
    {"name": "<section>", "note": "<optional>",
     "items": [{"name": "<dish>", "name2": "<second language, optional>", "price": "<as given>", "desc": "<optional>", "marks": "<optional>"}]}
  ]
}
```

- `size`: `a4` (default), `a5`, `letter` (US/Canada or if asked). `theme`: burgundy, green, navy, terracotta, charcoal, gold, teal (pick one that suits the venue; the user's colour if named). `columns`: 1 up to about 18 items (a single column fills an A4 page better than two half-empty ones), 2 for more; omit to let the builder decide.
- `png`: true only when the user wants a digital or social version; then PNG pages are also made.
- **Bilingual**: only when asked. Put the original name in `name` and the translation in `name2`, translated carefully; add a line in the reply that translations should be checked by a speaker.
- `legend`: only when marks are used. `note`: if any mark or allergen info is used, or the user asks, write this line, translated into the menu language: "Allergen and dietary information must be confirmed with the business before ordering." Use that meaning, not a different sentence. Add anything else the user asked to print (opening hours, service charge) exactly as given.
- Right-to-left languages (`ar`, `he`, `fa`, `ur`) are handled by `lang`.

## Step 3: Build

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. If `skill_view` gives no path, find `build.py` under `~/.computer/skills` with `search_files`. Run, with the full path:

`python3 SKILL_DIR/scripts/build.py /tmp/.scratch/menu/data.json /tmp/.scratch/menu/out`

It fills `templates/menu.html` and renders the PDF with headless Chrome, then prints JSON. Check it:
- `items` equals `items_in_html`, and equals the number of dishes the user gave (count them yourself in `execute_code` from the input if you are unsure).
- `missing_from_html` is `[]`.
- `pdf_pages` is 1 or 2 (3 at most for very long menus). If it is more, use `"columns": 2` or shorten descriptions, and run again once.
- The script finds Chrome itself (including the copy in `~/.cache/puppeteer`); do not install anything. If the JSON has an `error` about Chrome, publish the `.html` with `publish_artifact` (`kind: "html_preview"`) and say the PDF could not be made.

If PNG pages were made, call `media_analyze` once on the first one, asking whether any text is cut off, overlaps, or is hard to read; fix once and rebuild. Otherwise the checks above are enough.

## Step 4: Deliver

Publish the PDF with `publish_artifact` (`kind: "document"`), and any PNG pages with `kind: "file"`. Use a meaningful name.

The reply has: one line saying what you built (size, pages, columns); the counts ("12 dishes in 3 sections, all prices as given"); what you assumed (sections, theme, language); dishes with no price or unclear text; and, if marks were used, the sentence that allergen and dietary information must be confirmed by the business (say that the footer carries it). Do not paste the HTML.

## When the user asks for a change

Change only what was asked (a price, a dish, a section, the colour, the size) by editing the data file and rebuilding. Keep everything else exactly as it was, rebuild the same file type under the same name, and say in one line what changed.
