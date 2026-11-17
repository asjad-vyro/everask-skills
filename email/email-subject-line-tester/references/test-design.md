# Test design

Benchmarks are vendor-reported and unaudited: calibrate expectations, not targets.

## One variable, no peeking
- Test one variable: the subject angle (for B2C, the subject plus preview text pair). Hold sender name, send time, body and audience constant.
- Fix sample size and duration before launch. Stopping early on an apparent winner manufactures false positives. A changed variant is a new test.

## Sample size
Rules of thumb (floors, not power calculations; say so):
- Outbound: 200+ sends per variant for a subject test.
- List-based ESP campaigns: about 20% of the list split across the test variants, winner to the rest. On a small list this can be underpowered.
- Three variants need about 1.5x the total sends of two, four need about 2x. At low volume cap at 2 or 3 variants.

Power calculation (95% significance, 80% power, two-sided, two proportions). In `execute_code`:

```python
from math import ceil
def n_per_variant(p1, p2):
    z = (1.96 + 0.84) ** 2
    return ceil(z * (p1*(1-p1) + p2*(1-p2)) / (p1 - p2) ** 2)
```

Use the user's baseline as p1 and baseline plus a stated lift as p2. Show the result for two or three lifts (for example a modest, a medium and a large relative lift, chosen by you and labelled as assumptions). Compare with the sends actually available: if available per variant is below the requirement, say the test can only detect the larger lifts, and what lift it can detect (solve with the same function or a short loop). For a list of N split into k variants, per-variant sends are N / k.

Duration: at least one full week to cover day-of-week effects; 2 to 4 weeks is typical for outbound. For a single list send, the test window is the first send hours before the winner goes out; say what you assume. B2B avoids weekends; B2C should test them.

## Metric
- Open rate has been distorted since 2021: mail-privacy features pre-fetch tracking pixels, registering opens nobody made. Treat opens as directional only.
- B2B cold: decide on reply rate by default (auto-counted); positive replies if reply volume is high; meetings booked if the sequencer writes to the CRM. Never call a winner on opens alone.
- B2C lifecycle: open rate is usable as the primary read for a subject test, paired with click or conversion so a winner that attracts opens and repels action is caught. Name the single metric that calls the winner.

## Guardrails (a winner that trips one loses)
- Unsubscribe rate under 0.5%.
- Spam complaints under 0.1%.
- Bounce rate: a significant rise points to a list or sending problem, not a subject result.

## Calibration (vendor-reported, direction only)
B2B cold: average open around 28%, reply 4 to 6%, falling year on year. B2C lifecycle: open 20 to 40% by sequence type. Use only to sanity-check a baseline the user gave, never to fill in a missing one without labelling it an assumption.

## Test plan shape
- **Hypothesis**
- **Variants**: IDs and angles, all at or above the quality gate
- **Split**: for example 50/50, or 20% of the list for the test and the winner to the remainder
- **Sample per variant**: the number, and whether it came from a rule of thumb or the power calculation
- **Duration**: minimum one full week for outbound; state assumed dates as relative ("day 1 to day 7")
- **Decision metric**: one metric
- **Guardrails** with thresholds
- **Result**: winner, loser or inconclusive; inconclusive is a valid outcome
- **Next hypothesis**: one variable from the queue in `references/pattern-library.md`, or "volume does not support another test"
