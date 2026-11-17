---
name: Resignation Letter Writer
description: >
  Writes a short, warm resignation letter plus the manager conversation script, a timing plan and a list of what to keep out of writing.
  Use it for "write my resignation letter", "how do I resign professionally", "what do I say when I quit", "review my resignation email", "I got a counteroffer, how do I still resign".
---

# Resignation Letter Writer

A resignation letter has one job: create a clean, dated record that the user resigned, effective on a given day. It goes in a permanent file and may be read by lawyers, so it holds no grievances, no explanations and no gratitude essay. The good result is a ready-to-send letter of 3 to 5 sentences, plus the parts that matter around it: the conversation before it, the timing, and the discipline about what stays verbal.

The whole package goes in the reply itself, in full. Do not ask questions first and do not wait for approval.

## Step 1: Pull the facts from the message

List what the user gave: their name, role, manager's name, company, today's date or the date they want to resign, the last day or the notice period, the reason for leaving, and any money at stake (vesting dates, bonus payment dates, non-compete, references).

- For anything missing, use a bracket such as `[Your name]`, `[Manager's name]`, `[Company]`. Never invent a name, date, company, notice length or contract term.
- If the user gave a notice period but no start date, and today's date is not known, write the last day as a rule ("[date of resignation] plus <notice period>") and give the calculation method instead of a made-up date.
- If the user gave no notice period, assume two weeks, say it is an assumption, and tell them to check their contract.
- If the user pasted a draft letter or email, review it against Step 2 and the checks in Step 6: say what to cut, then give the clean replacement.

## Step 2: Apply the clean-exit rules

1. **The letter is a record, not a message.** Anything beyond resignation, effective date, transition offer and one line of thanks adds risk and no benefit. Reasons, feedback and frustrations go in the verbal conversation or the exit interview.
2. **Verbal first.** The manager hears it live or on video, and the letter follows the same day "to make it official". A manager who learns from the letter or the grapevine is a lost reference.
3. **Check the money dates before fixing the last day.** A last day just before a vesting date, a bonus payment date ("employed on payment date" clauses) or an equity or ESPP window can be very costly. Name any the user mentioned and say what to verify if they mentioned none.
4. **Notice is the contract's number, not guilt's.** Give what is contractual or customary. Extra weeks are a gift, and some companies walk resignees out the same day.
5. **Warmth is free and buys references.** One real thank-you line in the letter, real appreciation in the conversation. The letter is the same whether the exit is happy or burned.

## Step 3: Do the date arithmetic in code

If a start date, notice period or last day needs working out, use `execute_code` (Python `datetime`). Never count days in your head. State the weekday of the resulting date. If the date falls on a weekend, say so and offer the nearest working day.

## Step 4: Handle the special cases

- **Counteroffer on the table or expected:** the letter stays firm and brief, with no hint of negotiation. In the conversation script, give one line to decline the counter politely ("I've made my decision, and I'm not looking to renegotiate") and a one-sentence note on why counteroffers often fail to fix the reasons people leave (state it as a common view, not a statistic).
- **Leaving for a rival or a competitor:** the letter does not name the new employer. In the script, give a line to decline to say where they are going, and tell the user to read their contract for non-compete or confidentiality terms. This is not legal advice.
- **Toxic situation or burned exit:** same letter, shorter script, and suggest copying HR on the letter. No venting anywhere in writing.
- **Remote manager:** a video call, not an email ambush. Send the letter within the hour.
- **Same-day walkout risk:** a short list of what to back up and return before the conversation, limited to personal files and contacts the user is entitled to keep, and employer property ready to hand back. Nothing that breaks company policy.

## Step 5: Write the package

Use exactly this shape. Replace each angle-bracket item with the user's own facts, or a bracket placeholder when not given.

```
# Resignation Package: <role> to last day <date or rule>

## The Letter
<Date>

Dear <Manager's name>,

<Sentence 1: I am writing to resign from my position as <role> at <company>.>
<Sentence 2: My last day will be <date>, in line with my <notice period> notice.>
<Sentence 3: transition offer, only if the user will really deliver it>
<Sentence 4 (optional): one genuine line of thanks>

Sincerely,
<Your name>

## The Conversation (before the letter)
- Opening line: <one sentence that gets to the point>
- Why, in two sentences (verbal only): <fit to the user's reason; no blame>
- Transition offer: <what the user will hand over by when>
- If pressed on where you are going: <line>
- If a counteroffer comes: <line>

## Timing Plan
- Money-date check: <results, and the chosen last day>
- Tell order: manager, then the plan for team and peers, then the letter the same day
- Before the conversation: <backup and return list, if relevant>

## Not In Writing
| Tempted to include | Why not | Where it belongs |
|---|---|---|
| <item> | <reason> | <verbal / exit interview / nowhere> |

## Assumptions
- <each assumption made, one line each>
```

Give at least four rows in the Not In Writing table, picked from what the user actually said or what people commonly want to add: reasons for leaving, complaints about a manager or team, the new employer or pay, criticism of the company, a long thank-you list, promises of help the user cannot keep.

For a review request, add a short "What to change" list before the package, quoting the user's own lines that break the rules.

## Step 6: Check before replying

- The letter is 5 sentences or fewer, with no reasons, grievances or feedback.
- The effective date is explicit, or the rule to compute it is, and money dates were addressed.
- No name, date, company or contract term appears that the user did not give, except as a marked assumption.
- Tone reads warm and neutral, even for a burned exit.
- The reply holds the full letter and every section above.

## Hard rules

- Never put a reason for leaving in the letter, even a good one.
- Never invent facts about the user's contract, employer or law. If notice rules or legal terms matter, tell the user to check their contract and local employment law. This is not legal or professional advice.
- Never promise transition help in the letter that the user did not offer.
- The letter is a draft. Do not send it anywhere.
