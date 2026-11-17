# Hypotheses and evidence

Read this at Step 4, after the drill-down, to build the hypothesis table.

## A testable hypothesis has three parts

1. Proposed cause: specific and falsifiable ("a change to the checkout flow hurt mobile conversion").
2. Predicted effect: what the data would show if it were true ("the drop is only on mobile, from one date").
3. Test: the cut of the data that confirms or refutes it.

"Something broke" is not a hypothesis. Name the segment, the date and the direction.

## Common causes by metric type (candidates to test, not conclusions)

- Revenue or sales: price change, payment failures, a large customer lost, a channel or campaign paused, stock-outs, seasonality or calendar effects (fewer trading days, a holiday), refunds or currency moves.
- Conversion rate: a bug or UX change in the funnel step, traffic mix shifting toward lower-intent sources, page-speed regression, tracking or tag change that stopped counting events.
- Engagement or retention: a feature removed or degraded, notifications or emails suppressed, onboarding change, cohort ageing, competitor move.
- Error or cost rate: a release, a dependency or vendor change, volume spike, a config change.
- Data issues (check these first): late or partial data in the latest period, a changed metric definition, duplicated or dropped rows, a tracking change, a timezone or cut-off shift.

## Decompose before you drill

- Additive metric (revenue, orders, signups): change per segment, share of the net change and of the gross movement. Also split revenue = volume x price (orders x average order value) if both columns exist.
- Ratio metric (conversion, churn, margin): overall change = rate effect (segments' own rates moved) + mix effect (the weight of segments moved). If the mix effect carries the change, nothing "got worse" inside segments: the traffic or customer mix changed. The script prints both for a ratio metric.
- When segments offset each other (net change near zero) judge by share of gross movement, not share of net.

## Evidence quality, best first

1. Controlled experiment (A/B test).
2. Natural experiment: a change reached only some users, and affected and unaffected groups diverge.
3. Before/after with nothing else changing at the same time.
4. Segment pattern that matches the hypothesis.
5. Timing correlation alone (weakest: needs support).

## Verdicts

- Confirmed: explains the timing, the size and the affected population, and no alternative fits as well.
- Refuted: the predicted pattern is absent, the timing is wrong (the metric moved before the cause), or the wrong population moved.
- Inconclusive: say what extra data would settle it.

## Confounders to rule out

- Day of week: compare the same weekdays across weeks.
- Cohort: new users behaving differently from old ones.
- Denominator: a different mix entered the funnel; compare the denominator, not only the numerator.
- Period length: unequal numbers of days or trading days in the two windows.

Report every hypothesis tested, including the refuted ones, so nobody re-investigates dead ends.

## Confidence

High: timing, size and population all match and the alternatives are refuted. Medium: strong segment concentration and timing, no controlled test. Low: correlation only. A cause that cannot be proven from the data is labelled "most likely", never "confirmed".
