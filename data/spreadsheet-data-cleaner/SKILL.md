---
name: Spreadsheet Data Cleaner
description: >
  Cleans a messy spreadsheet or CSV and hands back a cleaned copy plus a before/after change report: trimmed spaces, consistent casing, real numbers, one date format, duplicates removed.
  Use it for "clean this data", "clean up this sheet", "fix the formatting", "dedupe this list", "standardize this column", "this data is messy".
---

# Spreadsheet Data Cleaner

A good result is a cleaned copy of the data (the original is never changed), a table of every issue found with counts and the fix applied, and a short before/after summary the user can check. Do the whole job in one reply: never stop to ask for confirmation between steps.

## Step 1: Load and profile

1. Work in `/tmp/.scratch/spreadsheet-data-cleaner/`. If the user attached a file, read it with pandas (`read_csv` or `read_excel`, with every column loaded as text: `dtype=str, keep_default_na=False`). If the data is pasted in the message, write it to a CSV first. If there is no data at all, use `clarify` once to ask for it.
2. If the user named a range or sheet, use it. Otherwise use the first sheet's whole used range. Say which you used.
3. Keep an untouched copy of the loaded frame (`raw = df.copy()`) to count changes against.
4. Profile each column: the dominant type (text, number, date, category), the share of cells that fit it, and the outliers.

## Step 2: Detect issues

Check each column for these, and count the cells or rows affected. Do the counting in `execute_code`; never estimate.

| Issue | What to look for |
|---|---|
| Whitespace | leading or trailing spaces, double spaces, non-breaking spaces |
| Casing | one value written several ways in a category column (`usa` / `USA` / `Usa`) |
| Number as text | numbers held as text, with stray `$`, `,`, `%`, spaces or brackets for negatives |
| Dates | mixed formats in one column (`3/8/26`, `2026-03-08`, `March 8 2026`) |
| Duplicates | exact duplicate rows, and near-duplicates that differ only by case or whitespace |
| Blanks | empty cells in an otherwise full column |
| Mixed types | a column that is mostly numbers with a few text entries |
| Encoding | mojibake (`Ã©`, `â€™`) and non-printing characters |
| Errors | `#REF!`, `#N/A`, `#VALUE!`, `#DIV/0!` |

## Step 3: Apply the fixes

Apply in this order, so later steps see clean values. Write the cleaned copy to a new frame; never edit `raw`. Record every change in one per-cell change log (row, column, before, after, fix) as you go. Each changed cell gets exactly one entry under the first fix that changed it. A cell like `London ` that only needed trimming counts as Whitespace, not Casing.

1. **Whitespace**: strip, collapse runs of spaces to one, replace non-breaking spaces. Remove non-printing characters. Repair mojibake only when the fix is unambiguous.
2. **Casing**: in category columns (country, status, state, department), map variants to one form. Use the most common spelling in the column; for acronyms such as USA keep upper case. For name columns use title case, but leave names like `McDonald` or `van der Berg` alone if unsure, and list them as "left as is". Never recase free text, emails (lower-case them), IDs or codes.
3. **Numbers**: strip currency symbols, thousands separators and `%`, treat `(123)` as negative, then convert with `pd.to_numeric`. If the column mixes `1.234,56` and `1,234.56` styles, decide per column from the majority and say so. A value that will not convert stays as it was and is listed, not guessed. Percent cells: keep the number as written (`12%` becomes `12`) and say the column is in percent, unless the user asked for fractions.
4. **Dates**: parse every value in a date column, write them all as ISO `YYYY-MM-DD`. For slash dates, decide day-first or month-first from the values themselves (a first part above 12 proves day-first). If it is still ambiguous, assume month-first, and state the assumption in the report. Values that cannot be parsed stay as they were and are listed.
5. **Duplicates**: after steps 1 to 4, drop rows that are identical across all columns, and rows identical in their key column (email, ID, or the name plus date if there is none) when the other columns agree or are blank. Keep the first occurrence. Where two rows share a key but differ in other columns, do not drop either: flag them in the log as "possible duplicate, needs review".
6. **Blanks, mixed types, errors**: do not fill or delete. Flag them in the log (cell reference, value, issue). Only blank out `#N/A`-style error text when the user asked for it.

Write the result as a new file named after the original, for example `<original name>_cleaned.xlsx` (or `.csv` when the input was a CSV). For `.xlsx` output, use pandas with `openpyxl`, with a second sheet `Change log` listing every changed cell (sheet, row, column, before, after, fix) and every removed duplicate row, with the number of the row it matched. Keep the column order and header text. Do not overwrite or alter the input file.

## Step 4: Verify

In `execute_code`, check the cleaned frame against `raw`: the row count equals the original minus the removed duplicates; no column other than the intended ones changed; every converted column now has one type; no leading or trailing spaces remain. Build the issue-table counts by grouping the change log by column and fix. Then check that the table's cell counts sum exactly to the "cells changed" total. Also compute how many of those changed cells sit in rows later dropped as duplicates. Fix anything that fails before replying.

## Step 5: Deliver

Start the reply directly with the deliverable. Do not open with a preamble line such as "I'll load the skill first". Publish the cleaned file with `publish_artifact` (`kind: "document"` for .xlsx, `kind: "file"` for .csv). For small data (about 25 rows or fewer) also show the cleaned table in the reply. Then reply with:

1. **What I did**: one line on the scope (file, sheet, rows by columns) and any assumption (date order, number style, key column).
2. **Issues found and fixed**: a table with the columns Column, Issue, Count, Fix applied. Every count comes from the code, and a row appears only for an issue that exists.
3. **Before and after**: rows before and after, duplicates removed, cells changed, and two or three example before-to-after values taken from the real data. The cells-changed figure must equal the sum of the issue-table counts. Say whether it includes cells in rows later removed as duplicates, for example "8 cells changed, 2 of them in a row later removed as a duplicate".
4. **Needs your review**: the values left unchanged or flagged, with cell references, such as unparsable dates, possible duplicates and mixed-type cells. Write "none" if there are none.
5. The link to the cleaned file.

## Rules

- The original data is never overwritten; the cleaned output is always a separate copy.
- No invented values: never fill a blank, guess an unparsable date or number, or merge records that might be different people. Flag them.
- Every count and total in the reply comes from code, never from memory or mental maths. The issue-table counts come from the change log, each cell is counted under one issue only, and they sum to the stated cells changed.
- Finish in one reply. State assumptions rather than asking, except when there is no data at all.
- If the user wants live formulas (`=TRIM(A2)` and similar) instead of cleaned values, load the built-in `xlsx` skill with `skill_view` and write the formulas in helper columns next to the originals.
