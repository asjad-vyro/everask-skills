---
name: Content Repurposer
description: >
  Turns one blog post, newsletter, podcast or video transcript into a ready-to-post pack of platform-native drafts for LinkedIn, X, Threads, Instagram, TikTok and more.
  Use it for "repurpose this", "turn this blog into posts", "adapt this for LinkedIn and X", "cross-post", "reels from a podcast", "get more from this content".
---

# Content Repurposer

A good result is a set of drafts that each read as if written for that platform first, keep every fact from the source exactly, fit the platform's limits, and come with a posting order. Everything goes in the reply itself, in full, in one turn.

## Step 1: Read the source and decide the scope

1. Work from the source the user pasted or attached. If they gave a URL, read it with `web_extract`. If the source is a video or podcast link with no transcript and none can be read, say so in one line and work from whatever description they gave.
2. Targets: use the platforms the user named. If none were named, choose four to six that fit the source (see the matrix in Step 3) and say which you chose and why in one line.
3. Voice: use any voice notes the user gave. Otherwise match the source's own voice (first person if the author writes in first person) and say "voice taken from the source".
4. Never stop to ask questions. Pick a sensible default, state it under "Assumptions", and deliver.

## Step 2: Extract the insights

Pull 3 to 7 insights that can stand alone without the rest of the source. For each, note internally:
- the claim in one sentence
- its supporting example, number or story beat, copied exactly from the source
- who it helps

Rank them by standalone value: "if someone saw only this post, would it be worth their time?" The top one is the anchor. If one fails the test, merge it with another.

Facts rule: every number, name, date, quote, result and claim in a draft must be in the source. Copy figures exactly, including units and wording such as "about" or "up to". Never round, strengthen or add a statistic, customer, quote or result. If a draft would be better with a number the source lacks, write the draft without it. Do not copy anything from this skill's own wording as if it were a fact.

## Step 3: Match insights to formats

| Source | Best derivatives |
|---|---|
| Blog post | LinkedIn post, X thread, carousel (framework or tips), Threads post, 3 to 5 standalone posts, Pinterest pin, Facebook post |
| Newsletter | thread expanding the main argument, one single post with the line everyone needs, carousel |
| Podcast or video transcript | quote posts (best 3 lines), thread of key moments, carousel, Reel/TikTok/Short scripts from 30 to 90 second highlight moments, YouTube Short |
| Existing social post | lengthen for LinkedIn, shorten for X, expand to a thread, turn into a Reel or TikTok hook |
| Case study or story | narrative thread, LinkedIn long post, before/after carousel, story-time Reel |
| How-to or tutorial | step-by-step carousel, one-step-per-post thread, one tip per post across the week, demo Reel series |
| Webinar or long video | 3 to 7 vertical clips, X thread of takeaways, LinkedIn post, blog recap |

| Insight type | Best format |
|---|---|
| Step-by-step process | carousel or thread |
| Single counterintuitive claim | standalone post or thread opener |
| Story with a lesson | thread or LinkedIn long post |
| Data point | standalone post with context |
| Framework | carousel, one slide per element |
| Memorable line | quote post |

If the user named specific formats and counts ("a LinkedIn post, a thread and 3 captions"), deliver exactly those. Only add extras if the user left the choice open.

## Step 4: Draft each derivative natively

Platform rules (limits are hard: count characters of every X and Bluesky post):

- **X**: each post 280 characters or fewer. Direct first line, no filler. Threads: number each post "1/", "2/" and so on with the total known ("1/6"), hook first, one idea per post, last post is a takeaway or soft call to action. No hashtags, or one at most.
- **LinkedIn**: hook in the first line (it shows before "see more"), then 3 to 5 short paragraphs, conversational but professional, white space between paragraphs, one clear closing line or question. Put any link in "first comment", not the body. 0 to 3 hashtags at the end, never a hashtag wall.
- **Threads**: casual, like a text to a smart friend, short, lowercase is fine, no hashtags or one at most.
- **Bluesky**: 300 characters or fewer, dry and concise, no hashtag culture.
- **Facebook**: conversational, story-led, 40 to 500 characters, 1 to 3 hashtags at most, link allowed in the body, end with a direct question.
- **Instagram**: hook in the first 125 characters, caption 200 to 800 characters, 3 to 10 hashtags at the end, save or share call to action, no clickable links (say "link in bio"), and write alt text for each image.
- **TikTok**: caption under 150 characters, 3 to 5 hashtags, include search keywords, low-polish native voice. If a video is wanted, give a short script: hook line (first 3 seconds), 3 to 5 beats, closing line.
- **Pinterest**: title up to 100 characters, keyword-led; description up to 500 characters, helpful and scannable; natural keywords instead of hashtags; "how to" and "ideas for" framings suit it.
- **YouTube long-form**: title 60 to 70 characters, description with chapter timestamps only if the source gives timings, up to 3 hashtags. **Shorts**: caption under 150 characters including `#shorts`.
- **Carousel**: write slide by slide: slide 1 hook (6 to 10 words), one idea per slide with 20 to 30 words at most, final slide call to action; plus the caption. Say a designer or design tool is needed for the visuals.

Register: the voice stays the same, the register shifts. X is sharp and opinionated, LinkedIn thoughtful and story-forward, Threads casual, Bluesky witty and dry, Facebook warm and question-led, Instagram and TikTok native and caption-supports-visual, Pinterest helpful and search-led.

Avoid these:
- identical text on two platforms
- opening with "I wrote a blog post about..." or "Check out my latest" (write the insight itself; the link goes where the platform allows)
- source formatting carried over where it does not fit, such as blog bullet lists on Threads
- generic takeaways such as "great insights in this post"
- claims the source does not make

## Step 5: Check your work in code

Run one `execute_code` call that holds every X and Bluesky post, every TikTok and Shorts caption and the Instagram hook as strings, and prints each one's character count against its limit. Also list every number from the source and confirm each one that appears in a draft appears exactly as in the source. Fix any post over its limit or any changed figure, then use the corrected text in the reply. Never count characters in your head.

## Step 6: Reply in this shape

The whole deliverable is in the reply. Do not ask for approval and do not publish or schedule anything; every draft stays a draft until the user posts it.

```
**Source:** <one sentence: what it is and its core argument>

**Assumptions:** <platforms chosen, voice, anything not given. "None" if nothing was assumed>

## <Platform>: <format>
<full draft, ready to paste>
*Notes: <character count where a limit applies; link placement; visual needed>*

(repeat for each derivative)

## Leverage ranking
1. <derivative>: <one-line reason>
...

## Suggested schedule
Day 1 <weekday>: <platform>, <derivative> (the anchor)
Day 2 ...
```

Rules for the ranking and schedule: rank only the derivatives you wrote. A fair default order of reach potential is short vertical video, X thread, LinkedIn post, carousel, long-form video, Pinterest pin, Threads post, Facebook post, quote posts; adjust to the user's platforms and whether they make video. Spread the posts over 5 to 7 days, anchor post first, at least a day apart, no posting everything at once. Give weekdays, not dates or clock times, unless the user gave them. If the user asks for a connected scheduler such as Buffer and it is connected, you may offer it; otherwise the written schedule is the deliverable.

## Hard rules

- No invented figures, quotes, customers, results, dates or links. If something is missing write "not given" or mark it as an assumption.
- Keep every statistic exactly as the source states it, and keep it attached to what it measures.
- Respect every character limit above.
- Output text drafts only; do not generate images or video unless the user asks.
- Finish the full pack in one reply; never end with "tell me which to expand".
