# Planning a paper from an unclear idea

Use this when the user has an idea, notes, a pile of results or a half-formed argument and needs a plan. Answer each question below from what the user gave you. Where the material has no answer, write "Open:" and carry it to the open questions. Do not interview the user and do not invent an answer: an honest gap is more useful than a made-up one.

## Questions to answer from the user's material

**The problem**
1. Who is affected? Name the specific group, not just "users".
2. What breaks for them today, concretely?
3. Why does it break? Look for a structural reason, not "more effort is needed". If the only answer is more data, compute or effort, this may be an engineering task rather than a research contribution.
4. What does leaving it unsolved cost? Use only what the user gave you.

**The gap**
5. What do the existing approaches assume that fails here? Name two or three.
6. Is the limit structural or quantitative? A purely quantitative gap invites the reply "incremental".
7. Put the existing approaches against the capabilities that matter in a small matrix: where is the empty cell?

**The claim**
8. Complete: "This paper shows that ____." The verb is *shows*, not *proposes*. If it cannot be completed, the contribution is not clear yet.
9. What is the one thing a reader should remember after a minute's skim?
10. Can the core idea be named in two to four words? A placeholder name is fine.
11. Evidence map: for each claim, what evidence there is and its status (have / running / planned / missing). A claim with no evidence is an aspiration: move it to the open questions.
12. The headline result, only if the user has one.
13. What the work cannot do: name the limitations now.

**The evidence**
14. Baselines or controls, by name, and why each is the right comparison.
15. Measures, and why these. Include any that might make the work look worse: report them anyway.
16. Data or sample: why it suits the claims, and whether others can check it.
17. Experiments or analyses mapped to claims, each with what happens if it fails.
18. Ablations or sensitivity checks, a breakdown by condition, and the generalisation story.

**Positioning**
19. Target venue or course, with its limits and conventions.
20. Type of paper (table below): the type decides what reviewers expect.
21. The two or three closest works (the user's own list). For each: the structural difference, a case where theirs would be better, and a one-sentence answer to "how is this different?"
22. New category, or competing in an existing one?

**Narrative**
23. The arc in three or four sentences: the problem exists, existing approaches fail because..., the insight, what was done, what was found.
24. The moment the design looks inevitable: the obvious approach that fails and motivates it.
25. The version that fits in 280 characters.

## Paper types (examples)

| Type | The contribution is... | Evidence stresses... |
|---|---|---|
| Builds something new (method, system, tool) | what was built and what it enables | comparison with named baselines, ablations, feasibility |
| Studies or measures something (empirical study, trial, survey) | what was found and what it means | rigour of method, sample, reproducibility, the "so what" |
| Tests or breaks an existing approach | a failure or weakness | how realistic it is, real-world impact |
| Synthesises a field (review, taxonomy) | a structured synthesis | coverage, quality of the taxonomy, gaps found |
| Argues a position or theory | an argument | the reasoning and the counterarguments it meets |
| Reports a deployment or case | lessons from practice | operational results, surprises, how far it transfers |

Papers that build something need more "why this design" argument; studies need more "so what".

## Output shape

```
## Paper plan
**Core claim:** This paper shows that ...
**Problem and gap:** three to five sentences.
**Contributions and evidence:** table with Claim | Evidence needed | Status (have / running / planned / missing)
**Study or evaluation design:** baselines or controls, measures, data or sample, and what each experiment tests.
**Section outline:** table with Section | Its job in one sentence | Key claim | Figures or tables needed
**Weak spots a reviewer will hit:** two to four.
**Open questions:** everything marked "Open:" above, most important first.
```

Then, if the user's material allows it, add an early draft of the introduction's first paragraph, labelled as a draft to rewrite once the results are in. Writing it early forces the framing to be stated and shows what the evaluation must demonstrate; the final introduction is rewritten from the real evidence.
