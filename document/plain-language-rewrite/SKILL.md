---
name: Plain Language Rewrite
description: >
  Rewrites jargon-heavy text in plain language for a named audience, with a table showing every fact, number and condition survived.
  Use it for "make this readable", "plain-English version of this", "translate this for non-experts", "de-jargon this announcement", "rewrite this so my customers understand it".
---

# Plain Language Rewrite

A good result is a translation, not a summary: every fact, number, condition and hedge in the original survives, and only the packaging changes (sentence length, word choice, structure). Most jargon is replaced. A few terms of art are kept and defined, because the reader will meet them again. "Usually", "up to" and "unless" are content, not decoration: a rewrite that drops them is a different document.

The whole job is done in one reply, with the rewrite and the checks written out in full. Do not open with questions.

## Step 1: Fix the inputs

1. The text is what the user pasted or attached. If they gave only a topic and no text, ask once with `clarify` for the text. Otherwise never ask.
2. The audience is what the user said ("customers who don't know insurance", "new hires"). If none was given, assume "an intelligent adult with no background in this field", and say so in one line.
3. The stakes: legal, medical, financial, safety or contractual text must keep every hedge exactly in meaning. Marketing or internal-announcement text has more freedom. State which you assumed.
4. Missing facts (a date, an amount the text refers to but doesn't give): never invent them. Leave a bracketed gap such as `[amount not given]` in the rewrite.

## Step 2: Extract the claims list before rewriting

Number every claim in the original: each fact, figure, date, amount, percentage, deadline, condition ("if", "unless", "provided that"), limit ("up to", "at least", "no more than"), hedge ("usually", "may", "typically"), exception and obligation (who must do what). Copy figures exactly as written. If the text has many sums or percentages to restate, check any arithmetic with `execute_code` and never do it in your head.

## Step 3: Triage the jargon

Give each jargon term or phrase one verdict.

- **Translate**: internal shorthand, abbreviations and padding ("utilize" becomes "use", "prior to" becomes "before", "remit" becomes "pay").
- **Keep and define**: terms of art that are contractual, regulatory, or that the reader will see again on a form, bill or policy ("deductible", "force majeure", "APR"). Keep the term and define it in plain words the first time it appears.

Never rename a term of art without keeping the original beside it.

## Step 4: Rewrite

1. Fix the structure first: one idea per sentence, subject at the front, active voice, an average near 20 words and none over about 30. Use a short list for parallel items and a numbered list for steps in order. Put what the reader must do or what affects them most first, unless order matters legally.
2. Then fix the words. Aim slightly simpler than the audience's level, but never talk down: plain and respectful are the same register.
3. Keep every claim from Step 2. Keep the original's order of conditions where order changes meaning. Don't add advice, examples with invented numbers, or reassurance the original does not contain.
4. If the text must serve two very different audiences (experts and novices), say that one text can't do both well, and write for the audience the user named.

## Step 5: Check fidelity

Go through the claims list one by one against the rewrite. Fix the rewrite until nothing is lost, hedges included ("usually" never becomes "always", "up to" never becomes "exactly"). Any deliberate cut is listed with the reason. Then re-read the rewrite as the target reader and note anything still unclear.

## Output shape

Write all of this in the reply, in this order:

```
# Plain rewrite: <what the text is> for <audience>

Assumptions: <audience, stakes, any gaps, one line each; omit if none>

## The rewrite
<the full rewritten text>

## Fidelity check
| # | Original claim, number or qualifier | Where it survives in the rewrite |
|---|---|---|
| 1 | <quoted from the original> | <the sentence or phrase in the rewrite> |

Lost or cut on purpose: <none, or each item with the reason>

## Jargon ledger
| Term | Verdict | Rendered as |
|---|---|---|
| <term> | Translated / Kept and defined | <plain wording, or the definition> |

## Readability
Average sentence length: before <n> words, after <n> words (count with `execute_code`). Longest sentence in the rewrite: <n> words.
Self-check: <one or two sentences: could the target reader retell it, and did any hedge or condition change meaning?>
For legal, medical or financial text: <one line that this is a readability rewrite checked by an AI, not professional advice, and a qualified person should confirm it before it is relied on>.
```

For the word counts, split on sentence ends in `execute_code` and copy the numbers; don't estimate.

## Hard rules

- Don't simplify by deletion. Dropped hedges, limits and exceptions are the worst failure.
- Every number, date, amount and name in the rewrite comes from the original. Nothing invented.
- Don't claim a human expert or a real reader tested it. The self-check is yours and is described as such.
- Keep the fidelity table complete: every number in the original appears in it.
- Don't ask for details the user can leave to your judgment; decide and state the assumption.
