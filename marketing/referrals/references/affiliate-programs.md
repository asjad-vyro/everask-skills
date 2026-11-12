# Affiliate and Partner Programs

Read this for any program that pays partners (creators, bloggers, newsletter writers, consultants, agencies, complementary products) a commission, as opposed to a refer-a-friend loop among customers. Work through sections 1 to 7 (section 8 is optional), then write the reply in the shape in section 9. Use the user's figures and mark every other figure "Assumed".

## Contents
1. Economics, commission structures, attribution window
2. Recruiting and activation
3. Executable rules (terms decisions, disclosure)
4. Enablement, reconciliation, payouts
5. Fraud and abuse
6. Measuring growth
7. Super-promoters and launch pushes
8. Tools (optional)
9. Reply shape

## 1. Check the economics before you offer a rate

Use collected, eligible revenue and the business's actual variable costs, refund and churn history, partner support, tooling, recruitment and payout fees. Decide whether taxes, discounts, refunds, renewals, upgrades and existing customers belong in the commission base. A headline percentage without its base and duration is not an offer.

```text
cohort contribution = collected eligible revenue after refunds
                    - product or service variable costs
                    - affiliate commissions
                    - partner support and program operations
                    - payout fees
```

Illustrative cohort, not an industry benchmark: $12,000 collected minus $2,000 refunds leaves $10,000 eligible revenue. At 20%, commission is $2,000. With $3,000 variable costs, $800 partner support, $1,200 program operations and $100 payout fees, contribution is $2,900. State the period, and do not count support in both variable costs and operations. A deferred or clawed-back commission needs its own ledger entry, not a second subtraction of the same refund.

For recurring commissions, model actual retention and commission duration by cohort. For lead or demo bounties, define the accepted action, and how duplicates, cancellations and qualification are treated, before you quote a rate. Compare with the acquisition cost and payback period used for other channels. Attributed revenue alone does not prove incremental revenue.

**Commission structures.** The ranges below are commonly quoted starting points, not benchmarks: the user's margin decides.
- **Percentage of sale:** often 10-30% of the first sale or first year. Fits e-commerce and SaaS with clear pricing. "Earn 25% of every sale you refer."
- **Flat fee per action:** often $5-500 depending on value. Fits lead generation, trials and freemium. "$50 for every qualified demo."
- **Recurring commission:** often 10-25% of recurring revenue. Fits subscriptions. "20% of the subscription for 12 months."
- **Tiered commission:** motivates high performers. "20% for 1-10 sales, 25% for 11-25, 30% for 26+."

**Attribution (cookie) window:** how long after a click the affiliate gets credit. Choose it from the buying cycle.

| Window | Use case |
|--------|----------|
| 24 hours | High-volume, low-consideration purchases |
| 7-14 days | Standard e-commerce |
| 30 days | Standard SaaS or B2B |
| 60-90 days | Long sales cycles, enterprise |
| Lifetime | Premium affiliate relationships |

## 2. Recruit for an audience and an activation plan

Where to find affiliates: customers who create content, industry bloggers and reviewers, YouTubers in the niche, newsletter writers, complementary tool companies, consultants and agencies. Editorial publishers, consultants, complementary products, creators and coupon partners differ: some introduce new demand and some intercept a purchase that was already coming.

Build a small shortlist with audience evidence, relevant content, channel and a realistic first placement. Name real prospects only if you found them with `web_search` or `web_extract` in this conversation, and link each one. Otherwise give partner types and where to look.

Use a funnel with denominators: qualified candidates, contacted, accepted, activated, first accepted conversion, retained productive partner. Count distinct partners, because several placements can belong to one partner. An accepted application or a generated link is not an activated partner: activation means a real, approved placement or campaign.

Prepare the offer: audience fit, commission base, rate and duration, eligibility, allowed channels, payment timing, support contact and the proposed first activity.

**Outreach template** (a draft; do not claim familiarity with work you have not reviewed):
```
Subject: Partnership opportunity - [Your Product]

Hi [Name],

I've been following your content on [topic], particularly [specific piece], and think there could be a good fit for a partnership.

[Your Product] helps [audience] [achieve outcome], and I think your audience would find it useful.

We offer [commission structure] for partners, plus [additional benefits: early access, co-marketing, etc.].

Would you be open to learning more?

[Your name]
```

## 3. Make the rules executable

Fill in this terms decision table with a recommended answer for each row. It is for the user's review, not invented legal boilerplate.

| Decision | Specify |
|---|---|
| Attribution | Link or code priority, window, repeat purchases, cross-device gaps, competing partners |
| Eligible conversion | New or existing customer treatment, accepted lead or order, refunds and cancellations |
| Channel policy | Brand bidding, coupon publishing, email outreach, paid ads, self-referrals, sub-affiliates |
| Commission | Base, rate, duration, tier transitions, currency and rounding |
| Payout | Hold period, threshold, schedule, verification, disputes, chargeback handling |
| Changes and exit | Effective date, treatment of accrued commissions, notice, dispute contact |

Do not promise a tracking rule the user's tool cannot implement. Legitimate coupon partners are not automatically fraud. Shared IPs or devices are a signal for review, not proof of abuse. Apply rules consistently and keep the evidence for decisions.

**Disclosure.** Partners should state the material connection clearly, near the recommendation or link, not on a hidden terms page and not with an ambiguous label. Example draft: "I earn a commission if you buy through this link." Match the real relationship; do not invent personal use or approve unsupported product claims. For US-facing endorsements, check the FTC's current endorsement and affiliate-disclosure guidance with `web_search` and link the page you found. Other countries and channels have their own guidance: say so.

## 4. Enable, reconcile and support

Give every partner:
- [ ] A tested tracking link or code
- [ ] Product overview and key benefits
- [ ] Target audience description
- [ ] Comparison to competitors (truthful)
- [ ] Creative assets (logos, banners, images)
- [ ] Sample copy and talking points
- [ ] Case studies and testimonials (real, permissioned)
- [ ] Demo access or a free account
- [ ] FAQ and objection handling
- [ ] Payment terms and schedule, disclosure guidance, a first-placement plan and a support contact

Test the customer journey and attribution with test data before inviting a wider cohort.

Reconcile each eligible conversion to a commission state (pending, approved or due, paid, refunded or adjusted, disputed) using the platform's actual states. Keep stable order, customer and partner identifiers and the policy version in force. Replayed webhooks and exports must not count a conversion or a payment twice.

Choose the hold period from real refund and cancellation exposure and the agreed terms. Check in the platform's own documentation whether it only calculates commissions or also sends payouts: marking a commission paid is not necessarily a money transfer.

Review the partner cohort regularly: inactive partners may need an asset or a clearer audience fit, and productive ones may need better landing pages or support. Settle a disputed sale from the actual attribution record, the policy and the refund state. Do not silently change earned commissions after the fact to make a report look better.

## 5. Fraud and abuse

**Common patterns:** self-referrals through fake accounts, rings of partners referring each other, unauthorized coupon distribution or attribution interception, fake email addresses, VPN or device spoofing.

**Technical:** email verification, device fingerprinting, IP monitoring, delayed payout until activation, a minimum activity threshold.

**Policy:** clear terms of service, a maximum number of referrals per period, clawback for refunds and chargebacks, manual review of suspicious patterns.

**Structural:** require the referred customer to take a meaningful action, cap lifetime rewards, consider paying in product credit.

## 6. Measure growth separately from attribution

Report active placements, accepted conversions, collected eligible revenue, refund and churn by cohort, commissions pending, due and paid, total program cost and contribution. Keep new customers apart from existing-customer upgrades and late coupon touches. Follow acquisition quality through retention instead of optimizing raw clicks.

Where possible, compare a bounded partner rollout or a holdout with an equivalent untreated cohort. Label observational comparisons and attribution limits honestly. Cookie or code attribution assigns credit; it cannot show what would have happened without the affiliate.

## 7. Super-promoters and launch pushes

These are commonly quoted rules of thumb, not facts about the user's program. Test them against the user's own data.
- **A few partners drive most results.** The "20/80" rule says roughly a fifth of affiliates produce about four-fifths of results. Do not spread effort across a long tail of dormant sign-ups. Find the super-promoters and invest in them: higher tiers, custom assets, co-marketing, a direct relationship, early access. Ten activated partners are worth more than a thousand passive ones.
- **Buyout clause.** For high-performing affiliates on recurring commissions, some programs reserve the right to buy out the future commission stream for a lump sum, often quoted at around 12 times the monthly commission. Treat that as a negotiating starting point, and get the terms reviewed.
- **Launch pushes.** Time partner promotion around a launch or a hard deadline to concentrate volume. Give partners a shared date, shared assets and a reason for their audience to act now (a bonus, a cohort, a closing offer), so promotion stacks instead of trickling.

## 8. Tools (optional)

Start without one if the first cohort is small: unique codes or links plus a spreadsheet. Tools people use (descriptions may be out of date, so check each vendor's current features and price before you recommend one, and quote no prices from memory):
- **Referral platforms:** ReferralCandy and Friendbuy (e-commerce), GrowSurf (SaaS), Ambassador and Mention Me (larger brands), Viral Loops (template campaigns).
- **Affiliate platforms and networks:** Impact, PartnerStack, Tapfiliate, FirstPromoter, Rewardful and Tolt (SaaS, often Stripe-based), Refersion (e-commerce). Dub is a link-tracking option.

Choose by: integration with the payment system, fraud detection, payout management, reporting, customization and price against program scale.

## 9. Reply shape for an affiliate program

Put all of this in the reply, in this order:
1. **What I'm working from:** the user's figures, then "Assumed:" lines.
2. **Economics:** commission base, rate and duration with the cohort arithmetic and a one-line verdict.
3. **Terms decisions:** the table above, filled in.
4. **Recruiting:** partner types, where to find them, the activation funnel, and one outreach email in full.
5. **Enablement checklist** and the **fraud and abuse rules.**
6. **Small launch plan:** first cohort, first placements, a first-30-days review, and the stop criteria set from the user's margins.
7. **Numbers to watch.**
8. One closing line: a working draft, not legal advice; have the terms and disclosure wording checked.

Recruiting, policy changes and payouts stay drafts until the user says to go ahead.
