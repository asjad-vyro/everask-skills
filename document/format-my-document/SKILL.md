---
name: Format My Document
description: >
  Reformats your Word document to a required standard (university, journal or office rules, or a named style such as APA 7) and returns the same text in a corrected .docx, with a rule-by-rule report.
  Use it for "format my report to these guidelines", "make my thesis 12pt Times with 1.5 spacing", "number my headings", "put my references in order", "add a table of contents and page numbers", "make it match the university template rules".
---

# Format My Document

The user has a document and a standard it must meet. A good result is the same document, word for word, in the required format, plus an honest list of which rules were applied and which were not. Formatting is never an excuse to change what the document says.

## Hard rules

- **Never change the wording.** Do not retype, fix typos, shorten or "improve" anything. The script edits the uploaded file in place and checks that the text is unchanged. The only text it may touch is heading numbers, caption numbers and reference punctuation or order, and only when asked.
- **Never invent for this job:** a formatting rule the user did not give and the named style does not clearly state; a missing author, year, title, page range or DOI in a reference. A rule you cannot stand behind goes under "Not applied, please confirm". A reference with a missing field stays as it is and is listed as incomplete.
- **Language**: reply in the language the user wrote in; keep the document's own language, names and figures.
- Do not open with questions. The first sentence of the reply is the result ("Your formatted report is ready ..."), never "I'll start by loading ..." or any other narration of tool use. Decide, state the assumption, deliver.
- The result is a draft for the user to check in Word. Nothing is sent anywhere.

## Step 1: Turn the standard into a numbered rule list

Sources, in this order: rules pasted by the user, a guideline file they attached (read it), then a named style (for example "APA 7"). Write the list in your reply working notes as `R1. <rule> (from: user | guideline file | <named style>)`. Cover, where the source says something: page size and margins, body font and size, line spacing, space between paragraphs, first-line indent, alignment, title, heading levels (font, size, bold, alignment, numbering), caption format for tables and figures, reference list (order, hanging indent), page numbers, table of contents.

If only a style name is given, use at most two `web_search`/`web_extract` calls to read the official formatting guidance and take only rules stated there, naming the page. Rules you did not find or are not sure of are not applied. If the user gave nothing at all to go on (no rules, no style name), use `clarify` once to ask which standard.

Some rules the script cannot do: page numbers in the header (it writes them in the footer), running heads, columns, footnote formatting, text boxes, equation formatting, cover-page layouts. List them under "Not applied".

## Step 2: Look at the file

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `format_docx.py` under `~/.computer/skills` with `search_files`. Run `mkdir -p /tmp/.scratch/format-my-document`. Never install a package; python-docx is already there.

If the user names a file in Google Docs or Google Drive and that app is connected, you may export it as .docx; otherwise ask them to attach it and carry on with what you have. The attached file is on disk in the sandbox; its path is in the message or the attachment list. Only `.docx` is edited in place. An old `.doc`: load the built-in `file-converter` skill with `skill_view` and convert to .docx first. A PDF has no editable styles: say the document is rebuilt from its text, or convert it with `file-converter` first, and say that layout may differ.

Run `python3 SKILL_DIR/scripts/format_docx.py audit <file>`. It prints the page size and margins, the fonts, sizes and line spacings in use, real headings, **manual heading candidates** (short all-bold paragraphs that are not styled as headings, with a suggested level), captions and the reference block. Use it to decide:

- Which candidates are really headings. If all are, use `"detect_manual_headings": true`. If some are not (a bold label, a title), use an explicit `"promote": [{"index": n, "level": l}]` list instead. The title paragraph is given as `"title": {"paragraph_index": n, ...}`.
- Where the reference list is (the heading text, for `references.heading`).

## Step 3: Write the rules file and apply

Write `/tmp/.scratch/format-my-document/rules.json` with `write_file`, using only the keys the rule list supports. Run `python3 SKILL_DIR/scripts/format_docx.py` with no arguments to see every key. Shape:

```
{"page": {"size": "A4", "margins_cm": {"top": <n>, "bottom": <n>, "left": <n>, "right": <n>}},
 "body": {"font": "<font>", "size": <pt>, "line_spacing": <multiple>, "alignment": "<left|justify>", "first_line_indent_cm": <n>},
 "title": {"paragraph_index": <n>, "size": <pt>, "bold": true, "alignment": "center"},
 "headings": {"1": {"size": <pt>, "bold": true}, "2": {"size": <pt>, "bold": true}},
 "detect_manual_headings": true,
 "heading_numbering": {"max_level": 3, "unnumbered": ["References"]},
 "captions": {"size": <pt>, "italic": true, "alignment": "center"},
 "references": {"heading": "References", "sort": "alphabetical", "hanging_indent_cm": <n>},
 "page_numbers": {"position": "center"}, "toc": {"levels": 3}}
```

Only put in a key the user's rules or the named style asked for. Use the values from the rule list, never your own defaults. Notes:

- `heading_numbering` writes "1", "1.1" as text at the start of each heading (existing manual numbers are replaced). Put headings that must stay unnumbered (References, Abstract, Contents) in `unnumbered`.
- `captions.renumber: true` renumbers tables and figures in order; use it only if the user asked for it or the numbers are clearly wrong, and say so.
- `references.sort: "alphabetical"` only reorders. For re-punctuating entries use `reference_edits` (`{"index": n, "text": "..."}`) and only when every word and number in the new text is already in the old entry; the script flags any edit that changes the words. For a numbered style (IEEE, Vancouver) use `"sort": "none"`.
- East Asian text: give `"east_asian_font"` and use `first_line_indent_chars` (2 means two characters) instead of cm.
- A text-only request (pasted text, no file): write the text to `/tmp/.scratch/format-my-document/in.txt` exactly as given (one paragraph per line, `# ` before the title, `## ` and `### ` before headings if the user marked them), run `python3 SKILL_DIR/scripts/format_docx.py new in.txt /tmp/.scratch/format-my-document/in.docx`, then continue with that file. The new file is A4; if the user's rules name another page size, put it in `page`. Tell the user about the A4 assumption in "Not applied, please confirm" when they gave no page size.

Run `python3 SKILL_DIR/scripts/format_docx.py apply <file> /tmp/.scratch/format-my-document/rules.json /tmp/.scratch/format-my-document/<original name>-formatted.docx`. It prints JSON: `rules` (each with status and number of places), `text_check`, `before` and `after`.

## Step 4: Verify

- `text_check.ok` must be `true` and `unexpected_text_changes` empty. If not, fix the rules (usually a wrongly promoted paragraph or a `reference_edits` entry that changed words) and run again from the original file.
- Compare `before` and `after` to confirm the rules took effect: one font, one size, the margins and spacing asked for. Anything that still differs (for example another font in a table or in text the script does not reach) is listed under "Not applied".
- Look at the numbers, not at what you intended. Report a rule as applied only if its status says `applied` and `after` agrees.

## Step 5: Deliver

Publish the file with `publish_artifact` (`kind: "document"`) under its meaningful name. Then the reply, in the user's language:

1. One line: the file name and that the wording is unchanged (from `text_check`).
2. **Rules used**: the numbered rule list with its source for each rule.
3. **Audit**: a table `rule | status | places changed`, from the script output.
4. **Headings promoted or renumbered**, and what was reordered or renumbered, so the user can see it.
5. **Not applied, please confirm**: every rule you left out and why (not stated by the source, unsure, or not possible in a .docx edit). Incomplete references (missing author, year or title) are listed here by number; they were not completed.
6. **To do in Word**: if a table of contents was added, open the file and choose Update Field (Word may ask on opening). Check the page numbers and the page count against any limit.

## Final self-check

Wording unchanged? Every rule traced to the user or a named source? Nothing invented (no added author, year, DOI or rule)? Every rule I could not do listed? File published?

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, start again from the original file (or the last version, if the user is building on it) with the same script and an updated rules file, save under the same name with the next version suffix, and say in one line what changed.
