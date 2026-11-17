---
name: Newsletter Issue Writer (Substack)
description: >
  Writes a complete newsletter issue or web essay from the user's notes, in their voice, with subject line options, preview text, a Notes teaser and optional social posts.
  Use it for "turn these notes into this week's newsletter", "write a Substack post", "ghostwrite a newsletter issue", "write in my voice", "draft Substack Notes".
---

# Newsletter Issue Writer (Substack)

A good result is a finished, publishable issue in the right voice: every fact the user gave is kept, nothing is invented, the subject line fits on a phone, and the writer has what they need to publish (preview text, a Notes teaser, image ideas). It all goes in the reply, in full, in one turn. Never stop to ask for approval of titles or hooks: pick the best one and show the alternatives.

## Step 1: Read the request and decide the mode

Work from the message, pasted notes, transcripts, attached files and pasted sample posts. Decide, and state in one line at the top of the reply, these four things:

- **Format**: "newsletter", "issue" or "email" means a newsletter issue (email-first). "Essay", "article", "evergreen" or "post" means a web post (web-first). If unclear, write a newsletter issue.
- **Voice**: own voice (the user publishes under their name) or ghostwriting (writing for a named person or client).
- **Audience, goal and length**: take them from the message. If missing, assume a general reader of the topic, a goal of keeping readers engaged and inviting replies, and a standard length of 700 to 1,200 words (about 500 to 800 for a short note, 1,500 or more for a deep dive). Say each assumption in a few words.
- **Series context**: only if the user mentioned earlier issues.

Use `clarify` only if there is no topic and no notes at all. Never open with a list of questions.

## Step 2: Fix the facts

Before you write, list for yourself every fact, number, name, date, quote and link the user gave. The draft must carry all of them, exactly as given. Rules:

- Use only facts from the user's material, from a source the user pasted, or from a web search you ran and can link. Anything else is an assumption: mark it or leave it out.
- Never invent statistics, customers, quotes, anecdotes, tenure, dates or results. Where a story would be stronger with a detail the user did not give, write the point without it, or leave a bracketed gap such as `[add your own example here]`.
- If the user gave a link to a post or a Substack to learn the voice from, read it with `web_extract` (at most two pages).
- If the topic is time-sensitive and the user gave no source material, run at most two `web_search` calls and cite what you used with links.

## Step 3: Get the voice

Read `references/voice.md` when the user supplied writing samples, a transcript, or asked for ghostwriting or "write like me". Follow its short process to build a voice guide of 6 to 10 markers, each backed by a quoted fragment from the samples.

If no samples were given, use a plain, warm, direct default voice (short sentences, first person, no hype) and say "No samples given, so I used a default voice" in the assumptions line. When ghostwriting without samples, never claim the draft matches the person's voice.

Check every paragraph against the guide as you write. Things the samples never do (emoji, exclamation marks, rhetorical questions, jargon) stay out of the draft.

## Step 4: Plan the title, hook and formatting

Read `references/formats.md` before you write the body. It has the length, paragraph and subheading rules for email versus web, the subject line and preview text limits, SEO fields for web posts, and Substack blocks worth suggesting. Apply its rules, in particular:

- Newsletter issue: subject line of 60 characters or fewer, with the interesting part in the first 40 (count the characters in `execute_code`); preview text of about 90 characters that adds to the subject line and does not repeat it; paragraphs of 2 to 3 sentences.
- Web post: title under 60 characters, SEO description of 150 to 160 characters (count it), a URL slug of 3 to 6 words, paragraphs of 3 to 4 sentences.
- Write three subject line or title options and pick one. Specific and honest beats clever. No fake urgency, no invented stakes.

## Step 5: Write the piece

Structure: hook (2 to 3 sentences, the strongest thing the notes offer), context (why now, in 1 to 2 paragraphs), body with a subheading every 200 to 400 words and 1 to 2 bold key phrases per section, a one-sentence takeaway, and a closing line that asks for one specific action. A question the reader can answer by replying is the strongest close.

- Keep the user's own claims, opinions and examples. Rewrite for rhythm and clarity; do not add new claims.
- Keep any code, numbers and names exactly as given. Long code goes to a link, not into an email.
- No filler openers ("In today's fast-paced world"), no hollow transitions, no inflated adjectives, no stacked hedges. Prefer concrete nouns and verbs.
- If the user asked for a length, hit it within about 10 percent. Count words in `execute_code` when a length was specified.
- If the user has a paid tier, say where a paywall divider would sit, and keep the best work free. Read `references/growth.md` only if the user asks about growth, paid tiers, Notes strategy or recommendations.

## Step 6: Check before you send the reply

Run these checks yourself, using `execute_code` for every count:

1. Every fact from Step 2 appears in the draft, unchanged.
2. Subject line or title length, preview text or SEO description length, and word count are within the limits above.
3. Nothing in the draft is stated as fact that the user did not give.
4. The draft sounds like the voice guide, not like generic marketing copy.
5. The closing action is specific and the subject line does not promise more than the issue delivers.

Fix anything that fails, then write the reply.

## Reply shape

Use these headings and fill every one. Angle brackets mark where the user's content goes.

**Assumptions**: one to three lines (format, audience, voice source, length).

**Subject line** (newsletter) or **Title** (web post): `<chosen>` (`<n>` characters), then two alternatives.

**Preview text** (newsletter) or **Subtitle, SEO description and URL slug** (web post).

**The issue**: the full piece in markdown, ready to paste into the Substack editor.

**Image ideas**: one to three, each with placement, purpose and a one-line description. Use `image_generate` only if the user asks for the images themselves.

**Notes teaser**: two to three sentences that stand alone with real value. Not "new issue is out".

**Social posts** (only if the user asked): a LinkedIn post of about 1,200 to 1,500 characters that gives a third of the value up front and ends on a reason to read the full issue, and a short X post or 3-tweet thread. Lead with the insight, never "I just published". No hashtags unless asked.

**Voice guide used** (only if ghostwriting or samples were given): the markers, each with its quoted evidence.

**Fact check**: one line listing the user's facts you preserved, and any gaps you left in brackets for the user to fill.

## Adapting existing content

When the user pastes a blog post, talk or thread to turn into an issue: pick the format (evergreen reference material suits a web post, timely commentary suits an issue), cut a newsletter version by a third to a half, front-load the point in the first two sentences, add the personal layer only from what the user told you, and end with a request. Do not copy paragraphs unchanged.

## Hard rules

- Everything goes in the reply. Never say "I've prepared" without the full piece below it.
- Nothing is published or sent. The result is a draft for the user to paste and send.
- No invented numbers, quotes, sources, anecdotes or benchmarks. Substack's features change, so for any current platform limit or price the user relies on, say it should be checked in Substack's help pages.
