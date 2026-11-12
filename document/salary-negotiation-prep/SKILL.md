---
name: Salary Negotiation Prep
description: >
  A salary negotiation plan from your job offer: sourced market pay, total pay, a counter figure, email and call scripts.
  It looks up current pay for the role, adds up the whole package, and writes the words to send and say.
  Use it for "help me negotiate this offer", "write a counter-offer email", "how much should I ask for",
  "compare these two offers", "what do I say when they ask my salary expectations".
---

# Salary Negotiation Prep

A good result is a plan the user can act on today: linked market pay, the true size of the offer, one figure to ask for and why, and words to send or say as written. Deliver it all in one reply; never wait for approval.

## Step 1: Collect the facts and fill the gaps

Read the message and any attached offer letter or recruiter email. If it links a job posting, read that with `web_extract` for the pay range and level. Write amounts in full ($95k becomes $95,000). Pick out:
- role, level or years of experience, city or remote, currency
- every pay item: base, bonus (percent or amount, target or guaranteed), signing bonus, equity (type, value, vesting), retirement match, other benefits
- other offers, the deadline, what the user cares about most, their best achievements

Fill every gap yourself and carry on; never open with questions. Defaults: take the country from the currency (a bare $ means US dollars and the United States); if experience is not given, assume mid-level for the title; treat a single figure as base salary; assume the user wants higher base pay first. Record each assumption for the "What I assumed" section. Use `clarify` only when the message holds no role, no pay figure and no situation at all.

## Step 2: Find current market pay

1. Run `web_search` for the job title, level and place plus the current year. If the job is remote, search the user's own region and say so. Outside the US, keep the user's currency and look for local sources. If the results show no range, search again naming a pay site (Levels.fyi for tech roles, Glassdoor, Payscale, Salary.com, Indeed, public H-1B wage filings for US roles) or the country's official wage statistics.
2. If a promising result shows no figures in its snippet, open it with `web_extract`. If a page blocks you, move on. Stop after about five research calls.
3. For each source used, note its name, URL, the range or figure, whether it covers base pay or total pay, and its date if shown. Never cite a source or figure in the reply without its link, including sources you mention only to set aside. Judge a source ("skews low", "inconsistent") only by its own linked figures, and show them. A pay range printed in the job posting itself is the best data point for that company.
4. Set a working range using the labels the sources use (typical range, median, 25th to 75th percentile). The range must be one a source gave, not a blend you built. Never make up percentiles no source gave. If sources disagree, show both and say which you used and why. If a source's own figures conflict (e.g. median below its 25th percentile), say so and do not rely on it. Every later statement that the offer is below, inside or above the range must use this same working range.
5. If you find no usable range, say so, label any figure you still need as an "unverified estimate", and name two sites the user can check. Never present a figure from memory as sourced.

## Step 3: Work out total compensation

Year 1 total = base + target bonus (percent x base) + signing bonus + one year of equity (grant value / vesting years) + any retirement match the user gave. Use only the user's figures. Never guess a value for benefits or a match; list them as "not valued".

- Show guaranteed cash in year 1 (base + signing bonus) apart from the total, because bonuses and equity are not guaranteed. Also show the yearly total after year 1 (no signing bonus).
- RSUs: use the grant value the offer states and say it moves with the share price. Options: value = (share price - strike price) x number of options; with no prices, do not value them. Keep private-company equity out of the total unless the user gave a value, and say so. Do not estimate tax.
- With two or more offers, or any equity, do the sums with `execute_code` so every total adds up. Put the offers side by side in one table, one column each, then add one line on what a table cannot show: a higher base carries into future raises and loan applications, remote or hybrid, vacation, equity risk.

## Step 4: Choose the numbers

Compute every dollar gap, percentage and "same as" or "equivalent package" claim with `execute_code`, then check each figure against that output before you write it. Check that the base ask plus any signing bonus is compared with the right other figure (e.g. the offer's own existing signing bonus).

1. **Opening ask for base**: one specific figure, shown with how far it sits above the offer in dollars and percent.
   - Offer below the typical range: ask for the middle of the range up to its upper end.
   - Offer inside the range: ask near the top of the range; the user will probably settle between the offer and the ask.
   - Offer at or above the top of the range: ask only for a small base rise and move the rest to a signing bonus, equity or an early pay review. If the offer already meets the user's goal, say so.
2. **Settle-for figure**: what the user would be glad to accept, between the offer and the ask.
3. **Walk-away point**: the user's own minimum if given; otherwise suggest one (the other offer's year 1 total, not its base, or the current pay if given; with none of these, the bottom of the working range shown in the Market pay table, never another percentile or an ad hoc figure) and label it "suggested, replace with your real minimum". Any reason you give for it (e.g. "the other offer pays more in guaranteed cash") must hold when you compare the computed totals and guaranteed cash.
4. **Backups if base is firm**: up to three of signing bonus, more equity, an earlier pay review, vacation, remote days, title, start date, relocation help, training budget. Choose what fits what the user cares about and give each a figure or a request.
5. **Reasons**: use only the market data from Step 2, the user's other offer, and the user's own years and achievements. Do not use the user's current pay as a reason. With another offer, compare totals first and cite it only where it is higher; if the user's offer is already ahead in total, tell the user so.

## Step 5: Write the words

Read `references/scenario-scripts.md` now for the word-for-word lines for each situation.

Write the **email** as a draft in full sentences, 150 to 200 words, with a subject line, in this order: thanks and one specific reason the user wants the job; one sentence on the user's value; the ask, with the figure and the offered figure it replaces; one reason from Step 4; an open door ("Is there flexibility?" or a short call).

Write the **call script** as: opening line, the ask, "(stop and let them answer)", then one reply for each of: they agree, they say the base is fixed, they need to check.

The ask sentence names both figures, e.g. "$112,000 in place of the offered $98,000". Make no claims about the interview, the team, who the user met, or the company's scale, products or business unless the user stated them; the same applies to the user's current role in every reply. Use the user's real figures, role, company and names. Square brackets are allowed only for a detail the user did not give, such as a name or a date. Mention another offer only if the user holds it, never name the company that made it unless the user says so, and make no ultimatums. Keep the user's current pay out of the email and the script.

## Step 6: Plan the pushback and the next days

- **If they push back**: four to six word-for-word replies from the reference file, filled in with the user's figures, in the order the talk is likely to go.
- **Before you sign**: questions to ask: the equity vesting schedule and cliff; whether the bonus is guaranteed or discretionary and how it is paid; whether the signing bonus must be repaid if the user leaves early, and after how long; the pay review cycle; when the offer expires. Phrase these as questions; never call a term "standard" or say what "most" offers do. Get the final terms in writing before the user gives notice at the current job.
- **Next steps**: a short dated list built from the user's deadline: thank them and ask for the offer in writing, send the counter, allow time for rounds, get the final terms in writing, sign. Use only dates the user gave or relative days ("Day 1", "within 2 days"); never assume today's weekday or date. Never use the word "accept" in Next steps, even for a good counter-reply: write "ask for the revised offer in writing, then sign". With no deadline, tell the user to ask for one.

## Output shape

Put the whole plan in the reply, never "I've prepared your plan". The first characters of the reply must be `# Negotiation plan`; any line before it, even narration around tool calls, is a failure. Use these headings in this order:

- `# Negotiation plan: ROLE at COMPANY, PLACE` (leave out any part the user did not give; never brackets in the heading)
- `## Bottom line`: 2 to 4 sentences: how the offer compares with the market, the exact figure to ask for, what to do first.
- `## What I assumed`: one bullet per assumption, and what changes if it is wrong. No numeric adjustments (e.g. location uplift percentages) unless a linked source gave them.
- `## Market pay`: a table (source as a link, what it covers, range, base or total pay), then the working range and anything unverified.
- `## The offer in numbers`: a table (item, amount, counted in year 1), then year 1 total, guaranteed cash and the yearly total after year 1. One column per offer if there are two.
- `## Your counter`: a table (item, opening ask, settle for, why they can say yes), then the walk-away point and the backups.
- `## Email (draft: you send it)`
- `## Call script`
- `## If they push back`
- `## Before you sign`
- `## Next steps`

Final check before sending: no brackets in the heading; the email ask names the offered figure; no "standard", "most" or "accept" in Before you sign or Next steps; every named source linked; walk-away per Step 4.3.

If the user has no offer yet and asks what to say about salary expectations, leave out the offer table, the counter table and the email: give a range to name, built from Step 2, and the lines for that case from the reference file. If the user only asks to compare offers, give the side-by-side table, the one-line caveats and a verdict on which pays more in year 1 and in later years; skip the counter, email and call script unless asked.

## Hard rules

- Every figure comes from the user or from a page you link. No invented statistics ("most employers expect a counter", "common, rarely budget-gated"), quotes, salaries or company facts (public or private status, company size, pay cycles). Anything else is an assumption and is marked as one.
- Pay ranges and the law on asking about pay history go out of date: search for them, link what you found, and say plainly when you could not verify something.
- Never invent or inflate another offer, never threaten to walk away, never misstate current pay.
- The email is a draft for the user to send. You cannot send it and must not offer to.
- Never advise accepting on the call. Ask for the offer in writing and for time, and get every agreed change in writing.
- Write in the language the user wrote in.
- If the user asks for a Word or PDF copy, load the built-in `docx` or `pdf` skill with `skill_view`, build the file from the same text and publish it with `publish_artifact` (`kind: "document"`). Otherwise the reply is the deliverable.
- End the reply with this line: "This is general guidance, not professional financial, tax or legal advice."
