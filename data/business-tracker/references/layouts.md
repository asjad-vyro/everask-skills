# Tracker layouts

## Common to all

- The entry sheet has the title in A1, a how-to line in A2, headers in row 4, data in rows 5 to 1004. Dropdown values live on `Lists`, one column per list (header in row 1, values from row 2). Use the user's own words for column headers, categories and statuses when they gave any; the names below are defaults, in English, to be written in the user's language.
- Column letters on `Lists` below are for one tracker. When two trackers share `Lists`, give the second tracker's lists the next free columns (for example C and D) and point its dropdowns and summary formulas at them.
- Formulas are written with English function names and commas between arguments, whatever the user's language (openpyxl stores them that way, and Excel shows them in its own language). Write sheet references in quotes, `'Sheet name'!$A$5`, so a translated name with spaces or accents still works.
- Every word a formula outputs or tests (`OK`, `CHECK`, `Reorder`, `No level set`, `Done`, `Paid`, `Overdue`, `Open`, the example marker) is written once, in the user's language, and must be identical everywhere it appears: the cell formula, the summary formulas, the conditional formats and `Lists`.
- Example rows (only when the user gave no rows) carry the marker `example, delete me` (translated) in one text column and nothing else: Sales and Expenses column C, Stock column B, Jobs column C, Invoices column J. They add nothing to any total or count.
- `Month` columns hold the first day of the month as a real date, formatted as month and year. Amount columns use the user's currency and decimals, not the `xlsx` skill's financial-model `$` format or colour coding.

## Summary sheet pattern (Sales log, Expense log)

Sheet `Summary` (or `Sales Summary` and `Expenses Summary` when there are two trackers). `E` below stands for the entry sheet's name, with its columns: date A, category B, amount D, payment method E.

- A2 "First month", B2:
  `=IF(COUNT('E'!$A$5:$A$1004)=0,"",MAX(DATE(YEAR(MIN('E'!$A$5:$A$1004)),MONTH(MIN('E'!$A$5:$A$1004)),1),EDATE(DATE(YEAR(MAX('E'!$A$5:$A$1004)),MONTH(MAX('E'!$A$5:$A$1004)),1),-11)))`
  This shows the 12 months ending with the month of the latest entry, or starting with the first entry when the data covers less than a year. Note in C2: "Type the first day of a month here to show other months. Older entries are in Earlier, newer ones in Later."
- Row 4: A4 "Category", B4 "Earlier", C4 `=B2`, D4 `=IF(C4="","",EDATE(C4,1))` copied right to N4 (twelve month columns, C to N), O4 "Later", P4 "Total".
- A5 to A24: the first 20 slots of the category list, `=IF(Lists!$A2="","",Lists!$A2)` down to `Lists!$A21`.
- B5 (Earlier): `=IF(OR($A5="",$C$4=""),0,SUMIFS('E'!$D$5:$D$1004,'E'!$B$5:$B$1004,$A5,'E'!$A$5:$A$1004,">0",'E'!$A$5:$A$1004,"<"&$C$4))`
- C5 (a month), copied right to N5: `=IF(OR($A5="",C$4=""),0,SUMIFS('E'!$D$5:$D$1004,'E'!$B$5:$B$1004,$A5,'E'!$A$5:$A$1004,">="&C$4,'E'!$A$5:$A$1004,"<"&EDATE(C$4,1)))`
- O5 (Later): `=IF(OR($A5="",$N$4=""),0,SUMIFS('E'!$D$5:$D$1004,'E'!$B$5:$B$1004,$A5,'E'!$A$5:$A$1004,">="&EDATE($N$4,1)))`
- P5: `=SUM(B5:O5)`. Copy row 5 down to row 24.
- Row 25 "Total": `=SUM(B5:B24)` copied right to P25. P25 is the grand total.
- Check: A27 "Total of entries", B27 `=SUM('E'!$D$5:$D$1004)`; A28 "Total in the table", B28 `=P25`; A29 "Check", B29 `=IF(ROUND(B27-B28,6)=0,"OK","CHECK")`. Note in C29: "CHECK means an entry with an amount but no date, or with a category that is not in the first 20 rows of Lists."
- Optional, A31 "Largest category", B31: `=IF(MAX(P5:P24)<=0,"",INDEX(A5:A24,MATCH(MAX(P5:P24),P5:P24,0)))`.
- "By payment method": heading in A33; A34 to A43 the first ten slots of the payment-method list (`=IF(Lists!$B2="","",Lists!$B2)` down to `Lists!$B11`); B34 `=IF($A34="",0,SUMIFS('E'!$D$5:$D$1004,'E'!$E$5:$E$1004,$A34))` copied down; B44 `=SUM(B34:B43)`; B45 `=IF(ROUND(B27-B44,6)=0,"OK","CHECK")` (an entry with no payment method shows `CHECK`).

Entry sheet conditional format for Sales and Expenses: light yellow fill on A5:G1004 where `=AND($D5<>"",OR($A5="",$B5=""))` (an amount with no date or category; such a row is why the check shows `CHECK`).

## Sales log

Entry sheet `Sales`. Columns:
- A Date (date validation)
- B Item or category (list: `Lists` column A)
- C Description (free text)
- D Amount (decimal >= 0)
- E Payment method (list: `Lists` column B; defaults Cash, Card, Bank transfer, Other)
- F Customer (free text, optional)
- G Month: `=IF(A5="","",DATE(YEAR(A5),MONTH(A5),1))`

Summary: the pattern above.

If the user wants quantity and unit price: insert Quantity and Unit price columns before Amount, make Amount `=IF(OR(<qty>5="",<price>5=""),"",<qty>5*<price>5)`, and move every amount, payment-method and conditional-format reference in the pattern to the new column letters.

## Expense log

Entry sheet `Expenses`. Columns:
- A Date (date validation)
- B Category (list: `Lists` column A; use the user's categories, otherwise: Rent, Supplies, Wages, Utilities, Marketing, Transport, Other)
- C Description
- D Amount (decimal >= 0)
- E Paid with (list: `Lists` column B; Cash, Card, Bank transfer, Other)
- F Supplier (free text, optional)
- G Month (formula as in Sales log)

Summary: the pattern above. If the user asked for a budget, compare it with one month, never with the 12-month total: Q2 "Budget month", R2 `=IF(COUNT('E'!$A$5:$A$1004)=0,"",DATE(YEAR(MAX('E'!$A$5:$A$1004)),MONTH(MAX('E'!$A$5:$A$1004)),1))` (the latest month; the user may type another first-of-month date); Q4 "Monthly budget", typed by the user, empty if not given; R4 "Left in budget month", R5 `=IF(OR($A5="",Q5="",$R$2=""),"",Q5-SUMIFS('E'!$D$5:$D$1004,'E'!$B$5:$B$1004,$A5,'E'!$A$5:$A$1004,">="&$R$2,'E'!$A$5:$A$1004,"<"&EDATE($R$2,1)))`, copied down to row 24.

## Inventory

Entry sheet `Stock`: one row per product, not per movement. Columns:
- A SKU or code (free text)
- B Product (free text)
- C Category (list: `Lists` column A)
- D Unit cost (decimal >= 0)
- E Quantity on hand (decimal >= 0; the user updates it)
- F Reorder level (decimal >= 0; the user's own threshold, left empty if not given)
- G Stock value: `=IF(OR(D5="",E5=""),"",D5*E5)`
- H Status: `=IF(OR(B5="",E5=""),"",IF(F5="","No level set",IF(E5<=F5,"Reorder","OK")))`
- I Supplier (free text)
- J Notes

Conditional format: rows whose Status is "Reorder" get a light red fill.

Summary sheet `Stock Summary`:
- Total products: `=COUNTA(Stock!$B$5:$B$1004)-COUNTIF(Stock!$B$5:$B$1004,"example, delete me")`.
- Total units `=SUM(Stock!$E$5:$E$1004)`, total stock value `=SUM(Stock!$G$5:$G$1004)`, products to reorder `=COUNTIF(Stock!$H$5:$H$1004,"Reorder")`.
- By category: categories from list A (20 slots, as in the pattern), then products `=COUNTIFS(Stock!$C$5:$C$1004,$A8)`, units `=SUMIFS(Stock!$E$5:$E$1004,Stock!$C$5:$C$1004,$A8)`, value `=SUMIFS(Stock!$G$5:$G$1004,Stock!$C$5:$C$1004,$A8)` (with the row of each category in place of 8), and a total row.
- Check: the by-category value total against total stock value, `OK` or `CHECK` (a product with no category shows `CHECK`).
- No monthly grid unless the user asked for a stock movement log. If asked, add a sheet `Movements` (Date, SKU, In or out as a list, Quantity, Note), add an Opening quantity column to `Stock`, and make Quantity on hand a formula: opening quantity plus `SUMIFS` of Movements quantity for that SKU and "In", minus the same for "Out".

## Client jobs

Entry sheet `Jobs`. Columns:
- A Date received (date validation)
- B Client (free text)
- C Job description
- D Status (list: `Lists` column A; defaults Quote, Booked, In progress, Done, Paid)
- E Due date (date validation, optional)
- F Quoted price (decimal >= 0)
- G Amount paid (decimal >= 0)
- H Balance: `=IF(F5="","",F5-G5)`
- I Overdue: `=IF(OR(E5="",D5="Done",D5="Paid"),"",IF(E5<TODAY(),"Overdue",""))`
- J Month: `=IF(A5="","",DATE(YEAR(A5),MONTH(A5),1))`

Conditional format: Overdue cells red.

Summary sheet `Jobs Summary`:
- Jobs per status: each status from list A with `=COUNTIF(Jobs!$D$5:$D$1004,$A5)`; jobs listed `=COUNTA(Jobs!$B$5:$B$1004)` (rows with a client); check: the status counts add up to jobs listed, `OK` or `CHECK` (a job with no status shows `CHECK`).
- Total quoted `=SUM(Jobs!$F$5:$F$1004)`, total paid `=SUM(Jobs!$G$5:$G$1004)`, total balance `=SUM(Jobs!$H$5:$H$1004)`, jobs overdue `=COUNTIF(Jobs!$I$5:$I$1004,"Overdue")`.
- Monthly table: the same First month cell, Earlier, twelve months and Later as the pattern, with date = column A, and three rows: jobs received (`COUNTIFS` on the date range), quoted (`SUMIFS` on F), paid (`SUMIFS` on G). Label the paid row as amounts paid on jobs received that month: the sheet has no payment dates.

## Invoices owed

Entry sheet `Invoices`. Columns:
- A Invoice number (free text, as the user gives it; never generated)
- B Client (list: `Lists` column A, client names; the user adds new clients there)
- C Invoice date (date validation)
- D Due date (date validation, typed). If the user gave payment terms in days, put the terms in a labelled input cell on `Lists` (for example B1 "Payment terms (days)" and B2 the number they gave) and make D `=IF(C5="","",C5+Lists!$B$2)`, with that cell's address.
- E Amount (decimal >= 0)
- F Amount received (decimal >= 0)
- G Balance: `=IF(E5="","",E5-F5)`
- H Status: `=IF(E5="","",IF(G5<=0,"Paid",IF(D5="","Open",IF(D5<TODAY(),"Overdue","Open"))))`
- I Days overdue: `=IF(H5="Overdue",TODAY()-D5,"")`, number format `0` (not a date format)
- J Notes

Conditional format: Overdue rows light red, Paid rows grey.

Summary sheet `Invoices Summary`:
- Total invoiced `=SUM(Invoices!$E$5:$E$1004)`, total received `=SUM(Invoices!$F$5:$F$1004)`, total outstanding `=SUMIFS(Invoices!$G$5:$G$1004,Invoices!$G$5:$G$1004,">0")`, credits (overpaid) `=SUMIFS(Invoices!$G$5:$G$1004,Invoices!$G$5:$G$1004,"<0")`, number open `=COUNTIF(Invoices!$H$5:$H$1004,"Open")`, number overdue `=COUNTIF(Invoices!$H$5:$H$1004,"Overdue")`.
- Outstanding by client: each client from list A with `=SUMIFS(Invoices!$G$5:$G$1004,Invoices!$B$5:$B$1004,$A<row>,Invoices!$G$5:$G$1004,">0")`, a total row, and a check of that total against total outstanding, `OK` or `CHECK` (an invoice whose client is not on `Lists` shows `CHECK`).
- Outstanding by age: not yet due or no due date `=SUMIFS(Invoices!$G$5:$G$1004,Invoices!$H$5:$H$1004,"Open")`; 1 to 30 days overdue `=SUMIFS(Invoices!$G$5:$G$1004,Invoices!$I$5:$I$1004,">=1",Invoices!$I$5:$I$1004,"<=30")`; 31 to 60 with `">=31"` and `"<=60"`; over 60 with `">60"`. Check: the four buckets add up to total outstanding, `OK` or `CHECK`.

Statuses, overdue flags and days overdue use `TODAY()`, so they change from day to day when the file is opened. That is by design and correct in Excel; say so in the reply, and give any overdue figure as of the day the check ran.
