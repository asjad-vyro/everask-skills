---
name: Press Release Writer
description: >
  Writes a journalist-ready press release from the user's news, with five headline options, a news-angle note and a
  distribution tip. Use it for "write a press release", "draft a news release", "announce our funding round", "improve
  this press release", "communiqué de presse", or "how do I tell the press about X". Optional pitch email to journalists.
---

# Press Release Writer

A press release is a news document, not an advertisement. A good result states the news in the first sentence, holds to the facts the user gave, sounds like a wire story, and is ready to paste. If there is no real news, say so and show how to strengthen the angle.

The whole job finishes in one reply, with the full release in the reply itself. Never open with a list of questions and never wait for the user to pick a headline.

## Step 1: Pull out the facts

Read the user's message and any attached or pasted material. List, for yourself, what was given on each of these:

1. The news (what happened, why now)
2. Release type: product launch, funding, partnership, event, crisis, executive hire, award, M&A, earnings, open source milestone
3. Company name, what it does, HQ city
4. Spokesperson name and title, and what they want to say
5. Numbers and proof points
6. Target region or market, language, and audience (trade or general press)
7. Embargo or date, boilerplate, press contact

Do not invent anything that is missing. Where a fact is missing, write a bracketed placeholder in the release, such as `[amount]`, `[Lead investor]`, `[Spokesperson name, title]`, `[date]`, and list every placeholder in the "Assumptions and gaps" part of the reply. Never write a made-up number, customer, investor, quote attribution, date or statistic, and never reuse example values from the reference files.

If the one thing the release cannot exist without is absent (for example the user gave no news at all), use `clarify` once, with a single short question. Otherwise decide, say what you assumed, and deliver. Defaults when not stated: US market and AP style, English, general business and tech press, for immediate release, markdown output.

## Step 2: Find the angle

Write the angle in one sentence and test it against news values: impact, timeliness, prominence, novelty, proximity. If the angle is weak (no number, nothing new, the news is only "we exist" or "we are excited"), say so plainly in the angle note and give two concrete ways to strengthen it, such as a real metric, a named customer or investor, a date, or a quote with an opinion in it. Still write the best release the facts allow, using placeholders for what is missing.

## Step 3: Read the references you need

Read at most two files, chosen in this order of need:

- `references/press-release-types.md`: read it always, for the structure, mandatory elements and timing of the user's release type.
- `references/regional-conventions.md`: read it only when the user names a region other than the US, asks for another language, or for a listed company with regulatory duties. Find the section for that region: dateline format, style guide, send times, regulatory notes.
- `references/journalist-email-pitch.md`: read it only when the user asks for a pitch email (and the release type is clear enough to skip the types file).
- `references/media-formats.md`: read it only when the user names broadcast, wire service, social or trade press, or asks for a press kit.

If you have already read two files and need a third, rely on what you know and keep it brief.

## Step 4: Write five headline options

Give five headlines, each labelled with its hook type, mixing types: data-driven, bold claim, contrast, human interest, urgency, problem-solution. Sentence case, under 100 characters, core news first, no banned words (list below). Only use data the user gave. Pick the strongest one yourself and say it is the one used in the draft. Do not wait for approval.

## Step 5: Write the release

Follow the inverted pyramid: the most important facts first, so any paragraph can be cut from the bottom without breaking the story.

```
FOR IMMEDIATE RELEASE   (or: EMBARGOED UNTIL <date, time, timezone>)

<Headline, sentence case>
<Optional subheadline, about 20 words>

<CITY>, <State or country> (<date>) -- <Lead: who, what, when, where, why, how, in 25 to 35 words>

<Body paragraph 1: expands on the lead, with the main number the user gave>

"<Quote that adds opinion or context>," said <Full name>, <title> of <Company>.

<Body paragraph 2: context, market need, how it works, or use of funds>

"<Optional second quote from a customer, partner or investor the user named>," said <Full name>, <title>.

<Availability, next steps, link or call to action, only if the user gave them>

About <Company>
<Boilerplate, under 100 words, factual, built only from what the user gave>

Media contact: <name> | <email> | <phone>   (use placeholders if not given)
###
```

Use the release-type template in `references/press-release-types.md` for the body order and mandatory elements. Put every mandatory element of the type (for a funding release: amount, round, lead investor and use of funds all in the first paragraph) in the draft or as a visible placeholder.

Writing rules:

- Third person throughout. No "we", "our" or "you" outside quotes.
- Active voice. Attribution verb is always "said", full name and title on first reference, last name after.
- Quotes must add opinion, vision or context the journalist cannot write alone. A quote that repeats the lead is wasted. Quotes are drafts for the spokesperson to approve: if the user gave no quote content, write a plain draft quote from the facts given and mark it "[draft quote, needs spokesperson approval]".
- Data beats adjectives: every claim rests on a number, a source or a quote. No unsupported superlatives.
- Banned words and phrases: thrilled, excited to announce, proud to, innovative, cutting-edge, world-class, best-in-class, synergy, leverage, disruptive, game-changing, revolutionary, paradigm shift, next-generation, "leading" (unless a market-share figure backs it), "competitive pricing" (give the price or a placeholder).
- Plain language: a general-assignment reporter must follow paragraph one. Trade jargon only for trade press, after the news is stated.
- One story per release. Total length 300 to 500 words (trade or technical announcements may reach 700).
- Use the date format and style of the target region (`references/regional-conventions.md`). If the date is not given, use `[date]`.
- Do not claim endorsements, legal approvals or regulatory filings the user did not state. For listed companies, M&A and earnings, add a line telling the user to have legal and investor-relations review the release and its regulatory legends before distribution.

## Step 6: Check it with code

Run `execute_code` (Python) on the final text to count, and copy the results; never count by eye:

1. The words in the lead sentence (after the dateline dash). It must be 25 to 35. If not, rewrite the lead and count again.
2. The total word count of the release.
3. The words in the boilerplate (under 100).
4. A search for every banned word and phrase above, in the whole release including quotes. Fix any hit.

Then confirm by reading: third person, "said" only, one concrete number or an explicit placeholder for it, end mark present, no invented facts.

## Step 7: Reply in this order

Everything below goes in the reply itself, in full:

1. **Headline options**: the five, with hook labels, and which one is used.
2. **The press release**, complete, in the target language.
3. **Angle note**: the one-sentence angle, and whether it is strong or weak with the reason.
4. **Checks**: lead word count, total word count, boilerplate word count, banned words found (none), from the code run.
5. **Assumptions and gaps**: each placeholder the user must fill, and each assumption you made (region, style, date, etc.).
6. **Distribution tip**: best day and time window for the target market (from the regional file, or Tuesday to Thursday mid-morning local time when none applies), whether an embargo suits, and a type-specific tip such as coordinating with investors for funding news.
7. If the user asked for a pitch email, social teaser or press kit: add it after the release, following the file for it. Otherwise end with one line offering a journalist pitch email and social posts. Do not write them unrequested.

## Improving an existing draft

If the user pastes a draft to improve, run Step 6 on it first, list what fails (lead length, banned words, buried news, "we" voice, missing mandatory elements, unsupported claims), then deliver the rewritten release in the same reply, followed by a short list of the changes. Keep every fact from the draft and invent none.

## Optional extras

- Word document: only if the user asks for a file. Load the built-in `docx` skill with `skill_view` and follow it, then publish with `publish_artifact`. Otherwise deliver markdown.
- Humanizing: do not run a humanizer by default. If the user asks for a more natural tone, load the built-in `humanizer` skill and tell it to leave the headline and the lead untouched.
- Bilingual: write each version for its market, not word for word, following the localization notes in `references/regional-conventions.md`.
