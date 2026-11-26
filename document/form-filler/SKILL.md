---
name: Form Filler
description: >
  Fills in a blank form (fillable PDF, scanned or flat PDF, Word or Excel template) from the details you give, and returns the completed file with a list of what is filled and what is still needed.
  Use it for "fill in this form for me", "complete this application with my details", "fill this PDF", "put my information into this template".
---

# Form Filler

The user has a blank form and details to put in it. A good result is the same form with every field the user gave an answer for filled in exactly as given, every other field left blank and listed, and nothing signed or declared on the user's behalf.

## Hard rules

- **Never invent a value.** Fill only from what the user wrote in the message or in a document they attached (a CV, an earlier form, a pasted list of details). A field with no supplied answer stays blank and is listed under "Still needed". Never guess a date of birth, address, phone number, email, ID, passport, tax, social security or bank number, never fill today's date, and never "infer" a value from a name.
- **Never tick or sign for the user.** Consent, agreement, declaration, terms, certification and "I confirm" boxes stay unticked, signature lines and signature fields stay empty, even if the user says "yes I agree" in the chat: the script blocks them, and you tell the user to do those themselves. If the user asks for a plain option box (for example "Student") to be ticked, that is allowed.
- **Write values exactly as the user gave them** (spelling, accents, capitals, number format). Dates go in the format the form shows (for example a label "DD/MM/YYYY"); if the user's date is in another order or format, rewrite only the order and say so, and if the format is unclear, write it as the user gave it and mention it.
- **Language**: reply in the language the user wrote in. Keep the form's own language and labels.
- Do not open with questions. The first sentence of the reply is the result ("I've filled in the ... form, 6 of 9 fields"), never "I'll load the skill ..." or any other narration of tool use. Decide, state the assumption, deliver. Never install a package; pypdf, PyMuPDF, python-docx and openpyxl are already there.
- The completed form is a draft for the user to check and sign themselves. Nothing is sent or submitted anywhere. For legal, immigration, tax or medical forms add one plain line: this is clerical help, not advice.

## Step 1: Find the blanks

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `fill_form.py` under `~/.computer/skills` with `search_files`. Run `mkdir -p /tmp/.scratch/form-filler`.

The attached file is on disk in the sandbox; its path is in the message or the attachment list. If the user names a file in Google Drive or Dropbox and that app is connected, you may download it; otherwise ask them to attach it and go on with what you have. An old `.doc` or `.xls`: load the built-in `file-converter` skill with `skill_view` and convert it first. A scanned PDF or a photo of a form has no text to place values on: say so, and offer to rebuild the form as a new document with the built-in `pdf` or `docx` skill with the same labels (the user must agree to the rebuild; do not do it unasked).

Run `python3 SKILL_DIR/scripts/fill_form.py fields <file>`. It prints every blank as JSON with an `id`, a `kind` (`text`, `checkbox`, `radio`, `choice`, `blank`, `cell`, `signature`), a `label` (the text beside or above it), and `protected: true` for anything that is a signature, consent or declaration. It handles:

- **PDF with form fields**: each field by name, with its current value and, for drop-downs, its options.
- **Flat PDF** (no fields): lines, underscore runs and empty boxes, with the label to their left or above.
- **.docx**: underscore or dotted blanks in paragraphs (`p<paragraph>.b<n>`), `☐` boxes (`.c<n>`), empty table cells next to a label (`t<table>r<row>c<col>`), content controls.
- **.xlsx**: empty cells to the right of a label or under a heading (`Sheet!B3`).

If `fields` finds nothing (count 0), look at the file with `media_analyze` (render it with `fill_form.py render <file> /tmp/.scratch/form-filler/page.png`), and tell the user what you see; do not guess positions.

## Step 2: Build the field table

Write the table for yourself (and later for the reply): `field | label | value from the user | where it came from (message, attached document) | status`. Match each supplied detail to the field whose label means that thing. If a label is ambiguous (two "Name" fields, "Address" with no hint of home or work), fill the one that clearly fits and list the other as still needed; do not copy a value into both. Use the form's own wording for options: a drop-down only accepts one of its listed options. For a plain text field write only the value the user gave, not extra words from the label (a field "Preferred start term" and the user's "the Autumn term" gets "Autumn").

Choose by what the label says, not by position. Fields with no supplied answer are `still needed`.

## Step 3: Fill

Write `/tmp/.scratch/form-filler/values.json` with `write_file`: `{"values": [{"id": "<id>", "value": "<text>"}, ...]}`. Use `true` or `false` as the value of an option checkbox. Include only fields the user gave answers for. Then run `python3 SKILL_DIR/scripts/fill_form.py fill <file> /tmp/.scratch/form-filler/values.json /tmp/.scratch/form-filler/<meaningful name>-filled.<ext>`.

It prints `log` (`done` or `NOT DONE` with the reason: text too long for the blank, value not in the drop-down, field read-only), `blocked` (signature and consent fields it refused to touch), `readback` (every value re-read from the new file, `ok` true or false), `all_readback_ok` and `left_blank`. Fix a `NOT DONE` once (shorter text, the right option) and run again from the original file. A flat PDF needs a Latin font for the text it writes; characters outside it use a system font if one is found, otherwise the script says so.

## Step 4: Check by eye (PDF)

For a flat PDF, and for a form PDF whose layout matters, run `python3 SKILL_DIR/scripts/fill_form.py render <output pdf> /tmp/.scratch/form-filler/page.png 1` and look at it once with `media_analyze`: is each value on its own blank, not overlapping a label, not cut off? If something is wrong, fix the value and run again once.

## Step 5: Deliver

Publish the completed file with `publish_artifact` (`kind: "document"`; a .xlsx too). Then the reply, in the user's language:

1. One line: the file name, and how many fields were filled out of how many found.
2. **Field table**: `field | value filled` for each filled field, as read back by the script.
3. **Still needed**: each blank left empty, with what is needed to fill it.
4. **For you to do yourself**: every signature, consent or declaration the script left alone, and any other point that needs the user's own eyes (a date format you changed, an ambiguous field).
5. One line: please check every field before you sign or submit it. For a legal, immigration, tax or medical form add: this is clerical help, not advice.

## Final self-check

Every filled value came from the user or an attached document? Nothing signed, ticked as a declaration, or guessed? Every unfilled field listed? Readback all ok? File published?

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, start again from the original form (or the last version, if the user is building on it) with an updated values file, save under the same name with the next version suffix, and say in one line what changed.
