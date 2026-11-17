---
name: Break-Even Analysis
description: >
  Finds your break-even revenue and units from fixed and variable costs, with margin of safety and what-if checks.
  Use it for "what's my break-even", "how many units do I need to sell", "break-even for my cafe", "what if my rent goes up".
---

# Break-Even Analysis

A good result is a short, correct break-even table in the reply: the revenue (and units, if a price is known) at which revenue equals total costs, how far current sales sit above it, and how that moves when costs change. Everything comes from the figures the user gave. The reply holds the full analysis; do not build a file unless the user asks for one.

## Step 1: Collect the inputs from the message

Pull these out of the user's message, pasted text or attached file:
- Fixed costs per period (rent, salaries, insurance, software, loan payments). Keep each line item.
- Variable costs: either a ratio of revenue (e.g. 35% COGS) or a cost per unit.
- Selling price per unit or average sale, if given.
- Current revenue or units sold for the same period, if given.

Rules:
- Never invent a figure. Anything missing is written "not given", and any figure you assume is labelled "assumption" in the reply.
- Do not open with questions. If the fixed costs or the variable costs are entirely missing, use `clarify` once; otherwise decide, state the assumption, and deliver.
- Keep one period throughout (monthly unless the user says otherwise). Convert annual or weekly figures and say so.
- If the user gave a bank export or transactions, classify each expense: fixed = costs that stay the same regardless of volume (rent, salaries, insurance, subscriptions, loan payments); variable = costs that scale with sales (materials, shipping, payment fees, commissions, packaging). Show the classification you used. Semi-variable costs (e.g. electricity) go to whichever part dominates, and you say so.

## Step 2: Calculate in code

Do every sum in `execute_code` (Python) and copy the results into the reply. No mental maths. Compute:

- Total Fixed Costs = sum of fixed line items.
- If variable cost is per unit: Contribution per Unit = Price - Variable Cost per Unit; Contribution Margin Ratio = Contribution per Unit / Price.
- If variable cost is a ratio: Variable Cost Ratio = Variable Costs / Revenue (or the given %); Contribution Margin Ratio = 1 - Variable Cost Ratio.
- Break-Even Revenue = Total Fixed Costs / Contribution Margin Ratio.
- Break-Even Units = Total Fixed Costs / Contribution per Unit (or Break-Even Revenue / Price). Always round units UP to the next whole unit, because selling a fraction of a unit does not reach break-even. Show the unrounded figure too.
- Margin of Safety % = (Current Revenue - Break-Even Revenue) / Current Revenue x 100, only if current revenue is given. If current revenue is below break-even, say it is a shortfall, and show the gap in revenue.
- Daily or weekly equivalent if it helps the user (e.g. units per day over the days they said they trade). Only use trading days the user gave.

If the contribution margin is zero or negative, there is no break-even: say so, and show what would have to change (price up or variable cost down).

## Step 3: Sensitivity

Recompute in the same code run, and show a small table:
- Fixed costs +10%.
- Variable costs +5% (increase the variable ratio or per-unit cost by 5% of itself).
- Price +5% if a price was given.
- Any scenario the user asked for (e.g. "what if my rent goes up").

For each, show the new break-even revenue, new break-even units, and the change against the base case. If the user asked only a what-if, still show the base case first.

## Step 4: Write the reply

Use this shape, with the user's own figures and labels. Do not copy any numbers from this template.

```
BREAK-EVEN ANALYSIS - <period>

Fixed costs (per <period>)
  <item>                    <amount>
  Total fixed               <total>

Variable cost                <ratio or per-unit figure>
Contribution margin          <ratio> (<per unit, if price given>)

BREAK-EVEN REVENUE           <amount> per <period>
BREAK-EVEN UNITS             <whole units, rounded up> at <price> (unrounded: <x.xx>)

Current revenue              <amount, or "not given">
Margin of safety             <% and amount, or "not calculated: no current revenue given">

What-if
  Scenario | Break-even revenue | Break-even units | Change
```

Then, in two to four sentences:
- What it means in plain words (e.g. how many units or how much revenue per period just covers costs).
- Which lever moves break-even most in the sensitivity table.
- The assumptions you made, each named.

## Notes to include when they apply

- Semi-variable costs: assign to the dominant side or split them.
- Break-even assumes a constant product mix. With several products at different margins, use a weighted-average contribution margin (weight by the share of sales the user gave; if no mix was given, say you assumed one price).
- Service businesses with fixed labour: break-even is roughly Fixed Costs / Hourly Rate = hours needed per period.
- Tax, loan principal and owner pay may or may not be in the fixed costs; if the user did not say, note it.
- Revisit quarterly, since fixed costs creep up.

This is a planning calculation based on the figures given, not financial advice.
