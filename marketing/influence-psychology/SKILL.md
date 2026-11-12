---
name: Persuasion Audit
description: >
  Scores your page, email or offer on 7 persuasion principles, flags manipulative tactics and rewrites the weak lines.
  Use it for "score my pricing page", "make this email more persuasive", "why aren't people converting", "is our countdown timer a dark pattern", "add social proof to my homepage", "get more people to say yes without being pushy".
---

# Persuasion Audit

A good result is a scored audit of the user's own page, email, offer or flow: which of the seven principles of persuasion it uses and how well, every deceptive or pushy tactic flagged and swapped for an honest one, and the weak lines rewritten with the principle behind each fix named. Persuasion helps people see value they would appreciate anyway; manipulation tricks them into choices against their interest. This skill does only the first.

## Step 1: Take in the material and pick the job

1. The material is whatever the user pasted, attached or linked. Read a URL with `web_extract`. If an image is attached and its text did not come through, look at it with `media_analyze`. If the user only described a page or flow, work from the description and say what you could not see.
2. Pick the job from the request:
   - **Audit** ("score this", "review", "why aren't people converting"): do Steps 2 to 6.
   - **Rewrite** ("make this more persuasive", "add social proof"): do Steps 2 to 6 and add the full rewritten text to the reply.
   - **Ethics check** ("is this a dark pattern", "is this allowed"): answer from Step 3 in under 200 words: the verdict (fine, a dark pattern, or depends on a named condition), the reason, and the honest alternative. No scorecard unless asked.
3. Note what the material is, who it speaks to and the one action it wants. If the user did not say, infer it from the copy and show it as "Assumed" in the reply.
4. Do not open with questions. Ask once with `clarify` only for an audit or rewrite that has no copy, link or description at all. With thin material, work with what is there, state your assumptions and deliver in full.

## Step 2: Find each principle in the material

For each of the seven principles, quote the shortest fragment that shows it, character for character (a changed word inside quotation marks is a misquote; for a flow, describe the step), or write "none" and rate it None. Before you write any fix, call `skill_view` on this skill with the file path to read the file for the principles with the biggest findings (Flagged first, then None, then Weak).

| Principle | A strong version has | Weak or flagged when | Read |
|---|---|---|---|
| Reciprocity | Real value given before the ask: a free trial or tool, useful ungated content, personal help | The gift sits behind a long form, strings are hidden, or the ask comes first | `references/reciprocity.md` |
| Commitment and consistency | A small voluntary first step; the user states a goal in their own words; later asks build on it; easy to undo | Pre-checked boxes, a trial that silently turns paid, cancelling harder than signing up, sunk-cost guilt | `references/commitment-consistency.md` |
| Social proof | Real, specific, current: exact counts, named testimonials with a result, logos, ratings with a source, people like the reader | "Thousands of happy customers", unnamed quotes, stale numbers, generated activity pop-ups, "most people don't..." framing | `references/social-proof.md` |
| Authority | Verifiable credentials, track record, certifications, expert voices, one honest limit stated up front | Superlatives with no source, borrowed badges, expertise stretched into another field | `references/authority.md` |
| Liking | A warm human voice, real people, the reader's own problem in their words, praise tied to something they did | Corporate boilerplate, stock faces, flattery with no basis | `references/liking.md` |
| Scarcity | A real limit (date, stock, capacity) stated exactly, with what changes after it | Timers that reset, "ends today" every day, "only 2 left" with no stock count, invented demand | `references/scarcity.md` |
| Unity | A specific shared identity or value ("for freelance designers"), built on what the group stands for | "Everyone" as the tribe; making a "them" to resent | `references/unity.md` |

Also read `references/copywriting.md` before you rewrite headlines, calls to action, emails or pricing pages. Read `references/ethics.md` when a tactic is borderline, the audience is vulnerable, or the user asks about the law. Read at most four reference files per job in all, these two included.

## Step 3: Run the ethics gate

Test every persuasive element in order:

1. **True**: is every number, quote, deadline, stock level and credential real? You cannot check the user's facts, so take them as true unless the material or the user's notes show otherwise. In flags, assert nothing the user did not say ("signup takes one click"). List what you could not check under "Verify".
2. **Transparent**: would it still work if the reader knew exactly what you were doing and why?
3. **Reversible**: can the reader say no or undo it easily (cancelling as easy as signing up, no pre-checked boxes, no hidden fees)?
4. **Helpful**: does it help the reader decide, or only push them to convert?
5. **Safe**: is it fair to vulnerable readers (children, people in financial stress, the elderly, the distressed)?

Always flag: countdown timers that restart or have no real deadline, evergreen "ends today" offers, "only N left" with no real stock, discounts from a price never charged, invented or unnamed testimonials, generated "someone just bought" pop-ups, credentials or press logos with no source, hidden fees, pre-checked boxes, trials that convert to paid without clear notice, cancellation that is harder than signup, and shaming opt-outs ("No thanks, I hate saving money").

If the user asks you to add a tactic that fails the gate (a fake timer, invented reviews), do not write it. Say why in one sentence and give the honest version that does the same job.

## Step 4: Score

Score the whole piece out of 10.

- **9-10**: several principles deliberately layered, every claim truthful, easy to reverse, still works if the reader knows the strategy, safe for vulnerable readers.
- **7-8**: principles layered and honest, with one gap, such as weak reversibility.
- **5-6**: one principle present but generic, or leverage left on the table.
- **4 or below**: no principle deliberately designed, or a deceptive or coercive tactic. Any fabricated proof, fake scarcity or hidden-cost dark pattern caps the score at 3, however strong the rest is.

## Step 5: Rewrite

Rewrite the weak and flagged lines, at most eight, the ones that matter most. Rules:

- **Facts.** Wording, labels and button text are yours to write; facts are not. Every fact in a line you write is the user's own words or numbers, arithmetic on their numbers, a bracketed `[placeholder]` for a figure, name, quote, logo, credential or date they did not give (such as `[number of customers]`), or an `[if true: ...]` condition. Never write a claim into the copy as fact and then list it under "Verify": if the user did not state it, it is a placeholder or a condition, or it is cut.
- **Typical slips.** Keep the user's own nouns: a count of "paying subscribers" stays "paying subscribers", not "families", and gets no added use ("plan their week", "run projects on"). Restate a credential with its exact scope ("advises us" stays "advises us"), and put what the person reviews or did in a placeholder. Do not add product features, how a feature works, what a plan includes, a pricing principle (such as "priced by projects, not people"), refund or guarantee terms, or processes and promises (reminder emails, "cancel any time", "email us and we'll reply") except as `[if true: ...]`. Do not infer trial or billing terms from hints: "card required" does not say the card is charged automatically, when, or how to cancel; keep it next to the trial. Write conditions without sample figures: `[if true: we email you before the trial ends]`, `[if true: <n>-day guarantee]`.
- List every placeholder and condition under "Before you publish". Suggest a product or policy change under "To reach 10/10", never inside the copy as if it already exists. Never invent figures, testimonials, customer names, awards, ratings or press mentions, in the copy or in the advice around it (write "a real customer count", not a sample number). The examples in the reference files are illustrations: never copy their numbers or names.
- On a pricing page, label the plan you recommend "Recommended" or "Best for <who it suits>". Use "Most popular" only if the user said it is. Work out who a plan suits, and write any headline, from the limits the user gave (a project or seat limit, say), not from an industry you guessed or a pricing principle. Check each headline and tagline against every plan on the page and drop any that one of them contradicts.
- Replace fake urgency with a real constraint the user confirmed (a cohort start date, a price-change date, a capacity limit). With no real deadline, use value and risk reversal instead (a guarantee, a free trial, cancel anytime), and only if the user's offer really includes them.
- Layer two or three principles on a page, not all seven: a landing page usually wants authority, social proof, liking and reciprocity. Keep the user's voice and length.
- **Last check.** Copy every quoted Before, flag and scorecard line from the user's text, never retype it ("love it" is not "love us"). Cut any After phrase that is not the user's words, arithmetic, a placeholder or a condition (such as "one bill" or a tier they never named). Name only the principle the After line applies.

## Step 6: Reply in this shape

The whole deliverable goes in the reply, starting at the score heading with no line before it, not in a file, unless the user asks for a file.

```
## Persuasion score: N/10
<One or two sentences on why. "Assumed: ..." for anything you inferred.>

## Principle scorecard
| Principle | Where it shows up (quote) | Rating | Gap |
<seven rows; Rating is Strong, Okay, Weak, None or Flagged>

## Ethics flags
- "<quoted line>": why it fails (false, coercive, hidden) -> the honest replacement. Write "None found" if there are none.

## Rewrites
**1. <where on the page>** (<principle>)
Before: "<the line copied character for character from the user's text>"
After: "<new line: the user's own facts, placeholders and conditions only>"
Why it works: <one clause on what the line does for the reader, with no claim about sales or conversion>
<one block per line>

## To reach 10/10
1. <the change that closes the biggest gap, with its principle>
<three to five lines>

## Before you publish
- `[placeholder]`: what real figure, name or quote to put there
- Verify: <a fact the user gave that you could not check>
```

For a Rewrite job, add `## Rewritten version` with the complete new copy after the Rewrites. If the user asked whether something is legal, search the web for the rules in their market, link what you found and end with: "This is not legal advice."

## Hard rules

- No invented facts, quotes, customers, numbers, sources, benchmarks, features or terms, in the copy or in the advice around it. What you cannot take from the user is a placeholder or a condition.
- No fake scarcity, fake proof, fake reviews or dark patterns in anything you write, even when asked.
- No claim that a change will lift or beat anything (conversion, sales, trust), advice included: no "converts better", "outperforms", "beats any", "costs you the sale", "does more than any", "the strongest" or "will out-persuade". Tests are suggestions.
- Do not call a tactic illegal or legally risky, or mention regulators or fines, unless the user asks. Never quote laws from memory. Search, link, and say it is not legal advice.
- Finish in one reply: no question and no offer to do more ("say so and I'll...") anywhere in it.
