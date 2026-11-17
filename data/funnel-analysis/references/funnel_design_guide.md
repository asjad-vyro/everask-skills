# Funnel design guide

## Defining steps
- Sequential: a user cannot reach step N without step N-1.
- Each user counted once per step.
- Steps are intentional actions (signup, add to cart), not page views that inflate the early steps.
- The first step is the denominator; every rate is relative to it.
- Anti-patterns: steps that can be done out of order; mixing session counts and user counts across steps.

## Two rates
- Step conversion = users at step N / users at step N-1. Use it to find where the biggest drop happens.
- Overall conversion = users at step N / users at step 1. Use it to describe funnel health.

## Time windows
- Open-ended: later steps count whenever they happen. Fits purchases that take days.
- Time-bounded: all steps within a fixed window from step 1 (for example 7 days). Fits onboarding.
- Cohort: group users by start date and give each the same observation window. Needed for a fair period-over-period comparison. Recent cohorts that have not had time to convert look worse than old ones.

## Prioritising drop-offs
- Rank by users lost, not only by rate. 40% lost at a step with 10x the traffic beats 40% lost at a late step.
- Recovery upper bound = users lost at the step x downstream conversion (final users / users at the step) x value per conversion. It is a ceiling, not a forecast: nobody recovers all of the lost users.

## Segments worth splitting by
- Acquisition channel (paid traffic often has lower intent).
- Device (mobile often drops at form steps).
- New vs returning users.
- Plan or price point.
- Small segments (under about 30 users entering) give noisy rates; say so instead of ranking them.

## Reading time between steps
A long median or P95 gap between two steps signals friction (slow page, waiting for verification email, unclear next step) even when the drop rate looks fine.

## Hypotheses to test for a leaking step
- Form or page too long, especially on mobile.
- Surprise cost (shipping, tax, fees) at the checkout step.
- Technical errors or slow load: check error logs for that step.
- A mismatch between what the ad or email promised and what the step asks.
- Tracking gap: the event fires only on some platforms, which looks like a drop that is not real. Check this first when a drop is extreme or only one device or platform shows it.

## Quality checklist
- Denominator and time window stated.
- Each user counted once per step.
- Every leaking step has at least one hypothesis and a next action.
- At least one segment split, if segment data exists.
