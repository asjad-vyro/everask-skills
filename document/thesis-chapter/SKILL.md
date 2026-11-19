---
name: Thesis Chapter Builder
description: >
  Builds or restructures one thesis or dissertation chapter to match the university's required structure, from the user's notes, data and sources.
  Use it for "write my methodology chapter", "restructure my chapter to the faculty guidelines", "draft chapter 1 of my thesis", "fit my results into the required headings". Not for polishing prose, answering reviewers or searching for literature.
---

# Thesis Chapter Builder

A good result is one chapter that has the sections, heading numbering, citation style and length the institution requires, and that says only what the user's own material supports. Every gap is visible, never papered over.

## Hard rules

- **Language**: write the chapter in the language the user wrote in, unless they ask for another (for example the university's language). Write all notes around it, and every marker below, in the user's language. Keep their names, figures, terms, hypotheses and research questions exactly as given.
- **Never invent** a source, quotation, statistic, participant count, sample detail, tool, date or finding. Use only the sources the user supplied. A claim that needs a source and has none gets a visible marker meaning "citation needed" in the chapter's language (`[citation needed]` in English) and goes on the gaps list. A method or result detail the user did not give gets a marker meaning "to be supplied: <what>" (`[to be supplied: <what>]` in English).
- **Keep the user's research whole**: never merge, drop, reword into something different or renumber their hypotheses, research questions, variables or data. Copy figures as given. Do any arithmetic (totals, percentages, means) in `execute_code` and copy the results.
- Cite only the references the user supplied, in the required style, and every in-text citation must match one of them. Do not add "further reading" the user did not give. Do not guess missing details of a reference (year, pages, DOI): mark them with a "check" marker in the chapter's language (`[check]` in English).
- **Do not open with questions.** Decide, state your assumptions in a line or two, and deliver in this reply.
- **Authorship**: the chapter is a draft built from the user's material. Do not help disguise authorship: decline any request to make the text pass AI detectors, read as "not AI-written" or hide that AI helped, and never hand the chapter to the built-in `humanizer` skill. Add one plain line at the end, in the user's language: the user is responsible for their institution's rules on AI assistance and should check them before submitting.

## Step 1: Find the required structure

1. If the user attached or pasted a guideline, handbook page or template, read it and list: required sections in order, heading numbering, citation style (with edition), length limits, tense or person rules, and figure/table rules. Use only what it says, with its own heading wording.
2. If no structure was given, read `references/chapter-structures.md` once and use the standard structure for the chapter type; say so in the assumptions line.
3. Citation style: use the one the guideline or the user names. If none is named, use author-date citations and say the style is an assumption. For APA 7th edition, follow the APA rules below. For any other style, follow it only where you are sure of the rule; otherwise keep the user's reference details as given and add the check marker.
4. If the guideline contradicts the user's request, follow the guideline and say so in one line.

**APA 7th edition (in-text and reference list):**
- Parenthetical citation (Author, Year); narrative citation Author (Year).
- One or two authors: name both in every citation, joined by "&" inside parentheses and by "and" in running text.
- Three or more authors: first author's surname plus "et al." from the first citation on.
- A direct quotation also gives the page: (Author, Year, p. <page>). Quote only words the user supplied.
- The list is headed "References" (or its equivalent in the chapter's language), in alphabetical order by the first author's surname, each entry with a hanging indent.

## Step 2: Map the material

Make a list of each required section, the user's material that belongs in it, and what is missing. Note which of the user's sources support which claims. Do not move on until every user item (each hypothesis, question, dataset, reference) has a home.

## Step 3: Write section by section

- Follow the required order and numbering exactly; use the guideline's own heading wording.
- Academic register, in the person and tense the guideline asks for; otherwise follow the usual academic convention of the chapter's language and field.
- Every paragraph rests on the user's material. Where the material is thin, write less and mark the gap rather than pad.
- Tables and figures: include the user's data; caption them as the guideline says; never create data.
- Finish with the reference list for the sources actually cited, in the required style, built only from the details the user gave.

## Step 4: Check before replying

1. Headings match the required list, in order.
2. Every in-text citation has an entry in the reference list and vice versa; none outside the user's list.
3. Every hypothesis and research question the user gave appears, numbered as they numbered it.
4. Every number in the text appears in the user's material or was computed in `execute_code`.
5. Count the words in `execute_code` and compare with any length limit.

## Step 5: Deliver

**Size**: write at most about 2,500 words of chapter text in one turn. If the chapter needs more, write complete sections in the required order up to that size, and list the sections that remain so the user can ask for them next. Complete sections beat a thin whole.

- If the chapter text is about 1,500 words or fewer and the user did not ask for a file, give it in the reply in full.
- If it is longer, or the user asks for Word or a file to submit, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build the .docx: headings as real heading styles, numbering as required, A4 paper unless the guideline or the user says otherwise. Do not add your own `publish_artifact` call. If the user asks for PDF, load the built-in `pdf` skill and build the PDF with it directly; never build a .docx and convert. Still give the lists below in the reply.
- If the user gave almost nothing (a topic only), do not fabricate content. Deliver a chapter skeleton: the assumed structure; for each section, its purpose in one sentence and bullet points of what it must contain; an opening paragraph written only from what the topic itself implies, with every claim that needs a source marked; and the list of what the user must supply.

Reply shape, all in the user's language (headings translated, not left in English):

1. One line: chapter type, structure used (the user's guideline or the assumed standard), citation style, language, and the format chosen (reply or file).
2. The chapter in full, or the file built above.
3. A gaps list: every citation-needed and to-be-supplied marker, each with what the user should add.
4. If the chapter is partial: the sections done and the sections that remain.
5. Assumptions made, briefly.
6. The AI-rules line from the hard rules.

## Optional sources

If the user asks to read their material from, or save the chapter to, Google Docs, Google Drive or Notion and that app is connected, do so. Otherwise work from what they gave you.
