# Revising research prose

Read this before you revise, draft or diagnose any text. The moves work in any language: apply them in the language of the user's text and in the user's field.

## 1. Polish or rewrite?

- **Polish** when the passage's claim is stable and the problems are in the wording.
- **Rewrite from the user's facts** when the passage promises more than the evidence shows, opens with the wrong thing (the tool instead of the problem), or is ordered the way the author discovered things instead of the way a reader needs them. Polishing sentences inside a wrong frame only gives a smoother weak paragraph. Treat the old text as material, not as the starting point.

## 2. Fix in this order

1. **Framing**: what is this passage really about, and does its opening say so?
2. **Structure**: reorder, merge or split; cut background the audience already knows.
3. **Terminology**: one name per concept; named methods, data and measures instead of generic nouns.
4. **Evidence and links**: tie each claim to its evidence. Where results sit with no interpretation, add the connecting sentence ("This shows...", "The implication is...").
5. **Compression**: cut what serves no claim (sections 4 and 6).
6. **Polish**: rhythm, punctuation, consistency.

Fixing wording before framing wastes effort: the sentences you polish may be the ones you cut.

## 3. Replace vague words with facts

| Vague | Replace with |
|---|---|
| "significant", "significantly" | the size of the difference and what it was compared with, using the user's numbers. Keep "significant" only where the user reports a statistical test that supports it |
| "novel", "innovative", "promising", "impressive", "state-of-the-art" | what is actually new or better, stated plainly (the mechanism, the data, the named comparison); otherwise delete the word. Use "state-of-the-art" only when naming the specific system |
| "effective", "robust", "efficient", "accurate" | the measure and the condition ("lower error than X on Y"), with the user's figure if there is one |
| "a large number of", "several", "over a period of time" | the number or duration the user gave |
| "data-driven approach", "various factors", "existing methods", "prior work" | the named method, the named factors, the named works or kinds of work |

The test: if a phrase could sit in any paper in the field, it does not belong in this one. If the user gave no fact to replace a vague word, do not supply one: delete the word, or leave a bracketed placeholder such as `[sample size]`.

## 4. Sentence and paragraph moves

- **Claim first, evidence second.** "Method X lowers the error on Y (Table 2)" in place of "Table 2 shows the results of the experiments".
- **Cut throat-clearing**: "It is important to note that", "In this paper, we", "It has been shown that", "in the framework of the present study", "a total of".
- **Put the action in the verb**: "The utilization of X led to an improvement in Y" becomes "Using X improved Y", but keep only the causal verb the design supports ("improved" needs a comparison; "was associated with" for observational data).
- **Voice.** Prefer active voice with a named actor ("We measured...", "The model predicts...") in abstracts, introductions and results. Passive is fine in methods when the field writes that way, and wherever the actor does not matter. Follow what the user's text and target venue do; do not force first person into a field that avoids it.
- **One idea per paragraph**, stated in its first sentence. Delete a paragraph that serves no claim. Merge paragraphs that make the same point and keep the best example, not three.
- **Delete tutorial material** the target readers already know (textbook definitions, standard background), unless the paper redefines the concept.
- **Numbers**: dense comparisons belong in a table or figure; prose states the pattern and points to it ("Table 3 lists all accuracies; the largest margin is over the static baseline").
- **Technical claims carry a citation** or a cross-reference to the section that supports them. When a later section restates a claim from an earlier one, carry the citation forward.
- **Split a sentence that carries two claims.** Long sentences are fine for parallel lists.
- **Headings.** If the venue or discipline prescribes headings (Introduction, Methods, Results, Discussion), keep them and let the first sentence of each paragraph carry the claim. Where headings are free, one that states the conclusion or the question ("Why linear baselines fail on bursty data") tells a skim-reader more than a topic label ("Baseline comparison"). The test: can someone reconstruct the argument from the headings alone?

## 5. Tone and calibration

- Say what the evidence shows with plain verbs. Hedge scope and mechanism ("our sample covers one hospital", "this may reflect..."), not the result itself. Never strip a hedge the design needs, and never add one the evidence does not need.
- Do not write "we solve the problem of X": say which aspect of which bounded problem the work addresses.
- Cut enthusiasm and filler: "great promise", "paradigm", "leverage", "utilize", "delve into", exclamation marks. Open a paragraph with "However" only for a real turn in the argument.
- At most one rhetorical question, and only in an introduction.
- Keep the user's register: formal and impersonal if that is the field's norm.

## 6. Cutting to a length

- Cut in this order: tutorial background, repeated examples, adjectives and filler, secondary detail. Cut last: results, the scope of the claim, and the limitations a reader needs to judge it.
- Never meet a limit by dropping a result or a citation the claim rests on.
- If the draft is already tight, say so and make only the fixes that matter instead of shrinking it for its own sake.

## 7. Before and after (the pattern, not facts to reuse)

| Before | After | What changed |
|---|---|---|
| "We propose a novel data-driven approach that leverages machine learning techniques to achieve significantly better results." | "We train [named model] on [named data] and compare it with [named baselines] on [measure]; [result, with the user's numbers]." | vague nouns named; the claim becomes a comparison; brackets mark what only the user can supply |
| "It is important to note that the measurements in the present study were taken from a total of 31 patients." | "We measured 31 patients." | throat-clearing and passive removed; the number kept |
| "Deep learning has shown great promise in many fields. We apply it to X." | "[Who has the problem] cannot [what breaks today], because [structural reason]. We ..." | opens with the problem, not the tool; the stakes must come from the user's material |
| "The results show that X causes Y." (observational data) | "X was associated with Y in this sample; the design cannot show that X causes Y." | claim matched to the design |
| "Experimental Results" (heading) | "[The method] beats all three baselines on both datasets" (only if that is true) | topic label becomes the conclusion |

## 8. Diagnosing a draft

When the user wants feedback instead of a rewrite, check for these in this order and report the ones that apply, most damaging first:

1. **Framing**: the opening does not match the real contribution, or the paper is framed too broadly or narrowly for its venue.
2. **Promise against evidence**: the abstract or introduction claims something the results do not show.
3. **Structure**: the order follows the author's process, not the reader's need; the background is longer than the contribution.
4. **Results without interpretation**: numbers with no stated pattern; unnamed baselines or controls; text that disagrees with a table.
5. **Terminology**: one concept with two names; generic nouns where a named method belongs.
6. **Contribution wording**: contributions written as activities ("we propose") rather than claims the paper defends ("we show"), or with nothing to point to.
7. **Missing links**: claims with no evidence, no citation and no cross-reference.

For each problem: a short quote, why it hurts the reader, and a one-sentence fix.
