---
name: Startup Financial Model
description: >
  Builds a 3-year startup financial model (monthly revenue, costs, burn, cash, runway, unit economics and conservative/base/optimistic scenarios) as an Excel workbook plus a summary in the reply.
  Use it for "build a financial model for my startup", "how many months of runway do I have", "model my seed raise", "project my MRR for 3 years".
---

# Startup Financial Model

A good result is a workbook whose every number traces to an assumption the user gave (or one you flagged as your own), plus a reply that shows the headline numbers, so the user does not need to open the file to get the answer. Not financial or investment advice.

## Step 1: Pin down the inputs

Take everything from the user's message and attachments. Never open with questions; decide, and list what you assumed. Do not call `clarify` unless there is no business description at all.

Collect: business type (SaaS by default; marketplace, e-commerce, services see `references/models.md`), price or ARPU, new customers per month and its growth, churn or a retention curve, starting cash, starting MRR and customers, monthly costs or headcount (salary, fully loaded), COGS %, any raise (amount, date, pre-money).

For each missing input pick a default, and record it in an Assumptions list marked "assumed". Read `references/models.md` for default ratios; call them "commonly quoted rules of thumb", not facts about this company. Never invent customers, traction, or market data. If the user gave 3 months of history, use it as the starting point.

## Step 2: Compute in code

Do all arithmetic in `execute_code` (pandas/numpy), never by hand. Monthly for 36 months. For each month:

- Customers: cohort method. Each month's new customers follow the retention curve (or a flat monthly churn: retained = new x (1 - churn)^age). Customers = sum over cohorts. If the user gave cohort sizes and retention, use exactly those.
- MRR = customers x ARPU (+ expansion MRR if given). ARR = MRR x 12.
- Revenue = MRR for the month (state if you ignore payment-term lag).
- COGS = COGS % x revenue. Gross profit.
- S&M, R&D, G&A: from headcount (fully loaded = salary x 1.3 to 1.4 unless told) plus non-people costs; paid acquisition spend = new customers x CAC if CAC is given.
- Net burn = total expenses - revenue (positive means cash is being used). Note: net burn is expenses minus revenue, not the reverse.
- Cash end = cash start + revenue - expenses + any funding. Funding lands in the month stated.
- Runway: months until cash end first goes below 0 (state "beyond month 36" if never). Quick runway = current cash / current monthly net burn; give both when they differ and say which is which.
- Metrics: MoM growth, CAC (S&M / new customers), LTV = ARPU x gross margin / monthly churn, LTV/CAC, CAC payback months = CAC / (ARPU x gross margin), burn multiple = net burn / net new ARR, headcount if modeled. If neither CAC nor S&M spend is given, pick a CAC default from `references/models.md`, mark it "assumed", and still compute LTV/CAC and payback from it, so no unit-economics line is left empty.
- Fundraising if asked: post-money = pre + raise; dilution = raise / post-money; use of funds table summing exactly to the raise; the funding need = raise needed so runway reaches the next milestone plus 6 months.

Roll up to annual totals (Year 1, 2, 3): revenue, gross profit, expenses, net burn, ending cash, ending MRR, ending customers.

Scenarios: run the same engine three times. Conservative: new customers -30%, churn +20% relative, ARPU -15%, CAC +25%. Base: the inputs. Optimistic: new customers +30%, churn -20%, ARPU +15%, CAC -25% (a user's own scenario definitions override these). Hold pricing structure and cost plan fixed. Show runway, month-36 MRR and cumulative burn per scenario.

If the user asks only a runway question with a few numbers, still do Step 2 for just that (a short projection) and answer directly; skip the workbook unless they asked for a model.

## Step 3: Sanity-check before writing

Check in code and fix or flag: cash never negative without being flagged; MRR equals customers x ARPU in every month; annual totals equal the sum of months; LTV/CAC and payback are plausible (commonly quoted targets: LTV/CAC above 3, payback under 12-18 months); growth rates are not absurd. If the user's own assumptions give an unrealistic result, deliver it anyway, and say plainly what looks aggressive.

## Step 4: Build the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it. Sheets: `Assumptions` (every input, with a Source column: "user" or "assumed"), `Monthly` (base case, all 36 months), `Annual` (one row per metric, columns Year 1 | Year 2 | Year 3; Year 1 sums Monthly months 1-12, Year 2 months 13-24, Year 3 months 25-36, each column pointing to its own range), `Scenarios` (three cases side by side), `Metrics`, and `Fundraising` only if a raise was given. Where the xlsx skill supports formulas, make the key rows live formulas off the Assumptions sheet; otherwise write the computed values. Before publishing, read the saved workbook back in `execute_code` (recalculate formulas, or recompute them from the referenced cells) and confirm: each Annual column references a different 12-month range and its values match the Year 1/2/3 totals from Step 2; the three Year columns are not identical; every figure you will put in the reply matches the workbook. Fix and re-save if anything differs.

Publish with `publish_artifact` (`kind: "document"`), file name like `startup-financial-model.xlsx`.

## Step 5: The reply

Put the answer in the reply itself. The first line of the reply is the headline; no preamble or process narration (no "I'll start by loading..."). In this order:

1. One-line headline: runway in months (and the month cash runs out), month-12 and month-36 MRR, and the funding gap if any.
2. **Annual summary** table (Year 1-3: ending MRR, ARR, revenue, expenses, net burn, ending cash, customers).
3. **Scenario table** (conservative, base, optimistic: runway, month-36 MRR, ending cash).
4. **Unit economics** (CAC, LTV, LTV/CAC, payback, burn multiple).
5. **Assumptions** list, each marked "from you" or "assumed".
6. **Watch-outs**: two or three plain observations (e.g. cash runs out in month N, so raise by month N-6; churn is the biggest lever). Any lever or comparison claim (e.g. "cutting churn beats adding X customers") must be checked by rerunning the engine in code for each option and quoting the resulting month-36 customers/MRR; if the numbers do not support the claim, drop or reverse it.
7. The link to the workbook, and the line: "This is a planning model, not financial advice."

All figures in the reply are copied from the code output, rounded consistently.

## Hard rules

- No invented figures: every number is from the user, from your code, or marked "assumed". No benchmark is stated as fact about the user's company; no sourced-sounding statistics.
- Do all sums in `execute_code` and copy results; never compute in your head. This includes every comparison or "biggest lever" claim.
- The reply opens with the headline line; no preamble.
- Do not wait for approval and do not ask questions in the middle; finish the whole job in one reply.
- Do not give investment, tax or valuation advice; for valuation requests give only the dilution arithmetic.
