---
name: Long Video to Social Clips
description: >
  Turns a long video (a webinar, podcast, interview, talk or livestream) into
  short vertical clips for Shorts, Reels, TikTok and LinkedIn. Finds the
  strongest moments that make sense on their own, cuts them on clean sentence
  boundaries, reframes them to 9:16 without cutting people out, burns in
  captions and a hook title, evens out the loudness, and writes a post caption
  for each clip. Use it for "clip this podcast", "make shorts from this
  webinar", "cut this video into reels", "find the best moments" or "repurpose
  this video for social".
---

# Long Video to Social Clips

Turn one long recording into a set of short clips, each one able to stop a scroll on its own.

A good clip starts on its point, makes sense to someone who never saw the full video, and ends right after the payoff. Most failed clips break one of those three rules, so the selection step matters more than the editing.

Work in `/tmp/.scratch/clips/` in the sandbox. Only the finished clips go to the user.

## Step 1: Get the source

- **Uploaded**: download the file's URL into the sandbox with `curl -L`.
- **A link** (YouTube, Vimeo, Drive, Zoom): load the built-in `web-intelligence` skill with `skill_view` and download the video with its media tool, at up to 1080p. YouTube often blocks downloads with a bot check. If the download fails, ask the user to upload the file.

Check it with `ffprobe`: the length, resolution, frame rate, and that there's an audio track. If it runs over 3 hours, ask which part to use.

Settle these, from the message or by default:

- **Number of clips**: 5 by default. Make fewer if the source doesn't have 5 strong moments, and never pad the set.
- **Platforms**: 9:16 for Shorts, Reels and TikTok. Use 1:1 when the user asks for LinkedIn or feed posts.
- **Length**: 20 to 60 seconds each, or up to 90 seconds for LinkedIn.
- **Topics** to focus on or avoid, if the user named any.

Ask a question only if the user gave no video.

## Step 2: Get a timed transcript

- **If the user gave a transcript or caption file with timestamps** (SRT, VTT, or an export from YouTube, Zoom or Riverside), use it and skip transcription. Convert it to a list of segments shaped like `{"timestamp": [start_seconds, end_seconds], "text": "..."}`.
- **Otherwise**, extract the audio, publish it to get a URL, and transcribe it:

  ```bash
  ffmpeg -y -i source.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 48k audio.mp3
  ```

  1. Call `publish_artifact` with the audio's path, `kind: "audio"` and `as_input: true`.
  2. Call `audio_transcribe` with the URL it returns and `timestamps: true`.
  3. The result has `segments`, each with `timestamp: [start, end]` and `text`. For a long recording the result is saved to a file in the sandbox. Load that file with Python, not by reading it into the chat.
  4. Save the segments as `segments.json`.

Fix the transcript's spelling of names, brands and terms, using the user's message, the video's title and its on-screen text.

## Step 3: Pick the moments

Read the whole transcript, printed as `[mm:ss] text`, one line per segment. List about twice as many candidates as you need. For each candidate, note:

- its start and end time, and its first line;
- its type: a bold claim, an insight, a story, proof (a number, a result, a demo), an opinion or a funny moment;
- a 1 to 5 score for the hook (do the first 3 seconds grab?), standing alone, value and energy.

Every pick must pass the **standalone test**:

- It starts on the point, not on a lead-in such as "so, um, going back to what I said".
- It doesn't depend on earlier context: no unexplained "he", "that" or "this slide", and no "as I mentioned".
- It ends after the payoff, not halfway through the thought.

Choose the final set by score, then make it varied: different parts of the video, different speakers, and different types. Write a hook title for each clip: up to 6 words, saying what the viewer gets. Don't use clickbait the clip doesn't pay off.

Then snap each in and out point to a pause, so no clip starts or ends mid-word. This prints the silences near a point:

```bash
ffmpeg -hide_banner -ss POINT_MINUS_2 -t 4 -i source.mp4 -af silencedetect=noise=-35dB:d=0.2 -f null - 2>&1 | grep -o "silence_[a-z]*: [0-9.]*"
```

The times it prints are counted from `POINT_MINUS_2`. Start a clip at the end of the pause before its first word, and end it at the start of the pause after its last word, plus 0.15 seconds.

## Step 4: Choose the framing

Grab a frame from the start, middle and end of each clip:

```bash
ffmpeg -y -ss TIME -i source.mp4 -frames:v 1 frame.jpg
```

Look at the frames with `media_analyze` and ask: where is the speaker's face, as a percentage of the frame's width from the left? Is anyone else, a slide or a screen share on screen? Then pick one of three layouts:

- **Crop**: one speaker who stays in roughly the same place. Cut a 9:16 window centred on the face.
- **Fit**: two people side by side, slides, a screen share, or a speaker who moves around. Keep the whole frame and fill the rest of the vertical canvas with a blurred copy. Never center-crop a wide shot that cuts people or slides off.
- **Keep**: the source is already vertical.

For the crop, the window is `ih*9/16` wide. Its left edge `X` is the face position times the frame width, minus half the window, kept between 0 and the frame width minus the window.

## Step 5: Make the captions

Captions are burned in, because most people watch muted. This code builds an ASS caption file for one clip from `segments.json`, timed from the clip's first frame. Each caption has 2 to 4 words, and the hook title shows for the first 4 seconds:

```python
import json, re

def ass_time(t):
    cs = max(0, int(round(t * 100)))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"

def caption_cues(segments, start, end, max_chars=20, max_words=4):
    """Short caption cues for the clip from start to end (seconds in the source), timed from the clip's first frame."""
    cues = []
    for seg in segments:
        s, e = seg["timestamp"]
        e = e if e is not None else s + 3
        words = re.sub(r"[{}\\]", "", seg["text"]).split()
        if e <= start or s >= end or not words:
            continue
        per_char = (e - s) / sum(len(w) + 1 for w in words)
        t, line = s, []
        for i, w in enumerate(words):
            line.append(w)
            text = " ".join(line)
            if (i == len(words) - 1 or len(line) == max_words or len(text) >= max_chars
                    or w[-1] in ".?!" or (w[-1] in ",;:" and len(line) > 1)):
                d = per_char * (len(text) + 1)
                a, b = max(t, start), min(t + d, end)
                if b - a > 0.15:
                    cues.append((a - start, b - start, text))
                t, line = t + d, []
    return cues

def write_ass(path, cues, width, height, hook="", hook_until=4.0, font="Noto Sans"):
    """Captions low in the frame but clear of the app's buttons, and an optional hook title at the top."""
    if height > width:
        cap, cap_margin, hook_size, hook_margin = 76, 560, 64, 270   # 9:16
    elif height == width:
        cap, cap_margin, hook_size, hook_margin = 60, 110, 56, 90    # 1:1
    else:
        cap, cap_margin, hook_size, hook_margin = 54, 60, 56, 60     # 16:9
    fields = "Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
    styles = [
        f"Style: Caption,{font},{cap},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,{cap_margin},-1",
        f"Style: Hook,{font},{hook_size},&H00FFFFFF,&H00FFFFFF,&H28000000,&H00000000,-1,0,0,0,100,100,0,0,3,16,0,8,70,70,{hook_margin},-1",
    ]
    events = [f"Dialogue: 1,{ass_time(0)},{ass_time(hook_until)},Hook,,0,0,0,,{hook}"] if hook else []
    events += [f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Caption,,0,0,0,,{text}" for a, b, text in cues]
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
                f"[V4+ Styles]\nFormat: {fields}\n" + "\n".join(styles) + "\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(events) + "\n")

segments = json.load(open("/tmp/.scratch/clips/segments.json"))
write_ass("/tmp/.scratch/clips/clip01.ass", caption_cues(segments, 754.2, 801.9), 1080, 1920, hook="Why your price is too low")
```

- **For 1:1**, use `max_chars=28, max_words=5` and a 1080 by 1080 canvas.
- **For languages other than English**: Noto Sans covers Latin, Greek and Cyrillic. For other scripts, use the family that `fc-list :lang=CODE family` prints, such as Noto Sans Arabic, Noto Sans Devanagari or Noto Sans CJK SC. Always burn in with the `ass` filter and `shaping=complex`, as below. Without it, Arabic, Urdu and Hindi render with broken letters.

## Step 6: Render

Render each clip separately. `START` and `DUR` come from Step 3, and `X` from Step 4. Each command cuts the clip, frames it, burns in the captions, brings the loudness to -14 LUFS (the level social apps play at) and fades the audio for a quarter of a second at each end, so there are no clicks.

**Crop**:

```bash
ffmpeg -y -ss START -t DUR -i source.mp4 \
  -vf "crop=ih*9/16:ih:X:0,scale=1080:1920,setsar=1,ass=clip01.ass:shaping=complex" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.15,afade=t=out:st=DUR_MINUS_0.25:d=0.25" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart clip01.mp4
```

**Fit** (the whole frame over a blurred copy):

```bash
ffmpeg -y -ss START -t DUR -i source.mp4 \
  -filter_complex "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.08[bgb];[fg]scale=1080:-2[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,ass=clip01.ass:shaping=complex[v]" \
  -map "[v]" -map 0:a:0 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.15,afade=t=out:st=DUR_MINUS_0.25:d=0.25" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart clip01.mp4
```

**1:1**: in the crop command, use `crop=ih:ih:X:0,scale=1080:1080`, with a caption file made for 1080 by 1080.

Keep `-ss` before `-i`. That makes the clip's timestamps start at zero, which is what the caption file assumes.

## Step 7: Check every clip

1. **`ffprobe`**: the length matches, the size is 1080 by 1920 (or 1080 by 1080), there's an audio track, and the file is under 100 MB.
2. **A contact sheet**: make one image per clip and look at it with `media_analyze`.

   ```bash
   ffmpeg -y -i clip01.mp4 -vf "fps=1/3,scale=270:-1,tile=6x1" -frames:v 1 sheet01.jpg
   ```

   The captions should be readable and spelled right, should not cover a face, and should stay clear of the bottom of the frame. The speaker should be in frame, and nothing should be black or frozen.
3. **The cut**: run `media_analyze` on the finished clip and ask for its first and last sentence word for word. If it starts or ends mid-word or mid-thought, move the point and render again.

If a clip still fails, deliver the rest and say which one failed and why.

## Step 8: Deliver

Publish each clip with `publish_artifact`, `kind: "video"`. Give each a name that says what's in it, such as `01-why-your-price-is-too-low.mp4`. Then reply with:

1. **A table**: number, hook title, length, where it comes from in the source (mm:ss to mm:ss), and one line on why it works.
2. **A post caption for each clip**: a hook-first line for TikTok and Reels with 3 to 5 hashtags, a Shorts title under 100 characters, and 2 to 3 short lines for LinkedIn.
3. **The posting order**: the strongest clip first, one a day rather than all at once.

Offer to cut more from the candidate list, to make 1:1 versions, or to change the caption style.

## What not to do

- Don't change what anyone said. Captions follow the speech; dropping "um" and "uh" is fine.
- Don't make a clip from a moment that only makes sense with context the viewer won't have.
- Don't center-crop a shot so that a speaker, a second person or a slide ends up cut off.
- Don't show the user scratch files: frames, audio, caption files or contact sheets.
