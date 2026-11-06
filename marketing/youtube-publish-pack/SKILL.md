---
name: YouTube Publish Pack
description: >
  Packages a finished video for YouTube: 5 title options, a description whose
  first lines work in search, chapters with real timestamps, tags, 3 thumbnail
  ideas, a pinned comment and an end-screen line, plus ready-to-post captions
  for Shorts, Reels, TikTok and LinkedIn. Works from the video file, a link,
  its script or a transcript, and uses only what the video actually says. Use
  it for "YouTube title and description", "write chapters for my video",
  "publish pack", "thumbnail text", "metadata for this video" or "captions to
  promote this video".
---

# YouTube Publish Pack

Give the user everything they paste into YouTube Studio, and into their other channels, when a video is ready to go out.

Everything in the pack must be true to the video. A title that promises what the video doesn't deliver loses viewers in the first 30 seconds, and YouTube notices.

## Step 1: Get the content

Use the best source available, in this order:

1. **A transcript or script with timestamps** from the user: use it directly.
2. **The video file**, uploaded or in the sandbox: call `media_analyze` with: "List every topic in order with the time it starts (mm:ss). Quote the main claims, numbers and names exactly. Describe the opening 10 seconds and the ending." `media_analyze` takes files up to about 50 MB. For a bigger file, download it into the sandbox and send just the audio, which is all chapters need:

   ```bash
   ffmpeg -y -i video.mp4 -vn -ac 1 -c:a libmp3lame -b:a 32k audio.mp3
   ```

   An hour of audio at this setting is about 15 MB.
3. **A YouTube link**: load the built-in `web-intelligence` skill with `skill_view` and download the audio only with its media tool. YouTube often blocks downloads with a bot check. If that happens, ask the user to upload the file, or to paste the transcript (in YouTube, under the video, "Show transcript").
4. **A script without timestamps**: write everything except the chapters. Give the chapter titles with `[mm:ss]` placeholders, and say they need times.

Also use what the user tells you about the channel, the audience, the keyword they want to rank for, links to include and the call to action. Ask nothing unless you have no content to work from.

## Step 2: Titles

Write 5 titles, each taking a different angle: how-to, curiosity, the result, a number or list, and a contrarian take.

- Put the main search phrase early.
- Keep each title under 60 characters, so it isn't cut off in search and on phones. YouTube allows 100.
- Make a specific promise the video keeps, such as "I Cut My Grocery Bill in Half in 30 Days". Avoid the vague kind, like "Grocery Tips".
- No all-caps titles, and no "you won't believe".

Pick 2 to test against each other, and say why.

## Step 3: Description

- **The first 2 lines** (about 150 characters) show in search and above "...more". Restate the video's value and include the main phrase naturally.
- **Then 2 to 4 short paragraphs** on what the video covers, written for people, with related phrases worked in naturally.
- **Chapters** (Step 4).
- **Links**: only links the user gave. Anything else they mention becomes `[ADD: link to ...]`.
- **Call to action**: one line, such as subscribe, the next video, or the user's offer.
- **3 hashtags at the end.** YouTube shows the first three next to the title.

## Step 4: Chapters

Chapters only show if the timestamps follow YouTube's rules:

- the first one is `00:00`;
- there are at least 3, in order;
- each chapter is at least 10 seconds long.

Each chapter title is 2 to 6 words saying what that part is about ("Why most budgets fail", not "Part 2"). Use only real timestamps from Step 1, rounded down to the start of the sentence. Never guess a time.

## Step 5: Tags

Give 8 to 15 tags: the main phrase, its variants and common misspellings, the broad topic, and the format (tutorial, review, explained). The whole list must stay under 500 characters. Tags matter much less than the title and the thumbnail, so don't spend effort on them.

## Step 6: Thumbnail ideas

Give 3 ideas. For each:

- **The text**: at most 4 words. It adds to the title rather than repeating it.
- **The image**: one clear focal point, such as a face with a strong expression, the result, or a before and after.
- **The layout and colours**: high contrast, readable at the size of a stamp.

The thumbnail should match the video's first seconds. If the user wants the image made, load the built-in `youtube-thumbnail` skill with `skill_view`. It needs a photo of the presenter or subject, and the thumbnail text.

## Step 7: Pinned comment and end screen

- **Pinned comment**: a question that invites replies, or the main resource link.
- **End-screen line**: one spoken line for the last 20 seconds that points to a specific next video.

## Step 8: Captions for other channels

Write one post for each channel, to promote the video or a short clip of it:

- **YouTube Shorts**: a title under 100 characters, with the search phrase.
- **TikTok**: a hook-first caption, and 3 to 5 hashtags.
- **Instagram Reels**: a first line that stops the scroll, 2 to 3 short lines, and 3 to 5 hashtags.
- **LinkedIn**: the insight first, 3 to 5 short paragraphs, no hashtag wall.

Each caption leads with a different hook. Don't paste the same text everywhere.

## Step 9: Check and deliver

Before replying, check:

- every claim in the titles, description and captions is in the video;
- the character counts are within the limits above;
- the chapters follow YouTube's rules.

Reply with the pack under clear headings, in the order of the steps, so each part is easy to copy. Offer to save it as a document, or to make the thumbnail.

## What not to do

- Don't invent results, numbers, guests, links or timestamps.
- Don't stuff keywords. Write for people first.
- Don't promise anything in a title or thumbnail that the video doesn't deliver.
