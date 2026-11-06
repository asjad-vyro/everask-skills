---
name: AI Video Prompt Writer
description: >
  Turns an idea, a script or a storyboard into shot-by-shot prompts for AI
  video models such as Seedance, Kling, Veo, Sora, Runway, Wan and MiniMax.
  Each prompt names the subject, action, setting, framing and camera move in
  precise film language, keeps characters and products identical from shot to
  shot, and fits the chosen model's preferred format and length. Can also
  generate the clips in EverAsk when asked. Use it for "write a video prompt",
  "prompt for Veo, Sora or Kling", "turn this script into AI video prompts",
  "shot list for an AI video" or "make my video prompt more cinematic".
---

# AI Video Prompt Writer

Write prompts that make AI video models produce the shot the user has in mind, not a generic one.

Video models are good at subjects and settings and weak at motion, framing and camera work. A vague prompt leaves those to chance. So every prompt here spells out all five: who's in the shot, what they do, where, how it's framed, and how the camera moves.

## Step 1: Gather the brief

From the user's message and files, note:

- **The idea or script**, and the total length;
- **the model**, if the user named one;
- **the aspect ratio**: 9:16 for Shorts, Reels and TikTok, 16:9 for YouTube, or 1:1;
- **references**: photos of a product, a person or a style. A shot that starts from a reference image becomes image-to-video;
- **sound**: dialogue, a voiceover added later, or no sound.

Ask a question only if you can't tell what the video shows. Otherwise make the creative calls yourself and state them.

## Step 2: Pick the model

If the user named a model, write for it. If they want EverAsk to make the clips, the `video_generate` tool's description lists the models available now with their lengths and options. Trust it over this list:

- **Dialogue, or sound made with the picture**: Seedance, Kling, Wan or MiniMax.
- **Long single takes**: Seedance, Kling 4.0 or Wan.
- **Fast, cheap drafts**: MiniMax.
- **A photo of a person speaking a script**: HeyGen Avatar 4. The prompt is the script plus a line on delivery.
- **Changing a clip that already exists**: a model that edits video, such as Google Omni Flash or Kling 4.0. Write the change as an instruction: "make it night, keep everything else the same".

## Step 3: Break it into shots

Plan one shot per generation, usually 3 to 10 seconds each. Seedance can take several shots in one prompt, written as `Shot 1 (...)`, `Shot 2 (...)`; other models get one shot per prompt. Give each shot one action and one camera move.

## Step 4: Write each prompt

Cover five parts, in this order:

1. **Subject**: who or what, with 3 to 6 fixed visual details, such as "a woman in her 30s, short grey hair, yellow raincoat".
2. **Action**: what happens, in time order, one beat per sentence.
3. **Scene**: the place, time of day, weather and era.
4. **Framing**: shot size, where the subject sits in the frame, what's in the foreground and background, and the camera height and angle.
5. **Camera**: the movement, lens, focus and speed.

Then add the light, the look (film stock, grade, art style) and, if the model makes sound, the ambience, effects and dialogue.

**Precision rules:**

- **Dolly is not zoom.** A dolly moves the camera; a zoom changes the lens. Pan is not truck: a pan turns the camera, a truck slides it sideways. Bird's-eye means straight down; aerial means high up.
- **"Static" means no movement at all**: no zoom and no focus change.
- **Describe the cause, not the feeling.** Write "low angle, backlit by the setting sun, silhouette", not "epic".
- **Name 3 to 5 colours** instead of "warm tones": "amber, cream, walnut brown".
- **Repeat each character's or product's description word for word in every shot.** Models don't remember "the same woman". Keep these descriptions in a continuity sheet (Step 5).
- **For image-to-video, describe the motion only.** The image already shows what things look like.
- **Keep text out of the picture.** Models misspell words, so add titles and logos in the edit. If a word must appear, keep it to 1 to 3 words in quotes.
- **Keep dialogue short**: about 10 words a line at most, with the speaker named, as in `The chef says: "Taste this."`
- **Write positively.** Say what should be there. Use "no ..." only in a negative prompt field, where the model has one.

## Model notes

These are starting points; the model's own current guide wins.

| Model | Format | Length |
|---|---|---|
| Seedance | The structure above, very literal about camera terms. Multi-shot as `Shot 1 (...)`, `Shot 2 (...)`. Quoted dialogue is lip-synced. Name each reference image, as in "Reference 1: the red sneaker". | 80 to 150 words a shot; up to about 300 for a multi-shot prompt |
| Kling | Subject, motion, scene, camera. Plain and direct. | 40 to 100 words |
| Veo | Rich prose that covers subject, action, scene, camera, lens, light, style, sound and dialogue. | 100 to 250 words |
| Sora | A prose paragraph first, then a camera block (lens, light, 3 to 5 colours), then the action beats. Short dialogue. | 100 to 250 words |
| Runway | Mostly image-to-video: describe the motion, not the look, in positive terms. | Under 60 words |
| Wan | Detailed, specific description. | 80 to 200 words |
| LTX | One paragraph in time order. | Under 80 words |
| MiniMax, Pika, Pixverse, Luma | One clear action, with the camera move stated plainly. | 40 to 100 words |

For any other model, use the five parts at 60 to 150 words.

## Step 5: Deliver

Reply with:

1. **A continuity sheet**: the fixed description of each character, product and location, to be pasted word for word.
2. **A shot table**:

   | Shot | Length | Model | Starts from | Prompt |
   |---|---|---|---|---|

   "Starts from" is text, or the reference image to use.
3. **Each prompt in its own code block**, so it copies cleanly.

Then offer to generate the clips in EverAsk.

## Step 6: Generate, only when asked

- **One clip**: call `video_generate` with the prompt, the model, the length and the aspect ratio. Add `image_url` for image-to-video.
- **Several clips**: first tell the user how many clips you'll make, and that each one uses credits, and get a yes. Then pass `generations_planned` with the total and `split_confirmed: true`.

After each clip, watch it with `media_analyze` and compare it with the prompt. If a shot misses (wrong camera move, a character who changed, garbled text), fix that part of the prompt and say what you changed before running it again.

## What not to do

- Don't use a vague mood word where a concrete instruction would work.
- Don't put more than one camera move or more than one main action in a shot.
- Don't generate anything the user didn't ask for, and don't run a multi-clip job without their yes.
- Don't copy a real film's shots, characters or logos, or a real person's likeness, unless it's the user's own material.
