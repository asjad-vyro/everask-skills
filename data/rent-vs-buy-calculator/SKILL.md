---
name: Rent vs Buy Calculator
description: >
  Works out whether renting or buying comes out ahead: a year-by-year comparison table and the breakeven year, with every assumption listed.
  Use it for "should I rent or buy?", "when does buying break even?", "run the rent vs buy numbers", "compare net position after 7 years".
---

# Rent vs Buy Calculator

Most rent-vs-buy arguments compare different things: one side counts equity and forgets transaction costs and upkeep, the other calls rent "thrown away" and forgets the renter can invest the difference. This skill runs a fair model, where both paths pay their real costs and both compound, and answers with a breakeven horizon ("buying wins if you stay past year N") rather than a universal verdict.

A good result is one reply with the table, the breakeven year, a comparison with how long the user plans to stay, a sensitivity check and the assumption list. Never open with questions: use the user's numbers, fill the gaps with labeled defaults, and go.

## Step 1: Collect the inputs

From the message, take: home price, comparable monthly rent (same kind of home, same area), down payment %, mortgage rate, term, expected years of stay, and growth assumptions. Defaults for anything not given, each labeled "default" in the reply:

- down payment 20%, rate 6.5%, term 30 years
- home appreciation 3%/yr, rent growth 3%/yr, renter's investment return 5%/yr
- carry costs (property tax, insurance, maintenance) 2% of home value/yr
- buying costs 3%, selling costs 7%
- model horizon 15 years

If the user gave no price or no rent, and gave no way to infer them, ask once with `clarify`. If they only said a city, use `web_search` (at most two searches) for a typical price and rent for a comparable home there, link the sources, and mark the figures as estimates. These defaults are generic assumptions, not facts about the user's market, so say so.

Mortgage rates and local prices change: if the user gave none, say the rate is a placeholder and they should check a current quote.

## Step 2: Run the model

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `rent_vs_buy.py` under `~/.computer/skills` with `search_files`.

Run with `terminal`:

```
python3 SKILL_DIR/scripts/rent_vs_buy.py --price <price> --rent <rent> --down <pct> --rate <pct> --term <years> --appreciation <pct> --rent-growth <pct> --invest-return <pct> --horizon <years>
```

Pass only the flags the user changed or you need to set; the others use the defaults above. Add `--json` if you want to process the rows. Run it again for the sensitivity check (Step 3). Do all arithmetic in the script or in `execute_code`, never in your head, and copy the numbers from the output.

How the model works: the renter's pot starts at the buyer's down payment plus buying costs, and each year absorbs the difference between the owner's outflow (mortgage plus carry costs) and the rent. The owner's net position is the home value minus selling costs minus the loan balance. Taxes and deductions are not modeled.

## Step 3: Sensitivity

Run the script at least twice more: appreciation one point lower and one point higher than the base case (or investment return varied, if the user cares about that). Record the breakeven year for each. If a run says "not within horizon", say so rather than inventing a year. If the user gave a stay length longer than the horizon, raise `--horizon` to cover it.

## Step 4: Write the reply

Put the whole answer in the reply, in this shape (the `<...>` are values you fill from the script output and the user's input, never invent them):

```
# Rent vs Buy: <price> home vs <rent>/month rent

## Assumptions
<table or list of every input; mark each as "given" or "default">
Renter invests the difference: <state that the renter's savings are invested at the return above>.

## Year-by-year
<table: year, owner net, renter net, edge; show years 1, 3, 5, 7, 10 and the final year, plus the breakeven year and the year matching the user's planned stay>

## Breakeven
<breakeven year, or "not within <N> years">. Before it renting won, after it buying won, on these assumptions.

## What it means for you
<Two or three sentences comparing the breakeven with the stay the user stated (or say "stay length not given" and show both sides). Name the assumption the result depends on most.>

## Sensitivity
<appreciation -1 and +1 points (or other variation): breakeven year for each>

## Not modeled
Taxes and deductions (they depend on where you live) · repair and renovation surprises · refinancing · moving or job changes · non-financial value such as stability, flexibility and the yard, which can reasonably outvote the math.

Educational model, not financial or professional advice. Check the figures with a licensed professional before acting.
```

## Hard rules

- State plainly that the renter is assumed to invest the difference. If the user would spend it instead, buying looks better by forced saving: that is a behavior question, not a math one. Say so in one sentence.
- Selling costs are inside the owner's net position at every year.
- Deliver a breakeven horizon, not a universal winner. Do not call rent "thrown away" without counting the owner's interest, tax and upkeep the same way.
- Compare like with like. If the rent and the purchase are different kinds of home (a one-bedroom rent against a three-bedroom purchase), say the comparison is skewed.
- Do not model tax benefits; list them under "Not modeled".
- Every number is from the user, the script output or a linked search result. Defaults are marked as defaults. Do not invent local prices, rates or market trends.
- If the numbers contradict what the user said they want (for example they say they will move in three years and the breakeven is year 9), state that tension plainly.
