# Balance sheet and cash flow reference

Presentation rules below are a summary, not the standard. When the user needs a precise or current answer (a standard's wording, an effective date), check it with `web_search` and link what you find.

## Build the balance sheet from a trial balance

1. Use the signed amounts from Step 2 (debit minus credit). Assets come out positive; liabilities and equity come out negative, so flip them for presentation.
2. Current assets and liabilities are those expected to be realized, used or settled within 12 months (or the operating cycle if longer). Use the user's grouping and the account names. If a due date or lease term isn't in the data, treat a loan or lease as non-current only when its name says long-term, and list that under assumptions. Debt falling due within 12 months moves to current.
3. Net contra accounts against their asset: receivables net of the allowance for credit losses; property and equipment net of accumulated depreciation.
4. Equity lines: common stock, additional paid-in capital, retained earnings (accumulated deficit when negative), accumulated other comprehensive income, treasury stock, owner distributions or dividends.
5. In a trial balance taken before closing, retained earnings is still the opening balance. Show it as opening retained earnings plus a line for the period's net income, or as one closing figure with the roll-forward in the checks. Skip this when the trial balance already has a current-year earnings line, or the income and expense accounts are all zero (it was closed: say so).
6. Date the statement "as of" the period end.

## Balance sheet layout

```
ASSETS
Current assets: cash and cash equivalents; short-term investments; accounts receivable, net; inventory; prepaid expenses and other current assets
Total current assets
Non-current assets: property and equipment, net; operating lease right-of-use assets; goodwill; intangible assets, net; long-term investments; other non-current assets
Total non-current assets
TOTAL ASSETS

LIABILITIES AND STOCKHOLDERS' EQUITY
Current liabilities: accounts payable; accrued liabilities; deferred revenue, current portion; current portion of long-term debt; operating lease liabilities, current portion; other current liabilities
Total current liabilities
Non-current liabilities: long-term debt; deferred revenue, non-current; operating lease liabilities, non-current; other non-current liabilities
Total non-current liabilities
Total liabilities
Stockholders' equity: common stock; additional paid-in capital; retained earnings (accumulated deficit); accumulated other comprehensive income (loss); treasury stock
Total stockholders' equity
TOTAL LIABILITIES AND STOCKHOLDERS' EQUITY
```

Use only the lines the data has. For an owner-run business, call the equity section "Owner's equity" and show owner contributions and draws instead of stock lines. Present as a two-column table (line, amount) with a bold row for every section heading, subtotal and total (Assets, Current assets, Liabilities, Equity and so on), and a prior-period column only when the user supplied that balance sheet.

## Build the cash flow statement (indirect method)

Only when the user supplies balance sheets for both ends of the period and the net income, or a ledger that gives both. Otherwise say what is missing; never estimate.

1. Start with net income for the period.
2. Add back non-cash items that are in the data: depreciation and amortization, stock-based compensation, impairments, losses (gains) on disposals, amortization of debt issuance costs, deferred income taxes.
3. Changes in operating assets and liabilities, from the two balance sheets: an increase in an operating asset (receivables, inventory, prepaids) reduces cash; an increase in an operating liability (payables, accruals, deferred revenue) raises it.
4. Investing: purchases of property and equipment and of investments, proceeds from sales or maturities, acquisitions net of cash acquired.
5. Financing: debt issued or repaid, stock issued or repurchased, dividends, debt issuance costs.
6. Check in code: operating + investing + financing (+ effect of exchange rates) = closing cash minus opening cash on the balance sheets. If it doesn't tie, show the difference; never plug.

```
CASH FLOWS FROM OPERATING ACTIVITIES
Net income (loss)
Adjustments: depreciation and amortization; stock-based compensation; amortization of debt issuance costs; deferred income taxes; loss (gain) on disposal of assets; impairment charges; other non-cash items
Changes in operating assets and liabilities: accounts receivable; inventory; prepaid expenses and other assets; accounts payable; accrued liabilities; deferred revenue; other liabilities
Net cash provided by (used in) operating activities
CASH FLOWS FROM INVESTING ACTIVITIES
Purchases of property and equipment; purchases of investments; proceeds from sale or maturity of investments; acquisitions, net of cash acquired; other
Net cash provided by (used in) investing activities
CASH FLOWS FROM FINANCING ACTIVITIES
Proceeds from issuance of debt; repayment of debt; proceeds from issuance of common stock; repurchases of common stock; dividends paid; payment of debt issuance costs; other
Net cash provided by (used in) financing activities
Effect of exchange rate changes on cash
Net increase (decrease) in cash and cash equivalents
Cash and cash equivalents, beginning of period
Cash and cash equivalents, end of period
```

## Presentation requirements (US GAAP and IFRS)

### Income statement (ASC 220; IAS 1)

- Present all items of income and expense recognized in the period.
- Classify expenses by nature (materials, labor, depreciation) or by function (cost of revenue, R&D, sales and marketing, G&A). Function is more common for US companies.
- Under IFRS, when expenses are shown by function, depreciation, amortization and employee benefit costs are disclosed by nature in the notes. US GAAP rules differ and are changing; check the current standard.
- Present operating and non-operating items separately, and income tax expense as its own line.
- Extraordinary items are prohibited under both US GAAP and IFRS. Discontinued operations are shown separately, net of tax.
- IAS 1 is being replaced by IFRS 18; for an IFRS reporter, check which applies to the period.
- Revenue disaggregation (ASC 606): categories that show how the nature, amount, timing and uncertainty of revenue are affected by economic factors.
- Stock-based compensation sits within the functional expense lines, with the total disclosed in the notes.
- Restructuring charges: a separate line if material, or inside operating expenses with a note.
- Non-GAAP measures (common in earnings releases) are clearly labeled and reconciled to GAAP.

### Balance sheet (ASC 210; IAS 1)

- Distinguish current from non-current assets and liabilities.
- Present assets in order of liquidity, most liquid first (standard US practice).
- Receivables are shown net of the allowance for credit losses (ASC 326). Property and equipment are shown net of accumulated depreciation.
- Goodwill is generally not amortized; it is tested for impairment at least annually (ASC 350). Private companies may elect to amortize it.
- Leases: right-of-use assets and lease liabilities for operating and finance leases (ASC 842), with a short-term lease exemption.

### Cash flow statement (ASC 230; IAS 7)

- The indirect method (start from net income, adjust for non-cash items) is most common. The direct method is allowed but rare, and needs a supplemental indirect reconciliation.
- Interest paid and income taxes paid are disclosed, on the face or in the notes.
- Non-cash investing and financing activities (assets acquired under leases, stock issued for acquisitions) are disclosed separately.
- Cash equivalents are short-term, highly liquid investments with original maturities of three months or less.
