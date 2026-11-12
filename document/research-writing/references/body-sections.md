# Related work, methods, results, discussion, conclusion

Use only the parts for the sections the user asked about. Where the user's venue or field has its own conventions, follow them.

## Related work: position the paper, do not survey the field

- Group prior work into two to four kinds of approach, named by the approach and not by author. More than four groups usually means the right grouping has not been found.
- For each group, state its limit, and make it structural (an inherent property of the approach) rather than quantitative ("did not do enough"). Tie each limit to what this paper does.
- End with one positioning sentence: "Unlike X, this work provides Y while keeping Z". Say honestly what the work does not do.
- Give space in proportion to how much each group matters for the positioning, not equal space to all.
- Cite only works the user supplied or you verified. Where the user's list is thin, write `[citation needed: what it must support]` rather than naming papers.
- Placement: after the results when the novelty is mainly empirical (it reads as confidence); early, folded into the background, when the reader needs the landscape before the contribution makes sense.
- Check that the baselines named here are the ones used in the results, and that a reviewer asking "how is this different from the closest work?" finds the answer already written.
- Avoid: an exhaustive survey, paper-by-paper summaries, and explanations of things the audience already knows.

## Methods or design

- Lead with the idea or the study design the reader should hold in mind, then the details.
- Say why this design and not the obvious alternative ("the simple approach fails because..."): it makes the choice look reasoned. Use only reasons the user gave.
- Break it into named parts in the order the reader traces them (stages of a pipeline, or design, participants or data, measures, procedure, analysis). Reuse the same names in the results.
- Give enough to reproduce it: data source and sample, software and parameters, measures, analysis plan. Keep formulas with their variables, units, assumptions and the conditions under which they apply.
- Name the main adjustable parameter or trade-off and say what it controls.
- Say what happens when the assumptions fail (edge cases, sensitivity). If the user has not said, leave it as an open point instead of inventing it.
- Passive voice is normal here in many fields.

## Results or evaluation

- **Setup in a few lines**: data, comparisons and measures, enough to reproduce and no more. Name every baseline, control and measure, and say why each was chosen (what does beating this baseline show?).
- **Head-to-head**: compare directly against the named baselines or the control, with the measures from the setup. This is the core evidence for the introduction's claims.
- **Where and when**: break the results down by meaningful conditions to show where the approach helps most and least. An honest breakdown makes the paper more credible.
- **Takeaway after each group of results**: one to three sentences saying what the pattern means and which claim it supports, readable without the detailed numbers ("Takeaway: [method] beats every baseline, with the largest margin under [condition]").
- **Ablations or sensitivity**: show which parts matter. If a variant beats the full approach, say so and explain it.
- **Robustness**: new data, new settings, cost or overhead, when the user has them.
- Report what cuts against the story (a non-significant primary outcome, a variant that wins) plainly in the body, not in a footnote.
- Two different kinds of claim (for example "it works correctly" and "it improves a downstream result") need separate subsections, each with its own baselines and measures.
- Text and tables agree: every number in the prose matches the table, with the same units and time range.
- **Captions**: lead with the finding ("X beats Y at every budget"), then say what is plotted; label axes with units; make each figure readable on its own.

## Discussion

Order each point as claim, evidence, explanation of why, then the limit. Compare with prior work the user cited. State limitations specifically (what the design cannot show) instead of a generic "further research is needed". Keep implications within what was tested.

## Conclusion

Answer the research question in the first sentence. Summarise the evidence in a few sentences without copying the abstract. State the limitations and the concrete next steps that follow from them.

## Whole-paper consistency

- Each promise in the introduction maps to a result.
- A named idea has the same name in every section.
- The headings follow the order of the contributions listed in the introduction.
- Every figure and table is cited by a claim in the text.
