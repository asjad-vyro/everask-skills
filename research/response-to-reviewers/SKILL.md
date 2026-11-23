---
name: Response to Reviewers
description: >
  Turns reviewer comments on a paper into a point-by-point response letter plus a checklist of the changes to make in the manuscript.
  Use it for "respond to reviewers", "write a rebuttal letter", "reply to reviewer comments", "revise and resubmit", "responder a los revisores".
---

# Response to Reviewers

A good response letter answers every comment, in order, politely and specifically, and says exactly what changed and where. It never claims a change, analysis, result or reference the author has not provided. The reply itself is the deliverable.

## Hard rules

- Write in the language the user wrote in unless they ask for another (journals often need English: if the user says so, write the letter in English and keep any notes in their language). Keep their names, figures and terms exactly as given. Keep the user's English variety (UK or US) if stated.
- Never invent a result, number, analysis, figure, page or line number, section, or reference. What the author did not tell you is written `[author to add: <what is needed>]`.
- Never invent citations. If the author asks for references to be added, find them with `web_search` (at most 3 searches) and give links, or mark `[author to add: reference on <topic>]`.
- Tense is evidence. Write "we added", "we corrected", "we redrew", "we recalculated" only for a change the author told you they made. For every other comment, the response sentence about the change is wrapped in `[proposed: ...]` (for example `[proposed: We will state how the sample size was chosen in Section <x>.]`) and the Change made line is `[author to add: ...]`. A letter in which the author said nothing about what they did therefore has no claimed changes at all, and every status is "Needs new work" or "Disagree", never "Accept and change". The opening paragraph then names no changes either.
- Self-check before the reply: read the letter once and underline every verb that says something was done ("we added", "we replaced", "we have checked", "we named", "has been redrawn"). Each must match a change the author reported, word for word in scope. "I have not done anything on R2.1" means R2.1 and its literature paragraph have no done-verb at all, and neither does a comment where the author gave only a reason (R1.1: "plots were all the cooperative allowed" justifies, it does not say a sentence was added). Where the author reported one change, do not add checks or extras they did not mention. Wrap everything else in `[proposed: ...]`, including summaries of literature and lists of confounders (those are new content for the author to approve). The opening paragraph lists only reported changes.
- Do not promise work the author has not said they will do. For comments that need new analysis or data, write the response as a placeholder the author completes, and list the task in the checklist.
- Tone: courteous, specific, calm. No grovelling, no sarcasm, no flattery beyond one short thanks per reviewer. Disagree respectfully with reasons, not with defensiveness.
- Never stop to ask. If something is missing, decide, say the assumption, and deliver the full result in one reply.

## Step 1: Collect the input

From the message and any attachment, note: the journal or editor name if given, manuscript title if given, the reviewers' comments, what the author says they already changed, what they refuse to change and why, and the decision (major or minor revision) if stated. If the manuscript is attached, read it once to locate sections.

## Step 2: Split the comments

1. Number every separate point as R1.1, R1.2 for Reviewer 1, R2.1 for Reviewer 2, and so on (E.1 for the editor). If a reviewer's paragraph holds two requests, split it into two points.
2. Keep each reviewer comment quoted exactly in the letter, not paraphrased. If a comment is long, quote it in full anyway.
3. If the reviewers are not labelled, call them Reviewer 1, Reviewer 2 in the order they appear.

## Step 3: Classify each comment

Give each one exactly one status, used in the checklist:

- **Accept and change**: the author has said what they changed. If they did not say so, use "Needs new work" instead, even for small fixes.
- **Partly**: part accepted, part declined or limited.
- **Disagree**: respectful rebuttal. Only if the author gave a reason or the comment is plainly a misreading; otherwise mark the reason `[author to add: reason]`.
- **Needs new work**: needs a new analysis, experiment, data or references the author must supply.

When the author stated what they changed, use their description and nothing beyond it. If they said nothing about a comment (this is every comment when they gave only the reviewers' text), propose a reasonable response in brackets that they can accept or edit, labelled `[proposed: ...]`, and make it the lightest honest option (for example, clarify in the text), never one that claims an action already taken.

## Step 4: Write the letter

Use this shape. Everything in angle brackets is replaced from the user's input or left as a marked blank.

```
<Journal or editor, as given; otherwise "Dear Editor">

Re: <manuscript title and ID if given, otherwise [author to add: title and ID]>

Dear <editor name if given, otherwise Editor>,

<One short paragraph: thanks to the editor and reviewers; one sentence on the main changes the author actually made or accepted; note that responses are below and changes are marked as the author will mark them (for example in colour or tracked changes), only if the author said so.>

## Reviewer 1

**Comment R1.1**
> <exact quote>

**Response:** <one clause of thanks if natural, then what was changed and where, or the reasoned reply>

**Change made:** <the author's wording of the change, or [author to add: new text and location]>

(repeat for every point)

## Reviewer 2
(same)

Sincerely,
<author name if given, otherwise [author to add: name]>
```

Rules for each response:
1. One clause of acknowledgement at most ("Thank you for this point"), then straight to substance.
2. Say what changed and where: "Section <x>" only if the author gave the section, otherwise `[author to add: section]`.
3. For a disagreement, give the reasoning in two to four sentences, point to evidence the author gave, and say what was done to make the point clearer for readers if the author did something.
4. Keep each response short: usually under 120 words.

## Step 5: Revision checklist

After the letter, add a table with columns: Point, Status, Action for the author, Done by author. One row per point, in the same order. Status is one of the four in Step 3. The action says concretely what to do ("run the sensitivity analysis the reviewer asks for", "add the reference or decline in the letter"). Put needs-new-work rows first in a short "Do these first" line above the table.

## Step 6: Reference check (only if the manuscript with its reference list is attached)

Do the matching in `execute_code`, not by eye:
1. Extract the in-text citations (numbered like [3] or author-year like "Smith, 2019") and the reference list entries.
2. Report citations missing from the list and list entries never cited. Say which citation style you detected. If the text is too messy to match reliably, say so instead of guessing.
3. Present results as two short lists. If no manuscript was attached, skip this step and write nothing about it.

## Step 7: Reply

The reply holds, in this order:
1. Two lines: counts per status (computed in `execute_code` if there are more than ten points), and the list of placeholders the author must fill in.
2. The response letter.
3. The revision checklist.
4. The reference check, only if Step 6 applied.

Only if the user asks for a file: load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build the letter and checklist as one .docx. Do not call `publish_artifact` for it.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, and say in one line what changed. If it was a file, rebuild the same file type under the same name.
