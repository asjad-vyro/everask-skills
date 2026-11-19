---
name: Spreadsheet Merge and Compare
description: >
  Combines several sheets or files into one, or compares two versions and lists exactly which rows were added, removed or changed, without altering any source value.
  Use it for "merge these files", "combine these sheets", "stack these monthly tables", "join these on email", "what changed between these two versions", "compare old and new list".
---

# Spreadsheet Merge and Compare

A good result is either one combined table, or a precise list of differences between two tables, plus a log, with row counts that reconcile exactly. Source values are never altered, rounded or converted. Do the whole job in one reply: never stop to ask for confirmation.

## Hard rules

- Write the deliverable in the language the user wrote in unless they ask for another: the reply, the sheet names, the log and the labels (the English names below are defaults to translate). Keep their column names, names, figures and terms exactly as given.
- Never alter, round, retype or reformat a source value. Normalisation (trim, collapse spaces, case) is for matching and comparing only and lives in helper columns that are not delivered as data.
- Never drop a row without listing it in the log.
- Every count in the reply comes from `execute_code`, never from mental maths.
- No invented values: never fill a blank, guess a key or match rows that might be different records. Flag them.
- If the user asks to pull a sheet from Google Sheets, Google Drive, Airtable or Dropbox and it is connected, use it. Otherwise work from the files and text they gave you.
- State assumptions (key column, sheet used, join type, which file is older) instead of asking. Use `clarify` only if there is no data at all.

## Step 1: Load and profile

1. Work in `/tmp/.scratch/spreadsheet-merge-compare/`. Read attached files with pandas, every column as text: `read_csv(dtype=str, keep_default_na=False)` or `read_excel(dtype=str, keep_default_na=False)`. This text copy is for matching, comparing and checking. For pasted tables, write each to a CSV first, named by the label the user gave it (for example the month). For a workbook with several sheets, use the first sheet unless the user named one, and say which.
2. Decide the job: MERGE (stack, or join) or COMPARE (two versions of the same table). "What changed", "differences", "old vs new" means COMPARE. "Combine", "stack", "append", "join", "lookup" means MERGE. Say which you chose if it is unclear.
3. Keep untouched copies of each input. For each input, print: name, rows, columns, header list, and for the likely key column the count of blank and duplicate values.
4. Compare headers across inputs. Matching means the same text after trimming and ignoring case; say which headers matched that way. For MERGE, columns present in only some inputs are kept, left blank where an input lacks them, and listed in the log. For COMPARE, see Step 3b.

## Step 2: Choose the key (join and compare only)

1. Use the key the user named. If none, pick the column with the highest share of unique, non-blank values. Prefer an ID or code column (id, sku, code, number) over email or name, because an email or name can itself change between versions. Say "Assumed key: <column>, because <share> of its values are unique", and go on.
2. Build a helper column `_key` = key value trimmed, lower-cased, inner spaces collapsed. Use the helper only for matching.
3. List duplicate keys and blank keys in each input. Do not drop them. For COMPARE, rows with a duplicated key are matched in order of appearance (first with first: add the occurrence number from `groupby('_key').cumcount()` to the helper), and the log notes that the key was not unique. Rows with a blank key never match anything, not even each other: keep them out of the match, treat them as only in their own file and flag them.

## Step 3a: MERGE

- **Stack** (same columns): concatenate in the order the files were given. Add a `Source` column holding the file or sheet name for each row (unless the user said not to). Keep every row, including exact duplicates. List exact duplicate rows in the log under "Possible duplicates, kept". Reconcile: `rows out = sum of rows in`.
- **Join** on a key: match on `_key`. Default to a full outer join, so no row is lost; use left or inner only if the user asked, and then list every row that did not make it. Where both files have a non-key column of the same name, keep both as `<name> (<file A>)` and `<name> (<file B>)`. Keep the key column once if every matched pair has identical original text; otherwise keep it from both files the same way and list the pairs that differ. If a key repeats on one side, the join multiplies rows: count and list those keys. Reconcile: `rows out = rows A + rows B - matched keys` for a one-to-one full outer join; for anything else show the arithmetic that applies.

## Step 3b: COMPARE

Call the older version A and the newer one B. Tell which is which from the user's words or the file names ("old", "new", dates, "v2"); if nothing says, assume the first file is older and say so.

1. **Only in A**: keys present in A and not B (removed).
2. **Only in B**: keys present in B and not A (added).
3. Compare every shared column of each matched row, cell by cell, on the original text:
   - **Changed cell**: the two values still differ after trimming leading and trailing spaces, collapsing inner runs of spaces and ignoring letter case.
   - **Formatting-only cell**: the values differ as written but are equal after that normalisation (`abc` / `ABC`, `x@example.org` / `X@example.org `). Not a change. List these separately so nothing is hidden. Any other difference, including `007` / `7` or `1,000` / `1000`, is a changed cell.
   For each changed or formatting-only cell record: key, column, value in A, value in B.
4. Classify each matched row: **changed** if it has at least one changed cell; **formatting only** if its only differences are formatting-only cells; **identical** otherwise.
5. Columns in only one file are listed as added or removed columns, not as cell differences.
6. Reconcile: `A rows = only A + matched`, `B rows = only B + matched`, `matched = changed + formatting only + identical`.

Do not flag a row that has no differing cell. If the user's two files differ only by row order, say there are no differences.

## Step 4: Verify

In `execute_code`, assert: the reconciliation equations above hold; no source value in the output differs from the input (compare each output cell to the raw text frames; a cell written as a number must give back the original text when shown with its number format); the number of rows listed in the log equals the counts you will report. Fix anything that fails before replying.

## Step 5: Build and deliver

Load the built-in `xlsx` skill with `skill_view` and follow it to build the workbook, named for the inputs (for example `merged_<names>.xlsx` or `comparison_<A>_vs_<B>.xlsx`). Its delivery step (a copy to its output folder plus its own `publish_artifact` call) is the only delivery: do not publish a second copy. If the user asked for CSV, write the CSV with code and publish it yourself with `publish_artifact` (`kind: "file"`).

Write every value in its original form, never as retyped text:
- From an .xlsx input, take the output values from a second read of that file with its own types (`read_excel` without `dtype=str`, same row order), so numbers and dates stay numbers and dates.
- From a CSV or pasted input, a value that is a plain number (optional minus, digits with no leading zero, optional decimals with a dot, or with a comma when the whole column uses a comma) goes in as a number, with a number format that shows exactly the decimals it was written with (`0`, `0.0`, `0.00`). Everything else (`007`, `1,234`, dates, codes) goes in as the original text.

Sheets for MERGE: `Merged` (all rows, the original header text plus any `<name> (<file>)` columns from a join, `Source` column first or last) and `Log`.
Sheets for COMPARE: `Summary` (counts), `Only in A`, `Only in B` (whole rows as in the source), `Changed` (columns: Key, Column, Value in A, Value in B), `Formatting only` (same columns, only if there are any) and `Log`.
`Log` lists: inputs with rows and columns, which file is A and why, assumed key and why, header matches, duplicate and blank keys, rows not matched or kept for review, and the reconciliation lines with numbers.

## Step 6: Reply

Start with the result, not a preamble. The reply holds:

1. **What I did**: job, inputs (name, rows by columns), key and assumptions.
2. **Counts**: a small table. MERGE: rows per input, rows out, duplicates flagged. COMPARE: rows in A, rows in B, only in A, only in B, changed, formatting only, identical. Then the reconciliation as an equation with the real numbers.
3. **The differences**: for COMPARE, list every removed row, every added row and every changed cell (key, column, A value, B value) in the reply when there are about 25 or fewer; otherwise list the first 25 and point to the workbook. Then one line with the number of formatting-only cells (and up to five examples), saying they were not counted as changes. For MERGE, show the whole merged table when it has about 25 rows or fewer, otherwise the first rows.
4. **Needs your review**: duplicate or blank keys, unmatched headers, assumptions that could change the result. Write "none" if there are none.
5. The link to the file.
