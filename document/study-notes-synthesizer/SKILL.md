---
name: Study Guide from Notes
description: >
  Turns pasted lecture notes, slides and readings into one exam-ready study guide with plain-language concepts, confusable pairs, self-test questions with answers, a cram sheet and a list of gaps in the notes.
  Use it for "make a study guide", "combine my notes", "prep me for the exam", "organize this course material".
---

# Study Guide from Notes

A good result is a guide built for retrieval, not a shorter copy of the notes. It organizes the material by how the ideas depend on each other, explains each idea plainly before formally, contrasts the ideas students mix up, tests the student at three depths, and says honestly what the notes do not cover or get wrong. The whole guide goes in the reply itself, in full.

## Step 1: Read the materials and fix the setup

Use only what the user gave: pasted text, attached files, a topic list. Note, from the message, the course and level, the exam format (multiple choice, essay, problems) and the topics the user says feel shakiest.

Do not ask questions. If something is missing, assume it, and list the assumptions in one short line at the top of the guide. Examples: "Assumed: undergraduate level, mixed exam format, no declared weak spots." If the user gave no notes at all and only a topic, write the guide from well-established textbook knowledge and say at the top that it is not based on their own notes, so the gaps list cannot be checked against them.

Never invent course names, exam dates, lecturer names, page numbers, definitions or figures the user did not give. Where a header detail is missing, write "not given".

## Step 2: Extract and check

Before writing, list for yourself:

1. Every concept, term, formula, rule and worked example in the materials.
2. Contradictions: places where two parts of the notes disagree (a different value, formula, date, definition or cause for the same thing). Never silently pick one.
3. Terms used but never defined, and topics mentioned only in a line or two.
4. If a syllabus or topic list was supplied, each of its topics against the notes.
5. Pairs of ideas students commonly confuse, from the notes or from the subject itself.

## Step 3: Organize by dependency

Group concepts into clusters ordered by what must be understood first, not by lecture order. Each cluster needs a short plain title. If a concept has no source in the notes, do not add it to a cluster: put it on the gaps list.

## Step 4: Write each cluster

For every cluster use this shape:

```
## <Cluster title>
**Plainly:** <explanation a newcomer could follow, 1-3 sentences>
**Formally:** <the exact definition, rule or formula, as the notes give it>
**Builds on:** <earlier cluster, or "nothing earlier">
**Confused with:** <the lookalike idea and the one difference that separates them>
**Worked example:** <only if the notes contain one or the subject clearly needs one; label it as from the notes or as added for illustration>

### Test yourself
1. Recall: <define or state>
2. Apply: <a small case to solve or classify>
3. Why X, not Y: <explain why one idea or method applies and its lookalike does not>
```

Confusable pairs get a small side-by-side table inside the cluster that holds them (two columns, three or four rows of distinguishing features).

Every question must be answerable from the guide. Write the answers in an "Answers" section at the end, not under the questions.

## Step 5: Do all arithmetic in code

If the notes contain worked calculations, or you write an apply question with numbers, compute every result with `execute_code` and copy the output. Never do sums or conversions in your head. Use numbers from the notes where possible; any number you make up for a practice question is labelled "practice figure".

## Step 6: Assemble the reply

Output in this order:

```
# Study Guide: <course, or "not given"> - <exam, or "not given">
*Assumptions: <one line>*

**Start here (your shakiest topics):** <the user's declared weak spots with where each is covered, or "none declared, so the order below follows dependency">

**Contradictions in your notes:** <each one: what the two places say, where they sit, which looks more likely right and why, and what to check in the textbook or with the lecturer. If none found, say "None found.">

**Gaps in your materials:** <topics the syllabus or the subject implies that the notes barely touch or never define, each with one line on what is missing. If a syllabus was given, check each topic against it. An empty list must be earned: say what you checked.>

<the clusters from Step 4, in dependency order>

## Answers
<numbered by cluster and question>

## One-page cram sheet
<at most 20 telegraphic items: the highest-yield facts, formulas and distinctions>
```

If the exam format was given, shape the emphasis: more calculation questions for a problem-based exam, more why-X-not-Y questions for essays, sharper definitions and distinctions for multiple choice.

## Hard rules

- Synthesize, never sequence: no lecture-by-lecture summary.
- Plain explanation first, formal definition second, for every concept.
- Do not fill a gap with invented material. Flag it. Where you add background knowledge to explain a concept the notes only name, mark it "added, not from your notes" so the student can check it.
- Flag every contradiction in the notes. Do not quietly resolve it.
- Do not write questions the guide cannot answer.
- Cram sheet: 20 items at most.
- Reply with the full guide. A file is only built if the user asks for a Word or PDF copy; then load the built-in `docx` or `pdf` skill with `skill_view`.
