---
name: Decision Memo and One-Pager
description: >
  Writes a finished decision memo or one-pager: recommendation first, a fair options table, what you would have to believe, risks and a clear ask with a deadline.
  Use it for "write a decision memo", "turn these notes into a one-pager for the CEO", "draft a recommendation memo", "help me get leadership to decide".
---

# Decision Memo and One-Pager

A decision memo exists to get a decision made, on the record, by the right person. A good one lets the reader say yes, no, or "here is my concern" in five minutes. The failure mode is a memo that reads like a discussion: lots of context, no recommendation, no ask.

The whole memo goes in your reply, in full. Never stop to ask questions first: use what the user gave, decide the rest, and list your assumptions at the end.

## Step 1: Pull out the pieces

From the user's message, notes and any attached file, find:

- **The decision**: the specific choice, phrased as a question with a finite answer (yes/no or A/B/C).
- **The recommendation**: what the user wants approved. If the user gave options but no preference, pick the option the facts support best and say it is your pick for them to confirm.
- **The options** and their trade-offs. Always include "do nothing / keep the status quo" if the user did not.
- **The decider and the deadline.** If missing, write `<decider not given>` or `<deadline not given>` in the header, and propose a sensible deadline in the ask, marked as a suggestion.

If the notes contain no decision and no ask (a status update, meeting notes, a pile of research), do not write a status update. Say in one sentence that there is no decision in them, then offer the most likely decision the material points to, mark it as an assumption, and write the memo around it. Put the open question "what do you want decided?" in the assumptions list.

## Step 2: Check the facts and the sums

- Use only facts, figures, names and dates the user gave. Never invent a number, quote, customer, benchmark or deadline. Where something is needed and not given, write "not given" or mark it as an assumption.
- Do every sum (totals, savings, break-even, percentages) in `execute_code` and copy the results. No mental maths.
- If the user wants market or pricing facts that they did not supply, use at most two `web_search` calls and cite what you found. Otherwise do no research.

## Step 3: Write the memo

Use exactly this shape. Keep it to about one page (400 to 700 words) unless the user asks for a longer six-pager.

```
# Decision Memo: <the decision as a short title>
**To:** <decider> · **From:** <the user, or "not given"> · **Date:** <today> · **Decision needed by:** <date>

**1. Recommendation** 
<2 to 3 sentences, first: what you want approved and the one-line why.>

**2. The decision**
<The question, framed so the answer is a clear choice: "Do we A, B or C?">

**3. Context**
<Only the background needed to judge it, and why it is on the table now. 3 to 5 sentences.>

**4. Options and trade-offs**
| Option | Pros | Cons | Cost / effort |
|---|---|---|---|
| <recommended option> | ... | ... | ... |
| <alternative> | ... | ... | ... |
| Do nothing | ... | ... | ... |

**5. Why this recommendation**
<The reasoning, then "What you would have to believe for this to be wrong:" with 2 to 4 assumptions the recommendation rests on.>

**6. Risks and mitigations**
<The real downsides and how each is handled. State whether the decision is reversible (a two-way door) or hard to undo (a one-way door), and size the rigour to that.>

**7. The ask**
<Exactly what the reader must do: approve / pick an option / give input, by the deadline. If the answer is yes, what happens next and who starts it.>

**Assumptions I made:** <bullets: anything you filled in, guessed or left as "not given">
```

Rules for each part:

- The recommendation sits in the first paragraph, not the conclusion.
- Be fair to options you are not recommending: give each real pros. A stacked deck or strawman reads as one and costs the author credibility.
- Pros and cons must come from the user's material or plain logic, not invented data.
- Do not over-agonise a reversible decision; match the length of the risk section to the cost of being wrong.
- Plain, direct sentences. No filler, no "in today's fast-paced world".

## Step 4: Check before you reply

Confirm each of these, and fix the memo if one fails:

1. The recommendation is in the first paragraph.
2. The decision is a clear question with a finite set of answers.
3. Every option has at least one real pro, and the status quo is included.
4. The memo says what would have to be true for the recommendation to be wrong.
5. It says whether the decision is reversible.
6. It has an explicit ask and a deadline (or a flagged proposed one).
7. Every number appears in the user's input or came from `execute_code`.

## Step 5: Reply

Reply with the memo in full, followed by the assumptions line. If the user asked for a Word or PDF file, load the built-in `docx` or `pdf` skill with `skill_view` and follow it to produce the file, then publish it with `publish_artifact` (`kind: "document"`); the memo text is still shown in the reply. Do not build a file otherwise. Treat the memo as a draft: do not send it anywhere.
