---
name: Document Proofreader
description: >
  Finds the errors in a contract, policy or formal document and lists each with its location and a suggested fix.
  Checks cross-references, clause numbering, defined terms, party names, dates, figures and typos, and flags problems without rewriting the document.
  Use it for "proofread this contract", "check this agreement before we send it for signature", "find the errors in this policy", "final QA pass on our terms of service", "do the clause numbers and cross-references line up?".
---

# Document Proofreader

A good result is a table of real errors, each with the exact words quoted, where it is, why it matters and a specific fix, and nothing flagged that is only a style choice. Treat it as a forensic audit, not a quick read-through, because wrong numbering, stale cross-references, unused definitions and clashing dates do not show on one read: check them in separate passes, until a second reviewer would find nothing material that you missed.

## Step 1: Get the document and look inside it

1. Work from what the user gave: an attached file (its text is already in the conversation) or text pasted into the message. If several files are attached, check each one and the references between them, such as a schedule named in the main agreement.
2. If there is no document and no text, ask for it with `clarify`, because the job cannot be done without it. Otherwise ask nothing: decide, state the assumption in one line and deliver.
3. If a file's text is empty or scrambled (a scanned PDF, for example), load the built-in `pdf` skill with `skill_view` and follow it to read the pages. If you still cannot read it, say so. Never guess at missing text. A PDF's text is otherwise enough for the text passes; use page numbers in Location when the text shows them.
4. For a `.docx`, also look inside the file, because the text hides some defects. Find it in the sandbox (`search_files` by file name). A `.docx` is a zip: with Python's `zipfile` and `re`, read `word/document.xml` for hyperlinks (`w:hyperlink`, whose target address is in `word/_rels/document.xml.rels`), tracked changes (`w:ins`, `w:del`) and fonts or sizes (`w:rFonts`, `w:sz`) that differ from the rest of the body text; read `word/comments.xml` for comments left in; read `docProps/core.xml` for the created and modified dates. Use at most three tool calls for this. If it fails, carry on with the text and say so in Step 5.
5. Pasted text has no file to look inside. Carry on with the text and say so in Step 5.

## Step 2: Build three reference maps

Keep these in your working notes, not in the reply, and build them before you look for any error:

- **Entity map**: every name used for each party, exactly as written (capitalization, punctuation, suffix such as Ltd or Inc.), and where each form appears. Two forms of one company name may be an error.
- **Section and numbering map**: every heading and clause number in order, so skipped, duplicated and mixed-level numbers show up. If there is a table of contents, map it separately and compare.
- **Defined-terms map**: every term the document defines, where it is defined, and each later use. This shows inconsistent use, capitalized terms that are never defined, and definitions that nothing uses.

For anything longer than a few pages, build the numbering list and the cross-reference check with a short Python script in `execute_code` (standard library `re`) rather than by eye: list every clause number, list every "clause X", "section X" or "Schedule X" mention, and flag any mention that points to a number not in the list. Word's automatic numbering may not appear in the extracted text, so if headings look unnumbered, check the file (Step 1) before you report missing numbers.

## Step 3: Run the eight passes

Run each row as its own pass with that one lens. When several anomalies cluster in one paragraph (an odd font, a wrong name, different quotation marks, a stray space), widen the check around it: text pasted in from another document often brings more than one error with it. Treat a cluster as a reason to look closer, not as proof. Skip a pass that does not apply to this kind of document (no defined terms in a letter, for example).

| Pass | What to check | Example of an error |
| --- | --- | --- |
| Definitions | Defined terms used the same way every time, including case; every capitalized term defined; no duplicate, conflicting or circular definitions; definitions that nothing uses; defined terms matching how the clauses use them. | "Financial Information" is defined once and never used again. |
| Cross-References | Every clause, section, schedule, exhibit, annex and other document mentioned exists, is the right one and is numbered correctly, including after drafting changes. | The preamble says "Terms of Use" but clause 4 says "Terms of Service" for the same document. |
| Internal Consistency | Terms, dates, parties, amounts, thresholds, notice periods, conditions, remedies or obligations that conflict, including a scope that includes Affiliates in one place and excludes them in another. | "Confidential Information" includes Affiliates in clause 1 but excludes them in clause 9. |
| Parties and Entity Names | Names, suffixes, registration details, capacities, addresses, signatories and role labels the same throughout; names that differ by a letter, a space or capitalization; conflicts between the preamble and the definitions. | "Acme Holdings, Inc." in the preamble but "Acme Holdings LLC" in the definitions. |
| Numbers, Dates, and Calculations | Amounts, percentages, dates, deadlines, periods, rates, formulas and schedules; words against figures; totals and date arithmetic recomputed (in `execute_code`, not in your head); dates that make no sense, such as an end date before its start date or a future date in the file properties. | "Under the age of 16 (seventeen)". |
| Grammar and Typos | Spelling, grammar, punctuation, missing or doubled words, tense, subject-verb agreement, unfinished sentences, missing final punctuation, leftover placeholders such as "[insert date]" or "TBC" (blank signature and date lines are normal). | A doubled word ("the the"), or a sentence that stops mid-clause. |
| Numbering | Clause, sub-clause, schedule, exhibit and table numbers: skipped, duplicated or out-of-order numbers, headings that should be numbered, mixed markers in one list, a table of contents that does not match. | Sections run 5, 7 with no 6; two clauses are both labelled (vii). |
| Formatting | Heading and list formatting, indentation, spacing, fonts, emphasis, heading case, hyphenation, hyperlink targets that differ from the visible text, leftover comments or tracked changes, stray spaces. | The link text says privacy@example.com but its target is privacy@example.org. |

## Step 4: Rate each issue

Rate by the likely consequence in this document, not by the type of defect. Do not downgrade an issue because the visible difference is small.

- **Critical**: may materially change rights, obligations, parties, timing or enforceability: the wrong legal entity, a link that sends a legal notice to the wrong recipient, a wrong operative date, numbering that breaks the cross-reference scheme.
- **High**: likely to cause ambiguity, negotiation friction or implementation risk: a truncated sentence, a conflict between figures, a material unused definition, a grammar error that changes the meaning.
- **Medium**: should be fixed but is unlikely to change the main effect.
- **Low**: a minor typo, punctuation, formatting or style slip.

## Step 5: Write the reply

Put the whole result in the reply. Do not publish a file unless the user asks for one. Use this shape:

1. One line: what you proofread (the file name, or "the pasted text") and how many issues you found (count the table rows).
2. A Markdown table with exactly these five columns, in this order, sorted Critical first, then High, Medium, Low:

   | Severity | Category | Location | Issue | Recommended Fix |
   | --- | --- | --- | --- | --- |
   | High | Grammar and Typos | Clause 12.1 | The sentence ends "...such as a phone number or an)", so it is cut off and the provision may be incomplete. | Complete the sentence, or delete the dangling words if nothing was meant to follow. |

   That row only shows the format. Then:
   - One row per problem. If the same error appears in several places, list every place in that row.
   - Category is the name of the pass that found it.
   - Location is the most specific place you can give: "Clause 6.2", "Schedule 1, second line", "Section 3, second paragraph". A Word file has no fixed page numbers, so use the clause or heading. If nothing is numbered, give the heading and the first words of the paragraph.
   - Issue says what is wrong, quotes the exact words from the document, and says in one sentence why it matters.
   - Recommended Fix is a specific correction, with short replacement wording where it helps. When the document does not show which version is right (two different dates, two spellings of a party's name, a figure that disagrees with its words), do not pick one: write "Confirm which is intended" and give both options.
3. **Summary of most critical issues**: the two to five items to fix first, numbered, most serious first, one line each.
4. **Checked:** one line on what you checked. **Not checked:** one line on what you could not check, or "nothing". If you worked from pasted text, or could not open the file, say that hyperlink targets, fonts, tracked changes, comments and file properties could not be checked, and that attaching the original .docx or PDF would allow it. If you did open the file, say what you looked at and what you found.
5. If the document is a contract or other legal text, end with one line: "This is a proofreading check, not legal advice."

If you find nothing material, give a single table row that says so, and still add the Checked and Not checked lines.

## Step 6: Check your work before you reply

- Every pass was run, or skipped on purpose because it does not apply, and any table of contents was compared with the real headings.
- Every Location exists in the document, and every quoted phrase is word for word what the document says.
- Every number and cross-reference you called wrong was looked up in your maps, not recalled.
- Nothing in the table is only a style preference.

## Rules

- **Flag, do not fix.** Do not rewrite the document or return an edited copy unless the user asks. If the user asks for a corrected copy, apply only the fixes you listed, leave marked any choice the user has to make, and build the file with the built-in `docx` skill.
- **Errors, not preferences.** Do not flag a consistent style choice you would have made differently: the Oxford comma, UK or US spelling, bullets or numbers, sentence length, readability, or a valid word choice. Style is an issue only where the document is inconsistent with itself. A reference to a clause by its top-level number is not an error when that clause exists and is specific enough in context. When you cannot tell whether something is an error or a preference, say so in the Issue column ("Possible error: confirm") instead of presenting it as certain.
- **Only what the document says.** Never cite a clause, name or date that is not in it. Judge the document against itself: do not rule on facts outside it, such as laws, prices or company details. If something looks wrong but cannot be checked from the document, list it with "To verify" in the Issue column.
- **Write fixes in the document's own style**, such as its UK or US spelling and its way of writing numbers.
- **Finish in one reply.** Do not show a plan and wait, and do not ask the user to approve the passes.
