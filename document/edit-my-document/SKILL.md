---
name: Edit My Document
description: >
  Makes the exact changes you ask for in a Word, Excel, PowerPoint or PDF file and returns the same file with everything else untouched.
  Use it for "change the name everywhere", "delete that paragraph", "fix the date", "make the title bigger", "move this section up", "remove slide 3", "change this figure in my file". Also works on pasted text.
---

# Edit My Document

The user has a file (or pasted text) and a list of specific changes. A good result is the same file with only those changes made: same styles, tables, formulas, slides and layout, not a rebuilt document. Never regenerate a file to apply a small edit.

## Hard rules

- **Language**: reply in the language the user wrote in. Keep the file's own language. Write replacement text exactly as the user gave it, with their spelling, names and figures. Do not "improve" anything.
- Make only the listed edits. Do not fix typos, restyle, reword or reformat anything else, even if you notice a problem; mention it in one line at the end instead.
- Never invent a replacement. If an edit needs a value the user did not give ("update the date" with no date), do not do it: list it under "Not done" and say what is needed.
- Do not open with questions. Decide, state the assumption, deliver.
- Do the edits with the bundled script, which edits the file in place. Do not recreate the file with another tool.
- The edited file is a draft for the user. Do not send it anywhere.

## Step 1: List the edits

Write the user's request as a numbered list, one edit per line, in this shape:

`1. replace "<old text>" with "<new text>" (everywhere / only the <n>th / only on <page, slide, sheet>)`
`2. delete the paragraph that starts "<first words>"`
`3. make the text containing "<words>" <n> pt / bold`
`4. move the section "<heading>" after the section "<heading>"`
`5. delete slide <n>; move slide <n> to position <m>`
`6. set cell <sheet>!<cell> to <value>`
`7. delete page <n> (PDF)`

Read "everywhere" as all occurrences. If the user says "change the name" and gives no scope, change all occurrences and say how many. Take old text exactly as the user wrote it. If the user's old text could be a prefix of something longer, check in Step 3.

## Step 2: No file attached, text pasted

Apply the edits to the pasted text by hand and return the whole text in the reply, in full, with only those changes. Then give the change log (Step 5). Count occurrences with `execute_code` (`text.count(old)`) rather than by eye, and do the replacement in code too: `text.replace(old, new)`.

## Step 3: A file is attached

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `edit_file.py` under `~/.computer/skills` with `search_files`. Run `mkdir -p /tmp/.scratch/edit-my-document`.

Supported files: `.docx`, `.xlsx`, `.pptx`, `.pdf`. An old `.doc`, `.xls` or `.ppt`: load the built-in `file-converter` skill with `skill_view`, convert it to the new format first, and say so. An image or a scanned PDF has no text to edit: say so in one line. If the user wants it editable, load the built-in `file-converter` skill (OCR section) and tell them what will and will not be editable.

1. **Scan**: `python3 SKILL_DIR/scripts/edit_file.py scan <file>`. It prints counts (paragraphs, tables, slides, sheets, formulas, pages) and an outline.
2. **Find each target**: for every replace edit run `python3 SKILL_DIR/scripts/edit_file.py find <file> "<old text>"`. It lists every occurrence, numbered in file order, with its place and some surrounding text.
   - Found exactly as many times as expected: fine.
   - Found 0 times: try the text without quotes or extra spaces. If it is still not found, the edit goes under "Not done" with what the file does contain that looks close.
   - Found several times when the user meant one ("change the date" and there are three dates): if the user said "everywhere" or the occurrences are plainly the same thing (the same name), change all. Otherwise change none of them, and list the occurrences under "Not done" so the user can pick.
3. **Write the edits file** with `write_file` to `/tmp/.scratch/edit-my-document/edits.json`: a JSON list, one object per edit, in the order of the list. Read the script's usage with `python3 SKILL_DIR/scripts/edit_file.py` (no arguments) for the exact operations; the common ones are:
   - `{"op":"replace","find":"<old>","with":"<new>","occurrence":"all"}` (or a number from `find`)
   - `{"op":"delete_paragraph","starts_with":"<first words>"}` (.docx)
   - `{"op":"format","contains":"<words>","size":14,"bold":true}` (.docx, .pptx)
   - `{"op":"move_section","heading":"<heading>","after":"<heading>"}` (.docx; `before` also works)
   - `{"op":"set_cell","sheet":"<sheet>","cell":"B4","value":<value>}` (.xlsx)
   - `{"op":"delete_slide","slide":3}`, `{"op":"move_slide","slide":3,"to":1}` (.pptx); slide numbers refer to the file after the earlier edits, so list several deletions from the highest number down
   - `{"op":"delete_page","page":2}` (.pdf)
   For an edit the script has no operation for (add a new paragraph, change a picture, change a colour), do not rebuild the file: say it is not covered under "Not done".
4. **Apply**: `python3 SKILL_DIR/scripts/edit_file.py edit <file> /tmp/.scratch/edit-my-document/<name>-v2.<ext> /tmp/.scratch/edit-my-document/edits.json` where `<name>-v2.<ext>` is the original file name with `-v2` before the extension (`report.docx` becomes `report-v2.docx`). The script keeps run formatting when the old text is split across formatting runs, never touches formulas in `.xlsx`, and prints a line per edit plus `before:` and `after:` counts.
5. **Verify**: read the printed lines. Each edit must say `changed` or `done` with the number you expected. A line containing `NOT DONE` is reported under "Not done". Compare `before:` and `after:`: only the counts the edits should change may differ (a deleted paragraph removes one; a deleted slide removes a slide and its shapes; replacements change nothing). If a count moved that should not have, or a count of `changed` is wrong, fix the edits file and run again from the original file, not from the output.
6. **Check one thing by eye**: run `find` on the output file for the old text (it should be gone, unless you changed only some occurrences) and for the new text (it should appear). For a PDF, render the changed page to an image (`pymupdf`: `page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(...)`) and look at it once with `media_analyze` to confirm the new text is visible and nothing overlaps. Fix once if wrong.
7. **Deliver**: `publish_artifact` with `kind: "document"` and the file name from step 4.

Limits to say in the reply when they apply:
- **PDF**: the old text is removed and the new text is drawn in its place; nothing reflows, so a longer replacement can run into the next word. The new text and the rest of that line are drawn in a standard font close to the original (serif, sans or mono, bold or italic), not the file's own font, and `find` is matched with exact capitals. Say this in the reply. The new text uses a Latin font, so replacing text with non-Latin letters (Arabic, Chinese, Korean and so on) is not supported: put that edit under "Not done" and offer to rebuild the page with the built-in `pdf` skill instead.
- **.xlsx**: charts and pictures inside the workbook may not survive being saved. Say so when the workbook has any (the scan counts do not show this, so say it when the user's file is known to have charts).
- **Headers, footers and text boxes** in .docx are searched too; text in pictures is not. Tabs and line breaks are not part of the searched text, so an `old text` that spans one is not found.

## Step 4: Edits that need more than the script

If the user asks for large changes (rewrite a section, redesign slides, new content), that is a different job: do only the specific edits that the script covers and say the rest was not part of this change. Do not rebuild the file.

## Step 5: Reply

1. One line: the file, how many edits were applied out of how many asked.
2. **Change log**, one line per edit in the user's language: `<n>. <edit> | <where: paragraph, slide, sheet, cell, page> | before: "<old>" -> after: "<new>"`. For pasted text also give the full edited text above the log.
3. The published file (or, for pasted text, the full text above).
4. **Not done**, only if something was: each item with the reason (not found, ambiguous with the places listed, needs a value, not supported).
5. **Noticed but not changed**, only if you saw something obvious, one line.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, start again from the original file (or the last version, if the user is building on it) with the same script, save under the same name with the next version suffix, and say in one line what changed.
