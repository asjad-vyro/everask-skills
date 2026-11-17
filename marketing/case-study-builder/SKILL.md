---
name: Customer Case Study Builder
description: >
  Turns a client win into ready-to-use proof: a proposal blurb, a social pull-quote and a sales story, or a full case study with real numbers.
  Use it for "write a case study", "turn this client result into social proof", "make a proposal insert from this win", "anonymize this client result".
---

# Customer Case Study Builder

A good result is a case study built only from the facts the user gave: the client is the hero, the user is the guide, and every number and quote appears exactly as supplied. The whole job is finished in one reply. Never open with questions.

## Step 1: Pick the mode

Choose from the user's words. Do not ask.

| Mode | Use when | What the reply holds |
|---|---|---|
| `quick` | "just something fast", "one line", "a blurb" | Format 1 only |
| `standard` (default) | no mode given, "social proof", "LinkedIn", "proposal" | Formats 1, 2 and 3 |
| `deep` | "full case study", "blog", "for the website", "FAQ" | Formats 1, 2, 3, plus Format 4 and Format 5 |

## Step 2: Build the fact sheet

Read the user's message and any attached or pasted material. Extract these eight fields, and write "not given" for any the user did not supply:

1. Client: industry, size or stage, named or anonymous.
2. Before: what was broken or painful, with any numbers.
3. Actions: what the user did, scope and role.
4. After: the results, with every number.
5. Timeline: how long the result took.
6. Quote: the client's exact words.
7. Naming: may the client be named? If the user did not say, anonymize (use a descriptor such as "a <industry> company") and say so.
8. Use: where the proof will be used.

Then do these checks:

- **Numbers.** List every figure the user gave, verbatim, with its unit and what it measures. Do not compute or show derived figures (differences, multiples, percentage changes) unless the user asked for that arithmetic. If they did, compute it in `execute_code` and use that output. Never do sums in your head. Show the formula in the fact sheet only if you derived a figure; label derived figures "calculated from your numbers".
- **Inconsistencies.** If the user's facts look inconsistent (for example "phone-only" before, yet a before figure for online bookings), record both facts exactly as given. Do not explain or resolve the conflict with a baseline or reason the user did not state. Flag it neutrally in "What is missing" as a question for the user.
- **Missing metric.** If the After field has no number, do not stop and do not invent one. Write the copy with the placeholder `[METRIC NEEDED: <what to measure, e.g. time saved, revenue change, lead volume>]` wherever a number would go, and use no stronger language than the result supports (see the tiers below). A rough estimate from the user is fine to use, marked as an estimate.
- **Quote.** Use the quote only if the user supplied it, word for word. If none was given, put `[QUOTE NEEDED: ask <client contact> for one sentence on <the change they noticed>]` in the quote spot. Never write a quote, and never put quote marks around a paraphrase.

Result tiers set how firmly to write:

| Tier | Type | Language |
|---|---|---|
| 1 | Hard metric the user gave | State it directly |
| 2 | Soft outcome (team aligned, calmer launches) | "For the first time..." only if the user said so; otherwise plain description |
| 3 | Indirect contribution | "Contributed to..." |
| 4 | Direction only ("much better") | "Noticeable improvement in..." with a metric placeholder |

## Step 3: Write the formats

Write every format from what the client experienced, not what the user delivered. Tell the story with a challenge in it: if the user gave no obstacle, do not invent one; describe the starting situation as given and note in the self-check that tension is thin.

Hard rules for every format:

- Use only facts from the fact sheet. No invented customers, names, dates, places, tool names, headcounts, prices, percentages or timelines.
- Each given figure appears exactly as the user wrote it. Rounding, "about" and "nearly" are not allowed unless the user said them.
- Do not add benchmarks, industry statistics or "typical" results.
- Do not invent feature descriptions, user-experience claims ("in a minute, on a phone"), customer behaviour, or site-, team- or location-level specifics the user did not state.
- Do not put a client name in the copy if the user wants it anonymous.
- Where a fact is not given, write around it or use a placeholder, never a guess.

**Format 1: Proposal blurb (two lines, under 45 words).** Shape: `<action verb> <what was delivered> for <client descriptor>. <outcome figure(s)> in <timeframe if given>.`

**Format 2: Social pull-quote.** If a quote was supplied, show it in quote marks with attribution as the user allowed (name and title, or an anonymized descriptor), then one line of context naming the headline figure. If no quote was supplied, show the `[QUOTE NEEDED...]` placeholder and, below it, a "headline-stat" version: one bold line stating the main figure, plus one line of context. Add two or three hashtag-free caption lines suitable for LinkedIn.

**Format 3: Sales story (150 to 250 words, four short paragraphs).**
- Set the scene: the client's situation and the stakes.
- Show the complexity: what made it hard, using only obstacles the user stated. If none were given, write one short plain sentence about the starting situation.
- What happened: only the actions the user stated, in their words (e.g. "rebuilt the online booking flow"), no feature lists. If the user gave no further detail, write one short generic sentence and add `[SCOPE DETAIL NEEDED: <what was changed>]`.
- What changed: the figure(s) and the shift for the client.

**Format 4 (deep only): Full case study.**

```
# Case Study: <client name or descriptor>
## The Challenge
## The Approach
## The Results
## Key Details
- Client / Industry / Timeline / Scope (use "not given" where missing)
## What Made This Different
## Client Quote
```

Results leads with the numbers. Keep the Challenge specific enough that a similar buyer recognizes their situation. Use the exact quote or the placeholder.

**Format 5 (deep only): FAQ variant.** Four to six questions a prospect would ask about this result (for example what was done, how long it took, what the numbers mean, whether it would fit a similar company), each answered only from the fact sheet. Where the facts do not answer a question, say what the user needs to supply.

## Step 4: Self-check

Before replying, check each format against this list, fix anything that fails, and put one line per format in the reply:

- Every figure matches the user's figure exactly, and none was added.
- The quote, if present, is word for word.
- The client is the hero.
- The blurb is two sentences or fewer and under 45 words; count the words one by one and report the true count.
- Read every sentence of every format and the fact sheet: each fact in it must appear in the user's message. Remove any that does not, and never write "nothing invented" until this check is done.
- The story's last paragraph contains the key figure or its placeholder.

## Step 5: Reply shape

Put everything in the reply itself, in full, in this order:

```
## Case study: <client descriptor>

### Fact sheet
<the eight fields; "not given" where missing; figures verbatim>
Result tier: <1-4>   Mode used: <mode>
Assumptions: <anonymized or named, mode chosen, anything inferred>

### Format 1: Proposal blurb
### Format 2: Social pull-quote
### Format 3: Sales story
### Format 4: Full case study            (deep only)
### Format 5: FAQ                        (deep only)

### What is missing
<a short list of placeholders to fill, e.g. each [METRIC NEEDED] and [QUOTE NEEDED], with what to ask the client; write "nothing" if complete>

### Self-check
<one line per format>

### Where to use each
<blurb: proposals, email bios, About section. Pull-quote: LinkedIn, website testimonials. Story: sales calls, posts. Full case study: website, PDF, RFP responses>
```

Do not publish a file unless the user asks for one. Do not send or post anything. Leave out an app-specific next step: if a quote is missing, the "What is missing" list is the next step.
