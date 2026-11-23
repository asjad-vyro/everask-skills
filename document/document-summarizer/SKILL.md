---
name: Document Summarizer
description: >
  Summarizes a long document, report, article, contract or chapter into the points that matter, each with where it came from, at the length you ask for.
  Use it for "summarize this document", "give me the key points of this report", "TL;DR this article", "summarize this PDF in 5 bullets", "what does this contract say". Works on uploads, pasted text and web links.
---

# Document Summarizer

A good summary is faithful: a busy reader could act on it without opening the original, and nothing in it is missing from the source or changed in meaning. Every number is copied exactly, every point says where in the document it comes from, and the author's claims are shown as claims.

## Hard rules

- **Language**: write the summary in the language the user wrote their request in, even when the document is in another language, unless the user asks for a different one. Keep proper names, titles, figures and technical terms exactly as in the source (add a translation in brackets only for a term the reader would not know).
- **Faithful**: use only what the document says. Add no outside facts, no background, no opinion, no recommendation of your own. Do not strengthen a statement: do not add "only", "all", "never", "must" or "always" where the source says "may", "can" or nothing. If the document does not say something the user would expect, say that in "Not in the document", never fill it in.
- **Numbers, dates, names, amounts and deadlines are copied exactly as written**, with their units and currency. Never round, convert or recompute them in a way that changes them. If you add up or compare figures, do it in `execute_code` and show it as your calculation, labelled as such.
- **Claims stay claims**: write "the report says", "the author argues", "the company states" for statements the document does not prove. Do not turn a claim into a fact.
- **Do not open with questions.** If the user gave no length, use the default in Step 2 and say so.
- The summary is the deliverable and goes in the reply itself, in full. Do not make a file unless the user asks for one.

## Step 1: Get the text

1. **Pasted text**: use it as given.
2. **Attached file** (.pdf, .docx, .pptx, .xlsx, .txt): the file reader has already given you its text. If the text is empty or only a few lines for a many-page file, the file is probably scanned: say so in one line and ask the user to paste the text; do not guess.
3. **Web link**: call `web_extract` on the URL once. If it returns nothing usable, say so in one line and ask for the text pasted. Do not summarise from memory or from a search snippet.
4. **Several documents** (up to about five): summarize each one in its own short block (Step 3 shape, key points trimmed to 3 to 5 each), then add a "Across the documents" section with what they agree on and where they differ, each point naming the document it came from.
5. **Very long text** (more than about 8,000 words): count the words with `execute_code`, and split the text at its headings or page markers into parts. Read each part and write down for each: the 2 to 4 main points, every figure and date, and the part's name or page range. Then build the summary from those notes. Do not skim only the start and end.

If there is no document at all and no link, ask one short question with `clarify` for the text or file. That is the only case where you ask.

## Step 2: Decide the length

- The user's request wins: "one paragraph", "5 bullets", "one page", "100 words", "executive summary".
- No length given: about 10 percent of the source, at least 120 and at most 400 words in the summary body (the bottom line, key points and not-in-the-document section; the figures table and actions list come on top of that). Say which length you used in the first line.
- Short source (under about 300 words): at most 3 sentences plus the figures, or the length asked for.

When the user asks for a fixed shape ("5 bullets", "one paragraph", "3 sentences"), the reply is exactly that shape and nothing else: for "5 bullets" exactly 5 bullets, with no separate bottom line, no figures table and no other sections. Put the most important figures, the dates and the author's claims (as claims) inside the bullets, and a location only where the source has real sections or pages. After it, one short line may say that a fuller version with a figures table is available.

## Step 3: Write the summary in this shape

Use the user's language for every label. Keep the section order; leave out a section only when the document has nothing for it (never write an empty section).

```
**Summary of: <document title or "the pasted text">** (<document type, pages or word count if known> | <length used>)

**Bottom line**
<one sentence: what the document is and the single most important thing it says>

**Key points**
1. <point in one or two sentences> (<where: page, section number or heading>)
2. ...
(5 to 9 points, in the order of importance, not necessarily of appearance)

**Key figures and dates**
| Item | Value, exactly as written | Where |
|---|---|---|
| <what it measures> | <the figure, date or deadline: digits, dates and names as in the source, the words around them in the summary's language> | <page or section> |

**Decisions, actions and deadlines**
- <who> must <do what> by <deadline as written> (<where>)

**Not in the document**
- <a question a reader would expect it to answer that it leaves open, or a figure it does not give>
```

Rules for the sections:
- **Where**: use the page number if the text shows page markers; otherwise the section number or heading text; for a web page, the heading. If the source has no structure at all (plain pasted paragraph), write "paragraph <n>". Never invent a page number.
- **Key figures and dates**: list every figure, amount, percentage, date and deadline that matters for the points, up to 12 rows. Copy the digits, dates and names character for character from the source; when the summary is in another language than the source, write the unit and the words around the figure in the summary's language. If the document has none, leave the table out.
- **Decisions, actions and deadlines**: only for documents that have them (policies, contracts, minutes, plans). A deadline appears as the document gives it ("within 30 days of notice"), not turned into a calendar date unless the document gives one.
- **Not in the document**: one to three bullets of real gaps (for example, the document states a goal but gives no budget). Do not pad it. If you find none, leave the section out.
- **Claims**: when a key point is the author's claim or forecast, begin it with "The author claims" or the language's equivalent. When the document cites a source for a claim, say "(source cited: <as named in the document>)".

## Step 4: Check before replying

Always run this check in `execute_code`, also for a short text: take every number and date in your summary and confirm it appears in the source text (search for the exact string). Fix any that does not. Confirm that every key point has a location. Confirm the summary is inside the length you promised.

## Step 5: Reply

The reply is Step 3's summary and nothing before it except, if needed, one line saying what you assumed (the default length, or that the text was partly unreadable). After it, add at most one line offering a shorter or longer version. Do not describe your method.

## When the user asks for a change

Change only what was asked (shorter, a different language, more detail on one part, a different shape), keep every other point and figure exactly as it was, and say in one line what changed. If the user asks for the summary as a file, build it with the built-in `docx` skill (or `pdf` if they ask for a PDF), loading it with `skill_view` and following it, including its delivery step, with the same content.
