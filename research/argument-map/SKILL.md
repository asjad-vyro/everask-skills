---
name: Argument Map
description: >
  Turns an essay, op-ed, memo, policy proposal or one-line claim into an argument map: the main claim, the reasons, the hidden assumptions each reason needs, the objections, and the weakest links.
  Use it for "map the argument in this", "where is this argument weakest", "what is this assuming", "break down the case for and against".
---

# Argument Map

A good result lays the structure of an argument out so every link is visible, and shows which unstated assumptions hold the whole case up. It judges the logic, not the style: a valid structure does not make the premises true, and the map never claims the argument is sound or unsound on structure alone.

The whole job is done in one reply. Never open with questions. If the user gave a text, map that text. If they gave only a claim or a topic, map the strongest case people usually make for it and say so.

## Step 1: Fix the contention

1. Find the single main claim the argument is trying to establish. Write it as one sentence in the author's own terms.
2. If the text makes several claims, pick the one the others serve and mention in one line what you left out.
3. If the input is only a claim, treat it as the contention and build the likeliest supporting reasons yourself. Label the map "Built from the claim alone: reasons are the usual ones, not the author's."

## Step 2: List the reasons

List each reason the text gives for the contention, in the order of the text. Each is one sentence. Quote or closely paraphrase the source; do not add reasons the author did not make (unless Step 1 item 3 applies). Note a reason that only restates the contention, or an appeal to authority, popularity, or "everyone else does it", as it is.

## Step 3: Surface the co-premises

This is the core step. For each reason ask: "What else must be true for this reason to actually support the contention?" Write that as a plain statement of the unstated assumption. Typical hiding places:

- Correlation treated as cause ("A and B move together" assumed to mean "A causes B").
- A sample, case or example assumed to represent the whole group.
- A past pattern assumed to continue.
- A cost, side effect or alternative explanation assumed away.
- A word used in two senses.
- A gap between "is" and "ought": a fact used to support a recommendation with no value stated.

Every reason gets at least one co-premise. If you cannot find one, say the reason supports the contention directly.

## Step 4: Add objections and rebuttals

1. Give the strongest objection to each reason where one exists, and the strongest objection to the contention itself, including a rival explanation or a cheaper alternative the text ignores.
2. Add a rebuttal only if the text offers one, or one is clearly available from what the text says. Otherwise write "none offered".
3. Objections come from reasoning about the text. Do not cite studies, figures, names or quotes the user did not give. If a fact check would settle a point, say what to check rather than stating the answer. Use `web_search` only if the user asked for evidence to be checked, at most two searches, and link what you found.

## Step 5: Flag the weak links

Mark each of these:

- an inference that does not follow even if the premise is true;
- a co-premise that is load-bearing (the contention fails without it) and unsupported in the text;
- an objection the text never answers.

For each, say what would have to be true or shown for it to hold. Rank them with the most damaging first. Mark a premise "load-bearing" only if removing it breaks the case.

## Step 6: Write the reply

Put the full map in the reply itself, not in a file, using exactly this shape. Read `references/TEMPLATE.md` for the shape with a short usage note before you write.

```
## Contention
<one sentence>

## Map
**Reason 1:** <reason>
  - Co-premise (unstated): <assumption>
  - Objection: <objection> -> Rebuttal: <rebuttal or "none offered">
**Reason 2:** ...
**Objection to the contention:** <objection> -> Rebuttal: <rebuttal or "none offered">

## Weak links and unsupported premises
| Link or premise | Problem | What it would need to hold |
|---|---|---|

## Verdict
<two or three sentences: is the structure valid as written; which premises are load-bearing but unsupported; what would have to be true for the contention to follow>
```

If the user's text was long, keep each cell to one sentence. After the verdict add one line listing any assumption you made (for example, which claim you picked as the contention).

## Hard rules

- Use only what the user gave. Do not invent statistics, sources, studies, quotes, names or numbers, and do not state outside facts as settled. Write "not given" where the text lacks a detail.
- Do not decide whether the conclusion is true. Say what its premises would need.
- Do not rewrite or improve the argument unless the user asks; map it as it stands.
- Keep the structure, not prose: a short reply with a complete map beats a long essay.
- This is a reasoning aid, not professional advice.
