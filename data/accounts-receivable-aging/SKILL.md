---
name: Receivables Aging Report
description: >
  Turns a list of unpaid invoices into an accounts receivable aging report: totals by client and by age bucket (not yet due, 1-30, 31-60, 61-90, 90+ days past due), the clients to chase first, and weighted average days overdue.
  Use it for "make an AR aging report", "which clients are more than 60 days overdue", "who owes me money", "receivables aging by client".
---

# Receivables Aging Report

A good result is a correct aging table the user can paste into a month-end pack, with the numbers computed by code, the assumptions stated, and a short list of who to chase and in what order. It finishes in one reply from what the user gave. It is general information, not accounting, credit or legal advice.

## Step 1: Get the invoices and the as-of date

- Take the invoices from the message, pasted text, or an attached CSV/XLSX. Needed per invoice: client, invoice number (if any), amount, due date. Also use invoice date, amount paid and paid date when present.
- As-of date: the one the user states. If none, use today's date from the sandbox (`date`) and say so.
- If a due date is missing but an invoice date and payment terms (e.g. Net 30) are given, due = invoice date + terms. If neither exists for a row, leave the row out of the buckets, list it under "Could not age", and carry on. Do not guess dates.
- Do not use any invoicing or accounting app unless the user asks and it is connected. Work from what they gave you.

## Step 2: Compute in code

Use `execute_code` (Python with pandas). Never add up or bucket by hand. Rules:

1. Outstanding = amount minus amount paid. If a payment total is given, use it; a row with a paid date and no paid amount is fully paid. Drop rows with outstanding <= 0 and list them as "Settled, excluded".
2. Days past due = as-of date minus due date (whole days).
3. Buckets, based on days past due: `Not yet due` (<= 0), `1-30`, `31-60`, `61-90`, `90+` (91 and over). A due date equal to the as-of date is not yet due.
4. Totals by client x bucket, column totals, and each bucket's % of total outstanding (one decimal).
5. Weighted average days past due = sum(outstanding x days past due) over invoices that are past due, divided by their outstanding total. Also report the share of outstanding that is past due.
6. Check before writing: the bucket totals, the client totals and the grand total must all agree, and the grand total must equal the sum of outstanding. Fix the code if not.
7. Credit notes or negative amounts: net them against the same client's outstanding and say so.

Print the result tables from the code and copy the figures into the reply exactly.

## Step 3: Write the reply

The report goes in the reply itself, in this order:

1. **Headline**: one sentence, e.g. total outstanding, amount and % past due, amount in 90+, as-of date, currency.
2. **Aging by client** table: one row per client sorted by total outstanding (largest first), columns Not yet due, 1-30, 31-60, 61-90, 90+, Total, then a TOTAL row and a % of total row.
3. **Invoice detail for anything past 60 days**: invoice number, client, outstanding, due date, days past due.
4. **Watch list**: clients with anything in 61-90 or 90+, or with several overdue invoices. Say what the data shows (amounts, days). Do not call a client "chronically late" without more than one overdue invoice or a payment history to point to.
5. **Suggested follow-up** by bucket: 1-30 a friendly reminder; 31-60 a firmer reminder and a call; 61-90 escalate to a senior contact and pause new credit or work; 90+ a final demand and a decision on collections or a bad-debt provision. These are common practice; the user decides. Offer to draft the reminder emails; draft them only if asked, and never send anything.
6. **Assumptions and gaps**: as-of date used, how due dates were set, rows excluded or not aged, partial payments applied, currency.

If the user wants a file, load the built-in `xlsx` skill with `skill_view`, build a workbook with the by-client table and the invoice list, and publish it with `publish_artifact` (`kind: "document"`). Still put the main table in the reply.

## Hard rules

- Use only amounts, dates and names the user gave. Never invent invoices, clients, payment history, interest or late fees. Do not compute interest unless the user gives a rate.
- Every number comes from the code output, not from memory or mental arithmetic.
- If the user asks for invoice-date aging instead of past-due aging, use that basis and say so in the headline.
- Do not stop to ask questions: state your assumptions and deliver the full report.
