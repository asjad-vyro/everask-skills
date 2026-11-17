---
name: Jobs To Be Done Canvas
description: >
  Turns customer notes, interview snippets or a product idea into a finished jobs-to-be-done canvas: job statement, functional, emotional and social jobs, competing solutions, hiring criteria and product implications.
  Use it for "build a JTBD canvas", "what job are customers hiring our product for?", "reframe our positioning around the customer job".
---

# Jobs To Be Done Canvas

A good canvas describes the progress a customer is trying to make in a specific situation, not the customer's demographics or the product's features. Every claim traces to something the user gave, or is clearly marked as an assumption. Deliver the whole canvas in the reply, in one turn, without asking questions first.

## Step 1: Take stock of the input

1. List what the user gave: interview notes, quotes, survey text, a product description, or only a name or idea.
2. Number the snippets S1, S2, ... as you read them, so every later claim can cite one.
3. Decide the evidence level and state it in the canvas header:
   - **Research-based**: the user supplied customer words or observations.
   - **Hypothesis only**: only a product name or idea. The canvas is then a set of hypotheses to test, and every finding is labelled "Assumption".
4. If the input mixes several different jobs, pick the one that appears most often, say which you picked and why in one line, and list the others under "Other jobs seen".
5. If web research would help to name real competing solutions, use at most two `web_search` calls. Cite only what a search returned. Otherwise use only what the user mentioned plus generic categories (see Step 4).

## Step 2: Fill the canvas

Work through these in order. Keep each section short and concrete.

1. **Job performer**: who is doing the job and in what circumstance, beyond demographics. The same person can have different jobs in different situations.
2. **Circumstance**: the trigger, where it happens, how often, how urgent. Be specific, never "anytime".
3. **Job statement**: exactly one sentence, "When <situation>, I want to <motivation>, so I can <desired outcome>." It describes progress, not a feature or a solution. Under it write "Evidence:" and the snippet numbers that support it, or "Assumption" if none do.
4. **Functional job**: the practical task, what "done" looks like (2 to 4 criteria), the main steps, the functional pains.
5. **Emotional job**: how they want to feel, and what they want to avoid feeling, each with the current trigger.
6. **Social job**: how they want to be seen, and by whom, and what they want to avoid. If the social dimension is weak, say so rather than inventing one.
7. **Competing solutions**: what they hire today. Include direct competitors, indirect alternatives, non-consumption (doing nothing) and DIY or manual workarounds. Add why they switch and why they stay.
8. **Hiring criteria**: must-haves (table stakes), differentiators (what tips the decision), nice-to-haves.
9. **Insights and implications**: three insights, each followed by a product or positioning implication. Each insight cites snippets or is labelled "Assumption".
10. **Supporting quotes**: copy quotes verbatim from the user's input with their snippet number. If there are no customer words, write "No customer quotes provided" and give no quotes at all.
11. **Questions for further research**: three to five questions that would confirm or kill the weakest assumptions.

## Output shape

Reply with this, in Markdown, in full:

```
# Jobs to be Done Canvas: <job name>
Evidence level: <Research-based, from <n> snippets | Hypothesis only> | Date: <today>

## Job Statement
> When <situation>, I want to <motivation>, so I can <outcome>.
Evidence: <S-numbers or "Assumption">

## Job Performer and Circumstance
## Functional Job
## Emotional Job   (table: feeling | why it matters | evidence)
## Social Job      (table: perception | by whom | evidence)
## Competing Solutions   (table: type | solution | strengths | weaknesses)
Why they switch / Why they stay
## Hiring Criteria
## Insights and Implications
## Supporting Quotes
## Questions for Further Research
## Assumptions and gaps
```

Tag each bullet in the canvas that is not directly supported by the input with "(Assumption)". Finish with "Assumptions and gaps": a short list of what you inferred, and what research would validate it.

## Quality check before replying

- The job statement follows "When... I want to... so I can..." and names a real situation.
- It describes the customer's progress, not the product's features.
- Competing solutions include non-consumption and a DIY option.
- Every quote is word-for-word from the user's input.
- Nothing in the canvas states a number, percentage, sample size, interview count, customer name or brand the user did not give, or a search did not return. Where a figure would help, write "not given".

## Hard rules

- Never invent quotes, participants, survey results or statistics. With thin input, the canvas is a hypothesis canvas and says so.
- Never ask the user to supply more before you start. Decide, state your assumptions, deliver.
- Do not wrap the canvas in a file; the reply is the deliverable. Only if the user asks for a document, load the built-in `docx` skill with `skill_view` and follow it.
