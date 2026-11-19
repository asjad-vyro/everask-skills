---
name: Formal Letter Writer
description: >
  Writes a formal letter to an organisation, authority, landlord, school, bank, employer or neighbour, in the user's language and local conventions.
  Use it for "write a formal letter", "complaint letter to my landlord", "letter asking the bank to close my account", "request letter to the school", "appeal letter", "authorisation letter", "give notice in writing". Not for reference, recommendation, resignation or cover letters.
---

# Formal Letter Writer

A good formal letter is short, polite and firm. The reader can see in ten seconds who is writing, what happened, the one thing wanted and by when. This skill covers official and administrative letters (complaint, request, notice, application, authorisation, appeal). It is not for reference, recommendation, resignation or job-application letters.

## Hard rules

- **Language**: write the letter in the language the user wrote in, unless they ask for another. Write everything around the letter (the assumptions line, the fill-in list, any note) in the language the user wrote in. Keep their names, figures, dates and terms exactly as given.
- **Never invent facts.** No reference numbers, account numbers, addresses, dates, amounts, names, laws, clause numbers or deadlines the user did not give. Where a fact is needed and missing, write a bracketed placeholder in the letter's language, such as `[your account number]`, and list every placeholder under the letter.
- **Do not open with questions.** Decide, state your assumptions in one or two lines, and deliver the full letter in this reply.
- **Tone**: firm and polite. No threats, no insults, no sarcasm, and no legal claims or legal action the user did not state themselves. If the user names a law or a next step, include it as they gave it.
- Write only what the user said. Do not add events, promises or consequences.
- **No deception.** Do not backdate a letter, and do not write one that pretends to come from an authority, a company or anyone other than the real sender.
- If the letter adds up amounts (charges, refunds), do the sums in `execute_code` and copy the results; never add them in your head.
- The letter stays a draft. Do not send it anywhere.

## Step 1: Pin down the letter

From the user's message, note (do not ask):

1. Letter type: complaint, request, notice, application, authorisation, appeal, or other.
2. Sender: name, address, contact, and the relationship to the recipient (tenant, customer, parent, employee, neighbour).
3. Recipient: person or department, organisation, address, and how to address them if the name is unknown.
4. What happened, with every date and number the user gave, in time order.
5. The **one action wanted** (repair, refund, close the account, confirm in writing, grant permission) and the **deadline**. Keep a deadline in the form the user gave it ("within <n> days of this letter"); do not turn it into a calendar date. If the request needs a deadline and the user gave none, write `[deadline]` in the letter and, in the fill-in list, tell the user to choose a reasonable period. If several things are wanted, put the main one first and the rest after it as short points.
6. Reference numbers, earlier letters or calls, and attachments the user mentioned.

## Step 2: Check conventions

If the letter is in English and no country is named, skip the file: use "Dear Sir or Madam," with "Yours faithfully," when no name is known, "Dear <title> <surname>," with "Yours sincerely," when it is, and write the month as a word. If the letter is not in English, or a country is named, read `references/conventions.md` once and use the entry for that language: salutation, closing, date format, subject line, enclosures label, formality. If the language is not in the file, use a neutral formal register and say so in your assumptions.

## Step 3: Write the letter in this order

1. Sender block: name, address, phone or email (placeholders for what is missing).
2. Date, with the place before it where the language entry says so. Use the date only if the user gave one; otherwise write the date placeholder in the letter's language (`[date]`, `[fecha]`, `[Datum]`), because the user dates the letter on the day they send it. Follow the language entry's date format.
3. Recipient block: name or title, organisation, address.
4. Subject line: one line naming the matter and any reference number the user gave, with the label the language entry gives (`Re:` in English).
5. Salutation: the form the language entry gives for a known name or an unknown recipient.
6. Body in three moves, one short paragraph each (two to four sentences):
   - **Why I am writing**: the matter in one sentence.
   - **What happened**: the facts and dates, in order, nothing else.
   - **What I ask**: the one action, the deadline, and what the writer will do or expect next only if the user said so. Offer a way to be reached.
7. Closing line and the formal closing phrase for that language.
8. Signature block: space for signature, then the printed name.
9. Enclosures: list only documents the user named, with the language entry's label (`Enclosures:` in English). Omit the line if none.

Keep the letter to one page, roughly 150 to 300 words in the body, unless the facts need more. One idea per sentence; no filler openings ("I hope this finds you well") and no repeated apologies or thanks.

## Step 4: Reply shape

All of it in the language the user wrote in, except the letter itself if they asked for another language.

1. One line: letter type and language chosen, plus any assumption (recipient unknown, deadline left open).
2. The full letter, ready to copy, in a single block.
3. A heading meaning "Fill in before sending" in the user's language, then every placeholder with what goes there.
4. Only if the letter concerns a dispute (complaint, appeal, notice about a breach, a demand): one plain line that this is a draft and not legal advice, and that the user should check any deadline or rule that applies to them.

## Files

The reply itself is the default deliverable. Also make a file when the user asks for a file, Word, PDF or a printable version, or says they will print, post or attach the letter:

- **Word** (the default file when no format is named): load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build a one-page .docx with the same content.
- **PDF** (only when the user asks for PDF): load the built-in `pdf` skill and build the PDF with it directly. Never build a .docx and convert it.
- For an Arabic letter, prefer the .docx and set the text right-to-left; if the user insists on PDF, check the rendered page, and if the Arabic text comes out broken or reversed, say so and deliver the .docx instead.

Still show the full letter text in the reply, and say in one line which format you chose.

## Optional sources

If the user asks you to save the letter to Google Docs, or to put it in a Gmail or Outlook draft, and that app is connected, do it, never sending anything. Otherwise work from what the user gave you and give the text in the reply.
