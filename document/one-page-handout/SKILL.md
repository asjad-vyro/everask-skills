---
name: One-Page Handout Maker
description: >
  Turns a long document, notes or a topic into a single printable page: the few points that matter, readable in a minute, delivered as a one-page PDF or Word file.
  Use it for "make a one-pager", "one-page handout", "cheat sheet", "fact sheet", "leave-behind", "summarise this on one page".
---

# One-Page Handout Maker

A good handout has one message the reader remembers, three to five supporting points, and fits on exactly one page at a size people can read. The work is cutting: keep the point, drop the rest.

## Hard rules

- **Language**: write the handout, and everything around it, in the language the user wrote in, unless they ask for another. Keep their names, figures, dates and terms exactly as given. Do not use date, currency or paper conventions that only fit one country: use A4 unless the user names US Letter or lives where Letter is standard.
- **Never invent facts.** Every figure, name, date, quote and claim comes from the source the user gave. When the user gave only a topic with no source, use only general, well-established knowledge you are sure of, include no statistics, and add a line in the reply that the content is general and should be checked. For facts that change (prices, laws, versions), do at most two `web_search` calls and cite what you found; otherwise leave them out.
- **Never drop a key number silently.** If a figure from the source has to be cut for space, say so in the reply.
- **No questions.** Decide, state assumptions in one line, deliver in this turn.
- **Do not shrink the font to fit.** Body text stays at 10 pt or larger. If the page overflows, cut words.
- Contacts, links and calls to action appear only if the user gave them; otherwise leave the block out or use a placeholder such as `<contact details>`.

## Step 1: Fix the message

From the user's request and source, write down (do not ask):

1. **Audience and use**: who reads it and where (meeting handout, customer leave-behind, class cheat sheet, event flyer back). If not stated, assume a general reader and say so.
2. **The one-sentence message**: what the reader must take away.
3. **Kind**: narrative one-pager (summary, project, proposal) or reference sheet (cheat sheet, shortcuts, steps). A reference sheet is organised in groups of items instead of prose.
4. **Scope**: if the content depends on a product, version or platform the user did not name (which app, Windows or Mac, which edition), pick the most likely one, put it in the title or summary line, and say so in the reply.

## Step 2: Pick and cut

1. List every candidate point in the source.
2. Keep at most **five** that directly support the message. Merge related points; drop background, history, caveats that do not change a decision, and repeated ideas.
3. Choose **at most one** table or figure (a small comparison table, a short numbered process, a key-numbers strip). Use it only if it says something a sentence cannot.
4. Mark which source figures you will keep. Keep the user's key numbers unchanged.

## Step 3: Draft to the word budget

Layout, top to bottom:

1. **Title**: says what the page is about (not a vague label).
2. **One-line summary**: the message from Step 1, one sentence.
3. **Three to five blocks**: a short bold heading plus one to three lines or two to four bullets each. A reference sheet uses grouped lists or a compact table instead.
4. **At most one table or figure.**
5. **Footer line**: contact, source or next step, only from what the user gave.

Word budget: about **350 words** in total for a text page on A4 or Letter at 10 to 11 pt, about 250 if a table is included. A dense reference sheet may reach about 400 words in two columns. Use `execute_code` to count the words of the draft (split on whitespace) and print the number. If it is over budget, cut the weakest block or shorten sentences, then count again. Do not count in your head. For a language written without spaces between words (Chinese, Japanese, Thai), a word count does not work: skip it and rely on the page check in Step 5.

Writing rules: lead each block with the takeaway, one idea per bullet, no filler openings, no adjectives you cannot back with the source.

## Step 4: Build the file

The handout is meant to be printed or handed out, so build a file in this turn:

- **PDF** (default): load the built-in `pdf` skill with `skill_view` and follow it, including its delivery step, to build the PDF directly. Never build a .docx and convert it.
- **Word**: when the user asks for Word or wants to edit it, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step.
- Page setup: margins about 15 to 20 mm, one or two columns, clear heading hierarchy, plenty of white space, one accent colour at most with dark text on light background.
- For right-to-left languages such as Arabic or Hebrew, set the text direction right-to-left; prefer the .docx if the PDF text renders broken.

Do not call `publish_artifact` for a file the built-in skill delivers. Do the page check in Step 5 on the scratch copy before the built-in's last step (copying the file to its output folder), so a two-page version is never delivered.

## Step 5: Check it is one page

Before the file is delivered, confirm in code that it has exactly one page, and print the count:

- **PDF**: count the pages of the built PDF with pypdf, as in the `pdf` skill's validation step (`len(PdfReader(path).pages)`).
- **.docx**: convert a copy to PDF with the `docx` skill's own converter (`scripts/office/soffice.py --headless --convert-to pdf`, in the docx skill's folder), writing it inside `/tmp/.scratch/docx/` so the copy is never delivered, then count its pages with pypdf. LibreOffice lays out text almost, but not exactly, like Word: if the page is completely full, cut a few more lines so it stays one page in Word too.

If it is two pages, cut words and rebuild; do not reduce font size below 10 pt or margins below about 12 mm. Repeat until one page. Do not deliver two pages.

## Step 6: Reply shape

In the user's language:

1. One line: the format chosen, the audience assumed, and the page count confirmed.
2. The full handout text, so it can be read in the reply (title, summary line, blocks, table).
3. **What was cut**: one to three short lines naming what you left out, and any key figure dropped.
4. Only if the content was written from a topic with no source: one line saying it is general and should be checked.

## Optional sources

If the user points to a Google Doc, Drive file or Notion page and that app is connected, read it from there and, if asked, save the handout back. Otherwise work from what the user pasted or attached.
