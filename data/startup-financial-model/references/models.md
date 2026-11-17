# Defaults and model variants

Read this when the user has not given an input, or the business is not SaaS. Everything here is a commonly quoted rule of thumb, not a fact about the user's company. Label any default you use as "assumed".

## SaaS defaults (early stage)
- Gross margin 75-85%; S&M 40-60% of revenue; CAC payback under 12 months; net revenue retention 100-120%.
- Retention curve if none given: month 1 100%, month 3 90%, month 6 85%, month 12 75%, month 24 70% (interpolate linearly; hold flat after month 24). If the user gave a flat monthly churn, use that instead.
- Fully loaded cost = salary x 1.3-1.4 (e.g. engineer $150K x 1.35 = $202.5K).
- Team mix: engineering 40-50%, S&M 25-35%, G&A 10-15%, customer success 5-10%.
- Hiring takes 3-6 months to fill and 3-6 months to ramp; attrition 10-15% a year. Add a 20% buffer to cost estimates when the user's costs look thin.
- Funding need = cash to reach the next milestone plus 6 months buffer.

## Marketplace
- Net revenue = GMV x take rate (10-30% by category). Model buyer and seller CAC separately; contribution margin 60-70%.

## E-commerce
- Revenue = visitors x conversion x AOV x purchase frequency. Gross margin 40-60%; contribution margin 20-35%; CAC payback 3-6 months.

## Services / agency
- Revenue = billable hours x rate x utilization (70-85%). Gross margin 50-70%. Revenue per employee is the key ratio.

## Scenario deltas (default)
- New customers +/-30%, churn +/-20% (relative), ARPU +/-15%, CAC +/-25%. Pricing structure, core opex and hiring roles are held fixed; shift hiring timing, not roles.

## Metric definitions
- Burn multiple = net burn / net new ARR. Magic number = net new ARR / S&M spend. Rule of 40 = growth % + profit margin %.
- Dilution = raise / (pre-money + raise).
