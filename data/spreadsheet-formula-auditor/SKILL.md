---
name: Spreadsheet Formula Auditor
description: >
  Audits a spreadsheet and returns a findings table of broken formulas, hardcoded numbers, inconsistent or short ranges,
  and balance sheet or cash errors, each with a cell reference, severity and fix.
  Use it for "audit this workbook", "check my formulas", "find formula errors", "my balance sheet doesn't balance",
  "sanity check this spreadsheet", "model review", "something's off in my model".
  Also use it when the user pastes balance sheet, income statement or cash figures as text and asks why they don't tie.
---

# Spreadsheet Formula Auditor

A good result is a findings table the user can work through cell by cell: every issue has a sheet, a cell or range, a severity, what is wrong and the fix. Every number in it comes from the file, computed by code, never guessed. Report only; do not change the user's file unless they ask.

## Step 1: Load the workbook

1. Find the attached file (.xlsx, .xlsm, .csv). If the user pasted cells, formulas or statement figures instead, type them into `execute_code` as a table (sheet or statement, line, period, value or formula) and run every check and sum on that table in code. Then go to Step 3 if they are financial statements, otherwise to Step 4. Pasted data still gets the full Step 4 report.
2. Do not ask for a scope. Audit the whole workbook, every sheet, including hidden ones. If the user named a sheet or range, audit that first and say so.
3. In `execute_code`, load the file twice with openpyxl if it is installed (`pip install openpyxl` in the terminal if not; if that fails, use pandas for values and unzip the .xlsx to read `xl/worksheets/*.xml` formulas):
   - `load_workbook(path)` gives formulas as text.
   - `load_workbook(path, data_only=True)` gives the cached values (may be None if the file was never calculated in Excel; then say values were not cached and recompute simple sums yourself).
4. Print for each sheet: name, visible or hidden state, used range, number of formula cells, number of constant numeric cells. Print hidden rows and columns too.

## Step 2: Run the formula-level checks (all workbooks)

Write one script that scans every cell and prints candidates. Then judge each candidate by looking at its neighbours. Checks:

| Check | How to find it |
|---|---|
| Error values | Any cached value that is a string starting with `#` (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`), and `#REF!` inside formula text |
| Hardcodes inside formulas | Formulas containing a numeric literal other than 0, 1 or 2 (for example `=B4*1.05`, `=C7/1000`). Ignore row or column arguments in functions |
| Inconsistent formulas | Convert each formula in a row or column to relative (R1C1-style) form and compare with neighbours. Flag the one that differs from the rest |
| Pasted-over formulas | A constant number sitting in a row or column where the cells on both sides are formulas |
| Short ranges | `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNT` ranges that stop one row or column before the data ends, or start one after the header; also totals that skip a populated row |
| Totals that do not match | Recompute each total from its parts in Python and compare with the cached value |
| Broken cross-sheet links | References to a sheet that does not exist, to `[external workbook]` links, or to blank cells |
| Unit or scale mismatches | One column in thousands and the next in millions; percentages stored as 5 instead of 0.05; mixed units in the same row |
| Hidden rows, columns, tabs | List them and say what they hold; flag any that contain formulas or numbers feeding visible cells |
| Circular references | Trace formula dependencies for loops. Note whether it looks intentional (interest on average debt) and whether an iteration setting exists |
| Text stored as numbers, blank cells in a SUM, mixed data types in a column | Check cell data types |

Also check formulas that divide without an `IF` or `IFERROR` guard when the divisor can be 0 or blank, and lookups (`VLOOKUP`, `INDEX/MATCH`) that use approximate match by accident (a missing `FALSE` or 0).

## Step 3: Run the model-integrity checks (any financial model)

If the workbook has a balance sheet, income statement, cash flow, DCF, LBO, merger or similar tabs, name the model type and run the checks. Read `references/model-checks.md` first for the list of tests per statement and per model type.

Do all arithmetic in `execute_code`: for every period, compute Total Assets minus (Total Liabilities plus Equity), CF ending cash minus BS cash, retained earnings roll-forward, and the sum of CFO, CFI and CFF against the change in cash. Print the gap per period. If the balance sheet does not balance, quantify the gap per period and trace where the gap first appears (the first period where it is non-zero, then the line whose change equals the gap or half of it). Put that trace at the top of the report.

How to word the trace:
- State the gap per period as a measured fact (for example "Year 2: assets exceed liabilities plus equity by 20").
- List possible causes as "Candidate causes to check", each with the line, the computed amount and what to check (for example the bank statement, the fixed-asset register, the debt schedule). Never say the error "is" on one side or that "only one line is wrong" unless the file shows it.
- A consistent roll-forward only shows a figure is consistent with the prior period. It supports the figure but does not prove it, and it does not rule out a misstated liability or asset.
- Do not invent flows the file does not show, such as assuming a fall in PP&E is depreciation with no capex. Say the split is unknown and list it as something to check.

For a workbook that is not a financial model (a budget, tracker, schedule), skip this step and instead check that totals equal the sum of their parts, that percentages sum as intended, and that dates and units are consistent.

## Step 4: Write the report

The report goes in the reply itself, in full, for files and pasted data alike. Always use this shape, including the summary line, findings table, Impact, What I checked, Not checked and Offer, filled only with what the file showed:

**Summary line:** `<Workbook name> — Overall: <Clean / Minor issues / Major issues> — <N> critical, <N> warnings, <N> info`. For a financial model, add `Model type: <type>` and the balance check result per period.

**Findings table**, ordered Critical first:

| # | Sheet | Cell or range | Severity | Category | What is wrong | Suggested fix |
|---|---|---|---|---|---|---|

- Critical: the output is wrong (error values, balance sheet out of balance, cash not tied, a total that skips data).
- Warning: risky (hardcodes in formulas, inconsistent formulas, pasted-over values, missing divide guards).
- Info: style and best practice (colour coding, labels, hidden but harmless cells).
- Give the formula as found and the corrected formula in the fix column, for example `=SUM(B2:B11)` in place of `=SUM(B2:B10)`, using the real cell addresses.
- Group repeated instances of the same pattern into one row with the range (for example `D5:D9`), but name every cell.

After the table, add:
1. **Impact**: for each Critical item, the size of the error as a number computed by code (for example the amount a short SUM leaves out, or the balance gap per period).
2. **What I checked**: one line listing the sheets and checks run, including how many formula cells were scanned.
3. **Not checked**: macros (VBA cannot be audited from formulas), external links that could not be opened, cached values missing, anything else skipped.
4. **Offer**: say the corrections have not been applied and that the user can ask for a corrected copy.

If nothing is wrong, say so plainly and still list what was checked. Do not invent issues to fill the table.

## Hard rules

- Every cell reference, formula and number in the report comes from the file or from your code output. Never write a cell address you did not see.
- Do every sum, difference and percentage in `execute_code`, including for pasted figures. Never calculate in your head.
- Report gaps as measured facts and causes as candidates to check. Never state a cause as established.
- Do not use industry benchmarks or margin norms as facts. If a growth rate or margin looks extreme, flag it as "worth confirming" and give the computed number.
- Do not edit or overwrite the user's file. If asked afterwards for a fixed version, save a new copy with a clear name and publish it with `publish_artifact` (`kind: "document"`).
- If the sheet is large (over about 50,000 cells), scan it all in code but list only the top findings by severity and say how many more were found.
