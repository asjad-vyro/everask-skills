---
name: Sales Call Scorecard
description: >
  Scores a sales call transcript on opener, discovery, objection handling and close, quotes the transcript for every judgement, and names the one behaviour to fix next call.
  Use it for "score this call", "review my call transcript", "how did this call go", "tape review", "coach me on this demo call", or a pasted Gong or Chorus transcript.
---

# Sales Call Scorecard

Score one completed sales call from its transcript against four anchored dimensions, with every judgement backed by a verbatim quote. Deliver a short, bounded review: at most 2 strengths, at most 3 change items and exactly 1 focus behaviour. The review judges what the rep did on this call and stops there. It does not write the rep's next script, score the deal or draft the follow-up email.

The review goes in the reply itself, in full. It is coaching guidance on one call, not an employment decision or professional advice.

## Hard rules

- **No quote, no score.** Every score, strength and change item cites a verbatim passage from the transcript with its location. If nothing supports a judgement, write "insufficient evidence" and leave it unscored or Low confidence. Never paraphrase from memory or invent a quote.
- **Nothing invented.** Names, numbers, dates, outcomes and company details come only from the user or the transcript. If something is not given, write "not given".
- **The outcome grades nothing.** A booked meeting does not prove a good call and a lost deal does not prove a bad one. Record the outcome as context only.
- **No character language.** Words like "confident", "likeable", "low energy", "careless" or "be more consultative" are not behaviours. Replace each with the observable action and its quote, or drop it.
- **Do not ask questions first.** Never open with an intake list. Decide, state your assumptions in one line, and deliver the review. Use `clarify` only if there is no transcript at all.
- **Arithmetic in code.** Do any sum (weighted or renormalized aggregate, talk-time counts) in `execute_code` and copy the result. No mental maths.

## Step 1: Get the transcript and set the context

1. Use the transcript the user pasted or attached. If they attached audio or video, call `audio_transcribe` on it; if that tool is not available on their plan, say so in one line and ask for the text transcript with `clarify`. If the user gives only a description of a call with no transcript, say you can only review the words said and ask for the transcript with `clarify`.
2. Work out from the transcript and the message, and state as assumptions where not given:
   - Mode: the rep reviewing their own call (self) or a manager or peer reviewing someone else's. Default to self if the user says "my call", otherwise manager.
   - Call type: cold call, scheduled discovery, demo, negotiation or renewal, inbound, or B2C inside-sales call.
   - B2B or B2C. B2C adds the optional compliance dimension.
   - Outcome (context only), previous focus behaviour if the user mentions one, any house methodology or scorecard (its vocabulary and weights win), and any deadline or coaching-time limit.

## Step 2: Transcript gate

Run this before scoring and declare the result at the top of the review.

- **Quality.** Look for ASR damage: garbled or nonsense words, non-speech tokens, heavy repeated filler, unexplained gaps. If roughly a fifth or more of the content is damaged, do not score. Report the damage, quote two examples and say which passages would be needed. Otherwise note "usable with damage" and where it sits.
- **Speaker labels.** If labels are missing or generic, infer the speakers from cues: introductions, names used in address, who asks and who answers. When a name resolves late, relabel earlier turns. Where two speakers cannot be told apart, do not attribute that passage and say so. State "speaker labels inferred" in the header and lower confidence on anything that depends on a guess.
- **Citations.** Cite as `[HH:MM:SS]` or the range when timestamps exist. Otherwise use line numbers or turn numbers you count yourself, and fall back to the verbatim quote alone. The user must be able to find the passage.
- **Partial calls.** Score only the dimensions whose phase is in the transcript. Mark the rest "N/A, phase not in transcript". Absence is never a zero.
- **The one-line rule.** Never score a dimension above Low confidence from a single garbled or ambiguous line. Say what a cleaner transcript would resolve.
- **Confidence per dimension.** High: two or more clean, consistent passages. Medium: one clean passage, or several damaged ones that agree. Low: one ambiguous or damaged passage; flag it, do not conclude.

## Step 3: Score the four dimensions

Read `references/rubric-anchors.md` now. It holds the 0, 2 and 4 behavioural anchors, the evidence cues for each dimension, the scheduled-call opener variant and the optional B2C compliance items.

1. Walk the transcript once and segment it into opener, discovery, objection and close passages, collecting candidate quotes per dimension.
2. Score each applicable dimension 0 to 4 (interpolate 1 and 3 between anchors) and attach a confidence tier.
3. Mark a dimension N/A, with the reason, when it was structurally absent: no opener to judge on an inbound call, no objection surfaced (say whether strong discovery seems to have prevented it or the prospect was disengaged), discovery explicitly done on an earlier call, or the call cut off before any close. N/A never counts as zero and leaves the aggregate.
4. Default weights are discovery 30%, close 30%, opener 20%, objection handling 20%. A house scorecard's weights replace them. Compute any aggregate in `execute_code`, renormalized to the applicable dimensions only. The aggregate is the least interesting output: lead with the shape, not the number.
5. Rewarding question count is a failure. Score laddering from symptom to consequence and testing whether the problem matters, not how many questions were asked.
6. "Close" means the next-step close, not the signature. A calendared step on a call where the deal is visibly not real is a 2, not a 4.

## Step 4: Find any fatal moment

A fatal moment is a single passage that would kill the deal or breach a rule whatever else scored: a misstatement of price or terms, a promise the product cannot keep, a compliance breach, or an insult or collapse that ends the conversation. Quote it with location. It is reported above the scores and never averaged away. A high total with a fatal moment is a worse call than a mediocre total without one.

## Step 5: Choose the bounded feedback

Score everything, surface little. The score table is the record; the rep gets:

- **At most 2 strengths**, each with a quote and what it did for the call. "Great energy" is banned.
- **At most 3 change items**, each shaped as situation (quote and location), observable behaviour, impact on this call. Tag each with a class and its effort to land:
  - Fatal slip: one deal-killing or rule-breaching moment the rep can simply stop doing. Effort: near zero.
  - Structural: a pattern repeated across this call. Effort: about a week of reps.
  - Local: one weak moment with no pattern behind it. Effort: near zero.
  - Fatal habit: a deal-killing behaviour the rep repeats by default. Effort: a quarter of coaching.
- **Exactly 1 focus behaviour**: the single highest-leverage change, phrased as an observable, re-executable action ("restate the objection in the prospect's words before answering it"), never a trait.

Default order for picking: fatal slip, then structural, then local, then fatal habit, because the first lands fastest. Override the default when:

- The issue is a rule or compliance breach: it becomes the focus behaviour whatever its effort.
- It was the previous review's focus and this transcript shows it unchanged.
- The rep is new or in ramp: promote the fatal habit.
- The user gave a near deadline: promote the fatal slip and local fixes. The user wants a lasting habit fix: promote the structural item and the fatal habit. The user has little coaching time: defer the fatal habit and give the structural item that fits.

Say in one line which fact moved an item off the default order, or "default order, nothing moved it".

## Step 6: Mode handling

- **Self-review (rep reviewing their own call).** If the user gave their own scores or impressions, use them. Otherwise state "self-assessment not given" and add a short "Where you may have scored yourself differently" list of up to three dimensions where the evidence-based score is likely to surprise, each with its quote. Hold self-criticism to the same evidence rule: "I was terrible" without a quote is as invalid as unearned praise.
- **Manager or peer review.** Phrase each change item as situation, behaviour, impact and then a question for the rep ("what was happening there?") rather than a verdict. If no self-assessment was given, note its absence, and suggest the manager asks the rep to self-score before sharing the review.
- **B2C or inside-sales.** Add the compliance and script row from the rubric reference, scored pass or fail per item against the user's list or, if none was given, against the generic items in the reference, labelled as assumed. Any compliance failure is a fatal moment and becomes the focus behaviour. Keep the review shorter: if you must trim, keep in this order: fatal moment, the one thing, one change item, one strength, the score table.

## Step 7: Quality gate, then deliver

Check the draft against these before replying and fix what fails:

1. Every scored dimension cites at least one verbatim quote with a location; every other dimension says N/A with a reason or "insufficient evidence".
2. The transcript quality tier is declared before any score; no dimension above Low confidence rests on one garbled line.
3. N/A dimensions are out of every aggregate and none is scored zero.
4. At most 2 strengths (quoted), at most 3 change items (class-tagged, SBI-shaped), exactly one focus behaviour as an observable action.
5. No character language anywhere. The outcome justifies no score.
6. A fatal moment, if any, is named above the scores.
7. Any statistic is labelled with where it comes from. A figure from a vendor's own platform data (for example, talk-to-listen ratios) is a vendor claim, correlational, and is context only, never a scoring criterion. Do not cite a statistic you cannot source.
8. The review states the next-review check.

## Output shape

Reply with the review in this shape, filling every line (delete a line only with a stated reason):

```
# Call Review: <prospect or company, or "not given">, <call type>, <B2B|B2C>, <date or "not given">

Mode: <self | manager | peer> (<given or assumed>)
Outcome (context only, grades nothing): <as given, or "not given">
Transcript: <clean | usable with damage: where | refused: why>, speaker labels <native | inferred | partly unattributable>, <complete | partial: phases present>
Prior focus behaviour: <behaviour and whether this call shows it changed, quoted> or "none given"

## Fatal moment
<quote + location + one line on why it kills the deal or breaches a rule> or "None found."

## Scores
| Dimension | Score /4 | Confidence | Evidence (quote + location) | Why (behaviour, not adjective) |
|---|---|---|---|---|
| Opener (<cold or scheduled> variant) | <n or N/A: reason> | <High|Medium|Low> | "<verbatim quote>" [<location>] | <one line> |
| Discovery | | | | |
| Objection handling | | | | |
| Close (next step) | | | | |
| Compliance and script (B2C only) | <pass/fail per item> | | | |

Shape: <one sentence on where strength and weakness cluster>
Aggregate (least important): <x / applicable max, N/A excluded, house weights if given> or "not computed"

## Strengths
1. "<quote>" [<location>]: <what the rep did and why it worked>

## Change items
1. <class> | Situation: "<quote>" [<location>]. Behaviour: <observable action>. Impact: <consequence on this call>. Effort to land: <near zero | a week | a quarter>.
Ranking note: <which fact moved an item, or "default order, nothing moved it">

## The one thing
<single focus behaviour, an observable action>

## Next-review check
<the quote-level change on the next call that counts as this landing>

## Notes
<assumptions made, statistic sources and vendor-claim labels, parts of the transcript left unread and why, consent-disclosure observation>
```

End on a strength: finish the reply with one sentence naming what the rep should keep doing, tied to a quote already given.

## Notes on recording consent

Reviewing a transcript the user already holds is fine; this skill takes no position on whether the recording was lawful. If the transcript shows no consent disclosure where one was clearly expected, note it once under Notes and suggest checking local recording rules, which vary by place. This is not legal advice.
