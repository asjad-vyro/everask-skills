---
name: FAQ Builder
description: >
  Turns tickets, chat threads, emails, a policy or a product description into a ready-to-publish FAQ, with duplicate questions merged and answers that lead with the answer.
  Use it for "build an FAQ", "turn these support emails into an FAQ", "I answer the same questions every week", "FAQ for new hires about our policy".
---

# FAQ Builder

A good FAQ is built from questions people really ask, worded the way they ask them, answered in the first sentence, and grouped the way the asker thinks. It never states anything the source material does not support. The whole FAQ goes in the reply, ready to paste.

## Step 1: Take stock of the material

Work from what the user gave: pasted tickets, emails, chats, a policy, a sales page, a product description. Do not open with questions and do not wait. Decide, then note your assumptions in one line.

- Name the audience (customers, new hires, another team). If not stated, infer it from the material and say so.
- Name the source type. It decides how the question list is built:
  - **Real questions supplied** (tickets, emails, chats): the list is mined from them. Go to Step 2.
  - **Only a document or description supplied** (policy, sales page): there is no demand evidence. Write the questions a reader of that document would most likely ask, and label the list "anticipated, not mined" so nobody mistakes it for measured demand.
- Where the FAQ will live is optional. If not given, write plain headings and bold questions that paste into any wiki, help centre or doc.

## Step 2: Build the question list

1. List every distinct question in the material, in the asker's own words. Only messages from askers count as questions or phrasings; support or staff replies are sources for answers, never variants or counts.
2. Merge duplicates by intent. "How do I reset my password", "locked out" and "can't log in" are one question. Use the most common phrasing as the heading and keep the other phrasings as variants.
3. Count how many times each merged question appears in the material. Do all counting with `execute_code` when there are more than about ten items, and copy the numbers from its output. Never count by eye. Frequency means "times seen in the material given", not a measure of the whole customer base.
4. Drop wish-list questions nobody asked ("What makes us unique?"). Keep a question only if it appears in the material or, for the anticipated case, follows directly from the document.

## Step 3: Write the answers

For each question:

1. The first sentence answers it ("Yes, ...", "No, ...", "Up to <the figure from the source> ...", "Go to ...").
2. Caveats and conditions come next, then a pointer to where to read more, if the source names one.
3. Use the asker's vocabulary, not internal jargon.
4. Use only facts, figures, dates, prices, names and links present in the source. If the source does not answer the question, write the answer as `Not covered in the material provided. <owner> to confirm.` Never fill the gap with a plausible guess.
   - A condition, deadline or step stated for one question (for example a cut-off given for address changes) belongs only to that question. Do not carry it over to another answer as "helpful" advice unless the source ties it to that question too.
5. If a policy or ticket answer is ambiguous or two sources disagree, say so in the answer and flag it in the reply's final notes.
6. Keep answers short. If the full answer is long, give the short answer and link or name the full document.
7. Owner: use a name or role only if the user gave one. Otherwise write `owner: to be assigned`.

## Step 4: Group and order

- Group by the asker's journey (for example getting started, using it, billing or pay, when something goes wrong), using only groups the material needs. Do not group by team or alphabetically.
- Within a group, put the most frequent question first. In an anticipated list, put the most basic first.
- Headings are the questions, worded as the asker would type them, and match the Question list wording exactly.
- Any ranking you mention ("most common", "second most common") is read from the Times seen column, highest count first.

## Step 5: Add the upkeep rule

Give a short upkeep plan: answered the same question twice outside the FAQ, it goes in this week; where candidate questions get logged (use a place the user named, otherwise "a shared list"); a prune of entries nobody reads and an owner correctness check on a regular cadence (state it as a suggestion, for example quarterly, not as a commitment made by the user).

## Output shape

Deliver exactly this in the reply. The reply starts with the `# FAQ` line: no narration before it (no "I'll load the skill"), and no sections beyond those shown (no "Published files" or similar):

```
# FAQ: <audience / topic>
Built from: <source type and how many items>. <Mined from real questions | Anticipated, not mined.> Assumptions: <one line>.

## Question list
| Question (asker's words) | Times seen | Other phrasings |
|---|---|---|
| <question> | <count from the material, or "n/a (anticipated)"> | <variants or "none"> |

## The FAQ
### <Group>
**<Question>**
<Answer-first sentence. Caveat. Where to read more.> (owner: <name or role given, else "to be assigned">)

## Keeping it current
<the answered-twice rule, where candidates are logged, the review cadence>

## Notes
<gaps the source did not answer, conflicts between sources, anything you assumed>
```

## Hard rules

- No invented facts: no figures, dates, prices, limits, names, quotes or policies that are not in the material. Gaps are marked "not covered", never guessed.
- No invented frequencies. Counts come from the material only.
- Every answer's first sentence is the answer.
- Questions that appear in the material are never dropped; questions that do not appear are never presented as mined.
- Deliver the full FAQ in the reply itself. Build a file only if the user asks for one; for a .docx, load the built-in `docx` skill with `skill_view` and follow it.
- Final check before replying: each question traces to the material, each answer matches it, headings use the asker's words, and no duplicates remain. Re-read every answer sentence and delete any condition, deadline or step the source does not state for that question.
- The reply begins with `# FAQ` and contains only the sections in the output shape.
