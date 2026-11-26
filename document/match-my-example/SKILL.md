---
name: Match My Example
description: >
  Builds a new Word or Excel document in the same structure, layout and style as an example you supply, filled only with your new content.
  Use it for "write this week's report like last week's", "same format as this letter, new details", "use this file as a template", "make another one just like this".
---

# Match My Example

The user gives an example (last week's report, an old letter, a template) and new content. A good result is a new document with the example's headings in the same order, the same tables, fonts, header and footer, tone and length per section, holding only the new content. Nothing from the example's old content survives unless the user says it still applies.

## Hard rules

- **Never carry over a fact from the example**: names, dates, figures, prices, amounts, addresses, reference numbers, quotes. Only the fixed parts (headings, labels, column titles, boilerplate the user says is standing text) stay.
- **Never invent for this job**: content for a section the user gave nothing for, a date, an author, a number, a name. Write `[to add: <what goes here>]` in that spot instead, in the example's own format. A placeholder names the kind of thing needed ("date", "venue"); it never suggests a value ("e.g. the school library"), not even after "like" or "such as" (write `[falta: otra atracción]`, never `[falta: otra atracción, como música]`) and never reuses one from the example. In a text reply write the placeholder word in its language (for Spanish `[falta: fecha]`); in a file keep `[to add: ...]` so the script can count it.
- **Language**: write in the language of the new content (or the language the user asks for). Keep the user's names, figures and terms exactly as given. If the example is in another language, its fixed labels stay as they are unless the user asks to translate them.
- Do not open with questions. The first sentence of the reply is the result ("This week's report is ready ..." or the new text itself), never "I'll load the skill ..." or any other narration of tool use. Decide, state the assumption, deliver.
- The result is a draft. Nothing is sent anywhere.

## Step 1: Gather

- The example: if it is a Google Doc, Drive file or Notion page and that app is connected, fetch it; otherwise ask the user to attach it or paste it. An attached .docx or .xlsx, or pasted text. A .pdf example or an old .doc: load the built-in `file-converter` skill with `skill_view` and convert it to .docx first, and say layout may differ. An image of a document: read it with `media_analyze` and treat it as pasted text.
- The new content: in the message or attached. If there is none at all, use `clarify` once to ask for it. If it is partial, go on and mark the gaps.
- If the user says which parts of the example are standing text (for example the footer or a disclaimer), note them for `fixed`.

## Step 2: Read the example's skeleton

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `match_example.py` under `~/.computer/skills` with `search_files`. Run `mkdir -p /tmp/.scratch/match-my-example`. The attached file is on disk in the sandbox; its path is in the message or the attachment list.

Run `python3 SKILL_DIR/scripts/match_example.py skeleton <file>`. It prints, for a .docx, every paragraph with its index, kind (heading, list, body), style, word count and a text preview, each table's shape and first rows, the header and footer text, the words per section; for a .xlsx, each sheet's size, first rows, formulas and merged cells.

Write the skeleton down for yourself as: `heading order | what each section holds (kind of content, rough length) | tables (columns) | recurring labels | tone`. Decide for every paragraph: **fixed** (a heading, label or standing text; keep), **value after a label** (like `Week ending: <value>`; keep the label, replace the value), **content** (replace), or **extra** (an example bullet or table row the new content has no match for; delete it).

## Step 3: Map the new content onto the skeleton

For each section, take the matching part of the new content. Keep the example's tone and rough length per section (use the words-per-section numbers): do not pad a thin section and do not copy the example's sentences. If the new content has more items than the example (more bullets, more table rows), add them in the same format; if fewer, delete the extra ones. A section with no new content gets one `[to add: ...]` line, not an invented one. Dates and sums the user did not give stay placeholders; if the document needs a total, compute it with `execute_code` from the user's figures.

## Step 4: Fill a copy (file examples)

Write `/tmp/.scratch/match-my-example/plan.json` with `write_file`. Run `python3 SKILL_DIR/scripts/match_example.py` with no arguments to see every operation. The plan lists `fixed` (the text that is meant to stay: headings, labels, column titles, standing text) and `ops`. Paragraph and table numbers are the example's own numbers from the skeleton, even after you insert or delete.

For .docx, the common ops are `set_paragraph` (with `keep_prefix` for `Label: value` lines), `insert_after` (a new bullet or paragraph formatted like an existing one), `delete_paragraph`, `set_table_rows` (all data rows of a table at once) and `replace_in_headers`. Every old value in headers and footers (names, dates) must be replaced or marked `[to add: ...]` too. For .xlsx: `clear_values` (keeps formulas), `set_rows` (new rows copy the format and formulas of the first row) and `set_cell`. Check that totals and ranges (`=SUM(D2:D4)`) cover the new rows, and fix them with `set_cell` if not.

Then run `python3 SKILL_DIR/scripts/match_example.py fill <example file> /tmp/.scratch/match-my-example/plan.json /tmp/.scratch/match-my-example/<meaningful name>.<ext>`. The example file itself is never changed.

## Step 5: Verify

Read the printed JSON:

- every log line says `done`; a `NOT DONE` line is fixed or reported;
- `headings_after` equals `headings_before` in order for fixed headings, `table_columns_same` is true;
- `leftover_phrases_from_example` and `numbers_also_in_example` (and, for .xlsx, `same_as_example_not_marked_fixed`) hold the old content that is still in the new file. Each one is either something you listed as fixed by mistake, or an old fact you must replace. Fix the plan and run again from the example, not from the output. A number that is truly the same in both (the user's figure happens to match) is fine: say so.

## Step 6: Deliver

- A file example: `publish_artifact` with `kind: "document"` and the output file.
- A pasted example, or when the user wants text (the reply starts with the new text, then the notes below): write the new document in full in the reply, with the example's headings in the same order, its list and table shapes (as Markdown tables), and its tone. If a file is wanted, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step; do not add your own `publish_artifact` call for that file.

Then the reply, in the user's language:

1. One line: what was made.
2. **Kept from the example**: headings, tables, styles, header/footer, labels.
3. **Filled with your content**: section by section, one short line each.
4. **Still missing**: every `[to add: ...]` spot and what is needed.
5. **Check**: no old names, dates or figures remain (or the ones listed as standing text, or the ones that match).
6. For a .xlsx example: charts and pictures inside the workbook may not survive being saved; say so if the example had any.

## Final self-check

Same headings, same order? Same table columns? No fact of the example left outside the fixed parts? Every gap a visible `[to add: ...]`? Nothing invented? File published or text in full?

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, start again from the example (or the last version, if the user is building on it) with an updated plan, save under the same name with the next version suffix, and say in one line what changed.
