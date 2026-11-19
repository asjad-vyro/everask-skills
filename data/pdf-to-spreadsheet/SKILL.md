---
name: PDF to Spreadsheet
description: >
  Turns the tables in a PDF, a scanned page or pasted text copied from a PDF into a clean Excel workbook, with numbers as real numbers and a Checks sheet that tests the totals the document prints.
  Use it for "extract the table from this PDF", "turn this PDF into Excel", "convert this price list to a spreadsheet", "get the data out of this statement".
---

# PDF to Spreadsheet

A good result is an .xlsx with one sheet per table, every row traceable to its source page, numbers stored as numbers, and a `Checks` sheet showing that the extracted columns add up to the totals the document itself prints. Nothing is invented and nothing is "corrected": an unreadable cell stays empty and is listed. Do the whole job in one reply, without stopping to ask.

Hard rules:
- Write the reply and the workbook's sheet and column labels in the language the user wrote in, unless they ask for another (the English names below, such as `Checks`, `Source page`, `Source text` and `match`, are defaults to translate). Keep the document's own names, figures, spellings and terms exactly as printed. Nothing here depends on English, on one date format or on one currency.
- Never invent, round, "fix" or infer a figure. If a printed total disagrees with the sum of its rows, report the difference and leave both as they are.
- Every count and sum comes from code (`execute_code` or `terminal`), never from mental arithmetic.
- Keep the source page number for every row.

## Step 1: Get the text

Work in `/tmp/.scratch/pdf-to-spreadsheet/`.

1. If the user pasted text instead of a file, write it to a file and go to Step 2. If there is no PDF, image or text at all, use `clarify` once to ask for it.
2. A PDF is attached as a local path or a URL. The built-in file reader may already have shown you its text, but that text loses column positions and page numbers, so extract it again here. If it is a URL, download it with `curl -L --fail -o /tmp/.inputs/<name>.pdf "<url>"`. Count the pages with pypdf: `len(PdfReader(path).pages)`.
3. Page limit: one turn handles at most about 15 pages. For a longer file, process pages 1 to 15 (or the pages the user named) and say in the reply which pages are done and which remain, so the user can ask for the next batch.
4. Extract each page with `pdftotext -layout -f N -l N <file> -` through `terminal`. Layout mode places text by its position on the page, so columns stay apart even in a table with no ruled lines. Print the first page's raw output and look at it before writing any parser.
5. **Scans.** If a page gives almost no text (a handful of characters), it is a scan. Render it at 300 DPI with `pdftoppm -r 300 -png -f N -l N -singlefile <file> /tmp/.scratch/pdf-to-spreadsheet/page-N`, which writes `page-N.png`. Then run `tesseract page-N.png page-N -l <lang> --psm 6 tsv` through `terminal`. `<lang>` is the document's language from the installed set `eng`, `spa`, `fra`, `deu`, `ara`, `chi_sim`, `jpn`, `kor`; join two with `+`, as in `eng+fra`. Never OCR a page as `eng` when its language is another one. If the language is not in the set, read the page with `media_analyze` instead and mark every figure as unverified. If the user attached an image directly, start here with that image. In the `.tsv` output, `conf` is each word's confidence from 0 to 100. Any cell whose digits have confidence below 80, or that you cannot read, goes in empty, with the raw OCR reading in the `Source text` column and a line in the `Checks` sheet. Never guess a digit. Say in the reply that the figures were read by OCR.

## Step 2: Inventory the tables

For each page, record in a small list: page number, table title (or "untitled table"), the header cells as printed, the number of data rows, and any total, subtotal or grand total line printed on the page. Decide which rows are data and which are total lines. A table that continues on the next page with the same header is one table; repeated header rows are dropped, not kept as data. Say in the reply how many tables you found.

If several tables on one page share a layout, still keep them as separate sheets unless the document presents them as one.

## Step 3: Rebuild the rows

In `execute_code`, build one pandas DataFrame per table.

1. Header: use the printed header text exactly. Split lines by column position (the character offsets in the `-layout` output) or by runs of two or more spaces, never by single spaces, so a description with spaces in it stays in one cell. When lines are single-spaced (pasted text often is), anchor from the right: take as many trailing values that read as numbers as the header has numeric columns, fill those columns from the right, and keep the text before them as the description. Merge wrapped description lines into the row above.
2. Add a `Source page` column to every table (for pasted text, write "pasted"). Add a `Source text` column only if some cell needs it: a cell that was unclear, read by OCR below the confidence cut-off, or would not convert keeps its original text there. A clean conversion such as `1,234.50` to 1234.5 needs no copy.
3. Numbers: a column that is numeric becomes numeric. Remove currency symbols, thousands separators and units from the stored value, and treat `(123)` or a trailing minus as negative. Decide the decimal style (`1,234.56` or `1.234,56`) per column from the values, and say which you chose. Mention the currency or unit in the column header instead of the cells. A value that will not convert stays as the original text and is listed.
4. Dates: keep them as printed unless every date in the column is unambiguous; then write them as ISO `YYYY-MM-DD`. If a column could be day-first or month-first and nothing proves which, keep the printed text and note it.
5. Identifiers (part numbers, account numbers, codes with leading zeros) stay as text.
6. Total lines are not data rows. Move them to the `Checks` data (Step 4), not into the table.
7. Blank cells stay blank. Do not carry values down from merged cells unless the page clearly shows a merged group label; if you do, say so.

## Step 4: Verify

In `execute_code`, for every table:
- Compare the row count to the count you recorded in Step 2.
- For each printed total, subtotal or grand total, sum the matching extracted column and compare. Use `Decimal` or round to the column's printed decimals when comparing, so float noise is not reported as a mismatch.
- If the document gives line items as quantity times unit price, recompute the line amounts, and list rows that differ from the printed amount. Report them; do not change them.
- List every empty or unconverted cell with page, row and reason.

Build a `Checks` table with the columns: Table, Check, Extracted, Printed, Difference, Result (`match`, `mismatch` or `no printed total`). Fix only extraction mistakes you can see in the raw text (a missed row, a split cell) and re-run before you write the workbook. Never change a figure to make a total match: a mismatch that remains after that is reported as it is.

## Step 5: Build and deliver the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it to build the workbook. Its delivery step (a copy to its output folder plus its own `publish_artifact` call) is the only delivery: do not publish a second copy. Number formats follow the document, not the `xlsx` skill's financial-model defaults (no `$`, no colour coding). Give it:
- one sheet per table, named after the table title (31 characters at most, no `/ \ ? * [ ]`), or `Table 1`, `Table 2` if untitled;
- the header row bold and frozen, column widths that fit, numeric columns right-aligned with a number format that shows the printed decimals (no currency invented that the document does not show);
- a final sheet `Checks` with the table from Step 4, plus the list of empty or unconverted cells;
- no formulas that replace extracted values: the sheet holds the values as printed. If the user wants live totals, add them below the data in a clearly labelled row.

Name the file after the source, for example `<source name>-tables.xlsx`. If the user asked for CSV, write one CSV per table with `execute_code` and publish each with `publish_artifact` (`kind: "file"`).

## Step 6: Reply

Start with the result, not a preamble. If the data is small (about 25 rows or fewer in total), show the extracted table in the reply as well. Then:

1. **What I extracted**: file name, pages covered (and pages not done, if any), number of tables, rows per table, with the figures from the code.
2. **Checks**: one line per printed total, with extracted sum, printed value and result. State plainly any mismatch with the difference.
3. **Assumptions**: decimal style, date handling, rows merged, scan or text source.
4. **Needs your review**: empty or low-confidence cells with page and row, and anything left as text. Write "none" if there are none.
5. The workbook, delivered by the `xlsx` skill's own step.

Optional: if the user asks for the result in Google Sheets, Google Drive or Dropbox and that connector is connected, use it. Otherwise deliver the .xlsx and say so.
