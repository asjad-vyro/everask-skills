# Retention patterns, definitions and pitfalls

## Definitions (state which one you used)
- Period 0: the cohort's first period. Cohort size is every user who joined in that period, whether or not they were active in it. Period 0 is below 100% when some users did nothing in their joining period.
- Bounded (period-N) retention: share of the cohort active within period N. This is the default.
- Rolling (unbounded) retention: share active in period N or any later period. It never goes down.
- Churn = 100% minus period-over-period retention. If a steady churn of c per period is assumed, expected lifetime is 1/c periods (an assumption, say so).
- User retention is not revenue retention: for revenue cohorts (NRR, GRR) say the analysis only covers users, or build revenue per cohort with the same matrix on a revenue column.

## Cohort choices
Signup date (default); first purchase (commerce); first key action (products with an "aha" event); acquisition channel, plan or region (as a segment on top of signup-month cohorts). Retention event: a real core action (purchase, session with a key action, API call), not a page view or passive login. Any single event type must be deduplicated to one signal per user per period.

## Shapes and what to say
1. Flattens to a stable floor after early drop: a retained core exists. Name the period where it flattens and the floor level.
2. Keeps falling with no floor: no lasting value for that group; a product issue more than an acquisition issue.
3. Newer cohorts higher at the same period: improving. Newer lower: declining. Compare only at the same period number, and name what could explain it (release, channel mix, pricing) as a hypothesis, not a fact.
4. Sudden step down at one period: look for a trial end, contract term, billing date or one-off event at that period.
5. Spike later in life: reactivation campaign or seasonality.

## Pitfalls to check before reporting
- Immature cohorts: recent cohorts have fewer periods. Never compare a late period of an old cohort to a recent cohort that has not reached it. Blank cells mean "not yet observable", not 0%.
- Small cohorts: a cohort of 20 with 80% means 16 people. Flag cohorts under the minimum size and leave them out of averages.
- Averages hide cohort differences: report per cohort first, then a size-weighted average.
- Data gaps: if a period has no activity for every cohort, suspect a tracking outage, not a churn event.
- Activity before the cohort date, duplicate users and test accounts distort the rates: report how many rows were dropped.
- Segment comparisons need segments of similar size and age; say so when they are not.
