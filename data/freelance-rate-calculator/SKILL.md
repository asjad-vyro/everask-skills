---
name: Freelance Rate Calculator
description: >
  Works out the hourly and day rate a freelancer or consultant must charge, from target income, billable time, overhead and tax.
  Use it for "what should I charge as a freelancer?", "set my day rate", "convert my salary to a contract rate", "why is my freelance rate so high?".
---

# Freelance Rate Calculator

New freelancers divide their old salary by 2,000 hours and run short of money. An employer pays for benefits, employer taxes, tools, holidays, sales time and gaps between clients, and all of that now sits inside the rate. A good result derives the rate backwards from the income the user wants, through honest billable hours, so the number arrives with its justification attached. The whole job is finished in one reply, from what the user gave.

## Step 1: Collect the inputs

Take what the user wrote. Never open with questions. Use `clarify` only if there is no income target at all and none can be inferred; otherwise fill gaps with the defaults below and label each one "assumed".

- **Target personal income per year**, before income tax. If the user says "take-home" or "after tax", say so, and gross it up as `target / (1 - assumed income tax rate)`, stating the assumed rate. Do that sum in `execute_code`.
- **Currency**: the user's. Never convert it.
- **Annual overhead** (insurance, software, accounting, workspace, equipment): default 12000 in the user's currency, labelled as a placeholder. A monthly figure is times 12.
- **Weeks off** (holiday, sick, admin-only weeks): default 6.
- **Billable %** of working time: default 60. Defend it in the reply: sales calls, proposals, invoicing, learning and gaps between clients are unbillable. 80% or more belongs to a mature practice with a full pipeline. Never use 100%.
- **Self-employment tax premium** (extra tax and social cost compared with being employed, as % of target): default 8, labelled a placeholder. It differs by country and business structure. If the user names a country and wants a real figure, do at most one `web_search` and link what you found; otherwise keep the placeholder and say so.
- Hours per week 40, hours per day 8, unless the user said otherwise.

## Step 2: Run the numbers

Never do the arithmetic in your head. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in the command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `freelance_rate.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/freelance_rate.py --target <income> --overhead <overhead> --extra-tax-pct <pct> --weeks-off <weeks> --billable-pct <pct> --json
```

Add `--hours-week` or `--hours-day` only if the user gave them. The JSON holds required revenue, billable hours, hourly and day rate, rounded-up quotes, the multiplier versus income/2000, and the hourly rate at 50, 60 and 70% billable. Copy figures from it; do not recompute them. If the user asks "what if", run the script again with the changed input and show the before and after.

## Step 3: Reply in this shape

Put everything in the reply itself, in full.

```
# Freelance rate: <user's name or practice, or "your practice">

## Inputs
<a short table: each input, its value, and "given" or "assumed">

## The derivation
- Required revenue = target + tax premium + overhead = <figure>
- Billable hours = <working weeks> weeks x <hours> h x <billable %> = <figure>
- Hourly rate = required revenue / billable hours = <figure>; day rate = <figure>
- Naive income / 2000 = <figure>, so the honest rate is <multiplier>x that, and why (employer costs, unbillable time)

## The rate to quote
<hourly and day rate, rounded up as in the script output, and one line why rounding up (you can discount from a higher rate, you cannot raise an anchored one)>

## What to say when a client asks "why so much?"
<2 or 3 sentences, no apology: what the rate covers and how it compares with the cost of an employee on that income>

## Sensitivity
<the hourly rate at 50, 60 and 70% billable, from the script, and a line that billable % is the input to watch>

## Check against the market
<one line: compare with what peers charge as a sanity check only, or say you did not look it up>

*Educational model, not financial or tax advice. Check the tax premium and business setup with a licensed professional.*
```

## Rules

- Derive backwards from the income the rate must fund. "What do others charge" is only a sanity check; if you cite market rates, they come from a `web_search` you linked, never from memory.
- Use only figures the user gave or the script returned. Anything else is marked "assumed". Do not invent market rates, tax rates or statistics. The commonly quoted idea that contract rates run well above the salary-equivalent hourly rate is a rule of thumb, not a figure to cite as fact.
- Do not assume 100% billable, or 80% for a new freelancer.
- Flag the tax premium as jurisdiction-dependent. Do not give country-specific tax advice.
- The client justification contains no apology and no "but I'm flexible".
- Do not price to win the client; price to fund the practice, then treat discounts as a deliberate choice.
