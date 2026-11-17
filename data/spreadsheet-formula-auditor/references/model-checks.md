# Model integrity checks

Check the balance sheet first. If it does not balance, everything downstream is suspect.

## Structure

| Check | Look for |
|---|---|
| Input/formula separation | Inputs in their own cells or tab, not buried in formulas |
| Colour convention | Blue inputs, black formulas, green links (or whatever the model uses), applied consistently |
| Tab flow | Assumptions, then income statement, balance sheet, cash flow, valuation |
| Date headers | Same periods across all tabs |
| Units | Thousands, millions or actuals consistently |

## Balance sheet

- Total Assets = Total Liabilities + Equity in every period.
- Retained earnings roll-forward: prior RE + net income - dividends = current RE.
- Goodwill and intangibles flow from the acquisition assumptions (if M&A).
- When it fails: the gap per period, the first period where it appears, then the line item whose movement equals the gap (or twice the gap, which points to a sign error).

## Cash flow

- CF ending cash = BS cash, every period.
- CFO + CFI + CFF = change in cash.
- D&A on the cash flow = D&A on the income statement.
- CapEx on the cash flow matches the PP&E roll-forward.
- Working capital changes have the right sign against the balance sheet movement (an increase in receivables or inventory reduces cash; an increase in payables adds cash).

## Income statement

- Revenue ties to segment or product detail.
- Tax = pre-tax income x tax rate (allow for deferred tax).
- Share count ties to the dilution schedule.

## Circular references

- Interest to debt balance to cash to interest is a common intentional loop in LBO and three-statement models. If intentional, check an iteration toggle exists. If not, trace the loop and say how to break it.

## Reasonableness (flag as "worth confirming", never as fact)

- Revenue growth above 100% in a period.
- Margins that jump between adjacent periods.
- Terminal value above about 75% of DCF enterprise value.
- Out-year projections that ramp sharply (hockey stick).
- Model breaks at 0% or negative growth, negative EBITDA, or negative leverage.

## By model type

**DCF:** discount rate applied to the wrong period (mid-year vs end-of-year); terminal value not discounted back; WACC built from book values instead of market values; free cash flow that includes interest expense; tax shield counted twice.

**LBO:** debt paydown that does not follow the cash sweep; PIK interest not added to principal; management rollover missing from returns; exit multiple applied to the wrong EBITDA (LTM vs NTM); fees not deducted from day-one equity.

**Merger:** accretion/dilution using the wrong share count (pre- vs post-deal); synergies not phased in; purchase price allocation that does not balance; foregone interest on cash missing; transaction fees missing from sources and uses.

**Three-statement:** working capital changes with the wrong sign; depreciation not matching the PP&E schedule; debt maturities not matching principal payments; dividends above net income with no explanation.

Sign-convention errors (cash outflows positive in one place and negative in another) are very common: check them. Hardcoded overrides are the most common source of silent errors: search for them in every forecast row.
