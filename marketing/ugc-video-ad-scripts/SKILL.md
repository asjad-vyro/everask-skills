---
name: UGC and Short-Form Video Ad Scripts
description: >
  Writes filmable UGC-style video ad scripts from a product and audience: several hook variants (spoken line, on-screen text, opening visual), body beats, CTA, delivery notes and disclosure lines.
  Use it for "write a UGC ad script", "TikTok creator script", "founder-led video ad", "testimonial video script", "5 hooks for a Reel ad".
---

# UGC and Short-Form Video Ad Scripts

A good result is a script package a creator can film today: hooks that are genuinely different angles, a body that pays off each hook, one clear ask, and disclosure lines already written in. Finish the whole job in one reply. Do not ask questions first.

## Step 1: Read the brief and fill gaps by assumption

Take everything from the user's message, pasted text and attachments. Work out: product and what it really does, offer, audience and awareness stage (unaware, problem-aware, solution-aware, product-aware), B2C or B2B, platform (default: vertical short-form feed), duration (default 20 seconds; B2B testimonial 45 to 90 seconds), performer (creator, customer, founder, employee, or uncast), markets, volume (default: 2 concepts, 4 hooks each, 2 CTAs), and any evidence given (reviews, comments, tickets, call notes).

Anything missing: choose a sensible default and list it under "Assumptions" at the top of the reply. Use `clarify` only if there is no product at all.

## Step 2: Build the evidence base

Real customer language is the raw material. Sources, in order of effort: public reviews or ad comments, support tickets, sales-call notes.

1. Use quotes the user supplied. If they gave none and the product is a real, public one, `web_search` or `web_extract` for recent public reviews and take a few.
2. Record each quote with: exact words, source, underlying desire or problem, emotional tag. Put this as a short "Evidence" table.
3. Hard rule: never invent a customer quote, review, testimonial, result, statistic, price or number. If the user gave no figure, do not write one. Where a number would help, write a bracketed slot such as `[your trial length]`, or leave the claim out.
   The same rule covers founder or employee backstory (origin stories, "I built this after...", "I paid for X for a year"), personal anecdotes, offer terms (free tier, "free to start", trial length, discount) and product features or behaviour the brief does not state. Write these as bracketed slots, e.g. `[founder: the moment you realised the problem]`, `[offer: e.g. free trial of [length]]`, `[feature from brief]`. Do not fill them in.
4. No evidence at all: say so, write from the brief alone, keep every line to what the brief states, and label every script `UNVALIDATED - voice-of-customer not sourced`. Lines that sound like a customer must be marked as example phrasing for the creator to replace with their own words.

## Step 3: Define concepts

A concept is one audience segment, one motivation (in the customer's words if you have them), one format. Fix the offer across concepts. Concept, hook and offer are three separate test variables: vary one at a time. Make concepts differ in angle (for example a time-saving angle versus a cost-of-the-old-way angle), not in wording.

## Step 4: Write the body

Fit it to the duration. Default spine is Problem, Solution, 2 to 3 value props, social proof, CTA, with PAS (Problem, Agitate, Solve) as the default frame. Use Before-After-Bridge only when the before state is already filmable. Beat split for 20 seconds: hook 0 to 3 s, value 3 to 15 s, proof or demo 15 to 20 s, CTA in the final 5 s. Under about 10 seconds under-communicates; past 45 seconds completion falls. Cut lines rather than lengthen.

- Name the moment the pain shows up, not a feature list.
- Use plain spoken words. No brand-speak in a person's mouth ("revolutionary", "cutting-edge", "game-changing", "#1").
- Keep the body fixed across hook variants; only the first body line is rewritten per hook so it extends that hook's premise.
- Estimate spoken time as word count divided by 2.5 words per second. Do this arithmetic in `execute_code` for each script and copy the result, so the timing column is right.

## Step 5: Write hooks (3 to 5 per concept)

Read `references/hook-archetypes.md` before writing hooks. Each hook is a triad: spoken line, on-screen text (3 to 7 words), opening visual. The three carry different information; never caption the visual with the spoken line. Each hook uses a different archetype from the reference, labelled in the table. Four hooks must be four different angles, not four rewordings. Generic test: if a competitor could say the opening line word for word, rewrite it. Open on motion, a face or the result, never a logo card.

Archetype menu rule: default to dialogue-only archetypes (skeptic's turn, problem callout, POV, question, confession). Add an asset-gated one (proof-first, silent review, before/after) only when the user has that asset. If a constraint rules an archetype out (health or weight-loss bars before/after; no footage kills silent review; no cleared result kills proof-first and bold claim), list it under "Deleted archetypes" with the reason; do not write it.

## Step 6: CTAs and delivery notes

- Two CTA variants, one ask each, no stacking (no "download, follow, use code and click the link"). Fake urgency ("today only") is banned unless the user gave a real deadline.
- Lock hook and CTA word for word. Locked lines may hold only facts from the brief plus bracketed slots. They must never hold an invented anecdote or offer term. If the user gave no offer terms, the spoken CTA reuses the same bracketed slot as the on-screen text (spoken "Try it free for [trial length]" with on-screen "[trial length] free"), never a concrete duration or "free". Brief the middle as beats with example phrasing the creator can say their own way. Fully locked scripts sound stiff; fully vague ones leave the creator to invent the strategy.
- Delivery notes per script: beat timings, what is on screen each beat, tone and read direction, setting, props to hold up, pacing, and a few do's and don'ts.
- On-screen text carries the message with sound off.

## Step 7: Compliance pass

Read `references/compliance-checklist.md` and run its checklist on every script. Disclosure lines are script lines: write them into an early beat, in the language of each market. Flag health, finance and supplement claims and say the package needs the advertiser's own legal review before filming. Rules change, so if you cite a specific law or regulation, check it with `web_search` and link what you found; otherwise describe the requirement generally. This is not legal advice.

## Step 8: Voice check

Reread every spoken line and on-screen text aloud in your head. Also check each line for a personal story, a feature or an offer term that the brief does not contain. Replace any you find with a bracketed slot. Use only archetype names that appear in `references/hook-archetypes.md`. Cut anything that sounds machine-written or like ad copy: stacked adjectives, "Discover", "Introducing", em-dash flourishes, tidy triplets. Spoken lines should be short, a little imperfect, and say things a person would actually say. Read `references/script-examples.md` once for the output shape and the failure example.

## Output shape (the reply itself, in full)

Keep the reply tight so it finishes quickly: delivery notes at most 5 lines per concept, no repeated boilerplate between concepts. Start with `Assumptions` (bullets) and the `Evidence` table (skip the table if there are no quotes). Then one package per concept:

1. **Concept**: segment, motivation (verbatim quote and source, or UNVALIDATED), format, offer, duration, performer.
2. **Hook variants** (table): number, archetype, spoken line, on-screen text, opening visual.
3. **Body**: table with time, spoken beat (example phrasing), on-screen text, visual. Note any per-hook transition line.
4. **CTA variants (2)**: spoken and on-screen wording, locked.
5. **Delivery notes**: read direction, setting, props, pacing, do's and don'ts.
6. **Compliance**: disclosure line(s) in plain words (e.g. "I'm the founder", "Paid partnership") with the markets they cover, claim notes, usage-rights reminder (creator usage rights must be signed before filming).
7. **Validation status**: grounded (with sources) or UNVALIDATED.
8. **Measurement plan**: the one variable this package tests (hooks, with body and offer held constant). Compare against the account's own trailing median hook rate and hold rate for the same placement, not a published benchmark. Diagnose in order: low hook rate means rewrite hooks; good hook rate but low hold means fix the body or transition; good hold but low click-through means the CTA; good click-through but low conversion means the offer or landing page.

End with "Deleted archetypes" (if any) and a one-line list of the edit combinations the shoot yields (hooks x CTAs against one body). Do not offer to produce video; the deliverable is the script text.

## B2B adaptations

Same spine and sound-off rules, but: lead with teaching, not pitching; credential the speaker in the hook; use Challenge, Solution, Outcome; avoid haul and discount-urgency framing; expect a buying committee, so write per awareness stage. Close the outcome with a result and a named role only if the user supplied one; otherwise leave a bracketed slot. Stand-ins for a creator testimonial: founder-led (fastest, weakest proof), employee-generated (real workflow on screen), customer testimonial (strongest proof, needs a documented result and their approval). Default to founder-led. If no documented customer result exists, say the customer testimonial is deleted for now.

## Hard rules

- No invented quotes, reviews, names, results, statistics, prices or benchmarks. Placeholders in square brackets for anything unknown.
- No invented founder or employee backstory, anecdotes, product features or offer terms (free tier, trial length). Use bracketed slots, and never put an invented one in a locked hook or CTA.
- Never write a fabricated testimonial or present an actor as a real customer without a disclosure line.
- One CTA per script. No fake urgency.
- Health, efficacy and finance claims only as the user supplied and can substantiate; no second-person "Do you have [condition]?" phrasing.
- Every script has a disclosure line when the performer received payment, product, commission or is an employee.
- Deliver the full scripts in the reply.
