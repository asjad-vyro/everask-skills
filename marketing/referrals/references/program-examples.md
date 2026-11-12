# Incentive Types, Sizing and Metrics

Read this before you choose a reward type and size it. It has the incentive types, a worked sizing example and the metric formulas.

## Contents
- Programs people point to
- Incentive types
- Sizing the reward
- Metrics and formulas
- Fixing an existing program

## Programs people point to

These show patterns. Their terms have changed over the years, so describe the pattern and never quote their current numbers as fact.

- **Dropbox (the early program):** extra storage for both sides. It worked because the reward was the product itself, sharing took one email, both sides gained and progress was visible.
- **Ride-hailing apps (Uber, Lyft):** ride credit for both sides, used on the friend's first ride. It worked because the value was immediate, the offer was double-sided, a code was easy to share and the ask came at natural moments.
- **Morning Brew:** tiered rewards for newsletter referrals, with physical rewards at growing milestones. It worked because tiers kept people referring, the rewards cost little next to a subscriber's value, and they gave status.
- **Notion:** credit for referrals, aimed at students, who share a lot and use the product in teams.

## Incentive types

| Type | Pros | Cons | Best for |
|------|------|------|----------|
| Cash or credit | Universally valued | Feels transactional | Marketplaces, fintech |
| Product credit | Drives usage | Only valuable if they will use it | SaaS, subscriptions |
| Free months | Clear value | May attract freebie-seekers | Subscription products |
| Feature unlock | Low cost to you | Only works for gated features | Freemium products |
| Swag or gifts | Memorable, shareable | Logistics complexity | Brand-focused companies |
| Charity donation | Feel-good | Lower personal motivation | Mission-driven brands |

## Sizing the reward

Keep the reward inside the total acquisition budget:

```
Total acquisition cost per customer = total reward cost + other acquisition cost
Max total reward cost = max(0, target acquisition cost - other acquisition cost)
Payback in months = (reward + other costs) / gross profit per month   (per order for one-off purchases)
```

- Use costs per newly acquired paying customer, over the same group of customers and the same period.
- Total reward cost includes both sides of a double-sided reward.
- Other acquisition cost includes allocated tool, campaign and management costs.
- Count credits and free months at what they cost the user (the revenue or margin given up), consistently. Do not treat face value as a cash cost, and do not treat it as free.

**Worked example (illustrative arithmetic, not a benchmark):**
- Lifetime revenue per customer $1,200; gross margin 70%, so lifetime gross profit is $840.
- Target acquisition cost $200; other acquisition cost per customer $40.
- Maximum combined reward: $200 - $40 = $160, for example $80 to each side.
- Check: $160 + $40 = $200, which meets the target.

**Free-month example (illustrative):** on a $20 monthly plan, one free month for each side is $40 at face value. Against a $30 target acquisition cost that reward does not fit, even before other costs. Use a smaller credit, reward one side only, or pay out later.

Lifetime gross profit tells you whether the acquisition budget is viable at all. It is not the reward budget. Check retention, refunds and cash payback before you commit. If other costs already meet or exceed the target, redesign the program: a zero reward budget does not make an over-budget acquisition acceptable. If payback is longer than the customer's expected lifetime, the program loses money on the average customer.

Do not start from a "typical" reward. Start from the ceiling and work down.

## Metrics and formulas

**Viral coefficient (K):**
```
K = invitations sent per customer x share of invitations that convert
```
K above 1 means each customer brings more than one new customer. K below 1 means referrals add to other acquisition instead of replacing it. Arithmetic illustration only: 3 invitations x 15% converting = K of 0.45.

**Referral rate** = customers who referred / total customers, over a stated period.

**Referrals per referrer** = qualified referred customers / customers who referred.

There are no benchmark figures here on purpose. Set targets from the user's own baseline after the first 30 days.

**Referral program return:**
```
return = (contribution before program costs - program costs) / program costs
contribution before program costs = net referred revenue - serving or product costs
program costs = reward cost + allocated tool and campaign costs + management hours x loaded hourly cost
```

Use the same group of customers and the same window for revenue and costs. Net revenue is after refunds and discounts; do not subtract a discount twice (once in net revenue and again in reward cost). Multiply by 100 to show a percentage. With zero program cost the ratio is undefined: report contribution and costs separately.

**Illustrative margin check:** $10,000 net referred revenue at a 20% contribution margin is $2,000 before program costs. With $3,000 of program costs, the return is ($2,000 - $3,000) / $3,000 = -33.3%, even though revenue minus program cost looks like +233.3%. Revenue is not profit.

Attribution does not prove that every referred sale is incremental: some of those customers would have come anyway. Where possible, compare against a holdout or another defensible design. If you only have attributed sales, call the result "attributed contribution return", state the incrementality assumption and do not claim causal ROI. Keep observed cash recovery apart from projected lifetime contribution.

**Track separately:**
- Cost per referred customer (acquisition cost via referral).
- Lifetime value and retention of referred customers against other customers. Measure it; do not assume referred customers are better.
- Payback period for the rewards.

## Fixing an existing program

Use the user's own numbers to find the weakest step in the loop (trigger, share, convert, reward), then change that step only.

| Problem | Fix |
|---------|-----|
| Low awareness | Add prominent in-app prompts |
| Low share rate | One tap to share, a pre-written message, a better moment to ask |
| Low conversion | Improve the friend's landing page and offer; show the referrer's endorsement |
| Fraud or abuse | Add verification, limits and a payout hold |
| One-time referrers | Add tiers or recognition |

Tests to run, one change at a time: incentive (amount, type, single or double-sided, timing), messaging (program description, button text, landing page copy), placement (where and when the prompt appears).
