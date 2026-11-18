# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## Topic sheet columns ("Video topics: <channel>")

| Column | Content |
|---|---|
| Rank | From `rank_topics.py` |
| Topic | Short name |
| Working title | Under 70 characters, says what the viewer gets |
| Score | 0-10 from `rank_topics.py` |
| Why | The script's `why` line |
| Best related video | Title and link of the channel's own related video, with views |
| Audience questions | Up to 3 question links (Reddit, forums, comments) |
| Search terms | YouTube search terms already bringing views |
| Covered recently | Yes / No |
| Status | Idea → Picked → Scripted → Recorded → Cut → Scheduled (date) → Live |

## Script outline (Google Doc "Script: <working title>")

```
<Working title>
Target length: <minutes, from the channel's best performers>
Voice: <3 bullets from the voice profile: sentence length, person, signature phrases>

HOOK (0:00-0:15, about <median_words_first_15s> words)
- Open the way the user usually opens (<question / bold claim / result first>).
- Say what the viewer will get, matching the title and thumbnail.
[B-ROLL: <shot that shows the payoff>]

SETUP (to ~0:45)
- Why this matters to the viewer, one example from <source>.

SECTIONS (one per chapter, each with a mini payoff before the next starts)
1. <point> — <fact, with its source in the notes>
   [B-ROLL: <shot>]
2. <point> ...
(Put the strongest point where past videos lost viewers: around <drop time from
retention_report.py>.)

OUTRO
- One-line recap, then the user's usual sign-off: "<sign-off from the profile>".

Notes: sources for every fact; questions answered (links).
```

Rules: no claims the sources do not support, no "guaranteed" results, no promises of
views or income.

## Thumbnail prompt (for `image_generate`, 16:9, three variants)

```
YouTube thumbnail, 16:9, in the style of the attached reference thumbnails
(<2-3 words on their style: e.g. "bold yellow text, close-up face, dark background">).
Subject: the creator from the attached frame, <expression that fits the video>,
<object or result that the video really shows>.
Text on image: "<2-4 words, different from the title>" in <their font style>.
High contrast, readable at small size, uncluttered. No logos, no fake UI, nothing
the video does not deliver.
```

Variants: A = face + result, B = before/after or object close-up, C = text-led.

## Title options (3-5, each under 70 characters)

Mix: a direct "how to" promise, a result-first title, a curiosity title that the
video fully answers. Use the search terms from step 1 where they fit naturally. Every
title must be true to the video.

## Description

```
<2 sentences: what the viewer will learn, using the main search term>

<Links the user wants: their resources, gear list, other videos>

Sources
- <source title>: <url>

<Music credit, if the licence asks for one>
```

`publish_kit.py` appends the chapters and checks the 5000-character limit.

## Shorts (2-3 per video)

Pick moments from the cut that:
- make sense on their own (no "as I said earlier"), 20-50 seconds;
- start on a strong line within the first second;
- end on a payoff or a clear question.

For each: start and end time in the cut, the opening caption line, a title under
60 characters, and a line pointing to the full video.

## Instagram reel caption (under 150 words)

```
<hook line from the Short>
<one-line value>
Full video on YouTube: <channel name> (link in bio)
<3-5 hashtags from the niche>
```

## Confirmation summary (step 6 Stop)

```
<channel> · <title>
Video file: <name, length>
Title: <chosen>            Thumbnail: <variant A/B/C>
Description + chapters: <first 2 lines…> (<n> characters)
Tags: <list>
Publish: <local time and zone> = <UTC>, uploaded as private until then
Captions: captions.srt
Altered or synthetic content: <Yes, because … / No>
Shorts: 1) <title> <local time>  2) …  3) …
Reel: <file>, caption below, <you schedule it in Instagram / post now>
Reply "confirm" to upload, or tell me what to change.
```

## Retention report (7 days after going live)

```
<title> · first 7 days

Kept at 30 seconds: <kept_at_30s %> (channel: <%>)
Average watched: <average_kept %> (channel: <%>)
Biggest drops: <time> (<what is on screen there>), …
Rewatched moments: <time> (<what is there>)

What to try next time
- <one change tied to a drop, e.g. "the intro ran 40 s before the first payoff">

Next three topics
1. <topic> — <evidence link>
2. …
3. …
```

Every number comes from `retention_report.py` on YouTube Analytics data. If a number
is not available, write "not available", never an estimate.
