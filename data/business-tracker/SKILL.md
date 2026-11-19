---
name: Small Business Tracker Workbook
description: >
  Builds a working Excel tracker for a small business: a sales log, expense log, inventory sheet, client jobs list or invoices-owed list, with live formulas, dropdowns and a monthly summary.
  Use it for "make me an expense tracker", "sales tracker in Excel", "inventory spreadsheet for my shop", "track my jobs and invoices", "bookkeeping sheet for my small business".
---

# Small Business Tracker Workbook

A good result is one .xlsx file the owner can start typing into today: an entry sheet, a lists sheet that feeds the dropdowns, and a summary sheet, all driven by live formulas. The workbook is checked after it is built, and the reply says plainly what it contains.

Hard rules:
- Write the workbook (sheet names, headers, notes) and the reply in the language the user wrote in, unless they ask for another. Keep their names, figures, category names and terms exactly as given. Use the currency and date format the user used; if they gave none, use a plain number format with no currency symbol and a `yyyy-mm-dd` date format, and say so. These formats override the `xlsx` skill's financial-model defaults (its `$` format and colour coding).
- Never invent business data. Rows come only from what the user gave. Without rows, the entry sheet holds only the two marked example rows described in Step 3.
- Do not add tax, VAT or GST columns unless the user asked. If they did, use the rate they gave; if they gave none, add a rate input cell left empty and say so.
- Finish in one reply. If the request leaves something open (categories, columns), choose sensible defaults from `references/layouts.md`, say what you assumed, and deliver. Use `clarify` only if you cannot tell what is being tracked at all.

## Step 1: Pick the tracker type

Choose from the request:
- sales, orders, takings, revenue: **Sales log**
- spending, costs, bills, receipts: **Expense log**
- stock, products, items on hand, reorder: **Inventory**
- jobs, projects, clients, bookings, work in progress: **Client jobs**
- invoices owed, who owes me, unpaid bills to collect: **Invoices owed**

If the user lists two needs ("sales and expenses", "jobs and unpaid invoices"), build one workbook with one entry sheet and one summary sheet per type (for example `Sales`, `Sales Summary`, `Expenses`, `Expenses Summary`) and one shared `Lists` sheet, on which each tracker's lists get their own columns. Do not build more than two trackers in one workbook.

## Step 2: Read the layout

Read `references/layouts.md` with `skill_view(name=<this skill>, file_path="references/layouts.md")` before you write any code. It gives, per tracker type, the exact columns, validation, formulas and summary layout. Follow it. Adjust column names, categories and the list of payment methods or statuses to the user's wording and business (a cafe's categories are not a plumber's); anything the user named goes in, in their words.

## Step 3: Build the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it for the build. Work in the folder it names. Deliver with its delivery step only after Step 4 passes; that step (a copy to its output folder plus its own `publish_artifact` call) is the only delivery, so do not publish a second copy.

Build with openpyxl. Every workbook has:
1. **An entry sheet** (name from the layout file). Headers in row 4, a title in row 1 and a one-line "how to use" note in row 2, data from row 5 down to row 1004 (1,000 rows of capacity, formulas and validation already in place for all of them). Freeze panes under the headers, filters on, column widths set, header fill, date and number formats applied to the whole column range.
2. **A `Lists` sheet.** One column per dropdown (categories, payment methods, statuses and so on), the user's values first, a few spare empty cells below each. Dropdowns point at the full column range of each list, so a value added to the list appears in the dropdown.
3. **A summary sheet** as defined in the layout file, made only of formulas that read the entry sheet. Use `SUMIFS` / `COUNTIFS` over the fixed ranges (`$E$5:$E$1004`), never pasted numbers. Copy the formulas from the layout file as written, changing only sheet names, column letters and the words the user chose. Avoid formulas the recalculation tool may not support (dynamic arrays, `LET`, `FILTER`, `XLOOKUP`); `SUMIFS`, `COUNTIFS`, `IF`, `IFERROR`, `INDEX`, `MATCH`, `EDATE`, `SUMPRODUCT` are fine.
4. **Data-entry guards** on every entry column: list validation for dropdown columns, a date validation for date columns, a decimal validation (zero or more) for amount and quantity columns, each with an error message in the user's language. Add the conditional formats the layout gives (for a sales or expense log, a highlight on rows with an amount but no date or category).
5. **A totals check** on the summary sheet: the total of the summary table against the total of the entries, showing `OK` or `CHECK`, with a one-line note on what a `CHECK` means (for a sales or expense log: an entry with no date, or a category missing from `Lists`). The monthly grid shows twelve months plus "Earlier" and "Later" columns, so no entry falls outside it.

Rows:
- If the user gave rows, write them into the entry sheet as typed values (dates as real dates, amounts as real numbers), keeping their wording. Computed columns still hold formulas. If a given row lacks a field, leave that cell empty and mention it.
- If the user gave none, leave the entry sheet empty apart from two example rows. An example row has `example, delete me` (in the user's language) in the text column the layout file names and everything else blank, so it adds nothing to any total. Style them in grey italics.
- Do not create sample data, sample customers, sample amounts or sample months anywhere, including the summary.

## Step 4: Verify

After saving, reopen the file in code and check, then fix whatever fails:
1. Run the recalculation tool the `xlsx` skill provides. It must return `"status": "success"` with no formula errors.
2. Load the recalculated copy with `data_only=True`. In pandas, sum the entry amounts and compare to the summary's grand total: they must be equal, and every check cell must show `OK`. If the user gave rows, also compute each category's total and each month's total in pandas from the rows you wrote, and confirm the summary cells match exactly.
3. Confirm with the formulas copy (`data_only=False`) that summary and computed cells begin with `=`, and that validations exist on the entry columns.
4. Take every figure you quote in the reply from this check, never from memory.

## Step 5: Reply

The workbook link comes from the `xlsx` skill's delivery step. Then reply with:

1. **What you got**: one line on the tracker type and sheet names, and one line on how to use it (type in the entry sheet from row 5, pick values from the dropdowns, read the summary sheet).
2. **Sheet by sheet**: a short list of each sheet's columns or sections, with which cells are formulas.
3. **Your data**: if the user gave rows, a small table of the monthly or category totals the summary shows, copied from the verification step. If not, say the entry sheet is empty apart from two marked example rows.
4. **Checks run**: the formula-error check and the totals check, with the verified total. Any overdue count or status is as of the day the check ran, and changes as days pass.
5. **Assumptions**: currency and date format, categories used, rows of capacity (1,000), anything left empty, and which twelve months the summary shows and how to change them.

## Rules

- The summary is formulas, not pasted values; entries and lists are the only typed values.
- Every number in the reply comes from code run on the saved file.
- Mark every assumption as one; never present a default as something the user told you.
- Not accounting or tax advice: say in one line that it is a tracking sheet, and that the user should check tax treatment with an accountant.
- If the user asks to pull data from Google Sheets, Google Drive, QuickBooks or Airtable and it is connected, you may use it as the source of rows. Otherwise work from what they gave you.
