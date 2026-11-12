---
name: DCF Valuation Model
description: >
  Estimates what a business or stock is worth with a DCF model: an Excel workbook with live formulas and a clear answer.
  Use it for "build a DCF", "what is this company worth", "fair value of this stock", "value my business", "calculate WACC", "sensitivity to discount rate and terminal growth".
---

# DCF Valuation Model

## Step 1: Take the inputs from the message

Note what the user gave in the message, a pasted table or an attached file: the company or business; currency and units; base-year revenue; growth by year; margins (EBITDA, EBIT or profit); tax rate; D&A, capex and working capital; the discount rate or the parts of WACC; terminal growth or an exit multiple; debt and cash; share count; current share price.

- Do not ask for what is missing: Step 2 fills it. Only when there is no company and no figures at all, ask once with `clarify` for the company or its revenue and profit. If the user has nothing, build an illustrative model on example figures and say so at the top of the reply.
- A named public company with no figures given: use `web_search` and `web_extract` to find the latest full-year revenue, operating income, D&A, capex, debt, cash, diluted shares and the share price, from the company's own filing or investor-relations page where you can. Record the fiscal year and URL of each. Never fill these from memory. If one cannot be found, assume it and mark it Assumed.
- If the user gives free cash flow directly, project it with the growth rates and skip the margin build.
- If the user gives a start and an end value ("growth 25% fading to 15%"), move in equal steps between them and show each year's value.
- If the user asks only for part of this (a WACC, or a sensitivity table on a cash flow they gave), build just that part.

## Step 2: Fill every gap with a stated assumption

For each input the user did not give, choose a value from this table and note the reason in a line.

| Input | Default when not given |
|---|---|
| Horizon | 5 years. Use 10 if year-5 growth would still be more than 3 points above terminal growth. Fade growth in equal steps so it ends near the terminal rate. |
| Growth and margins | Move from the base year toward a sustainable level, not a recent spike. |
| D&A and capex | Percent of revenue, from the base year if known. If the business still grows in the final year, capex is at least D&A. |
| Working capital | Percent of the change in revenue. State the percent (0% only with a reason). |
| Tax rate | The rate the user or the company's filings give. Otherwise an assumed rate for the country (if none is stated, take it from the currency and say so). |
| Terminal growth | At or below long-run nominal growth of the economy (2 to 3% is commonly used in developed markets), and always below the discount rate. |
| Terminal method | Gordon growth on the final-year free cash flow. If the user gave an exit multiple, use that as the method and show Gordon as the cross-check. |
| Debt, cash, shares | Public company: latest balance sheet and diluted shares, found and linked. Small private business with nothing given: no debt, no share count, so value the whole business and give no per-share figure. |
| Timing | Cash flows arrive at year end, and the valuation date is the end of the base year. Say so. |

**Discount rate.** If the user gave one, use it as given. Otherwise build WACC on its own sheet: cost of equity = risk-free rate + beta x equity risk premium; after-tax cost of debt = cost of debt x (1 - tax rate); weights from the market value of equity and debt. Look up the current 10-year government yield for the currency with `web_search`, quote it exactly as the source shows it, and link it. Find the beta online and link it, or assume 1.0. The equity risk premium is an assumption (4 to 6% is commonly quoted). A small private business has no beta: use risk-free + equity premium + a size and illiquidity premium, well above a listed company's rate. Give each piece its own row in the assumptions table with its own Basis.

Label every input with a Basis: **Given** (the user gave it), **Found** (a tool returned it: give the URL) or **Assumed** (your choice).

## Step 3: Calculate in Python first

Use `execute_code`, with all inputs in one dict so the workbook in Step 4 is built from the same figures.

```
Revenue(t) = Revenue(t-1) x (1 + growth(t))
EBIT       = EBITDA - D&A
Tax        = max(EBIT, 0) x tax rate
UFCF       = EBIT - Tax + D&A - Capex - change in working capital
DF(t)      = 1 / (1 + r)^t                      t = 1 ... N
Terminal value, Gordon   = UFCF(N) x (1 + g) / (r - g)
Terminal value, multiple = EBITDA(N) x multiple
Enterprise value = sum of UFCF(t) x DF(t) + terminal value x DF(N)
Equity value     = Enterprise value - net debt - minority interest and preferred (if any)
Value per share  = Equity value / shares
```

Net debt is debt minus cash. Subtract it once; never subtract net debt and then add cash back.

Run these checks and fix or flag anything that fails:
- r must be above g. If not, the Gordon formula is meaningless: change the inputs and say so.
- Terminal value as a share of enterprise value. Report it. Above about 75%, say the answer leans on the terminal assumptions.
- Cross-check the terminal value: Gordon TV / EBITDA(N) is its implied exit multiple. Flag an absurd result.
- If final-year free cash flow is negative or still ramping, the Gordon method fails: lengthen the horizon until cash flow is positive and steady, or use the exit multiple, and say so. For an early-stage or loss-making company say plainly that a DCF is a weak tool.
- If the user gave a share price, give the percent difference between the value per share and the price, as a fact about the model.
- Do not compare the result with market prices or call it typical or sensible unless you found and linked that benchmark this turn; outside a found band, say above or below.

Also compute the Step 4 sensitivity grid in Python, to show in the reply and to check the workbook.

## Step 4: Build the workbook with live formulas

Load the built-in `xlsx` skill with `skill_view` and follow it to write the file. Build these sheets in this order:

1. `Summary`: value per share (equity value if there is no share count), enterprise value, equity value, the value range, terminal value as a share of enterprise value, and a check block of TRUE/FALSE formulas (sensitivity centre equals the DCF result; discount rate above terminal growth). The range is the lowest and highest value in the centre 3 by 3 of the sensitivity grid. End with the not-advice line.
2. `Assumptions`: one row per input with label, value, unit, Basis (Given, Found with the URL, or Assumed) and a short note. Yearly inputs (growth, margins, D&A, capex, working capital) run across the years. Typed inputs in blue font, formulas in black. Put the currency and units at the top.
3. `DCF`: years across; one row per line of the Step 3 formulas from revenue to present value (with NOPAT, discount period and discount factor). Below: terminal value and its present value, enterprise value, net debt, equity value, shares, value per share, share price and difference, terminal value share, implied exit multiple. Every cell is a formula pointing at Assumptions.
4. `WACC`: only when you built the rate. The build-up and weights, ending in the rate that Assumptions points to.
5. `Sensitivity`: a 5 by 5 grid of value per share. Rows are discount rates, columns are terminal growth rates. The centre is the base case: rate steps of 1 point (2 points for a small private business) and growth steps of 0.5 point. Keep the step sizes as input cells on Assumptions and build the axes by formula. Fill every grid cell with a closed-form formula, not a pasted value and not a Data Table:

```
=IF(r<=g,"n/a",(SUMPRODUCT(UFCF_row/(1+r)^period_row)+UFCF_last*(1+g)/(r-g)/(1+r)^period_last-net_debt)/shares)
```

Here r is the row's rate cell and g the column's growth cell, and every other part is an absolute reference to the DCF or Assumptions sheet. With no share count, drop `/shares` and label the grid equity value. If the terminal value is by exit multiple, make the columns exit multiples and replace the growth term with `EBITDA_last*multiple/(1+r)^period_last`.

Rules for the workbook:
- No typed numbers inside formulas except 1. No error values (#DIV/0!, #REF!, #NAME?).
- For bear, base and bull cases: one Assumptions column per case for the inputs that differ, one DCF sheet per case, and a comparison on Summary.
- If the user asks for Google Sheets or Excel online and it is connected, save a copy there; otherwise deliver the .xlsx. Never ask the user to connect an app.

## Step 5: Verify, publish and reply

1. Recalculate and check the workbook the way the `xlsx` skill describes. Confirm its enterprise value, value per share and sensitivity centre match your Step 3 figures and that no cell shows an error. If they differ, fix the workbook, not the reply.
2. Publish it with `publish_artifact`, `kind: "document"`, with a file name that carries the company, such as `DCF-Harbor-Logistics.xlsx`.
3. Write the reply in this shape, with every figure taken from the Step 3 run:

```
## <Company or business>: DCF valuation

**Value per share: <amount>** (range <low> to <high>)   [equity value if there is no share count]
<One or two sentences: what that means against the share price if given, and the biggest driver. Name any multiple by its DCF-sheet label; TV / EBITDA(N) is the implied exit multiple, not EV / EBITDA.>

| Result (<currency and units>) | Amount |
|---|---|
| Present value of cash flows, years 1 to N | |
| Present value of terminal value (<x>% of enterprise value) | |
| Enterprise value | |
| Less: net debt | |
| Equity value | |
| Shares | |
| Value per share | |

### Assumptions
| Input | Value | Basis |
|---|---|---|
(every input with its Basis; Found rows give the full URL; plus a Timing row "Cash flows at year end; valuation date = end of base year" and every default you used, e.g. cash = 0, sensitivity steps, all Assumed. Never write that nothing was assumed.)

### Free cash flow
(years across, each line so columns add up: revenue, EBITDA, D&A, EBIT, tax, D&A back, capex, working capital, FCF, PV)

### Sensitivity: value per share
(the 5 by 5 grid printed from the Step 3 Python grid, axis labels included, never retyped; rate down, growth across; bold only the centre cell)

### Read before relying on this
(2 to 4 bullets: the terminal-value share, the assumption the value swings on most, the assumed inputs that matter most, any limit from Step 3. No what-if amount unless Python computed it this turn. Unless you searched for comparables, say the result was not checked against market prices or comparables.)

### Workbook
<file name> and its link, both written in the reply. Change the blue cells on Assumptions and everything recalculates. List only sheets that exist; no unchecked counts.

This is an estimate from the assumptions above, not investment advice.
```

For a small business, say first, in the assumptions, what you took the user's "profit" to mean (operating profit before tax, and whether the owner's pay is already deducted), because it moves the value more than anything else. Paste that exact note on Summary and in the bullets. If the owner's pay is not deducted, profit, and so the value, is overstated.

## Hard rules

- Never stop to wait for the user. Decide, say what you assumed, and deliver the full reply and the workbook.
- No figure for a named company from memory. A benchmark, market multiple or "typical" range appears only if a tool returned it this turn and you link it; otherwise leave it out. Anything not given or found is marked Assumed.
- The workbook holds formulas, not pasted results, and the reply's numbers equal the workbook's.
- Never say buy, sell or hold. End the reply and the Summary sheet with the not-advice line.
