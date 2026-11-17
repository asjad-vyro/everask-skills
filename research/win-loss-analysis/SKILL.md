---
name: Win-Loss and Churn Analysis
description: >
  Turns deal notes, call notes or churn notes into the real reasons deals were won, lost or churned, with loss categories, patterns and specific fixes.
  Use it for "why did we lose that deal", "win-loss review", "analyze these closed deals", "why do we keep losing to a competitor", "deal post-mortem", "why did this customer churn", "build a win-loss interview guide".
---

# Win-Loss and Churn Analysis

A good result separates the polite reason a buyer gave from the real one, backs every claim with evidence from the user's notes, finds patterns across deals, and ends in changes someone can make this week, month and quarter. The whole job is done in one reply, from what the user gave. Do not open with questions.

## Step 1: Take stock of the input

1. Read everything the user pasted or attached. Decide the mode:
   - **Single deal**: one deal, win, loss or churned customer.
   - **Batch**: two or more deals. Batch also gets a single-deal read of any deal that stands out.
   - **Interview guide or CRM fields**: the user asks for a win-loss interview guide, a summary template or fields to capture. Read `references/interview-and-crm.md` and produce that.
2. Note what is missing (company size, deal values, cycle length, competitors, who decided). Do not ask. Write "not given" in the output and list the main gaps under "Assumptions and gaps".
3. If the user names a CRM (HubSpot, Salesforce) and it is connected, you may pull deal records from it. Otherwise work from the message and attachments. Never pull from an app the user did not ask for.

## Step 2: Principles to apply to every deal

1. The stated reason is rarely the real reason. "Price" often means value was never established. "Timing" often means it was not a priority. "Went with a competitor" explains nothing until you find what the competitor did differently.
2. Wins get the same scrutiny as losses. A win can be for the wrong reason.
3. Patterns beat anecdotes: one loss is a data point, several with the same cause are a finding. With fewer than about five deals, call patterns "early signals", not proven trends.
4. Separate sales execution (discovery, multi-threading, follow-up) from product or market fit (missing capability, wrong buyer). They need different fixes.
5. Seller notes are filtered through the rep's view. Where the buyer's own words are in the notes, weigh them more and quote them; say so when only the rep's view exists.
6. Every analysis ends in recommendations.

## Step 3: Classify each deal

Give every lost or churned deal exactly one primary category (and one optional secondary):

| Category | Meaning | What it usually points to |
|---|---|---|
| Competitive loss | Chose a named competitor | Positioning, differentiation or proof points did not win |
| No decision | Chose to do nothing | Pain was not big enough, or was not made big enough |
| Status quo | Stayed with the current solution | Switching cost beat perceived value |
| Timing | Budget or priority shift | Verify it is real, not a polite no |
| Price | Too expensive | Value not established, or deal too small for the ICP |
| Value not established | Price was cited but the notes show no ROI, business case or quantified pain | Discovery and business-case gap |
| Champion left | Internal advocate departed | Single-threaded deal |
| Wrong ICP | Never a good fit | Qualification or targeting failure |
| Sales execution | Rep mistakes | Coaching gap |
| Product gap | Missing critical capability | Roadmap input |
| Procurement | Legal, security or compliance blocker | Enterprise readiness |

Reclassification rule: when a buyer says "price" or "budget" and the notes contain no ROI discussion, no quantified pain and no business case, classify it as **Value not established** and show both labels: "Stated: price. Assessed: value not established, because <evidence from the notes>". Keep **Price** only when the notes show value was agreed and the number itself was the blocker (for example a competitor quoted lower for the same scope).

For churned customers, also record: when churn happened relative to onboarding, whether adoption or a champion was lost, the trigger event, and whether the signs were visible beforehand.

## Step 4: Analyse

**For each deal** (every deal in a batch gets a short row; standout deals get the full read):

- Stated reason (what the buyer said) versus signals (behaviour in the notes: silences, new stakeholders, requests for materials, the buyer quoting language you never used) versus assessment (what most likely happened).
- Timeline of the key moments, only from the notes. Mark any inferred step as "inferred".
- Buyer's journey: what likely happened in meetings the seller was not in. Label this as reconstruction, not fact.
- Key moments: two or three that tipped the outcome.
- What could have been done differently, specific ("asked who else must be comfortable with this before the proposal"), never "sold harder".

**For wins**, check the win red flags and flag any that apply as "won for the wrong reason":

- Discount-driven: a heavy discount (about 30% or more) carried the deal.
- Hero-ball: it only closed after an executive stepped in.
- Single-use-case: won on one narrow use case only.
- Slow win: the win took far longer than typical, so the default was not to buy.

Then extract repeatable win themes: the buyer profile, the pain that led to wins, the proof points that landed, where the process created separation. Call them "plays to run again".

**For a batch**, do all arithmetic in `execute_code` (counts, percentages, win rate, average deal size, average cycle, discount averages) and copy the results into the reply. Never calculate in your head. Only report a statistic the notes support; if a figure cannot be computed because a field is missing, write "not given". Cut by segment, source, competitor or deal size only where the data allows it. Find patterns using this form for each:

1. Pattern: what keeps happening, with the deals that show it.
2. Root cause: why, with evidence.
3. Impact: how many deals and how much value (computed), or "value not given".
4. Recommendation.

## Step 5: Reply in this shape

Put the full analysis in the reply itself. Use these sections, in this order.

**Single deal**

1. Deal profile (company, outcome, value, cycle, category, competitor, decision-maker, champion, source; "not given" where missing)
2. Timeline and buyer's journey reconstruction
3. The real reason: stated versus assessed, with evidence
4. Key moments
5. Lessons (specific)
6. Recommendations (quick wins this week, process changes this month, strategic shifts this quarter)

**Batch**

1. Summary table: one row per deal with outcome, value, stated reason, assessed category, one-line evidence
2. Summary statistics (computed)
3. Loss reason distribution: stated reasons versus assessed categories, side by side, and what changed on reclassification
4. Competitive picture (only competitors named in the notes)
5. Top patterns, up to three, in the pattern form above
6. Wins: themes to double down on, and any wins flagged as wrong-reason
7. Recommendations: quick wins (this week), process changes (this month), strategic shifts (this quarter), each tied to a pattern
8. Assumptions and gaps, plus what data to capture next time and a suggestion to run buyer interviews on the most important losses (offer the interview guide; do not wait for an answer)

## Hard rules

- Use only facts from the user's notes. Never invent a deal detail, number, name, quote, competitor, date or benchmark. Write "not given" or mark an assumption.
- Quote the buyer only with words that appear in the notes.
- Separate what the notes say, what you infer, and what you assume.
- Do not treat a stated reason as the cause without checking the notes for supporting evidence.
- Do not name a person as at fault; describe the process gap.
- Any message or email to buyers stays a draft until the user says to send it.
