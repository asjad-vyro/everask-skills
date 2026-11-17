---
name: Debt Payoff Planner
description: >
  Turns a list of debts, rates and spare monthly cash into avalanche and snowball payoff plans, with debt-free date and total interest compared.
  Use it for "make a debt payoff plan", "avalanche vs snowball", "when will I be debt-free", "how much interest will I save if I add $200 a month".
---

# Debt Payoff Planner

A good result is a clear plan the user can follow: which debt to attack first, how many months until debt-free, total interest under each method, and what the extra payment saves. Every figure comes from a simulation, never from mental maths. General education, not financial advice.

## Step 1: Collect the debts from the message

For each debt take: name, current balance, APR (annual rate, percent), minimum monthly payment. Also take the extra amount per month the user can add on top of the minimums. Use only what the user gave.

- Minimum payment missing: assume interest for one month plus 1% of the balance, rounded up to the next whole currency unit, and say so as an assumption. Do not ask.
- Extra payment missing: run with 0 extra and also with a few sample extras (for example 100 and 200 per month), labelled as examples, not as the user's budget.
- Currency: use the user's. Default to the symbol they wrote.
- If the user wants bank transactions or budget data pulled from an app, work only from what they pasted or uploaded. Never invent balances or rates.

## Step 2: Run the simulation

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path where it says `SKILL_DIR`. If `skill_view` gives no path, find `payoff.py` under `~/.computer/skills` with `search_files`.

1. Write the debts to `/tmp/.scratch/debt-payoff-plan/debts.json` as `[{"name": "...", "balance": 0, "apr": 0, "min": 0}]` (percent for apr, for example 24 for 24%).
2. Run `python3 SKILL_DIR/scripts/payoff.py /tmp/.scratch/debt-payoff-plan/debts.json EXTRA --csv-dir /tmp/.scratch/debt-payoff-plan/out`.
3. It prints JSON for both strategies: months, total interest, total paid, target order, order debts clear, balances at each year end, and writes the month-by-month schedules as CSV.
4. If the script is unavailable, do the same in `execute_code` with this logic. Each month: add interest (balance x APR / 12) to every open debt, pay every minimum, put all remaining budget (minimums plus extra) on the first open debt in the target order, and when a debt clears, its payment rolls to the next. Avalanche order is highest APR first; snowball order is smallest balance first.
5. For extra comparisons (for example "what if I add 200 more"), rerun the script with the other EXTRA values. Do not estimate.
6. If `paid_off` is false (minimums do not cover interest), say the debt never clears at that payment and give the monthly interest on the worst debt.

## Step 3: Check before writing

- Avalanche total interest must be less than or equal to snowball. If not, something is wrong: recheck inputs and rerun.
- Total paid should equal starting balances plus total interest (within rounding).
- Months to payoff: also give the debt-free month as "month N" and, only if the user gave a start date, the calendar month.

## Step 4: Write the reply

Put the whole deliverable in the reply itself. Use this shape, with figures from the script output:

1. **Your debts** - a table: Debt, Balance, APR, Minimum. Mark any assumed minimum.
2. **Monthly budget** - total of minimums + extra = total per month.
3. **Comparison** - a table: Method, Months to debt-free, Total interest, Total paid. One line on the difference: avalanche saves `<difference>` in interest, snowball clears the first debt in `<n>` months versus `<n>`.
4. **Avalanche plan** - target order with the reason (highest rate first), the month each debt clears, and a condensed schedule: a table of the first 6 months for every debt (Month, Debt, Payment, Principal, Interest, Remaining), then one row per payoff milestone and the final month.
5. **Snowball plan** - the same.
6. **Recommendation** - avalanche if the saving is meaningful; snowball if the user said they need quick wins or the interest gap is small. Say that the best plan is the one they will stick with.
7. **Notes** - assumptions made, plus these caveats when relevant: rates are treated as fixed (variable rates change the result); interest is simple monthly (APR / 12), so real statements differ slightly; new purchases on the cards are not modelled; if the extra is under about 50 a month, say that growing income or cutting costs will do more than choosing a method; keep a small starter emergency fund (commonly about 1,000) while paying down debt rather than dropping savings to zero.
8. One plain line: this is general education, not professional financial advice.

If the user asks for a spreadsheet or the full schedule, load the built-in `xlsx` skill with `skill_view`, build a workbook with a Summary sheet, and one schedule sheet per method from the CSV files, then publish it with `publish_artifact` (`kind: "document"`). Otherwise do not build a file.

## Hard rules

- Never state a balance, rate, payment or date the user did not give, except labelled assumptions.
- Every number in the reply is copied from script or `execute_code` output.
- Do not open with questions. Decide, state the assumption, and deliver the full plan in the same reply.
- Do not recommend specific lenders, balance-transfer products or calculators.
