---
name: Document Translator
description: >
  Translates a whole document into another language and hands it back in the same layout, or side by side with the original.
  Use it for "translate this document", "translate this contract into Spanish", "translate this Word file", "put it in English and keep the original next to it", "translate my spreadsheet". Works on uploaded .docx, .xlsx, .pdf or pasted text.
---

# Document Translator

A good result reads naturally in the target language, has the same sections, lists, tables and numbering as the original, and every name, figure, date and reference code is exactly as it was. It is not a certified or sworn translation.

## Hard rules

- **Target language**: the language the user asked for. If they named none, translate into the language their message is written in; if the document is already in that language, translate into English and say so in one line. Write everything around the translation (notes, the summary line) in the language the user wrote in.
- **Never change** numbers, amounts, currencies, dates as written, names of people and companies, addresses, reference or case numbers, codes, URLs, email addresses. Do not convert units or currencies, and do not reformat dates unless the user asks. Copy every figure character for character, including its thousands and decimal separators and its currency symbol or word: `1,150 euros` stays `1,150 euros` in a Spanish text, never `1.150`. Say in a Notes line if the target language normally writes figures differently.
- **Addresses and names in another script**: an address, street or place name that is not written in the Latin alphabet (Korean, Chinese, Arabic, Cyrillic and so on) is kept as written and followed at once, in brackets, by its romanization or customary Latin form with the street number unchanged (`서울 마포구 월드컵북로 21 (21 Worldcup-buk-ro, Mapo-gu, Seoul)`), so a reader of the translation can use it. This is the only addition allowed. Do not make the translated text bold or otherwise styled unless the source is.
- **Translate everything** that is words, including headings, table cells, headers, footers and captions. Do not summarise, shorten, explain or add anything. If a passage is unclear, translate it as literally as is natural and add a short note at the end, not inside the text.
- **Do not open with questions.** Decide, state the assumption in one line, deliver.
- If the user asks for a certified, sworn or legally valid translation, say in one line that this is a working translation and a sworn translator must certify it for official use.
- The result is a draft for the user. Do not send it anywhere.

## Step 1: Read the source and the request

1. Note the source language, the target language, and the format: pasted text, `.docx`, `.xlsx`, `.pdf`.
2. Note the layout wanted: **translation only** (default) or **bilingual** (the user says "side by side", "bilingual", "keep the original", "both languages"). For bilingual, note the order: source first unless the user says otherwise ("English above Korean" means English first).
3. Note a register if the user gave one (formal, friendly). Otherwise match the register of the source.
4. If the user attached a file you cannot open, say so in one line and ask them to paste the text. Do not guess its content.

## Step 2: Build a fixed-terms list

Before translating, read the whole source once and write down, in your head or in a short list: names, product and company names, defined terms that recur, abbreviations, and codes. Decide each translation once (or "keep as is") and use it every time. Keep a defined term the same everywhere, for example the same word for "Tenant" in every clause.

## Step 3: Translate, by input type

### Pasted text, or a short document the user wants in the chat

Translate section by section. Keep the same headings, paragraph breaks, bullet or numbering styles and table layout (as a Markdown table). Then go to Step 4. The reply is the deliverable.

For a bilingual request, interleave paragraph by paragraph: each paragraph (and each heading, list item and signature line) in the requested order, the other language directly under it, then the next paragraph. Never give the whole translation first and the whole original after it. Pattern for "English above Korean": heading in English, the same heading in Korean, paragraph in English, the same paragraph in Korean, signature line in English, signature line in Korean. Use plain text, no bold or headings of your own.

### Uploaded .docx (translated in place so the formatting survives)

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `translate_units.py` under `~/.computer/skills` with `search_files`.

1. `mkdir -p /tmp/.scratch/document-translator`
2. Extract: `python3 SKILL_DIR/scripts/translate_units.py extract <the uploaded file> /tmp/.scratch/document-translator/units.json`. It prints how many units there are.
3. Read `units.json` with `read_file`. Each unit is `{"id": "p3", "text": "..."}`.
4. Translate the units and write a JSON object `{"p1": "<translation>", "p2": "<translation>"}` with `write_file` to `/tmp/.scratch/document-translator/t1.json`. For more than about 80 units, write `t1.json`, `t2.json` and so on, about 60 units each. Every id must appear. Keep a unit that is only a number, code or name exactly as it is. Translate one unit to one unit: never merge or split units, and keep tabs and line breaks in the text.
5. Apply: `python3 SKILL_DIR/scripts/translate_units.py apply <uploaded file> /tmp/.scratch/document-translator/<name>-<target language code>.docx /tmp/.scratch/document-translator/units.json <MODE> <ORDER> <RTL> /tmp/.scratch/document-translator/t1.json [t2.json ...]`
   - MODE is `replace` or `bilingual`.
   - ORDER is `source-first` or `translation-first` (it only matters for bilingual).
   - RTL is `rtl` when the target language is Arabic, Hebrew, Persian or Urdu, otherwise `ltr`.
   - `<name>` is the original file name without its extension, so `lease.docx` into Spanish becomes `lease-es.docx`.
6. Read the printed report. If it lists untranslated ids or numbers missing from the translation, fix those units in a new JSON file and run `apply` again with all the translation files. A number listed as missing because the target language writes digits differently (for example Arabic-Indic digits) is fine: keep the digits as in the source unless the user asked otherwise.
7. Publish the .docx with `publish_artifact` (`kind: "document"`).

### Uploaded .xlsx

Same as the .docx steps, with these differences. The script extracts only text cells that are not formulas and never touches numbers, formulas or sheet names. Ids look like `Sheet1!B4`. In bilingual mode each cell holds both texts on two lines. Run the same `extract` and `apply` commands with a `.xlsx` output name (RTL is ignored). Publish with `publish_artifact` (`kind: "document"`). Say in one line that charts and images may not survive a rewrite; check with the user's file before claiming they were kept.

### Uploaded .pdf

A PDF cannot be translated in place. Say so in one line: "The layout is rebuilt, not identical to the original."

1. Run `extract` on the PDF the same way (ids like `pg2-b3`, blocks in reading order). If it reports 0 units, the PDF is scanned: load the built-in `file-converter` skill with `skill_view`, follow its OCR section to get the text, and translate that.
2. Translate the units into a JSON file as above, then run `check /tmp/.scratch/document-translator/units.json t1.json` for the numbers report and fix what it lists.
3. Build the new document: load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build a .docx with the same headings, lists and tables, one page of text per page of the source where reasonable. If the user asked for a PDF, load the built-in `pdf` skill instead and build the PDF with it. In bilingual mode, use a two-column table (source left, translation right) for each paragraph, in the order the user wants. Do not add your own `publish_artifact` call for a file those built-ins deliver.

## Step 4: Check before replying

Run these checks in code, not by eye:

- The same number of headings, paragraphs, list items and table cells as the source (the script does this for files; for pasted text count with `execute_code`).
- Every number in the source appears in the translation. For pasted text, use `execute_code` to pull the numbers out of both texts with a regular expression such as `\d+(?:[.,:/-]\d+)*` and compare them; fix any that differ.
- No sentence left in the source language unless it is a name, code or quotation that should stay.

## Step 5: Reply

1. One line: source language to target language, the layout (translation only, or bilingual with the order), and the file name if a file was made.
2. For pasted text: the full translation (or the bilingual text), in the reply. For a file: the published file, plus one line on what was kept (styles, tables, formulas) or rebuilt.
3. For a .docx, one line saying that the paragraph styles, tables, headers and footers were kept, and that bold or italic on single words inside a paragraph may be lost.
4. A short "Left as in the source" line listing names, codes or images of text you did not translate, only if there are any. Text inside images cannot be translated by this method: say so when the file has images of text.
5. "Notes" only when a passage was unclear or a term has no clean equivalent: one line each.
6. Only if asked for a certified translation, the one-line certification note from the rules.

## When the user asks for a change

Change only what was asked (a term, a tone, one paragraph), keep everything else exactly as it was, rebuild the same file type under the same name with the same process, and say in one line what changed. For a changed term, apply it to every place it occurs.
