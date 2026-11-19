---
name: Invoice and Quote Maker
description: >
  Makes a finished invoice, quotation or pro forma invoice as a PDF, with line items, discount, tax, totals and payment terms worked out correctly.
  Use it for "make an invoice", "create a quote for my client", "pro forma invoice", "bill a client for 20 hours", "price quotation with VAT", "invoice in euros".
  Not for payment reminder emails or for proposals that describe a scope of work.
---

# Invoice and Quote Maker

A good result is a document that can be sent as it is: every figure adds up, nothing is invented, and anything the user did not give is a clearly marked blank. The same steps cover an invoice, a quotation (quote, estimate) and a pro forma invoice.

## Hard rules

- **Language**: write the document and the reply in the language the user wrote in, unless they ask for another. Keep their names, figures, item wording and terms exactly as given. Use the currency they name, in the number format that language uses. If no currency is named, write the amounts as plain numbers and use the placeholder `[currency]`.
- **Never invent facts.** No invoice or quote number, tax or VAT ID, bank details, addresses, dates, rates, prices or client names the user did not give. Use a bracketed placeholder in the document's language, such as `[invoice number]`, `[your tax ID]`, `[IBAN]`, `[issue date]`. Do not use today's date as the issue date unless the user asks for it. List every placeholder in the reply.
- **Tax**: apply only the tax name and rate the user gave. If none was given, issue the document with no tax line, and say in the reply that no tax was applied because none was given. Never guess a country's rate or whether tax is due; never copy a rate from memory.
- **All arithmetic is done in `execute_code`** (Step 2). Never add or multiply in your head. The reply and the file show the same numbers.
- **No deception.** Use the issue date the user gives; a date in the past is not wrong in itself (they may be recording an invoice they issued then). But if the user asks for a date earlier than the real issue date ("backdate it", "date it last year so it goes in last year's accounts"), do not use that date: say in one line that you can't backdate, and leave `[issue date]` for the day it is really issued. Do not make an invoice or receipt for a sale, work or payment the user says did not happen (for example to support an expense claim, a loan or a visa application), and do not mark an invoice "paid" when they say it was not. Do not alter or reissue another company's invoice, or copy someone else's letterhead or identity. The rest of a legitimate request is still done in full.
- **Do not open with questions.** Decide, state assumptions in one or two lines, and deliver the document in this turn. Use `clarify` only if there are no items or amounts at all.
- Nothing is sent anywhere. The document is a draft for the user to send.
- Add one plain line: this is not tax or legal advice, and invoice rules vary by country, so check local requirements.

## Step 1: Read the request

From the message and any attachment (a timesheet, price list or earlier quote), note:

1. **Document type**: invoice (default), quotation, or pro forma. Title it that way, in the user's language.
2. **Seller**: name, address, contact, tax ID, bank details (each only if given).
3. **Client**: name, address, contact, PO or reference number if given.
4. **Line items**: description, quantity, unit, unit price. If the user gives only a total for an item, quantity is 1.
5. **Discount**: a percentage or fixed amount, and which lines it applies to ("on the hours only" means only those lines). If it is not stated which lines, apply it to all lines and say so.
6. **Tax**: name and rate, and whether it applies to all lines or only some. If the user says prices already include tax, work back from the gross amount (Step 2).
7. **Dates**: issue date and terms. "Net 30" means due 30 days after the issue date. Compute the due date only if the issue date was given; otherwise write it in words in the document's language, such as "30 days after the issue date". For a quotation, use the validity period the user gave, else `[valid until]`.
8. **Payment details and notes**: how to pay, late-fee wording, deposit or amount already paid (reduce the amount due by it).

## Step 2: Calculate in code

Run one `execute_code` call using `Decimal`. Method:

1. Line total = quantity x unit price, rounded per line with `ROUND_HALF_UP` to the currency's minor unit: 2 decimals for most currencies, 0 for currencies such as the Japanese yen or Korean won, 3 for the Kuwaiti, Bahraini or Omani dinar. With no currency named, use 2 decimals. Use the same number of decimals for every figure below.
2. Subtotal = sum of the rounded line totals.
3. Discount: a percentage is taken on the lines it applies to and rounded; show it as a negative line. Apply it before tax.
4. Taxable amount per rate = the lines the rate applies to, less their share of the discount. If several rates are used, work out each rate separately and show one tax line per rate. Split a fixed-amount discount across rates in proportion to their line totals, so the parts add up to the discount exactly.
5. Tax = taxable amount x rate, rounded per rate.
6. Total = subtotal - discount + tax. Amount due = total - any deposit or amount already paid.
7. Tax-inclusive prices: net = gross / (1 + rate), rounded; tax = gross - net.
8. Due date: with `datetime.date` plus `timedelta`, only when an issue date was given.
9. Print every figure, then check that the line totals add to the subtotal and that subtotal - discount + tax equals the total.

Copy the printed results into the document unchanged.

## Step 3: Build the document

Layout, top to bottom:

1. Title (Invoice, Quotation or Pro Forma Invoice, in the document's language) with number, issue date and due date (or validity date for a quote).
2. Seller block and client block.
3. Items table: description, quantity, unit price, line total.
4. Totals block: subtotal, discount (if any), tax line per rate (if any), total, amount due (if different from total).
5. Payment terms and payment details (only what was given; placeholders for the rest).
6. Notes: late-fee wording or deposit wording only if the user gave it. For a quotation, the validity period and one line, in the document's language, saying it is a quotation and not a request for payment.
7. If the user said the buyer handles the tax (reverse charge) or that the sale is tax-exempt, print the wording the user gave and no tax line. Do not add legal wording of your own.

Format: invoices are sent as PDF, so unless the user names another format, load the built-in `pdf` skill with `skill_view` and follow it, including its delivery step, to build the PDF; it has an invoice blueprint (`doc:invoice`) to start from. If the user asks for Word, load the built-in `docx` skill; for a spreadsheet, load the built-in `xlsx` skill (use real formulas for totals there, with `ROUND` per line so they give the same figures as Step 2). Each built-in delivers the file with its own delivery step: follow it and do not add a `publish_artifact` call of your own. Give the file a meaningful name, such as `invoice-<client>.pdf`. Leave placeholders visibly marked in the file so the user can fill them.

If the user explicitly asks for plain text or markdown, skip the file and put the full document in the reply.

## Step 4: Reply shape

All in the user's language:

1. One line: document type, file format and language chosen, plus assumptions (discount lines, tax not applied, currency).
2. The totals, copied from the code: subtotal, discount, tax per rate, total, amount due, and the due date when computed.
3. A line meaning "Placeholders to fill in", followed by the list, or "none".
4. The not-advice line from the hard rules.

The user can ask for changes (another item, a different rate); redo Step 2 completely and rebuild the file.

## Optional sources

If the user asks you to take the client's details, the items or the prices from QuickBooks, Stripe or a Google Sheet, and that app is connected, read them from there. Do not create, finalise or send an invoice inside those apps. Otherwise work from what the user gave you.
