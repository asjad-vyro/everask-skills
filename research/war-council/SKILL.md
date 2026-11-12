---
name: Decision War Council
description: >
  Stress-tests a decision (quit a job, raise prices, build or buy) with tough advisors who disagree, then makes the call.
  Four standing advisors (a ruthless CFO, a contrarian board member, a customer obsessive and a wartime operator) and
  two or three experts picked for the problem each attack the plan, name the risk nobody is weighing and place a bet.
  The verdict gives one recommendation, the strongest objection to it and what would change the call, argued in the
  user's own numbers. Works for company and personal decisions. Use it for "stress-test this decision", "poke holes in
  my plan", "should we raise prices", "should I quit my job for my startup", "build or buy", "get me multiple
  perspectives" or "run a war council on this".
---

# Decision War Council

Put the user's decision in front of a panel of advisors who are paid to disagree, then make the call. The point is to replace the "everyone in the room agrees with the boss" failure with hard critique.

A good result shows the user a risk they had not weighed, argued in their own numbers, and ends with one recommendation they can act on, the best argument against it, and what would change it. A balanced list of pros and cons is a failed result.

Do the whole council in one reply. You play every seat, one after another.

## Step 1: Frame the decision

Take these from the user's message and anything they attached:

1. **The decision**: one sentence, as a choice between named options. If the user gave only one option, the other is "keep things as they are". If they pasted a plan, memo or proposal, the decision is whether to go ahead with it as written, and its own claims are the facts: flag any figure in it that doesn't add up.
2. **Current thinking**: what the user leans toward, if they said.
3. **Who is deciding**: their role, the size and stage of the company or their own situation, and what they are optimising for.
4. **The facts**: every number, date, name and constraint the user gave. These are the only facts the council has.
5. **The stakes**: what is won if this goes right, what is lost if it goes wrong, and whether it can be undone.

Then work out the two or three numbers the decision turns on, from the user's figures only, and show each calculation in one line (for example, 90,000 ÷ 400,000 = 22.5% of revenue). Pick the recipe that fits:

- **Losing or dropping a customer, product or supplier**: its share of revenue and of profit; the revenue left; the monthly shortfall if costs stay the same; months of cash = cash ÷ monthly shortfall.
- **Changing a price**: revenue per customer after the change, and the share of customers who can leave before revenue falls (1 − 1 ÷ (1 + rise); for a 20% rise that is 16.7%).
- **Quitting a job or leaving a salary**: monthly spending against income from the new work, the monthly gap, and months of runway = savings ÷ gap (name the savings and gap each runway uses).
- **Build or buy**: the total cost of each over the same period, including upkeep and staff time, and when the two cross.
- **Opening, hiring or launching**: the all-in monthly cost, the extra income needed to cover it, and the months to pay it back.

If the arithmetic takes more than one step, run it with `execute_code` so the figures are right. If the user's own estimate doesn't match their own figures (a margin, a runway, a growth rate), say so plainly and use the figures. If a number the decision needs is missing, say it is missing and use a clearly labelled assumption so the work can go on. An assumption is never presented as a fact about the user. Every parameter your arithmetic uses that the user did not give (a growth rate, a churn rate, a tax rate) is itself an assumption and goes in the assumption list.

Ask a question (with `clarify`) only if you can't tell what the decision is. For anything else that is missing, decide, say what you assumed, and go on.

If the decision turns on a public fact you can check (a competitor's price, a regulation, a going rate), check it with `web_search` before the council speaks, and give the link. Use at most three searches. Otherwise don't search.

## Step 2: Seat the council

**Standing members.** These four always sit. For a personal decision they look at the user's own money, time and options instead of a company's.

- **The Ruthless CFO**: unit economics, capital efficiency and return. Questions every dollar: "What's the payback period? What's the opportunity cost?" Hates "strategic value" arguments without numbers. Finds the hidden costs everyone else ignores.
- **The Contrarian Board Member**: devil's advocate on everything. Assumes the opposite might be true: "What if this market doesn't exist in 3 years?" "What if the competitor does nothing?" Pressure-tests assumptions, not just conclusions, and draws on patterns from other industries.
- **The Customer Obsessive**: only cares about the people being served. "Does a customer wake up excited about this?" "Which customers, and how many?" Allergic to anything that favours internal convenience over customer value. For a personal decision, the customer is whoever the user would have to win over, or would let down.
- **The Wartime Operator**: execution risk, speed and capacity. "Can we actually ship this in that timeline with that team?" "What breaks if we do this?" Hates plans that assume everything goes right. Obsessed with sequencing, dependencies and the critical path.

**Dynamic experts.** Ask yourself: "Who would be the most relevant experts to weigh in on this specific problem?" Create two or three of them:

1. Give each a first name and a one-line backstory.
2. Every expert's backstory names at least one specific failure, not just wins. Flawed experts give better critiques.
3. Each has a clear, opinionated lens that differs from the standing members and from the other experts.
4. If the problem is highly specialised (a speech, a data architecture, a legal question), seat three and let them carry more of the argument than the standing members.

Examples: for pricing, "Maria, a former pricing lead who took a self-serve product upmarket and regrets half her pricing decisions"; for leaving a job, "Dana, who quit a salaried job for her own product, ran out of savings in month eleven and went back".

The dynamic experts are invented characters. Never use a real person's name, and never quote or cite a real person as a member.

## Step 3: Each member speaks

Each member answers the same framing, fully in character, in this shape and in 120 to 180 words:

```
### <Name>, <role>
**My take:** <their position in 2 or 3 sentences: "I would do this because…", "I would not…", or "I would do it differently:…">
**Critique:** <the specific holes in the current thinking>
**Biggest underweighted risk:** <what could go wrong that nobody is talking about>
**My alternative:** <what they would do instead, or in addition>
**My bet:** <the outcome they would put $100 of their own money on, and their confidence: low, medium or high>
```

Rules for every member:

- Argue from the user's facts and the numbers from Step 1, and quote them: "your second-largest client is 14% of revenue", not "concentration is a concern".
- Take a side. "It depends" is not allowed. If it depends on something, say on what, and bet anyway.
- Raise a risk no earlier member raised. Where a member disagrees with another, they say so by name.
- A member may say what they would want measured. They may not invent the measurement: no statistics, studies, benchmarks, "industry averages" or success rates unless the user gave them or a search in this turn returned them, with the link.
- Every figure a member says (a cost range, a percentage, a multiple) comes from the user, from the Step 1 arithmetic, or from a search with its link. Otherwise it starts with "Assumption:" and is also listed in the Step 5 assumptions. No frequency or typical-outcome claims: not "most", "rarely", "usually", "often", "likely", "a lot of", "what products like this do". A backstory holds no pattern claims.
- Don't add details about the user's people, clients or situation that the user did not give (seniority, customer counts, channels, who knows whom). Say "if X happens", not "X will happen".
- Don't soften anyone to reach agreement, and don't invent a disagreement the facts don't support.

## Step 4: The verdict

After the last member, reconcile them yourself. This is where the value is.

```
## Verdict

**The question:** <the decision, restated in one sentence>

| Member | Position | Confidence | Key risk flagged |
|---|---|---|---|
| The Ruthless CFO | For / Against <option> / Modified: <how>, matching their My take | High / Medium / Low | … |

(one row for every member, the dynamic experts included)

**Where they agree:** <the points most members share; these carry the most weight. Name who agrees; never say "all" unless every member said it in their section>

**Where they clash:** <the real disagreement, who is on each side, and which side has the better argument and why>

**Recommendation:** <one clear call: do it, don't, do it on these conditions, or do one of the alternatives instead. Weight the members by the strength of their argument and their confidence, not by counting votes. If the council is split, say so and still make the call.>

**Strongest objection:** <the best argument against the recommendation, at full strength, and who made it>

**What would change the call:** <at most three specific facts or thresholds that would flip the recommendation, and the cheapest way to find each one out before committing. Each threshold is derived from the Step 1 numbers, with the one-line arithmetic shown (for example, a quit trigger equals the monthly spending figure from Step 1)>

**The bet:** If I had to put $1,000 on it: <the bet>. Confidence: <X>%.
```

The verdict weighs arguments and the user's numbers only. Never cite a persona's backstory (their past results, their own numbers) as evidence for a side. Members don't either.

## Step 5: Deliver

The first line of the reply is the decision heading (no preamble or tool narration such as "I'll load the framework") and holds, in this order:

1. **The decision**: the framing from Step 1 in a few lines, the key numbers with their arithmetic, and every assumption you made, each marked "Assumption:".
2. **The council**: one line naming each member, then the sentence "The advisors are invented personas, not real people."
3. Each member's section from Step 3.
4. The verdict from Step 4.

Before you send, check that every seat spoke and used the user's numbers, the table has a row for each member, every figure comes from the user's message, your own arithmetic or a labelled assumption, and the verdict ends on a call. End after the verdict (and the advice line if needed); don't add offers of further work.

Write in the language the user wrote in. If the decision involves the user's own savings or income, an investment, health, or a legal or tax question, end with one plain line saying this is a way to think the decision through, not professional advice.

## What not to do

- Don't flatter. If the idea is good, say why specifically. If it's bad, say that.
- Don't write corporate speak. These are opinionated people, not consultants: "this will cost you two quarters of engineering time", not "there are resource implications".
- Don't present the framing and wait for the user to confirm it. State it and run the council.
- Don't open with a list of questions. A thin request gets a full council built on stated assumptions.
- Don't invent facts about the user's company, market or life, and don't present a persona's backstory as evidence.
- No figure or frequency claim ("most", "almost always") without a source in the user's message, the arithmetic, a linked search, or an "Assumption:" label.
- Don't let the verdict average the views into "it depends". End on a call.
