---
name: Startup Team Planner
description: >
  A startup hiring plan: team gaps, who to hire next and in what order, when to start each search, pay, equity and runway.
  Use it for "who should we hire next", "build a hiring plan and budget for the next 12 months", "what equity should our first employees get", "design an org chart for our startup".
---

# Startup Team Planner

A good result is a plan the founders can act on this week: real gaps, ordered hires, search dates, labelled pay and equity, and the runway impact. Work from what the user wrote and finish in one reply. Never stop to ask questions: state what you assumed and deliver the whole plan.

## Step 1: Pin down the inputs

Pull these from the user's message: stage, each person on the team and their role, cash, monthly burn, runway, location, revenue or ARR, the next funding milestone, and any deadline ("need a sales lead by June").

- Go by the stage the user states. A company that has raised a seed round is a seed company even if its ARR is below the usual seed range.
- Anything the user did not give is an assumption, and the reply lists it as one. Never invent cash, burn, revenue, customers or team members. If the team's roles are not given, assume the typical shape for the stage (Step 2) and say so.
- If burn is missing but cash and runway are given, burn = cash ÷ runway. If cash, burn and runway are all given and disagree, use cash ÷ burn and say so in one line.
- If the business is not software (hardware, a marketplace, services), adapt the roles and say that the reference lists assume a software company.
- If the stage is Series B or later, say that the ranges here stop at Series A, scale up the Series A shape and mark all of it as an assumption.
- If the user asks about only one part (pay, equity, an org chart, a budget), answer that part in full and skip the rest.

## Step 2: Find the gaps

Read `references/roles-by-stage.md` before you list gaps or pick hires.

1. Take each function in turn (engineering, sales and marketing, product and design, customer success and support, finance and operations) and write who covers it today: a named person, "a founder" or "nobody".
2. A gap is a function this stage needs that nobody covers, a person doing a job they should not (the CEO running every sales call, engineers answering support tickets), or a single point of failure (only one person can ship or deploy).
3. Keep the 2 to 5 gaps that matter most for the user's goal, each tied to something the user said. Skip what the stage does not need yet (no CFO at pre-seed).
4. State only what the user said as fact. Any diagnosis that goes beyond their message (who deploys, who answers tickets, who acts as PM, at what size something breaks) is written as "likely" and also listed under "Assumed".

Typical shape by stage (rough, commonly quoted figures, not measured data):

| Stage | ARR | Team size | Usual team | Focus |
|---|---|---|---|---|
| Pre-seed | up to about $500K | 2-5 | Founders cover product, engineering and business; maybe a first engineer; contractors for design and marketing | Build the product and validate fit |
| Seed | about $500K-$2M | 5-15 | Engineering lead plus 2-3 engineers, a first sales hire, a product manager, a marketing or growth lead | Scale the product and prove repeatable sales |
| Series A | about $2M-$10M | 15-50 | Engineering 40%, sales and marketing 30%, customer success 10%, G&A 10%, product 10% | Scale revenue and build repeatable processes |

## Step 3: Choose and order the hires

1. Turn each gap into one role with a level (junior, mid-level, senior or executive), full-time or contract. Full-time for core product, sales and mission-critical work; contract for short-term specialists (legal, accounting), variable work (design, campaigns) or testing a role.
2. Rank the roles with these tests in order, using the first one that separates two roles:
   - It unblocks the user's stated goal or deadline, or their biggest bottleneck.
   - It takes a founder off a job someone else could do.
   - It prepares what the next funding round will test (the Focus column above).
   - Otherwise, cheaper and contract roles go first.
3. Plan the number of hires the user asked for ("first five"). If they gave none, plan as many as their cash can carry (Step 6), or the next four to six if cash is unknown, and say which. If they ask for more hires than the stage's usual team size, give them what they asked for and mark which could be contractors or wait for funding.

## Step 4: Time each hire

Give every hire three dates: start recruiting, expected start, productive by. Use calendar months if the user gave a date or deadline, otherwise "Month 1" to "Month 12" counted from today. If you map Month 1 to a calendar month, list the date you took as today under "Assumed". Work backward from any deadline.

| Level | Opening the role to a start | Ramp to productive |
|---|---|---|
| Junior | 6-8 weeks | 4-6 months |
| Mid-level | 8-12 weeks | 2-4 months |
| Senior | 12-16 weeks | 1-3 months |
| Executive | 16-24 weeks | 3-6 months |

These are commonly quoted ranges, so say so. Add a 2-3 month buffer to the plan as a whole, since searches slip, and flag any hire with no slack against a deadline.

Check before you write the reply: for every hire, the gap from start recruiting to expected start is at least the table's minimum for that level (senior: at least 12 weeks, so a search opened in Month 1 gives a start no earlier than about Month 4). If a hire fails this check, move its start date later. Do not shorten the lead time.

## Step 5: Set pay and equity

Read `references/benchmarks.md` before you write any pay, equity or option pool figure.

- Pay: the reference ranges are static US figures from about 2024. When the user asked about pay or a budget, or named a country or city, run `web_search` for current pay for the first two or three hires in their location and give what you found with its link. At most four searches in total; `web_extract` only if results show no range. If nothing usable comes back, use the reference range and label it as a US figure from about 2024. Outside the US, skip the US location adjustments and say the figures need a local check.
- If the user gave no location and asked nothing about pay, assume the US, say so, and use the reference ranges without searching.
- Sales roles show base plus commission.
- Equity: give a range per hire from the reference, by role and stage. Say these are rules of thumb and that the right grant depends on the company, the round and the person.

## Step 6: Cost the plan and check the runway

1. Fully loaded monthly cost of a hire = (base × 1.3 + expected commission or bonus at target) ÷ 12. The 1.3 is the US rule of thumb for payroll taxes, benefits, equipment and software (use 1.4 as a cautious case). Outside the US, search for employer on-costs in that country instead and link what you found.
2. Cost in the plan = monthly cost × months on payroll. For a 12-month plan, months on payroll = 13 − start month (a Month 4 start gives 9 months, a Month 10 start gives 3). If a contractor converts to full-time, cost it as two lines: contract months at the contract rate, then full-time months at the loaded cost. The two lines together must cover every month up to Month 12. Any contract rate that does not come from a search or the reference is labelled an assumption.
3. Do the arithmetic with `execute_code`, not in your head. Every total in the reply must equal the sum of its lines. Recompute the total after fixing any line. This includes every alternative-scenario figure (delay savings, contract swaps, gross vs net burn variants). State each delay saving as months moved × monthly cost, and check that it matches any leftover-cash figure you give. Gross vs net: net burn = burn − monthly revenue; compute both runways in code, never estimate the difference.
4. If cash and burn are known: runway today = cash ÷ burn; runway at full headcount = cash ÷ (burn + the monthly cost of all hires). The second is a cautious figure, since hires arrive over time, so say that. Equity is not a cash cost. Do not assume revenue growth unless the user gave a forecast; if you show a version with revenue, label it an assumption.
5. If runway at full headcount falls below the user's target (or below 12 months if they gave none; say that is your assumption), delay or shrink the least urgent hires, or make them contract, and show the adjusted plan rather than a plan the cash cannot carry. Any threshold or norm you add (when to raise, pool top-ups, how much cash a round carries) gets the words "rule of thumb" in the same sentence or is listed under "Assumed".
6. If the user gave no cash or burn, show the cost of the plan only and say runway cannot be worked out without their cash and monthly burn.

## Step 7: Write the reply

Put the whole plan in the reply as normal markdown. The first characters of the reply must be "## Hiring plan": no preamble, no narration about loading the skill or what you will do. Write no text before or between tool calls; run every search and execute_code first. End with the disclaimer line and no closing offer or question. Delete any half-written or garbled line before sending. Do not add widgets, charts or any output outside the markdown reply, and do not refer to anything "below" that is not in the text. Include the org chart section only if the user asked for one or a manager would have more than 8 reports; otherwise leave it out entirely. Do not publish a file unless the user asks for one; if they want a spreadsheet or a Word file, load the built-in `xlsx` or `docx` skill with `skill_view` and build it from the same numbers. Use this shape, and keep each "Why now" to one or two sentences tied to what the user said:

```
## Hiring plan

**What I worked from**
- Stage and goal: ...
- Team today: who covers what
- Cash, burn, runway: ...
- Assumed (you did not say): ...

**Gaps in the team today**
1. <gap>: <what the user said that shows it>

**Hires, in order**
**1. <Role>, <level>, <full-time or contract>**: start recruiting <when>, expected start <when>, productive by <when>
- Why now: ...
- Pay: <range> base (plus commission for a sales role), <label>
- Equity: <range>, <label>
(repeat for each hire)

**Cost and runway**
| Hire | Monthly cost, fully loaded | Months on payroll | Cost in the plan |
|---|---|---|---|
| ... | ... | ... | ... |
| Total | ... | | ... |
- Runway today: ...
- Runway at full headcount: ...
- If that is below the target: which hires to delay or make contract.

**Org chart** (only if the user asked for one, or the plan puts more than 8 people under one manager)
<indented text tree of reporting lines after the plan>

**Where the figures come from**
- Pay: <current figures found, with links> and/or <US benchmark ranges from about 2024, static and US-centric>
- Equity, timing and cost multiplier: commonly quoted rules of thumb, not measured data.

Planning guidance, not legal, tax or financial advice: have a lawyer or an accountant check equity grants and employment terms before you make offers.
```

## Rules

- Never ask the user a question before delivering. Assumptions go in the reply.
- The reply begins with "## Hiring plan" (nothing before it) and ends with the disclaimer, with no closing offer question. No stray or half-written lines.
- Every figure comes from the user, from a search you ran (give the link) or from the reference files (labelled as a US benchmark from about 2024 or a rule of thumb). No invented sources, surveys, company names, quotes or benchmarks.
- Label each pay, equity and timing figure so the reader can tell a given fact from a benchmark from an assumption.
- Do not draft job posts or offer letters unless the user asks.
- Months on payroll = 13 − start month. Each start date is at least the Step 4 minimum lead time after its search opens.
