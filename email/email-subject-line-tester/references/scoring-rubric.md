# Scoring rubric

Score each variant in two passes: hard fails first, then the 10-point scorecard. A shipped variant needs at least 8/10 and zero hard fails.

## Hard fails (score 0, rewrite)
- Fake "Re:" or "Fwd:" prefix, or any framing implying a conversation that never happened (deceptive subject lines are what CAN-SPAM prohibits).
- The subject promises something the body does not deliver.
- Spam-trigger vocabulary in the subject: "free", "guarantee", "act now", "limited time", "click here", ALL CAPS words, stacked "!!!" or "???".
- B2B cold only: the prospect's first name in the subject (a mail-merge signal).
- Over the truncation budget: about 35 characters B2B cold, about 50 B2C.
- Duplicate angle: differs from another variant only in wording.

If a user's own offer is genuinely free shipping or similar, the word may be the honest wording: still flag it, score it, and offer a rewrite without the trigger word.

## 10-point scorecard
| Criterion | Points | Full marks means |
|---|---|---|
| Length and truncation fit | 0-2 | B2B cold: 1 to 4 words, within about 35 characters. B2C: within about 50 characters, preview text 90 to 140 characters that extends and never repeats the subject |
| Angle execution | 0-2 | Concretely expresses the chosen angle, not a generic gesture at it |
| Reader's-world framing | 0-2 | Anchored to the recipient's job or life, not the sender's product; no salesy verbs, urgency words or pitch |
| Body-promise match | 0-2 | The body's opening fully honors what the subject implies |
| Set distinctness | 0-1 | Angle genuinely distinct from every other variant |
| Human sound | 0-1 | Reads like something a person would type; no templated AI phrasing |

## Table shape
| # | Subject | Angle | Words / chars | Score | Notes |
|---|---|---|---|---|---|
| A | `<subject>` | `<angle>` | `<computed>` | `<n>/10` | `<control, challenger, or why it fails>` |

Add `Preview text` for B2C. Score arithmetic is the sum of the six criteria; add them in `execute_code` if there are many rows.
