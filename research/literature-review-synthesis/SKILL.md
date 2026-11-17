---
name: Literature Review and Annotated Bibliography
description: >
  Searches arXiv on a topic and writes a literature review: themes, agreements, disagreements, gaps, a short annotation per paper, and a reference list in APA, IEEE or BibTeX.
  Use it for "do a literature review of...", "survey the research on...", "annotated bibliography of 10 papers on...", "what do recent papers say about...".
---

# Literature Review and Annotated Bibliography

The user gets a review that synthesises many papers, not a list of them: themes, where papers agree and disagree, what is missing, one annotation per paper, and correctly formatted references. Every paper cited must have come from a search result in this conversation. Finish the whole job in one reply.

## Step 1: Fix the scope

Take everything from the user's message and decide the rest without asking. Write down:

- **Topic**: keep every qualifier the user gave (population, application, comparison, time window).
- **Paper count**: the user's number; if none, 10. Maximum 30 per review (the search script caps at 50 per query).
- **Citation format**: APA 7th, IEEE or BibTeX. Default APA, except BibTeX when the user mentions LaTeX or .bib.
- **Window and category**: only if the user gave them (for example "last 2 years" becomes `--start-date`, using today's date; "NLP" becomes `--category cs.CL`).

Read the one reference file for the chosen format now, before writing anything: `references/apa.md`, `references/ieee.md` or `references/bibtex.md`. It holds the citation rules and the report skeleton.

## Step 2: Search arXiv

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path where this says `SKILL_DIR`. If `skill_view` gives no path, find `arxiv_search.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/arxiv_search.py "<topic phrase>" --max-results <N> [--category <cat>] [--sort-by relevance|submittedDate|lastUpdatedDate] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD] > /tmp/.scratch/litreview/search1.json
```

Make the directory first (`mkdir -p /tmp/.scratch/litreview`). The script prints a JSON array with `id`, `title`, `authors`, `abstract`, `published`, `categories`, `abs_url`.

- Multi-word queries are searched as an exact phrase, so use a short concept phrase ("retrieval-augmented generation"), not a sentence. If the topic has several parts, run two to four complementary searches with different phrases and merge them.
- Use relevance sorting for a topical review, date sorting when the user wants the latest work.
- Ask for more than you need (about 1.5 times the count), then screen: drop papers off-topic for the user's actual question and duplicates (same `id`). Keep the requested number of the best fits.
- Read results with `execute_code` (load the JSON, print id, year, title, first author and the abstract) rather than printing raw files.
- If the script fails or arXiv is unreachable, try once more. If it still fails, use `web_search` for "arxiv <topic>" and `web_extract` on arxiv.org/abs pages, and take title, authors, date and abstract only from those pages. If neither works, tell the user the search failed and stop. Never fill in paper details from memory.
- If fewer papers come back than requested, report the real number. Do not pad.

## Step 3: Extract evidence

For each kept paper, write down from the abstract: research question (one sentence), method (one or two sentences), key findings the abstract states, and limitations (what the abstract admits, or what is clearly out of its scope; write "not stated in the abstract" if nothing). You read abstracts, not full texts: say so in the report, and never state numbers, datasets or results that are not in the abstract. Check that every kept paper has its arXiv id, authors, year and title before moving on.

## Step 4: Synthesise

Group the papers into themes the evidence supports (as many as there are, usually three to six; do not force them). Then identify:

- **Convergences**: findings or assumptions several papers share, with citations.
- **Disagreements**: differing conclusions or incompatible methods, with the papers on each side. If the papers study different things, say they are not directly comparable rather than inventing a conflict.
- **Gaps**: what the set leaves open, drawn from stated limitations and from what the set conspicuously does not cover.

If the set is too small or too varied for themes, say so plainly.

## Step 5: Write the report in the chosen format

Follow the skeleton in the format's reference file: title, date (today), papers reviewed, search scope, executive summary, methodology and limitations, themes, convergences and disagreements, gaps and open questions, per-paper annotations, references. For an "annotated bibliography" request, make the per-paper annotations the centre of the report and keep the synthesis short.

Format traps:

- APA and IEEE: author names come from the search result; do not guess missing initials. Titles in sentence case.
- BibTeX: every entry for an arXiv paper is `@misc` with `eprint`, `archivePrefix` and `primaryClass` taken from the first category in the result, unless the abstract page or the user verified a journal or conference version. Put all entries in one fenced `bibtex` block.
- Every cited paper appears in both the annotations and the references, and every in-text citation matches a reference.
- Methodology states the real queries, filters, sort order, the date searched, how many results were returned, how many were kept and why, and that only abstracts were read.
- Limitations says this is an arXiv-only search: it excludes journals and databases not on arXiv, and preprints may have changed or been published since. It is not an exhaustive survey.

## Step 6: Deliver

Put the complete report in the reply, including all annotations and the full reference list. Also save it as a Markdown file with `write_file` and publish it with `publish_artifact` (`kind: "file"`, name like `literature-review-<topic-slug>.md`) so the user can download it; the reply must still hold the whole report. Open the reply with one line stating the assumptions you made (count, format, window).

## Hard rules

- Only cite papers that appeared in a search result in this conversation. Never invent a paper, author, id, year, venue, quote or number.
- Findings come from abstracts and are labelled as such. No claims about full-text content, figures or tables.
- Do not claim the review is exhaustive or systematic in the PRISMA sense.
- Do not ask the user questions before starting; state assumptions and deliver.
- One paper only, or a request to critique a single paper, is not this skill: review that paper directly.
