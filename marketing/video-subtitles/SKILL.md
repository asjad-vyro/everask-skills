---
name: Video Subtitles and Translations
description: >
  Makes subtitles for a video in its own language and translates them into any
  others: SRT and VTT files ready for YouTube, LinkedIn, Vimeo or a video
  editor, plus, if asked, a copy of the video with the subtitles burned in.
  Keeps names and product terms consistent, keeps lines short enough to read,
  and checks the timing. Use it for "add subtitles", "translate the
  subtitles", "subtitle this in Spanish", "make an SRT file", "burn in
  captions" or "caption my video in Arabic".
---

# Video Subtitles and Translations

Produce subtitle files that are accurate, easy to read and correctly timed, in every language the user needs.

Subtitles are judged on three things: the words are right, especially names; each subtitle stays up long enough to read; and the timing matches the speech. Translation adds a fourth: the meaning survives in fewer characters.

If the user wants the speech itself replaced with another language (a dub), load the built-in `short-drama-multilingual-dubbing` skill with `skill_view` instead.

Work in `/tmp/.scratch/subs/` in the sandbox. Only the finished files go to the user.

## Step 1: Get the video and the brief

- **Uploaded**: download the file's URL into the sandbox with `curl -L`.
- **A link**: load the built-in `web-intelligence` skill with `skill_view` and download the video with its media tool. If YouTube or another site blocks the download, ask the user to upload the file.
- **Subtitles already exist** (an SRT or VTT the user attached): skip Step 2. Read each cue in as a segment shaped like `{"timestamp": [start_seconds, end_seconds], "text": "..."}`, and carry on from Step 3.

Settle these from the message:

- **Target languages.** If none are named, make subtitles in the video's own language only.
- **Files or burned in.** Make files by default. Burn subtitles into a copy of the video only if the user asks.
- **Names and terms** that must stay exactly as written: people, brands, products, places.

## Step 2: Transcribe

Extract the audio, publish it to get a URL, and transcribe it:

```bash
ffmpeg -y -i source.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 48k audio.mp3
```

1. Call `publish_artifact` with the audio's path, `kind: "audio"` and `as_input: true`.
2. Call `audio_transcribe` with the URL it returns and `timestamps: true`. If the user named the spoken language, pass its code as `language`; otherwise the language is detected and returned as `detected_language`.
3. The result has `segments`, each with `timestamp: [start, end]` and `text`. For a long video the result is saved to a file in the sandbox. Load that file with Python rather than reading it into the chat, and save the segments as `segments.json`.

## Step 3: Clean the source text

Fix what speech recognition gets wrong, without changing what was said:

- names, brands and terms, using the user's list, the video's title and its on-screen text;
- numbers, units and dates, written the way the speaker said them;
- filler words ("um", "uh"), which you can drop.

Keep the speaker's meaning and words. Don't paraphrase.

## Step 4: Build the cues

Each subtitle (cue) has at most 2 lines of 42 characters, and stays up for 1 to 7 seconds. It shows no more than 17 characters per second, so it can be read. This code turns the segments into cues and writes SRT and VTT files:

```python
import json

def wrap(text, max_line=42):
    """At most two lines, broken at the space nearest the middle (or mid-text for languages without spaces)."""
    text = " ".join(text.split())
    if len(text) <= max_line:
        return text
    mid = len(text) // 2
    spaces = [i for i, ch in enumerate(text) if ch == " "]
    if not spaces:
        return text[:mid] + "\n" + text[mid:]
    cut = min(spaces, key=lambda i: abs(i - mid))
    return text[:cut] + "\n" + text[cut + 1:]

def subtitle_cues(segments, max_line=42, max_cps=17, min_dur=1.0, max_dur=7.0):
    """Transcript segments -> subtitle cues: up to 2 lines each, at a readable speed."""
    cues = []
    for seg in segments:
        s, e = seg["timestamp"]
        words = seg["text"].split()
        if not words:
            continue
        e = e if e is not None else s + max(min_dur, len(seg["text"]) / max_cps)
        per_char = (e - s) / len(" ".join(words))
        t, cur = s, []
        for i, w in enumerate(words):
            cur.append(w)
            text = " ".join(cur)
            nxt = words[i + 1] if i + 1 < len(words) else None
            if (nxt is None or len(text) + 1 + len(nxt) > 2 * max_line or per_char * len(text) >= max_dur
                    or (w[-1] in ".?!" and len(text) > max_line * 0.6)):
                d = per_char * (len(text) + (1 if nxt else 0))
                cues.append([t, t + d, text])
                t, cur = t + d, []
    for i, c in enumerate(cues):  # give short or fast cues time to be read, without running into the next one
        limit = cues[i + 1][0] - 0.08 if i + 1 < len(cues) else c[1] + 2
        c[1] = max(c[1], min(c[0] + max(min_dur, len(c[2]) / max_cps), limit))
    return [(a, b, wrap(text, max_line)) for a, b, text in cues]

def stamp(t, sep):
    ms = max(0, int(round(t * 1000)))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"

def write_srt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        for n, (a, b, text) in enumerate(cues, 1):
            f.write(f"{n}\n{stamp(a, ',')} --> {stamp(b, ',')}\n{text}\n\n")

def write_vtt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for a, b, text in cues:
            f.write(f"{stamp(a, '.')} --> {stamp(b, '.')}\n{text}\n\n")

segments = json.load(open("/tmp/.scratch/subs/segments.json"))
cues = subtitle_cues(segments)
write_srt("/tmp/.scratch/subs/product-demo.en.srt", cues)
write_vtt("/tmp/.scratch/subs/product-demo.en.vtt", cues)
```

Name the files `<video name>.<language code>.srt`, for example `product-demo.es.srt`.

**For a vertical video** with burned-in subtitles, use `max_line=24`.

## Step 5: Translate

Translate cue by cue, so every language keeps the source timing:

- **Keep the cue count.** Translate the list of cue texts as a numbered list, then check that you got the same number back.
- **Translate the meaning, in the way people speak.** Don't translate word for word.
- **Condense where needed.** A translation often runs 20 to 30% longer (German and French, for example). Shorten it so the cue still reads at 17 characters per second or less.
- **Keep the user's names and terms exactly**, along with brands, URLs and code.
- **Line lengths**: wrap each translated cue with `wrap(text, 42)`. For Chinese and Japanese, use `wrap(text, 16)`; they read at about 9 characters a second.
- **Right-to-left languages** (Arabic, Hebrew, Persian, Urdu) need nothing special in SRT or VTT files.

Write each language's files with the source timings and the translated text.

## Step 6: Check the files

For every file, check that:

- the cue numbers run in order;
- every cue ends after it starts, and no cue overlaps the next;
- no line is longer than the limit, and no cue has more than 2 lines;
- every language has the same number of cues as the source.

Spot-check 5 cues across the video against the audio, with `media_analyze` on short excerpts if needed.

## Step 7: Burn in, only if asked

Build an ASS file from the cues, with sizes in pixels for the video's own dimensions, and burn it in with the `ass` filter and `shaping=complex`. Without complex shaping, Arabic, Urdu and Hindi render with broken letters.

```python
def write_ass(path, cues, width, height, font="Noto Sans"):
    size, margin = (64, 420) if height > width else (round(height * 0.05), round(height * 0.06))
    def t(x):
        cs = max(0, int(round(x * 100)))
        return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"
    rows = [f"Dialogue: 0,{t(a)},{t(b)},Sub,,0,0,0,,{text.replace(chr(10), chr(92) + 'N')}" for a, b, text in cues]
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Sub,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,80,80,{margin},-1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(rows) + "\n")
```

```bash
ffmpeg -y -i source.mp4 -vf "ass=product-demo.es.ass:shaping=complex" \
  -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -c:a copy -movflags +faststart product-demo.es.mp4
```

- **Font**: Noto Sans covers Latin, Greek and Cyrillic. For other scripts, use the family that `fc-list :lang=CODE family` prints, such as Noto Sans Arabic, Noto Sans Devanagari or Noto Sans CJK SC.
- **Check the result**: look at 3 frames with subtitles on screen, using `media_analyze`. The letters should be joined and correct, with no empty boxes, and the text should be readable and clear of faces.
- **Size**: a delivered file must be under 100 MB. For a long video, encode at 720p (`scale=-2:720`) with a higher `-crf` (23 to 26). If it still won't fit, deliver the subtitle files and say why the video wasn't included.

## Step 8: Deliver

Publish each file with `publish_artifact`: `kind: "file"` for subtitle files and `kind: "video"` for burned-in videos. If there are more than 6 files, zip them as well, with `kind: "archive"`. Then reply with:

- the files, by language;
- the cue count and the video's length;
- the first 3 cues in each language, so the user can judge the tone;
- how to add the files on YouTube: YouTube Studio, then Subtitles, Add language, Upload file, With timing.

Say once, briefly, that machine translation should be checked by a native speaker before public or legal use.

## What not to do

- Don't change what the speaker said, or soften it.
- Don't let a translation drift on names, product terms or numbers.
- Don't merge or split cues in a translation; keep the source timing.
- Don't show the user scratch files: the audio, segments or ASS files.
