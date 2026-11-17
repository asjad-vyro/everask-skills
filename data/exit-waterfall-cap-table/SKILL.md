---
name: Exit Waterfall and Cap Table Payouts
description: >
  Works out who gets what at each exit price from a cap table: a payout table per stakeholder, who converts, and the exit price below which common gets nothing.
  Use it for "model an exit waterfall", "what do I get if we sell for X", "explain liquidation preferences on my cap table", "compare payouts across exit prices".
---

# Exit Waterfall and Cap Table Payouts

A cap table lists percentages; an exit waterfall shows the money. Liquidation preferences, participation and option strikes make payouts differ from ownership percentages. A good result is a payout table the user can re-check, plus plain sentences saying what the structure means for each party. The whole job is done in one reply, from what the user gave.

## Step 1: Build the cap table

Read the user's message and any attached file. For each class note: name, shares, type (`common`, `preferred`, `options`); for preferred also amount invested, preference multiple (default 1) and participating or not (default non-participating); for options the strike.

- If the user gives percentages and no share counts, assume 10,000,000 fully diluted shares and set each class's shares to its percentage of that. Say so.
- If percentages add to less than 100%, say what you assumed the rest is (default: more common stock, same holders as "Other common") and name it as an assumption.
- If no exit prices are given, test five prices: half, 1x, 2x, 4x and 10x the latest post-money valuation (invested divided by ownership of the latest round), labelled as a default. If that cannot be worked out, use five round numbers that bracket the total preferences.
- Anything missing that has a standard default (1x, non-participating, no options) gets that default, stated as an assumption. Never invent an amount, date, name or share count the user did not give. Write "not given" instead.

## Step 2: Run the script

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `exit_waterfall.py` under `~/.computer/skills` with `search_files`.

1. Write the cap table to `/tmp/.scratch/exit-waterfall-cap-table/cap.json` with `write_file`:
   `{"classes": [{"name": "...", "shares": 0, "type": "common"}, {"name": "...", "shares": 0, "type": "preferred", "invested": 0, "pref_multiple": 1, "participating": false}, {"name": "...", "shares": 0, "type": "options", "strike": 0}], "exits": [0, 0]}`
   (the zeros are placeholders; fill in the user's figures).
2. Run `python3 SKILL_DIR/scripts/exit_waterfall.py /tmp/.scratch/exit-waterfall-cap-table/cap.json` with `terminal`. Add `--json` for machine-readable output, or `--exit <value>` to test one more price.
3. Check that every row's payouts sum to the exit value (options are net of strike, so a small gap there is expected). If a row is off, find the cause before replying.

The script finds who converts at each price: a non-participating preferred class takes the larger of its preference and its as-converted share. Participating preferred takes its preference plus its pro-rata share of what is left. Options exercise only when common's value per share exceeds the strike. Preferences are pari passu (no seniority) and participation is uncapped. If the script fails (for example, more than one common class: option exercise looks only at the first), compute the same table in `execute_code` and say so.

## Step 3: Find the cliff points

Do all sums in `execute_code` or the script, never in your head.

- **Zero-for-common price**: the total of all preferences (invested times multiple, summed over classes that do not convert). Below it, common gets nothing.
- **Conversion price** for each non-participating class: the exit at which its as-converted share equals its preference. For a class with fraction f of the shares that convert alongside common, it is roughly preference divided by f when no other class is still holding its preference. Confirm it by running the script at prices just below and just above it.
- **Option money price**: where per-share common value passes the strike.

## Step 4: Reply with this shape

The reply itself holds all of it, in full.

# Exit Waterfall: <company, or "your company" if not given>

## Cap table used
A short table of classes, shares, type, preference terms, with each assumption marked "(assumed)".

## Payout table
Rows are exit prices, columns are stakeholders, plus a "converts" column naming the classes that convert. Add a second small table of each stakeholder's share of proceeds against its ownership percentage.

## What this means
- **Below <zero-for-common price>:** who gets paid and that common gets nothing.
- **At <conversion price>:** which class converts and what changes.
- **The sentence:** "Your <n>% is worth <n>% only above <price>; below <price> it is worth <amount>." Use the user's real figures from the run.
- If the user named a deal price or range, give a sentence for that price specifically.

## Assumptions and limits
List every simplification against the real documents: pari passu preferences (seniority stacking would usually be worse for later common), uncapped participation (a cap would reduce the preferred's take), no accrued dividends, no transaction fees, escrow or management carve-outs, no later dilution, options valued by the treasury method, and any default you assumed.

*Educational model, not financial, legal or tax advice. Check it against the actual documents and a qualified adviser before acting on it.*

## Hard rules

- Every figure in the reply comes from the user or from the script or `execute_code`. Do not round conversion points by eye.
- Never present ownership percentages as payout percentages; the gap is the point of the exercise.
- Do not average across exit prices; the cliffs are the information.
- Do not ask questions before delivering. Decide, state the assumption, and give the full result.
- If the user's structure is more complex than the model (capped participation, seniority, multiple common classes), still run the model, name the difference and which way it moves the numbers.
