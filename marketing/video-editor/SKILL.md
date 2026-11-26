---
name: Video Editor by Timestamp
description: >
  Applies your own edit list to an uploaded video and returns the edited file: remove or keep time ranges, join clips,
  make it vertical 9:16, square or 16:9 without stretching, add a logo or text for a time range, picture-in-picture,
  speed, freeze, mute, replace the sound, grab a frame or make a GIF. Use it for "cut 10s to 15s out of this video",
  "make this vertical", "add my logo from 0:05 to 0:20", "put the text ... top left".
---

# Video Editor by Timestamp

The user gives you a video and says what to change and when. A good result is the same video changed exactly as asked, nothing else touched, with the length, size and sound checked and the edit points looked at.

Reply in the language the user wrote in, unless they ask for another. Text added to the video is written exactly as the user typed it.

Never invent: timestamps the user did not give and you did not find in the video, durations, or what is in the picture. Every number in the reply comes from the script or `ffprobe`. Say what you did not check.

Write no text before or between tool calls: no "I'll load the skill", no "first I will probe it". The only text you write is the final reply, and it starts with the result.

## Step 1: Get the file and look at it

Download each uploaded file (the video, a logo or image, a second clip) from the URL in the message into `/tmp/.scratch/video-editor/` with `curl -L -o /tmp/.scratch/video-editor/<name> "<url>"`, keeping the extension. A YouTube or Drive link is not an upload: use a connected Drive or Dropbox if there is one, otherwise ask for the file.

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `video_edit.py` under `~/.computer/skills` with `search_files`.

Probe: write `{"input": "<file>"}` to `/tmp/.scratch/video-editor/edit.json` and run `python3 SKILL_DIR/scripts/video_edit.py /tmp/.scratch/video-editor/edit.json`. It prints duration, size, frame rate and whether there is sound, plus a warning if the video is long or 1080p or larger.

## Step 2: Settle the times

- Use the times the user gave exactly. Accept `mm:ss`, `h:mm:ss` and seconds.
- **Cut means remove.** "Cut / remove / delete / drop / trim off the first 5 seconds" (Turkish "ilk 5 saniyesini kes", Spanish "corta los primeros 5 segundos", French "coupe les 5 premières secondes") removes those seconds and keeps the rest: `{"op":"trim","start":5}`. Only "keep / only / just the first 5 seconds" or "shorten to 5 seconds" keeps that part. The result length is the original minus the removed part; check this against what you expect before you run.
- **Text or a logo with no times given** is shown for the whole edited video: leave out `start` and `end`. Never limit it to a range you invented.
- If they describe a moment instead ("when the slide shows", "the cough"), find it: pull frames with `ffmpeg -ss <t> -i <file> -frames:v 1 f.jpg` every few seconds (or ask `media_analyze` about the video) and confirm the time. State the time you chose.
- If times are missing and cannot be found, ask once with `clarify`. Otherwise decide, say what you assumed, and go on.
- Times in each operation refer to the video as it is after the previous operation. Put time-range operations (text, logo, cover, mute) before operations that remove time, and use original times, or say which timeline you used.

## Step 3: Say the limits

Say these before editing when the request needs them:

- No cutting a person out of their background, no changing what someone says, no lip-sync.
- No clean removal of objects or people. A burned-in logo or watermark cannot truly be removed: only cover an area the user gives (box, blur or pixelate) and say it is a cover-up.
- Long or large videos are slow: over about 10 minutes or 1080p, warn and offer 720p (`{"op":"scale","height":720}`).
- Quality is kept (x264 quality 18, AAC) and the original size is kept unless asked.

## Step 4: Write the edit list

Number the operations and repeat every time back in the reply. Write the JSON to `/tmp/.scratch/video-editor/edit.json`:

```json
{"input": "/tmp/.scratch/video-editor/<file>", "output": "/tmp/.scratch/video-editor/<name>-edited.mp4", "ops": [ ... ]}
```

| The user wants | Operation |
|---|---|
| Remove parts | `{"op":"remove","ranges":[{"start":"0:10","end":"0:15"}]}` |
| Keep only parts (joined in order) | `{"op":"keep","ranges":[{"start":5,"end":20}]}` |
| Remove the first 5 s, or keep only from 0:05 on | `{"op":"trim","start":5}` |
| Keep only the first 45 s (remove the end) | `{"op":"trim","start":0,"end":"0:45"}` |
| Vertical, square, wide | `{"op":"resize","aspect":"9:16"}` (also `1:1`, `4:5`, `16:9`), with `"mode"`: `blur` (default: whole picture kept on a blurred copy of itself), `pad` (bars, optional `"color"`), or `crop` (fills the frame and cuts the sides; `"focus_x"` 0 to 1 is where the subject is). A `"size":"1080x1920"` overrides the default size. |
| Smaller file or 720p | `{"op":"scale","height":720}` |
| Logo or picture on top | `{"op":"overlay_image","file":"<path>","position":"top-right","start":5,"end":20,"width":0.15,"opacity":1}` |
| Text on top | `{"op":"text","text":"<the user's text>","position":"top-left","start":0,"end":4,"size":0.07,"color":"#FFFFFF","box":true}` |
| Hide an area | `{"op":"cover","x":0.7,"y":0.05,"w":0.25,"h":0.1,"mode":"blur","start":0,"end":10}` (`mode`: `blur`, `box`, `pixelate`; only where the user gave the area or you found it in a frame and said so) |
| Small clip or zoomed area in a corner | `{"op":"pip","file":"<path>","position":"bottom-right","width":0.3,"start":5,"end":15,"audio":"mix"}` or `{"op":"pip","region":{"x":0,"y":0,"w":0.4,"h":0.4},...}` for part of the same video |
| Join clips after the video | `{"op":"join","files":["<path>","<path>"]}` (all scaled to the first video's size without stretching) |
| Faster or slower | `{"op":"speed","factor":2}` or with `"start"`, `"end"` for a range (0.25 to 8; sound keeps its pitch) |
| Hold a frame | `{"op":"freeze","at":"0:05","duration":3}` |
| Show a picture over a range | `{"op":"image_segment","file":"<path>","start":10,"end":14,"mute":false}` |
| Mute, quieter, louder | `{"op":"mute","start":5,"end":8}`, `{"op":"volume","gain_db":-6}` (no times means the whole video) |
| Replace the sound with a file the user gave | `{"op":"replace_audio","file":"<path>","loop":true,"gain_db":0}` |

Positions are `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right`, or `{"x":..,"y":..}` as the top-left corner. Sizes and positions from 0 to 1 are fractions of the frame; bigger numbers are pixels. If the user says "top corner" and not which, use `top-left` and say so. Text uses a Noto font and is drawn as a picture, so accents work; right-to-left scripts may not shape correctly, so look at the frame.

Not offered here: removing a person or object cleanly, keying out a background, changing speech.

## Step 5: Run it

Run `python3 SKILL_DIR/scripts/video_edit.py /tmp/.scratch/video-editor/edit.json`. The JSON result has `ok`, `change_list`, `before` and `after` (duration, width, height, size in bytes), `expected_duration`, `actual_duration`, `duration_ok`, `size_ok`, `audio_present`, `warnings`, `edit_points_in_output_seconds` and `check_frames` (a picture at each edit point).

- If `ok` is false, read `error`, fix the edit list once, run again. If it still fails, tell the user what failed.
- Several operations are applied one after another; each re-encodes at high quality, so do all edits in one run.
- `duration_ok` and `size_ok` must be true, and `audio_present` true if the original had sound. If not, say so.
- Frame grab: `{"action":"frame","input":"<file>","at":"0:07","output":".../frame.png"}`. GIF: `{"action":"gif","input":"<file>","start":2,"end":5,"width":480,"fps":12,"output":".../clip.gif"}` (keep it short; warn if over 10 MB).

## Step 6: Look at it once

Ask `media_analyze` to look at the pictures in `check_frames` (or the output video) once: is the text or logo where it should be and fully visible, is anything cut off or stretched, is there a glitch at a cut. Report what it says and fix once if something is wrong. If a frame is not what the edit list should give, say so rather than claiming it is right.

## Step 7: Deliver

Publish the file with `publish_artifact` (`kind: "video"`; `kind: "file"` for a .gif or .png). Reply with:

1. **Change list**: the numbered operations with the times as the user gave them, and what you assumed.
2. **Before and after**: duration, resolution and file size, from the script.
3. **Check**: length found against length expected, sound present, what the frame check showed (or that you did not check).
4. **Limits or warnings** from the script in plain words.
5. One offer, for example another format for another platform.

## When the user asks for a change

Change only what was asked and keep everything else as it was. Re-run the edit from the original file with the adjusted list, not from the edited one. Rebuild the same file type under the same name, and say in one line what changed.

## Hard rules

- Work from the user's video and files only. Never generate footage, speech or music, and never claim an object, logo or person was removed.
- Every number in the reply is from the script or `ffprobe`; compute any sum in code.
- Do not install anything. The script needs `ffmpeg`, `ffprobe`, Python and Pillow (for text).
- Final self-check: times repeated as given, no invented times or picture contents, length and size verified, reply starts with the result.
