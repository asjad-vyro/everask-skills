---
name: Talking Avatar Video
description: >
  Turns a photo of a person and a script into a talking-presenter video: a
  spokesperson ad, a product explainer, a training lesson, a personal sales
  message or a social clip. Checks that the photo will animate well, writes
  the script to be spoken, picks a voice, sizes the video for each platform,
  splits long scripts into segments and joins them, and checks the lip sync.
  Can lip-sync to your own recording instead, or create a presenter if you
  have no photo. Use it for "make this photo talk", "talking avatar", "AI
  spokesperson video", "presenter video from my headshot", "HeyGen video" or
  "turn my script into a talking-head video".
---

# Talking Avatar Video

Make a photo of a person speak a script, well enough to publish.

The result depends most on two things the model can't fix: the photo, and a script written to be spoken. A side-on, shadowed photo gives a warped mouth, and a script written for reading gives a stiff, breathless presenter. Get both right before rendering, since every second of avatar video uses credits.

Work in `/tmp/.scratch/avatar/` in the sandbox. Only the finished files go to the user.

## Step 1: Check consent

Only animate:

- the user themself;
- someone who has agreed to it, such as a colleague or a client the user works for;
- a fictional presenter made for the job.

Don't animate a public figure, a child, or anyone the user can't speak for, and don't make anyone say something they wouldn't stand behind. If you can't tell whose photo it is, ask once.

## Step 2: Gather the brief

From the message and files, note:

- **The purpose**: an ad, explainer, training lesson, sales message, announcement or social clip.
- **The script**, or notes to write one from.
- **The platform**, which sets the shape: 9:16 for TikTok, Reels, Shorts and Stories; 16:9 for YouTube, websites, LinkedIn and presentations; 1:1 or 4:5 for feed posts.
- **The voice**: one of the avatar's own voices, or the user's recording.
- **Captions**, on by default for social video, which most people watch muted; and **the background**.

## Step 3: Check the photo

A photo that animates well shows:

- one person, framed from the head and shoulders down to the waist, facing the camera (turned less than about 30 degrees) and looking into the lens;
- a sharp image at least 512 pixels on its short side, with the face large in the frame, in even, soft light;
- nothing over the face or mouth (sunglasses, a mask, a hand or hair), the mouth closed or in a slight smile, and the chin and forehead in frame;
- the same orientation as the video: a portrait photo for 9:16, a landscape one for 16:9.

Look at the photo with `media_analyze` and check each point. If it fails one, say which and ask for another photo. A photo that's only slightly soft or dark can be cleaned up with `image_generate` and Nano Banana Pro Edit ("improve the lighting and sharpness; keep the person's face and features exactly the same"). Show the result and confirm it's still the same person before using it.

**No photo?** Offer to make a fictional presenter with `image_generate` and Nano Banana Pro: "Photorealistic portrait of a fictional presenter, [age, look and clothes that suit the topic], facing the camera and looking into the lens, head and shoulders, soft even studio light, relaxed slight smile with the mouth closed, plain light grey background", in the video's aspect ratio. Never make a likeness of a real person.

## Step 4: Write the script to be spoken

Presenters speak at about 150 words a minute: about 38 words for 15 seconds, 75 for 30 seconds and 150 for a minute. Count the words with `wc -w` in the sandbox rather than estimating.

- Sentences of 10 to 20 words, one idea each, with contractions. Rewrite anything that sounds like a brochure.
- Numbers as words ("twenty percent"), acronyms spelled with hyphens ("C-R-M"), and hard names respelled the way they sound.
- Open on the point; viewers decide in the first 3 seconds.
- One call to action, at the end.
- Only facts the user gave. Mark anything missing as `[ADD: ...]` and ask for it, rather than inventing it.

Shapes that work:

| Video | Length | Shape |
|---|---|---|
| Ad | 15 to 30 seconds | The problem or promise, proof, a call to action |
| Explainer | 60 to 90 seconds | A question, why it matters, three points, a recap, a call to action |
| Training | 2 to 4 minutes a chapter | What you'll learn, the steps, a recap, the next step |
| Sales message | 30 to 60 seconds | The person's name and situation, one benefit, proof, a simple ask |

For anything over 30 seconds, show the script and the plan (voice, length, segments) and get a yes before rendering.

## Step 5: Choose the voice

- **The avatar's own voices**: pass the script as `prompt` and a voice in `options.voice`, matched to the presenter's apparent gender and age and to the audience. Always name one, even when the user didn't: the tool's usual rule of passing only the settings the user asked for doesn't apply here, because without a voice the avatar speaks in a default one that may not match the person in the photo. For a woman, try "Calm Chloe", "June - Lifelike", "Stephanie" or "Ivy"; for a man, "Dexter - Professional", "Professor Dean", "Mellow Marcus" or "Charming Charles - Friendly 😊". `media_models` with `category: "video"` lists them all; pass the name exactly as listed.
- **A separate voiceover**, passed as `options.audio_url`: when the user has their own recording, when the avatar's voices don't suit the language, or when the voice needs control they don't offer (a named ElevenLabs voice, audio tags, exact pronunciation). Make it with `audio_generate` and check it first, since its length sets the video's length. Use the URL `audio_generate` returns or, for a file you edited in the sandbox, publish it with `publish_artifact` (`as_input: true`) to get one. Use clean speech only, and add any music after the video is made.

## Step 6: Generate

Call `video_generate` with:

- `model: "HeyGen Avatar 4"`;
- `image_url`: the photo;
- `prompt`: exactly the words to be spoken, with no stage directions. Leave it out when you pass `audio_url`;
- `aspect_ratio` for the platform, and `resolution`: "720p" for a draft, "1080p" for the final;
- `options`:
  - `voice`: the voice you chose in Step 5, every time, or `audio_url` for a recording;
  - `talking_style`: "stable" (the default) for corporate, training and finance; "expressive" for social hooks and lively scripts;
  - `expression: "happy"`, only for upbeat scripts;
  - `background`: a colour, as in `{"type": "color", "value": "#F2F2F2"}`, or `{"type": "image", "value": URL}` with an image in the same aspect ratio. Pick a colour that contrasts with the person's hair and clothes;
  - `caption: true` to burn captions in.

Leave out `duration`: the speech sets the length. A call looks like this:

```json
{"model": "HeyGen Avatar 4", "image_url": "https://.../photo.jpg", "prompt": "Big news from Brewly. Starting today...",
 "aspect_ratio": "16:9", "resolution": "1080p",
 "options": {"voice": "Calm Chloe", "talking_style": "stable", "caption": true}}
```

**Long scripts**: split them into segments of 30 to 60 seconds at the end of a section, never mid-sentence. Use the same photo file, voice, style, background, aspect ratio, resolution and caption setting for every segment. Tell the user how many segments you'll render and that each one uses credits, and get a yes. Then pass `generations_planned` with the total and `split_confirmed: true`.

**For a long or important video**, render the first segment, check it (Step 7), and only then render the rest.

## Step 7: Check it

Download the video and ask `media_analyze` to watch the start, middle and end, and every join:

- Do the lips stay in time with the words to the end, with no drift?
- Is the mouth clean, with no blur, smearing or odd teeth, and is it still the same person?
- Do the expression and head movement suit the words? Is there any flicker or warping?
- Are the captions spelled right and clear of the face? Is any word said wrong?

Vision models can report lip sync as fine when the mouth never moves, so also check it on frames. Take one second of speech from the middle as a strip of six frames, and ask `media_analyze` to describe the mouth in each frame, then compare the six descriptions:

```bash
ffmpeg -y -loglevel error -ss 8 -t 1 -i presenter.mp4 -vf "fps=6,scale=320:-1,tile=6x1" mouth-strip.jpg
```

If the mouth is the same in all six frames while someone is speaking, the face isn't talking: render that segment again.

Fix what failed, and render only that segment again:

| Problem | Fix |
|---|---|
| A word said wrong | Respell it in the script, or use a voiceover with IPA (ElevenLabs v4) |
| Lips drift late in a long take | Shorter segments |
| The face warps or the teeth smear | `talking_style: "stable"`, no `expression`, or a better photo |
| Poor sync with a recording | Remove the music and noise from the recording |
| Captions over the face | Render without captions and add them afterwards |

If it still looks uncanny after two attempts, say so plainly, and offer a voiceover over the user's own footage or slides instead.

## Step 8: Join and deliver

Join segments in order, and even out the loudness:

```bash
cd /tmp/.scratch/avatar
ffmpeg -y -loglevel error -i seg1.mp4 -i seg2.mp4 -i seg3.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a0];[a0]loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart presenter.mp4
```

Publish a joined video with `publish_artifact` (`kind: "video"`); a single segment is already in the chat. Then reply with:

- the video, its length, and the voice, style and aspect ratio used;
- what you checked, and a request to watch it once before posting: automated checks can miss a mouth that drifts or doesn't move, so don't call the lip sync verified;
- the script as spoken;
- a reminder that platforms such as YouTube, TikTok and Instagram ask creators to label realistic AI-generated people, so turn on the AI label when posting.

## What not to do

- Don't animate anyone without their consent, or a public figure or a child.
- Don't put words in the presenter's mouth that the user hasn't approved: claims, prices, endorsements or quotes.
- Don't render a long video before the user has approved the script, the voice and the number of segments.
- Don't use a frame from a rendered video as the photo for the next segment; always use the original photo.
- Don't show the user scratch files.
