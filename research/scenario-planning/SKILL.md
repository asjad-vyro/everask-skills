---
name: Scenario Planning
description: >
  Builds four contrasting future scenarios from two key uncertainties and tests how well your strategy holds up in each one.
  Use it for "scenario plan for my business", "build scenarios for our strategy", "test our 3-year plan across different futures", "what if regulation tightens or loosens".
---

# Scenario Planning

The user gets a scenario set: two named uncertainty axes, four short contrasting worlds, and a robustness read of their strategy across all four (which moves survive every world, which are bets, which early signals show which world is arriving, which options to keep open). It is structured speculation, not a forecast. The full set goes in the reply itself.

## Hard rules

- Never rank the worlds by likelihood, never give them probabilities, never say one is "most likely". If the user asks which will happen, say the method does not predict, and point to the signal watch-list.
- Use only facts the user gave. Do not invent company figures, market sizes, dates, statistics, quotes or sources. Scenario narratives are plausible stories: write them as "imagine" or "in this world", and mark any outside fact you did not verify as an assumption.
- Do not ask the user questions. If the decision, horizon or uncertainties are missing, choose sensible ones, say so in an "Assumptions" line, and deliver.
- Do not use web search unless the user asks for current facts. If you do, at most two searches, and link what you used.
- If the user gives no strategy to test, state the most likely current strategy as an assumption and test that.
- Not professional advice: for big financial, legal or regulatory decisions, the user should check with a qualified adviser. Say this in one line at the end.

## Step 1: Frame the decision

Write one line for the focal decision (the choice under pressure) and one for the horizon. If the user gave a strategy but no horizon, pick 3 to 5 years and say it is an assumption. List the strategy or candidate moves you will test (the user's, or 3 to 5 you derive from what they said).

## Step 2: Scan the forces

List 6 to 10 outside forces the user does not control (regulation, technology adoption, demand, competitors, costs, social change, macro or geopolitical). Cover at least four categories. For each, give impact on the decision (high or low) and uncertainty (high or low), in one short line.

- High impact and low uncertainty: list as **predetermined elements**. They apply in every world and are not axes.
- High impact and high uncertainty: these are the **critical uncertainties**.

## Step 3: Pick two axes

If the user named two uncertainties, use them, unless they are clearly not independent or one is predictable. In that case say so and replace it. If they named none, pick the two best critical uncertainties and give one sentence on why each was chosen over the rest.

Each axis is a spectrum with two named poles (for example "tightens" to "loosens"). Check the two are independent: one should not simply cause the other. If the best two are linked, reselect and say why.

## Step 4: Build the four worlds

Cross the axes. Give each quadrant a short evocative name and a narrative of 3 to 5 sentences showing how both poles and the predetermined elements play out together: what customers, competitors and regulators do, and what the decision looks like from inside that world. The worlds must truly contrast. Do not write four mild variations of today, or one obvious good world and one bad world. If a quadrant is implausible, say why and replace it with a smaller set of three, but prefer four.

## Step 5: Test the strategy

Make a table with one row per move and one column per world. Each cell is one of: wins, survives, weak, fails. Do not count or score in your head: if you add up anything numeric, use `execute_code`. Then classify each move:

- **Robust**: survives or wins in every world. Commit to these.
- **Bet**: wins in one world and loses in another. Name the world it bets on.
- **Gap**: an exposure no current move covers.

Optionally, if one strategy is already favoured, name the specific conditions in each world where it would fail and how to adapt it.

## Step 6: Signals and options

For each world, give 2 or 3 leading indicators the user can actually watch that would show that world arriving. Then name 2 or 3 options worth keeping open precisely because the worlds diverge (cheap hedges, staged investments, partnerships), and say which worlds each one pays off in.

## Output shape

Reply with exactly these sections, in order. Replace every `<...>` with real content.

```
## Focal decision and horizon
- Focal decision: <one line>
- Horizon: <period>
- Assumptions: <what you assumed because the user did not say, or "none">

## Driving forces
- Predetermined elements: <forces that hold in every world>
- Critical uncertainties: <the contenders and why the two axes were chosen>

## The two axes
- Axis A: <name>, from <pole> to <pole>
- Axis B: <name>, from <pole> to <pole>
- Independence check: <one sentence>

## The four worlds
| | <Axis B pole 1> | <Axis B pole 2> |
|---|---|---|
| <Axis A pole 1> | World 1: <name> | World 2: <name> |
| <Axis A pole 2> | World 3: <name> | World 4: <name> |

- World 1: <name> (<pole> x <pole>): <3 to 5 sentence narrative>
- World 2, World 3, World 4: same shape

## Robustness read
| Move | World 1 | World 2 | World 3 | World 4 | Verdict |
|---|---|---|---|---|---|
| <move> | <wins/survives/weak/fails> | ... | ... | ... | <robust/bet/gap> |

- Robust moves: <commit regardless of which world arrives>
- Bets: <each bet and the world it relies on>
- Gaps: <uncovered exposures>

## Signal watch-list
| World | Early signals that it is arriving |
|---|---|
| <name> | <2 to 3 observable indicators> |

## Options to keep open
<2 to 3 options and the worlds they pay off in>

These worlds are structured speculation, not predictions or ranked probabilities. <one-line note that this is not professional advice, if the decision is financial, legal or regulatory>
```

## Before you reply

Check: the decision and horizon are stated; both axes are high-impact, uncertain and independent; the four worlds really differ; every move is tested in every world; every world has signals; nothing is ranked by likelihood; no invented figures. Then send the full scenario set in the reply.
