---
name: Research to Spreadsheet
description: >
  Researches a list of companies, products, schools, tools or places on the web and delivers a comparison
  spreadsheet where every cell has a source link or is marked "not found". Use it for "compare these tools in a
  spreadsheet", "research these 5 companies and put it in a table", "make a comparison table of these universities".
---

# Research to Spreadsheet

The user gets an Excel workbook with a Comparison sheet (items down, attributes across) and a Sources sheet that gives the link and the date seen for every value, plus a short reply with the gaps. A cell is either a value found on a page you opened, or "not found". Nothing is filled in from memory without a label.

## Hard rules

- Write the workbook and the reply in the language the user wrote in, unless they ask for another. Keep item names, figures, units and technical terms exactly as the source gives them.
- Every value in the Comparison sheet must come from a page you read in this turn, and its URL goes in the Sources sheet. If you could not find it, write `not found` (in the user's language). If you are sure of a value but have no page for it, write it followed by `(unverified)`. Never present a remembered value as found.
- Prices and other figures that change carry their currency, their period (per month, per year, per user) and the date seen.
- Never invent a number, a URL, a release year or a licence. Never write a URL you did not get from a search result or a page.
- Only organisations, products, places and things. Do not research or list private individuals (no people lists, no personal contact details). If the user asks for that, leave it out and say so in one line.
- The reply is not finished until the workbook is published.

## Step 1: Fix the rows and the columns

1. **Rows (items).** Use the items the user named, exactly. If they named none ("the best CRM tools"), pick well-known ones that fit, say in the reply that you chose them, and why. At most 10 rows. If they asked for more, take the first 10 and say the rest was left out for this run.
2. **Columns (attributes).** Use the ones the user named. If they named none, choose 5 to 7 that help someone compare these items, such as the item's type or category, who runs or owns it, the year it began, a price or fee, one or two features that decide a choice, and the official website. At most 7 columns. If they asked for more, take the first 7 and say so. State the columns you chose in the reply.
3. When you choose the columns yourself, prefer ones the items' own official pages answer (type, owner, year founded, size, fee, official website). Avoid columns that need a separate lookup for every item, such as third-party rankings, unless the user asked for them: they use up the call budget.
4. Each attribute needs a clear question you can answer from a web page ("What licence is it released under?"). Decide the unit up front (one currency, one period) so cells are comparable.

Do not ask the user anything. Decide, state what you chose, and go on.

If the user asks you to pull the item list from, or send the table to, Google Sheets, Airtable or Notion and that app is connected, you may. Otherwise deliver the workbook.

## Step 2: Research, a few calls

Budget: about 12 `web_search` and `web_extract` calls in all. Plan them before you start.

1. Get today's date once with `terminal`: `date +%F`. This is the "date seen".
2. For each item, find its official page first (a `web_search` for the item name plus the main attribute). Prefer the item's own site, its documentation, its official repository or registry, a government or university site for schools, and a recognised reference page. Read the best page with `web_extract`. One page often answers several columns.
3. If the table is large, one good comparison or list page covering several items is cheaper than one search per item. Use it, but note which page each value came from.
4. After each item, write down what you found with `write_file` into `/tmp/.scratch/research-to-spreadsheet/data.json`, so nothing is lost. One record per cell:

```
{"item": "<item>", "attribute": "<attribute>", "value": "<value as the page gives it>",
 "url": "<page you read>", "date_seen": "<from date +%F>", "status": "found"}
```

   `status` is `found`, `unverified` or `not found`. For `not found`, leave `value` as "not found" and `url` empty. For a found value, copy it as the page states it, short (a few words or a figure), not a pasted paragraph.
5. Count your calls (`web_search` and `web_extract`, also when called inside `execute_code`, plus any `curl` of a page). When the budget is spent, stop. Every cell you did not reach is `not found`. Do not do more searches to fill the last gaps; say what is missing.
6. If two sources disagree, use the official one and mention the disagreement in the Sources sheet's note column.

## Step 3: Build the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it, including its delivery step. Do not call `publish_artifact` for this file. Name the file after the topic, for example `<topic>-comparison.xlsx`. Build it with openpyxl from `data.json`, using the labels in the user's language. One plain font throughout.

**Sheet 1, Comparison.**
- Row 1: header. First column is the item name, then one column per attribute. One item per row, in the order you were given them.
- Each cell shows its value. When the cell has a URL, make the value a hyperlink to that URL. `not found` cells are grey text on a light grey fill; `(unverified)` cells have a light amber fill.
- Bold header with a fill, freeze the top row and the first column, wrap text, column widths 18 to 30, row height that shows the whole value. It should fit on one screen without scrolling sideways for 7 columns.
- Under the table, after one blank row: `Researched on <date seen>` and one line, "Grey: not found. Amber: unverified." in the user's language.

**Sheet 2, Sources.**
Columns: `Item | Attribute | Value | Source URL | Date seen | Status | Note`. One row per cell of the Comparison sheet (items x attributes), in the same order, including the `not found` rows. Header bold, filter on, top row frozen, the URL as a hyperlink.

Before delivering, check in code: the Comparison sheet has one row per item and one column per attribute; the Sources sheet has items x attributes rows; every `found` row has a URL starting with http; no cell is empty (it holds a value or `not found`). Fix once if not.

## Step 4: Reply

In the user's language, in this shape:

```
<One line: the workbook is ready, with its name.>
<The table, as a Markdown table, when it is 6 rows by 5 columns or smaller; otherwise leave it out and name the columns.>
**Not found or unverified:** <each item and attribute left open, or "none">
**Main sources:** <one linked page per item, as [name](URL)>
**Choices I made:** <items or columns you picked, anything cut for size, anything left out for privacy, the date seen>
```

Do not paste the Sources sheet into the reply.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. To add an item or a column, research only the new cells (keep the old values and sources in `data.json`, or read them back from the existing workbook), rebuild the workbook under the same file name, and keep the 10 by 7 limit. To fix a value, replace that cell and its source row. Say in one line what changed.
