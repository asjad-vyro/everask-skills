---
name: Academic Paper Review
description: >
  Turns a research paper (attached PDF, pasted text, arXiv or DOI link, or a title) into a structured peer-review: summary, strengths, weaknesses tied to sections, methodology ratings, questions for the authors and a recommendation.
  Use it for "review this paper", "critique this arXiv paper", "is the methodology sound?", "write a peer review", "summarise this study and its weaknesses".
---

# Academic Paper Review

A good result is a balanced review a conference or journal reviewer could submit: every strength and weakness points to a specific section, table or figure of the paper, every weakness comes with a fix, and the verdict follows from the evidence. The whole review goes in the reply itself, in full. Do not ask the user questions first: decide, state your assumptions, and deliver.

## Step 1: Get the paper

1. Attached PDF or pasted text: use what is there. Attachments are already read for you.
2. A URL (arXiv, DOI, publisher, OpenReview): call `web_extract` on it. For an arXiv abs link, try the `/pdf/` version if the abs page gives only the abstract.
3. Only a title or topic: run one `web_search` to find the paper, then `web_extract` the best match (arXiv preferred). If you cannot find or open the full text, say so in the first line, review only what you could read (abstract, public summary), mark the review as "abstract-level, not a full review", and do not invent sections, results or numbers.
4. Paywalled: work from the abstract and any open preprint, and say so.

Record the metadata: title, authors, venue or preprint status, year, field, and paper type (empirical, theoretical, survey, systems, position). Use "not stated" for anything the paper does not give. Never guess authors, venues or years.

## Step 2: Read for claims

Read in this order: abstract and introduction (claimed contributions), related work, method, experiments or proofs, limitations, conclusion. Then list the 3 to 5 main claims, each with the evidence the paper offers and a strength of Strong, Moderate or Weak. Compare what the conclusion says with what the results show; gaps between them are the best weaknesses.

## Step 3: Context search (at most two searches)

Run at most two `web_search` calls to place the work: recent strong baselines or surveys on the same problem, and known criticism of the main technique. Use findings only for the Literature Positioning section and name the source with its link. If nothing useful comes back, say "no external context found" rather than citing from memory. Never cite a paper you did not see in the input or a search result.

## Step 4: Assess

Read `references/rubric.md` for the rating scales, the focus areas for each paper type and the reviewer pitfalls. Apply the focus areas for this paper's type. Rate each of the six criteria 1 to 5 with a one-line justification drawn from the paper. If the paper gives no basis for a criterion (for example no variance reported), rate it low and say that is the reason, or write "not assessable".

## Step 5: Write the review

Use exactly this shape. Replace each `<...>` with content from the paper; write "not stated" where the paper is silent.

```
# Paper Review: <paper title>

## Paper Metadata
- Authors: <...>   - Venue / status: <...>   - Year: <...>
- Field: <...>   - Paper type: <...>   - Material reviewed: <full text / abstract only>

## Executive Summary
<2-3 paragraphs: what the paper does, the main findings as the paper reports them, and your overall verdict up front.>

## Summary of Contributions
1. <claimed contribution, one sentence>
2. <...>

## Strengths
### S1: <title>
<What, where (section / table / figure), why it matters.>
### S2: ... ### S3: ...

## Weaknesses
### W1: <title>   (Major / Minor)
<What, where, why it matters for the claims, and how the authors could fix it.>
### W2: ... ### W3: ...

## Methodology Assessment
| Criterion | Rating (1-5) | Assessment |
|---|:---:|---|
| Soundness | <n> | <one line from the paper> |
| Novelty | | |
| Reproducibility | | |
| Experimental design | | |
| Statistical rigor | | |
| Scalability | | |

## Questions for the Authors
1. <question that targets a real ambiguity>
2. <...>
3. <...>

## Minor Issues
- <notation, clarity, missing details, typos>

## Literature Positioning
<How the work relates to prior art; what is missing or unfairly compared; sources found in Step 3 with links.>

## Recommendation
- Overall: <Accept / Weak Accept / Borderline / Weak Reject / Reject>
- Confidence: <High / Medium / Low> because <reason, e.g. outside my expertise, could not check appendix proofs>
- Contribution level: <Landmark / Significant / Moderate / Marginal / Below threshold>
### Actionable suggestions
1. <specific fix>  2. <...>  3. <...>

## Limits of this review
<What you could not verify: proofs, code, data, parts of the paper you could not open.>
```

If the user wants a quick triage instead of a full review, give the Executive Summary, the top 3 strengths, the top 3 weaknesses and the Recommendation only.

## Hard rules

- Ground every strength and weakness in the paper text with a section, table, figure or equation reference. If you cannot point to where, drop it.
- Use only numbers, results and quotes that are in the paper. When you quote a figure, copy it exactly. Do not invent baselines, p-values, dataset sizes or citations.
- Give at least 3 strengths and 3 weaknesses when the full text was read; fewer only if the material is too thin, and then say why.
- Separate major from minor issues. Do not demand experiments out of scope for the paper, and review the paper submitted, not the one you would have written.
- The overall assessment must match the strengths and weaknesses listed. Do not judge by author or institution.
- Keep the tone professional and constructive: "Section 3.2 uses notation X before defining it, which makes Theorem 1 hard to follow" rather than "poorly written".
- Say plainly what you could not check. The review is an aid for the user's own judgment, not a substitute for expert peer review.
- Do not build a file unless the user asks for one; the review itself goes in the reply. If they ask for a Word document or PDF, load the built-in `docx` or `pdf` skill with `skill_view` and follow it.
