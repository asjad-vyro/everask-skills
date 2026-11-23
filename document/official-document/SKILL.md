---
name: Official Document Writer
description: >
  Writes an official memo, circular, notice, decision or decree, or internal regulation in the formal structure an organisation or government office uses, as a ready .docx.
  Use it for "write a memo to all staff", "draft a circular", "Surat Keputusan", "official notice", "internal regulation", "공문", "公文通知", "приказ". Mirrors a previous document if you provide one.
---

# Official Document Writer

A good official document is correct in form before it is elegant: the header fields, the numbering, the operative part and the signature block are where the reader looks, and each one is either filled with what the user gave or shows a visible placeholder. It is for institutional documents (memo, circular, notice, decision, regulation, administrative letter between offices). A personal letter to an organisation is a different job.

## Hard rules

- **Language**: write the document in the language the user wrote in, unless they ask for another. Write the assumptions line and the fill-in list in that language too. Keep the user's names, titles, figures and dates exactly as given.
- **Never invent**: no document numbers, dates, legal bases, regulation or article numbers, names, titles, budgets or deadlines the user did not give. Where the form needs one, write a visible placeholder in the document's language in square brackets, for example `[nomor]`, `[number]`, `[번호]`, `[编号]`, `[дата]`, and list every placeholder under the document.
- **Dates**: use only dates the user gave, in the form they gave them. The document's own date and number stay placeholders unless the user gave them.
- **No forgery**: do not write a document meant to pass as genuine from a real government body, court, university or company the user does not work for, and do not copy an official seal, logo or official's signature. If the request looks like that, decline that part in one line and offer to write the document for the user's own organisation instead.
- **Do not open with questions.** Decide, state the assumptions in one or two lines, deliver the full document in this reply.
- Do not give legal advice. The document is a draft for the user's office to check against its own rules before issuing.

## Step 1: Pin down the document

From the user's message note, without asking:

1. **Kind**: memo, circular, notice, decision or decree, internal regulation, assignment letter, administrative document, or other. If the user gave only a purpose ("tell staff about new hours"), choose memo for an internal message to staff and notice or circular for a message to many readers outside one team; say which you chose.
2. **Issuer**: organisation, the person or office issuing it and their title.
3. **Readers**: who it is addressed to, and any copies or distribution.
4. **Content**: every fact, name, role, amount and date the user gave, and what must be decided or done.
5. **Effective date or deadline**, as the user gave it.
6. **Language and country**, from the request.

## Step 2: Pick the format

1. **A previous document from the user** (attached or pasted, or "same as before", "like last time" with a document given): mirror its structure, numbering style, headings, phrasing and level of formality exactly, and change only the content. This beats every skeleton. If the user says "same as before" but gave nothing to copy, say so in one line and use the skeleton.
2. **Otherwise** read `references/formats.md` once and use the section for the kind and language (a decision in Indonesian, a notice in Korean or Chinese, a Latin American resolution in Spanish, a portaria in Brazilian Portuguese, an order in Russian, a generic memo, circular or regulation for everything else). Follow the order of its parts. It is common practice, not law: do not describe it as legally required.

## Step 3: Write the document

1. Put the header fields first: organisation, document type, number, date, subject or title, and the recipient lines that the format has.
2. Write recitals or basis (for example "considering", "having regard to") only in kinds that have them, and only from facts and bases the user gave. If the format needs a legal basis and none was given, write the placeholder, never a real-sounding one.
3. Write the operative part as numbered points or articles, one action or rule each, in the formal register of the language: "must" for obligations, "may" for permissions, no slang, no contractions, short sentences. Give the effective date as the user gave it. Do not add rules, penalties, amounts or deadlines the user did not state. Also add no sentence that makes a new request, obligation or claim: no closing line asking managers to inform their teams, no "this replaces the current practice", no "all staff must be present" when the user only gave hours. The body is the user's facts, written formally, and nothing more.
4. Put names and titles of people exactly as given, in a list or table when there are several (name, role).
5. Close with the place and date line (placeholders unless given), the signature block (title, space for signature, printed name of the issuer as given), and the distribution or copies list if the format has one and the user named recipients.
6. Official documents are short, so aim for one page, but a second page is fine: do not shrink fonts, margins or spacing to force one page.

## Step 4: Build the file

1. Load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, to build the .docx: A4 page, one plain serif or sans font used throughout, left-aligned numbered points (right-aligned and right-to-left for Arabic, Hebrew, Persian and Urdu), a letterhead line at the top with the organisation name from the user, a table only for lists of names and roles, no decoration, no logo. Name the file in the document's language, for example `memo-new-office-hours.docx`. Do not add your own `publish_artifact` call.
2. If the user asked for plain text, or for a PDF, give the text in the reply, or load the built-in `pdf` skill and build the PDF with it.
3. Say in one line which format you chose.
4. Build the file once with sensible spacing (11 or 12 pt text), render it once to look at it, and fix only a real fault (text cut off, a table broken). Do not iterate on spacing.

## Step 5: Reply

1. One line: the kind of document, the language, and that a .docx is attached (or that it is text only).
2. **Assumptions**: one or two lines (the kind chosen, the skeleton used and that it is common practice, anything the user did not specify).
3. The full document text, ready to copy (so it can be read without opening the file).
4. **To fill in before issuing**: a list of every placeholder and what to put there, plus anything the user's office must check (the legal basis, the numbering system).
5. If the user supplied a previous document: one line saying the structure follows it.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was (the same numbering, wording and layout), rebuild the same file type under the same name, and say in one line what changed. If a change adds a fact (a new date, a new name), use the user's exact words and leave other placeholders as they were.
