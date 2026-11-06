---
name: Video Breakdown and Remix
description: >
  Watches a short video the user likes (a Reel, Short, TikTok or ad, uploaded
  or linked) and breaks down why it works: the hook, the structure and pacing,
  every shot and camera move, the on-screen text, and the voice, music and
  sound. Then proposes 2 to 3 original versions for the user's own topic or
  product, each with a hook, a timed script and a shot list. Keeps the
  techniques, never the content. Use it for "break down this video", "why does
  this reel work", "analyse this TikTok", "make something like this" or "remix
  this ad for our product".
---

# Video Breakdown and Remix

Take a video the user admires apart, shot by shot, so they can see exactly why it works. Then turn what you learned into original videos for their own topic.

The value is in specifics. "Strong hook, good pacing" teaches nothing. "The first frame is the finished cake, the voiceover starts on frame 1 with a question, and there's a cut every 1.5 seconds until 0:06" can be copied as a technique.

If the user wants their own footage edited or cut into clips, this is the wrong skill: this one is for a reference they want to learn from.

## Step 1: Get the video

- **Uploaded**: the message carries the file's URL. Use it as it is.
- **A link** (Instagram, TikTok, YouTube, X): load the built-in `web-intelligence` skill with `skill_view` and download the video with its media tool, at 720p or less. Some sites block downloads, and YouTube often asks to confirm you're not a bot. If the download fails, say so and ask the user to upload the file. Don't analyse a video from its page text or thumbnail.
- **Over about 50 MB**: `media_analyze` takes files up to about 50 MB. Download it into the sandbox and make a smaller copy first, for example:

  ```bash
  ffmpeg -y -i source.mp4 -vf "scale=-2:720" -c:v libx264 -crf 30 -preset veryfast -c:a aac -b:a 96k small.mp4
  ```

  Then pass the sandbox path of the small copy to `media_analyze`.

Several references? Break each one down, then compare them in a short table before proposing anything.

## Step 2: Watch it twice

Call `media_analyze` twice on the same video, with these two questions.

1. **The whole video.** "Describe this video second by second. Give its total length. Quote every spoken line and every piece of on-screen text word for word, with the time each appears. Describe the music (style, tempo, energy, where it changes or drops out) and the sound effects."
2. **The shot list.** "List every shot in order. For each: start and end time; shot size (extreme close-up to extreme wide); camera height and angle; camera movement (static, pan, tilt, dolly, tracking, handheld, zoom); who or what is on screen and what they do; the setting; any text, captions or graphics on screen and where; and how it cuts to the next shot. Say whether each shot looks like real camera footage, a screen recording, AI-generated video, an animated still image or motion graphics."

Report only what the answers support. If something can't be told from the video, write "can't tell" rather than guessing.

## Step 3: Write the breakdown

Use these sections, in this order:

1. **What it is**: one line on what the video is, how long it runs, and who it's for.
2. **The hook (0 to 3 seconds)**: what's seen, said and written in the first 3 seconds, and the kind of hook: a bold claim, a question, the result shown first, a pattern break, a contrarian take or a story opening.
3. **Structure**: the beats with timestamps, such as hook, setup, turn, payoff and call to action.
4. **Pacing**: the shot count and average shot length, and where it speeds up or slows down.
5. **Shot table**:

   | # | Time | Shot and camera | On screen | Text on screen | Sound |
   |---|---|---|---|---|---|

6. **Text and captions**: the style, where they sit, how long each stays up and how many words each has.
7. **Sound**: voice (who speaks, pace, tone), music (style, energy, where it hits) and sound effects.
8. **How it was made**: filmed, screen-recorded, AI-generated, stills or motion graphics, with the evidence you saw.
9. **Why it works**: 3 to 5 reasons, each tied to a moment in the video.

## Step 4: Get what you need for the remix

You need the user's topic or product, the platform and length, and how they'll make it: filming themselves, a voiceover over visuals, or video made with AI. Use whatever the message already says. If the topic or product is missing, ask that one question and stop. Otherwise assume the reference's platform and length and say so.

## Step 5: Propose 2 to 3 original versions

Each version takes a different route from the reference:

- **Same structure, new subject**: the reference's beats and pacing, carrying the user's topic.
- **Same subject, new angle**: a different point of view, such as the customer's, a counter-take, or a myth corrected.
- **Same feel, new visuals**: for example, live action becomes motion graphics, AI video or a screen recording.
- **New platform or length**: a 15-second cut of a 60-second idea, or a vertical take on a wide video.

For each version, give:

- a name and a one-line concept;
- what it keeps from the reference (techniques only) and what's new;
- **the hook**: what's seen, said and written in the first 3 seconds;
- **the script**, timed to length. Spoken words run about 2.5 a second, so 15 seconds is about 35 words, 30 seconds about 75 and 60 seconds about 150;
- **the shot list**: time, shot and camera, action, text on screen and sound;
- **how to make it**: what the user films, and what EverAsk could make for them (AI video clips, motion graphics, a talking avatar, a voiceover);
- music and sound direction, described by mood and tempo, not by naming a copyrighted track to use.

Recommend one version and say why in a sentence.

## Originality rules

- Copy techniques: structure, pacing, the kind of hook, camera language and caption style.
- Never copy content: the script's lines, the characters, the jokes, logos, the creator's name or face, or the exact music.
- Use only the user's facts about their product: prices, results, features and claims. Where a version needs a fact you don't have, write `[ADD: what goes here]`.

## Step 6: Offer the next step

Offer one of these: write AI video prompts for the recommended version's shots, write the full script for filming, or make it with EverAsk's video tools. Generate video only when the user asks for it, since every clip uses credits.

## What not to do

- Don't describe a video you couldn't watch. If `media_analyze` or the download failed, say so.
- Don't invent views, likes, the creator's intent or how well it performed. Report numbers only if they're visible in the video or the user gave them.
- Don't propose a near-copy, even when the user asks for one "exactly like this". Explain the line and offer the closest original version.
- Don't paste the raw tool output. Write the breakdown in your own words.
