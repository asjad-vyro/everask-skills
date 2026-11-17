---
name: Personal Budget Planner
description: >
  Turns a monthly income and a list of expenses (typed, pasted or a bank CSV) into a budget with a 50/30/20 check, a savings rate and a plan to save more.
  Use it for "make me a monthly budget", "where is my money going", "I can't save money", "how do I save $X a month", "zero-based budget".
---

# Personal Budget Planner

A good result is a short, correct budget the user can act on today: every number checked by code, the gaps against 50/30/20 named, and three specific cuts with amounts. Everything goes in one reply. This is general guidance, not professional financial advice.

## Step 1: Collect the numbers

1. Take monthly take-home income, expenses and any goal from the message or attachment. Use the user's currency.
2. If the input is a bank statement or transaction CSV, read it with `execute_code` (pandas), sum by month, and use the monthly average. Say which months you used.
3. If income is missing, ask once with `clarify`. If only some expenses are given, work with them and say the rest is unknown. Never invent income, expenses or amounts.
4. Annual or irregular items (insurance, subscriptions): divide by 12 and say so.

## Step 2: Categorise

Read `references/spending-categories.md` if any line is not obviously a need, want or saving. Put each line into Needs, Wants or Savings (including extra debt repayment). Minimum debt payments are Needs. State any judgement call (for example internet as a need) in one line.

## Step 3: Compute with code

Never do sums in your head. Write a CSV with columns `category,type,amount` (type is `income`, `needs`, `wants` or `savings`) into `/tmp/.scratch/personal-budget-planner/`, then run the script. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in the command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `budget.py` under `~/.computer/skills` with `search_files`.

`python3 SKILL_DIR/scripts/budget.py /tmp/.scratch/personal-budget-planner/budget.csv`

If income is not in the CSV, add it as a second argument. The output gives totals, share of income, 50/30/20 targets, gaps, savings rate, the shortfall to a 20% savings rate, and `unallocated` (income not assigned to any line). Copy the figures from it; if the script fails, do the same sums in `execute_code`.

## Step 4: Choose the method

Default to 50/30/20 as the baseline. If the user asks for a zero-based budget, or `unallocated` is not near zero and they want control, also give a zero-based version: assign every unit of income to a named line until the remainder is 0. Read `references/budgeting-methods.md` only if the user asks which method suits them or names the envelope or pay-yourself-first method.

If the user gives a savings goal (for example "save X a month"), use it as the savings target in place of 20%, and compute what must be cut: goal minus current savings, shown against the unallocated money first, then the cuts.

## Step 5: Reply in this shape

**Budget summary**
- Monthly income: `<figure>`; months used and any assumptions.
- A table: Needs, Wants, Savings, Unallocated, each with amount, % of income, 50/30/20 target, gap (over or under).
- Savings rate: `<figure>`%. Below 10% is a warning; 20% or more is the common target.
- Surplus or deficit.

**Where the money goes**: the largest 3 to 5 categories with amounts.

**Action plan**
1. Three specific cuts or moves, each with a category, the current amount and a new cap in the user's currency, and the saving. Take them from the largest Wants first, then from Needs if Needs are over 50%. Say plainly if Needs alone are over 50% and cuts to Wants cannot close the gap.
2. The total of the three, and the savings rate it would give (computed by code).
3. Automation: move the savings amount on payday, before spending ("pay yourself first").

**30-day check-in table**: columns Category, Planned cap, Actual, Difference, with the user's categories and planned caps filled in and Actual left blank.

## Hard rules

- Use only figures the user gave or the script computed. No made-up amounts, percentages or averages. Write "not given" where something is missing.
- Check that categories add up to the total, and say so if the user's lines do not match any total they stated.
- Do not ask the user a list of questions. Decide, state the assumption, deliver.
- No recommendations of specific financial products, funds or providers. If the user asks about taxes, debt strategy or investing, answer briefly in general terms and suggest a qualified adviser for their situation.
- If the user mentions heavy debt or hardship, add one plain line pointing to a free local debt-advice service, and do not name a specific one unless you searched for it.
