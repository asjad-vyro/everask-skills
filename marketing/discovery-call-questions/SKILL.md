---
name: Discovery Call Question Planner
description: >
  Builds a ready-to-use discovery call sheet: sequenced questions sized to the call length, follow-ups, branches and a do-not-ask list.
  Use it for "discovery call questions", "what should I ask this prospect", "qualification questions", "first meeting agenda", "SPIN questions", "prep me for a discovery call".
---

# Discovery Call Question Planner

A good result is one call sheet a rep can skim 20 minutes before the call: a few well-ordered questions that find a real problem, its cause, what it costs in the prospect's own numbers, and why now, ending in a dated next step. It works for B2B (SDR qualification through multi-stakeholder discovery) and for considered, high-ticket B2C consultations (remodeling, coaching, financial advice).

Never stop to ask the user questions. Work from what they gave you, decide the rest, and list your assumptions on the sheet. The whole sheet goes in the reply itself, in full.

## Step 1: Read the inputs and fill gaps

Pull out of the user's message: B2B or B2C; the persona and seniority; what the product does and the problem it solves; call type and length in minutes; inbound or outbound; what is already known about the prospect; the success outcome (next step) and any date; any methodology the team mandates (SPIN, MEDDPICC, Sandler, GAP).

For anything missing, pick a sensible default and write it under "Assumptions" on the sheet: 30 minutes if no length is given; B2B unless the user describes a consumer service; outbound unless they say the prospect asked for contact; success = a booked, dated next meeting. Use placeholders such as `<product>` or `<persona's process>` where the user gave no specifics. Never invent facts about the prospect or their company: no company details, figures, names or quotes the user did not provide. If the user names a company and you have a spare web search, one `web_search` or `web_extract` call for public facts is fine, but the sheet works without it. Research answers situation questions so the call does not have to.

## Step 2: Write 2-3 pain hypotheses

State each as a guess to test, never a fact to confirm. If the user named a pain, it is H1. Otherwise derive them from the persona, the product's problem and the situation. Mark them "hypothesis".

## Step 3: Size the set to the call

Count the questioning minutes: call length minus about 3 minutes for the frame and 3 for the close. Plan one primary question plus its follow-ups per 3-4 minutes. Do this arithmetic in `execute_code` and copy the result into the sheet; do not do it in your head. Examples of the method: 15 minutes leaves about 9, so 2-3 primaries; 45 minutes leaves about 39, so 9-12. Executives get about half the count, with the sharpest hypothesis first and no situation questions. Never cite a "magic" question count; the size comes from the minutes.

If the budget is tight, cut from the tail in this order: decision context, technical impact, extra situation questions. Never cut root cause or business impact. If the user mandates a methodology, label each stage with its vocabulary and drop the other frameworks' labels. A transactional or B2C deal has no decision-context stage.

## Step 4: Draft the questions

Read `references/question-bank.md` before drafting. Rewrite every wording into the persona's vocabulary and the deal's specifics. Follow the spine, one-way, in this order:

1. **Frame**: one-line agreement on purpose, time and possible outcomes.
2. **Situation**: at most 1-2 questions, only what research could not answer.
3. **Pain**: a named problem with a recent, specific example.
4. **Root cause**: why it happens and what they already tried. Cause, not symptom.
5. **Impact**: at least one figure in the prospect's own number, across at least two of technical, business and personal (B2C leads with personal: household time, money, stress).
6. **Urgency**: why now and what happens if nothing changes. If there is no compelling event, record that honestly; never manufacture one.
7. **Decision context** (complex B2B only): how a decision would get made, who else has a say, what success would look like. Questions only, no scoring.
8. **Close**: a summary in the prospect's words, then a dated next-step ask.

Each primary question gets a 2-3 rung follow-up ladder (tell me more, give me a specific example, how long, what have you tried, what did it cost) and a "listen for" note. Rules for every question:

- Open before closed; closed questions only confirm or quantify.
- One idea per question. No compound or stacked questions.
- No leading questions (the answer embedded in the wording).
- Past-specific over hypothetical: "when did that last happen" beats "what would it cost if".
- Product-agnostic until the close; the product enters after the gap is established.
- Let the prospect say the number. Never supply a figure for them.
- Budget, timeline and "who decides" are never openers; they come after impact.
- Every question must change what the rep does next. Cut any that would not.

## Step 5: Add branches and the do-not-ask list

Branches are unranked, each fires on its own condition: no pain after two hypotheses (switch hypothesis or ask "What would have to be true for this to be worth your time?"); impact volunteered early (bank it, return for root cause); an executive joins (halve the questions, lead with the sharpest hypothesis); answers stay surface-level (drop one ladder rung rather than moving on); price or demo asked mid-call (brief answer, then trade one more stage of questions). B2C couples: ask pain and impact to each person separately.

The do-not-ask list holds the generic offenders from `references/question-bank.md` plus two or three leading or hypothetical questions specific to this deal.

## Step 6: Check the set, then reply

Check the draft against this list and fix anything that fails before you reply:

1. Every question maps to one stage; no stage empty without a stated reason.
2. Each stage opens open-ended.
3. Root cause is probed before impact, and impact has a quantifying question before any urgency question.
4. Impact covers at least two dimensions.
5. No leading and no compound questions.
6. Past-specific wherever possible.
7. Logistics only after impact.
8. The set fits the call length per Step 3.
9. No question that changes nothing.
10. Ends with a summary prompt and a dated next-step ask, and has branches and the do-not-ask list.

## Output shape

Read `references/call-sheet-template.md` and fill it in. The reply has, in this order:

1. The call sheet itself (the template, complete, in the reply).
2. **Assumptions**: a short list of what you decided because the user did not say.
3. **Time budget**: the minutes available, questions planned, and the arithmetic from `execute_code`.
4. One closing line: the sheet is a map, not a script; follow the prospect's answers and use the branches.

## Hard rules

- Never state a fact about the prospect, company, market or pain as true unless the user gave it or a tool returned it. Write "not given" or mark an assumption.
- Use no invented statistics, benchmarks, customer stories or quotes. Do not cite question-count or talk-ratio benchmarks.
- No pricing, ROI claims or product pitch inside the question path.
- Regulated buyers (healthcare, finance, government) and regulated B2C categories: add procurement or compliance-path questions, and tell the user to check what can be asked with their compliance team. This is sales-coaching guidance, not legal advice.
