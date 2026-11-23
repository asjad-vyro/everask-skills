---
name: Product Catalog Maker
description: >
  Turns a product or service list, pasted or from a spreadsheet, into a tidy PDF catalogue or price list with a cover, contents, sections, codes, descriptions and prices.
  Use it for "make a product catalogue", "price list PDF", "turn this spreadsheet into a catalog", "services price list for my salon", "raise all prices by 5 percent".
---

# Product Catalog Maker

A good catalogue is accurate first and pretty second: every product, code and price exactly as the user gave it, grouped by category, easy to scan, with page numbers. The result is a PDF of a few pages.

**Hard rules**
- Write the catalogue in the language the user wrote in, unless they ask for another. Keep product names, codes, units, prices and currency symbols exactly as given.
- Never invent a product, specification, description, price, unit, code, discount or company detail. A missing value stays blank (the column is simply empty); list products with a missing price in the reply.
- No generated pictures presented as the product. Use a product photo only if the user supplied an image file for it.
- Price changes are done in code only (Step 3), never in your head.

## Step 1: Read the list

- Pasted text: read it into rows with these fields: `category`, `code`, `name`, `desc`, `unit`, `price`.
- An uploaded .xlsx or .csv: read it with pandas in `execute_code` (`pd.read_excel(path, dtype=str)` or `pd.read_csv(path, dtype=str)`; keep everything as text so codes like `007` and prices keep their form). Print the column names and the first rows, map each column to a field above by its header (in any language), and use `fillna("")`.
- No category column or no categories given: use one category named after the list's kind (for example the title the user gave).
- Keep the user's category order and row order. Count the rows: this count must match the PDF.

## Step 2: Write the data file

Use `execute_code` or `write_file` to save `/tmp/.scratch/catalog/data.json`. When the data came from a spreadsheet, build the JSON with Python so nothing is retyped.

```json
{
  "filename": "<company-or-topic-catalogue>",
  "title": "<title as the user gave it, or a plain one such as Price List>", "subtitle": "<optional, as given>",
  "company": "<as given, optional>", "lang": "<ISO code>", "size": "a4", "theme": "blue",
  "labels": {"code": "<Code>", "name": "<Product>", "desc": "<Description>", "unit": "<Unit>", "price": "<Price>"},
  "contents_label": "<Contents>",
  "page_per_category": false, "cover": true,
  "note": "<footer line the user asked for, e.g. valid until a date they gave; otherwise omit>",
  "price_change_percent": null,
  "categories": [{"name": "<category>", "items": [{"code": "", "name": "<as given>", "desc": "", "unit": "", "price": "<as given>", "image": "<optional file path>"}]}]
}
```

- `labels` and `contents_label` must be in the catalogue language (translate only these headings). `theme`: blue, green, burgundy, charcoal, teal, orange, purple (the user's colour if named). `size`: `a4` (default) or `letter` (US/Canada or if asked).
- Columns with no data in a category are dropped automatically. `page_per_category`: true only for long catalogues with big categories.
- `cover`: true (default) gives a full-page cover with the contents. For a short list (one category, or 12 products or fewer in total) set `"cover": false`: the title becomes a header on page 1, so a small price list is one page, not a cover and a nearly empty page.
- Do not put a date, validity period or terms on the cover unless the user gave them.
- **Price change** ("raise all by 5 percent", "10 percent off"): set `price_change_percent` to 5 or -10. The builder applies it to every price with a number, keeps the symbol and decimal style, and rounds half up to the original number of decimals. It lists every old and new price in `price_changes`. State the rule in the reply and show the first three changes as examples. Never edit prices yourself.

## Step 3: Build

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. If `skill_view` gives no path, find `build.py` under `~/.computer/skills` with `search_files`. Run, with the full path:

`python3 SKILL_DIR/scripts/build.py /tmp/.scratch/catalog/data.json /tmp/.scratch/catalog/out`

It fills `templates/catalog.html` and renders the PDF with headless Chrome (cover with contents and page numbers, or a plain header, then one table per category, page numbers at the bottom), then prints JSON. It finds Chrome itself (including the copy in `~/.cache/puppeteer`): do not install anything. Check:
- `items` equals `items_in_html` and equals the row count from Step 1.
- `missing_from_html` is `[]`.
- `pdf_pages` is at least 1 (at least 2 with a cover). If `pdf` is null, say so and publish the `.html`.
- If the JSON has an `error` about Chrome, publish the `.html` with `publish_artifact` (`kind: "html_preview"`) and say the PDF could not be made.

## Step 4: Optional price-list spreadsheet

Only if the user asked for a spreadsheet too: load the built-in `xlsx` skill with `skill_view` and follow it, including its delivery step, to build a workbook with one row per product (category, code, name, description, unit, price) from the same data, prices as the final text shown in the PDF.

## Step 5: Deliver

Publish the PDF with `publish_artifact` (`kind: "document"`) under a meaningful name.

The reply has: one line saying what you built (pages, size, theme, language); the counts ("10 products in 2 categories"); any price change rule with the first three examples; what you assumed; products with a missing price or unclear data. Do not paste the HTML.

## When the user asks for a change

Change only what was asked (a product, a price, a category order, the colour, the size, a price rule) by editing the data file and rebuilding. Keep everything else exactly as it was, rebuild the same file type under the same name, and say in one line what changed. A new price rule applies to the original prices, not on top of an earlier change, unless the user says to stack it.
