---
name: Certificate Maker
description: >
  Makes print-ready certificates, one landscape page per person, as a single PDF from one name or a whole list: participation, completion, award or attendance.
  Use it for "make a certificate", "certificates for my class list", "certificate of participation", "attendance certificate", "award certificate for each winner".
---

# Certificate Maker

A good certificate has the recipient's name spelled exactly right, a clear title, what it is for, who issues it, a date and a signature line, on a clean landscape page ready to print. One page per person, all in one PDF.

**Hard rules**
- Write the certificate in the language the user wrote in, unless they ask for another. Spell every name exactly as given, including accents and non-Latin scripts. Never correct, shorten, reorder or transliterate a name.
- Never invent an organisation, date, hours, course name, signatory, serial number or signature. Anything the user did not give is left as a visible blank line on the page (the builder does this for the date, the course line and the signatory), and the reply lists what is blank.
- No seals, accreditation marks, stamps or logos of real bodies, and no fake signatures.
- Do not make a certificate that imitates a real institution's credential for someone to pass off as genuine (a university degree or diploma, a professional licence, a government or exam-board certificate). Say so in one sentence and offer a clearly generic certificate instead (a "certificate of completion" from the organisation the user names, with no official wording). Ordinary participation, completion, attendance and award certificates from a club, school, company or event are fine.

## Step 1: Collect the names and fields

- Names: from the message, a pasted list, or an uploaded .xlsx or .csv (read it with pandas in `execute_code`, keep everything as text, use the column that holds names; if first and last names are separate columns, join them with a space in the order given). Keep the user's order. Count them.
- Fields, only if given: `title` (for example the kind of certificate), `subject` (course, event or achievement), `organisation`, `date`, `extra` (for example hours, grade, place won), `signatory_name`, `signatory_role`.
- Per-person values (a different award or grade for each person) go on that person's entry.
- Page size: `a4` (default), `letter` for the US or Canada or if asked. Colour theme: navy, burgundy, green, gold, teal, purple or charcoal; the user's colour if named.
- If the user gave no names at all, ask one short question with `clarify`; otherwise do not ask anything.

## Step 2: Write the data file

Use `execute_code` (or `write_file`) to save `/tmp/.scratch/certificates/data.json`. When names came from a file, build the JSON in Python so no name is retyped.

```json
{
  "filename": "<short-name-with-hyphens>", "lang": "<ISO code>", "size": "a4", "theme": "navy",
  "title": "<Certificate of Participation, in the certificate language>",
  "intro": "<This certificate is presented to, in that language>",
  "reason": "<for completing / for participating in / for outstanding achievement in, in that language>",
  "subject": "<course or event as given, or empty>",
  "organisation": "<as given, or empty>",
  "date": "<as given, or empty>", "date_label": "<Date, in that language>",
  "extra": "<for example Duration: 12 hours, written from what was given, or empty>",
  "signatory_name": "<as given or empty>", "signatory_role": "<as given or empty>",
  "signature_label": "<Signature, in that language>",
  "recipients": ["<name 1>", {"name": "<name 2>", "extra": "<this person's own line>"}]
}
```

- The fixed words (`title`, `intro`, `reason`, labels) are yours to write in the certificate language; keep them short and plain. The `subject`, `organisation`, `date`, `extra` and signatory values are copied from the user, never made up. For hours, write the label in the certificate language and the number exactly as given.
- `date_label` and `signature_label` are the captions under the lines. `signature_label` is shown only when no signatory name or role is given.
- A value left empty shows as a blank line (date, signatory, subject) or is omitted (organisation, extra).

## Step 3: Build

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. If `skill_view` gives no path, find `build.py` under `~/.computer/skills` with `search_files`. Run, with the full path:

`python3 SKILL_DIR/scripts/build.py /tmp/.scratch/certificates/data.json /tmp/.scratch/certificates/out`

It fills `templates/certificate.html` and renders the PDF with headless Chrome. It finds Chrome itself (including the copy in `~/.cache/puppeteer`): do not install anything. Check the printed JSON:
- `pages_match` is true: `pdf_pages` equals `recipients` equals the number of names from Step 1.
- `missing_names` is `[]`.
- If it fails or the JSON has an `error` about Chrome, publish the `.html` with `publish_artifact` (`kind: "html_preview"`) and say the PDF could not be made.

## Step 4: Deliver

Publish the PDF with `publish_artifact` (`kind: "document"`) under a meaningful name.

The reply has: one line saying what you built (the number of certificates, size, language); the list of names exactly as printed (so the user can proof them); a line "Left blank" naming each field that is blank on the page (or "nothing blank"); and any wording you wrote (title and intro) so the user can change it. Do not paste the HTML.

## When the user asks for a change

Change only what was asked (one field for everyone, one name, the colour, the size, one person's line) by editing the data file and rebuilding all pages. Keep everything else exactly as it was, rebuild the same file type under the same name, and say in one line what changed. When one field changes for everyone (for example the hours), every page is rebuilt with only that field different.
