# Segmentation playbook

## RFM scores

Each customer gets three scores from 1 to 5 (5 is best), by rank within this customer list:
- R (recency): days since last order, fewer days scores higher.
- F (frequency): number of orders. Customers with the same count share a score, so many one-order customers all get F = 1 (or the same low score).
- M (monetary): total spend.

The script then assigns one segment per customer, first match wins:

| Segment | Rule | Who they are | Action to propose |
|---|---|---|---|
| Champions | R 4-5, F 4-5, M 4-5 | Bought recently, often, big | Reward and recruit: early access, referral ask, review request. Do not discount; they already buy. |
| Loyal | R 3-5, F 4-5 (not Champions) | Frequent buyers, less spend or slightly less recent | Upsell to higher-value items, loyalty perks, bundles. |
| Potential Loyalists | R 4-5, F 2-3 | Recent, a few orders | Second and third purchase nudges: replenishment, complementary products, membership. |
| New Customers | R 4-5, F 1 | Recent first order | Onboarding sequence, second-order incentive within the usual repeat window. |
| Promising | R 3, F 1-2 | Middling recency, few orders | Brand-building content, a light second-purchase prompt. |
| Need Attention | R 3, F 3+ | Above-average buyers cooling off | Time-limited, personalised reminder before they slip. |
| At Risk | R 1-2, F 3+ | Used to buy often, gone quiet | Win-back: personal message, "we miss you", ask what changed, an offer sized to their past spend. |
| Cant Lose | R 1, F 4-5, M 4-5 | Biggest past customers, now silent | Top-priority personal outreach (call or personal email), not a mass discount. |
| Hibernating | R 1-2, F 1-2 (not Lost) | Low-activity, fairly old | Low-cost reactivation email; suppress if no response. |
| Lost | R 1, F 1 | One order, long ago | Last-chance email, then stop spending on them. |

## Reading k-means clusters

The script standardises log-recency, log-frequency and log-spend, tries 3 to 6 clusters (or the number asked) and numbers clusters by average spend (1 = highest). Name each cluster from its table row:
- High spend, many orders, low recency days: best customers.
- Moderate spend, several orders, high recency days: lapsing regulars (win-back).
- Low spend, about one order, low recency days: new customers.
- Low spend, about one order, high recency days: lost one-timers.

Judge the fit with the silhouette score: above 0.5 clear groups; 0.25 to 0.5 usable but overlapping; below 0.25 not meaningful, so recommend RFM or a rule-based split instead. More clusters than the user can act on (over about 6) is not useful.

## Rule-based and field segments

When the user wants segments by an existing field (plan, channel, region): group by it, report n, share, average of the metric and index = segment average / overall average x 100. An index of 120 or more over-indexes, 80 or less under-indexes. Also report the share of revenue per segment.

## Checks before you reply

- Simpson's paradox: if the user compares two groups overall (for example channel A against B), check whether the result holds within each segment.
- Small segments: under about 30 customers are unreliable; merge or caveat.
- Survivorship: an orders file contains only people who bought; say that non-buyers are not in the analysis.
- Size bias: the biggest segment will dominate totals; compare averages and indexes, not only totals.
- Time window: a short window makes everyone look new, a long window makes everyone look lapsed. State the date range used. Recency cut-offs from quintiles depend on it.
- Currency and refunds: the script drops orders of 0 or less; mention how many.
