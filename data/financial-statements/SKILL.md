---
name: P&L and Financial Statements
description: >
  Turns a trial balance, export or pasted totals into an income statement and balance sheet, with big swings explained.
  Compares with prior period and budget, sums in code, and gives an Excel workbook and summary.
  Use it for "build the P&L from this trial balance", "income statement for March vs budget",
  "balance sheet for October", "why did expenses jump", "flag the big variances",
  "what adjustments before I close the books".
---

# P&L and Financial Statements

A good result is a pack-ready income statement: every figure traced to the data and totaled in code, comparisons only where supplied, big swings called out with next checks.

## Step 1: Read what the user gave you

Work from the message, pasted text and attached files. Pull data from QuickBooks, Zoho Books, Google BigQuery, Databricks, Google Sheets or Excel only if the user asks and the app is connected.

1. Name the input: a trial balance (debit and credit columns, or signed balances), a P&L or ledger export, or pasted totals. Group a ledger of transactions by account and period first.
2. Note the period; the currency and units (keep the data's own symbol and scale; if no currency is shown, show plain numbers and say so); and which comparison data exists: prior period, prior year, budget or forecast.
3. Work out whether income and expense balances cover the month or the year to date, from titles, column headers or the user's words. A trial balance dated at a month end usually carries year-to-date balances, so one month needs the prior month-end trial balance subtracted. Without it, report year to date, label it so, and say what the month needs.
4. Choose the statements: the income statement always; the balance sheet when the data holds asset, liability and equity accounts or the user asks; a cash flow statement only when asked and balance sheets for both ends of the period exist.
5. If the user asks a reference question instead (close adjustments, US GAAP or IFRS presentation), skip Steps 2 to 6: read the matching reference file, answer in the reply and build no workbook. A close checklist always covers accruals, prepaids, deferred revenue, depreciation, bad-debt allowance and income tax provision (verify, never estimate); check against the reference file's full list.
6. Never open with questions. If the figures the job needs are missing altogether, ask once with `clarify`. Otherwise decide, state each assumption in the reply, and deliver everything in that one reply; never wait for approval.

## Step 2: Map the accounts, in code

Read an attached file inside the code you run, so no figure is retyped (if its path isn't shown, one `search_files` look, then use the text shown). Put pasted figures in the code exactly as written.

1. Drop total and subtotal rows from exports ("Total Income", "Gross Profit", "Net Income") before summing, so nothing is counted twice. Keep them to compare with your totals in Step 3.
2. Turn each account into one signed amount: debit minus credit. Revenue, liabilities and equity then come out negative; flip the sign only when you present a statement.
3. Give each account a statement line:
   - Income statement: revenue; cost of revenue; operating expenses (by function if the chart or the user shows it, otherwise under the user's account names); other income (expense), such as interest; income tax.
   - Balance sheet: current assets; non-current assets; current liabilities; non-current liabilities; equity. Contra accounts (accumulated depreciation, allowances) net against their asset.
   - Account numbers help (1xxx assets, 2xxx liabilities, 3xxx equity, 4xxx revenue, 5xxx cost of sales, 6xxx-9xxx expenses, other and tax), but names and the user's grouping come first.
4. When an account could sit on two lines, pick the likelier one and list it under assumptions. Never split an account between lines or invent a functional split of a cost.

## Step 3: Compute and check, in code

Do all the arithmetic in one `execute_code` run that prints every statement line, subtotal, variance, margin and check. Never add numbers in your head or change a printed number by hand. Round only for display, and half up with `Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)`: `round()` and f-strings round ties to even, and the reply must match the workbook.

- Variance $ = current minus comparison. Variance % = variance divided by the absolute comparison figure ("n/m" when the comparison is zero). Margins are % of revenue; their changes are in percentage points.
- Favorable means revenue or income above the comparison, or an expense below it. The other direction is unfavorable.
- Net income = revenue - cost of revenue - operating expenses + other income (expense) - income tax.
- Print these checks and show their totals in the reply:
  1. Trial balance: total debits = total credits.
  2. Subtotals: your gross profit, operating income and net income match the export's own totals, if it had them.
  3. Balance sheet: total assets = total liabilities + total equity. In a trial balance taken before closing, retained earnings is still the opening balance, so add the period's net income to equity (unless a "current year earnings" line already holds it).
  4. Net income ties to retained earnings: opening retained earnings + net income - distributions = closing retained earnings on the balance sheet. If the data gives an independent closing balance, compare it with this figure.
- When a check fails, show the difference and the likely causes (a missing account, a wrong sign on a contra account, a period mismatch), carry on, and label the statement "does not balance by X". Never plug, round or adjust a figure to make a check pass.

## Step 4: Build the statements

Show only the columns the data supports (current; prior with variance $ and %; budget with variance $ and %). Never add an unsupplied comparison or fill one with estimates.

Income statement, with this column shape and these lines in this order (skip a line with no accounts):

| Line | Current (a) | Prior (b) | Var $ (a-b) | Var % | Budget (c) | Var $ (a-c) | Var % |
|---|---:|---:|---:|---:|---:|---:|---:|

Revenue (one line per revenue account), Total revenue, Cost of revenue, Gross profit, Gross margin %, Operating expenses (one line per account or function), Total operating expenses, Operating income (loss), Operating margin %, Other income (expense) lines, Total other income (expense), Income before taxes, Income tax expense, Net income (loss), Net margin %.

Show expenses as positive numbers under their heading, income as positive and expense in parentheses under other income (expense) so that section adds up, and negative results in parentheses.

Then a key metrics table, `| Metric | Current | Prior | Change |`, with revenue growth %, gross margin %, operating margin %, net margin %, operating expenses as % of revenue, and effective tax rate % (only when there is a tax line). Changes are in percentage points.

Read `references/balance-sheet-and-cash-flow.md` before building a balance sheet or cash flow statement, or for US GAAP or IFRS presentation. Read `references/adjustments-and-reclassifications.md` for close adjustment or reclassification questions, or when the trial balance looks unadjusted (no depreciation, accrual, tax or bad-debt lines).

## Step 5: Explain the material variances

1. Flag a line when the user's threshold is exceeded. If they gave none, flag a line whose variance is at least 10% of its comparison figure and at least 1% of total revenue, plus the three largest dollar movements, and state the rule you used.
2. For each flagged line give the variance in $ and %, favorable or unfavorable, and what the data shows about the cause: which sub-accounts moved, the mix between revenue lines, the effect on margin. State mix as share of revenue; call a line lower-margin only if the data gives its cost. Build any "other items" split in code from the flagged total's own section, and print its sum; it must equal the remainder you state. When the data has volumes, prices or currencies, split the variance into volume, price, mix, new or discontinued items, and currency effects.
3. Copy Var $ and Var % from the income statement, same sign, tax and other lines too (current minus comparison): an expense that rose is a positive number marked Unfavorable. Never flip signs for favorability, in the reply or the workbook.
4. Never state a business reason you weren't given, and don't guess what an account is made of (campaigns, project work, seasonality). Put likely reasons as questions for the user ("Did a campaign launch in October?") and name the follow-up: investigate, update the forecast, or check a timing difference.

## Step 6: Build the Excel workbook

Load the built-in `xlsx` skill with `skill_view` and follow it. Write the numbers your code printed; never retype or recalculate them; a metric cell holds the printed %, never a link to an amount. Sheets (skip one that would be empty):

1. `Income statement`: the columns from Step 4, with the key metrics under it.
2. `Balance sheet`: when built.
3. `Variances`: the flagged lines, direction, what the data shows, and the follow-up questions.
4. `Mapping`: every input account, its signed amount and the line you put it on, so the user can correct a mapping; any total there shows expenses as positive.
5. `Checks`: each check with its totals and PASS or FAIL.

Format amounts with thousands separators and negatives in parentheses (a currency symbol only if the data shows one), percentages to one decimal, bold subtotal rows, fitted column widths and a frozen header row. A percentage-point change is the difference of the two margins times 100, formatted like `0.0" pp"`. Under each statement add note lines for the assumptions and gaps that matter. After saving, read the file back in code and confirm every total and metric cell equals your printed numbers, fixing any mismatch. Publish it with `publish_artifact` (`kind: "document"`) named like `income-statement-2025-10.xlsx`. If the user wants the answer in chat only, skip the workbook. If it can't be built, say so; the reply still carries the full statements.

## Step 7: Write the reply

The reply carries the full result, starting at the headline with no tool narration. In this order:

1. A headline of two or three sentences: revenue, gross margin and net income for the period, and how they moved against each comparison.
2. The income statement table, then the key metrics table.
3. The balance sheet table, when built.
4. Checks, one line each with the totals, for example "Total assets 500,000 = liabilities 200,000 + equity 300,000: PASS". A failed check says FAIL and gives the difference.
5. Material variances as a table: `| Line | Var $ | Var % | Fav/Unfav | What the data shows | Action |`.
6. Assumptions and gaps: the mapping choices and anything the user didn't supply (no budget, no tax line, year to date versus month).
7. Two to four follow-up questions about variances you can't explain, then one line offering to drill into any line the user names.
8. The workbook's file name and sheets, then this line: "This is a working draft for review by a qualified accountant, not financial, accounting or audit advice."

Over about 40 account lines, group them in the reply; the workbook keeps every account.

## Rules

- Every figure comes from the user's data or from your code run on it. No estimates, benchmarks, industry averages, or invented prior-period or budget numbers.
- Commentary restates figures from your tables. No opinions such as "healthy" or "stable", and no claim you haven't checked against a printed number.
- Never estimate income tax. With no tax line, say net income is before tax. If the user asks for a tax rate or a rule that may have changed (a current accounting standard), check it with `web_search`, link the source and give the date.
- Don't book entries or change the user's books.
