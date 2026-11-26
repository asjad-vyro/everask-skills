---
name: Audio and Video Sound Fixer
description: >
  Fixes the sound of a recording, song file or finished video you upload: evens out the volume, sets the loudness,
  trims, fades, cuts out a section, mutes or lowers a time range, mild noise reduction, speed, or music ducked under
  a voice. Use it for "make this louder", "even out the volume", "cut the first 3 seconds of this audio", "add a fade
  out", "lower the music at 1:20", "remove the cough at 0:45".
---

# Audio and Video Sound Fixer

The user gives you a sound that already exists (an audio file, or the soundtrack of a video) and says what is wrong. A good result is the same recording, changed exactly as asked, with the loudness measured before and after and the length checked. This skill never makes new music or new speech.

Reply in the language the user wrote in, unless they ask for another. Keep their file names, times and figures exactly as given.

Never invent: loudness figures, times, durations or what is "in" the recording. Every number in the reply comes from the script's output or from `ffprobe`. If you did not hear something, say you did not check it.

Write no text before or between tool calls: no "I'll load the skill", no "let me measure". The only text you write is the final reply, and it starts with the result.

## Step 1: Get the file

- Uploaded audio or video: download the URL from the message into `/tmp/.scratch/sound-fixer/` with `curl -L -o /tmp/.scratch/sound-fixer/<name> "<url>"`. Keep the original extension.
- Music or a voice for mixing is a second uploaded file: download it the same way.
- A link to YouTube or a cloud drive is not an upload: if the user has a connected Drive or Dropbox, use it to fetch the file; otherwise ask them to upload the file.

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `sound_edit.py` under `~/.computer/skills` with `search_files`.

## Step 2: Say the limits, then measure

Before you edit, say plainly what cannot be done here, if the request needs it:

- Separating a voice from music that is already mixed into one track, removing one instrument, or removing a song that plays under speech: not possible. Offer what is: lower or mute that time range, or cut it out.
- Removing echo or reverb, repairing clipped (distorted) peaks, or making a bad recording sound like a good one: not possible. Mild noise reduction helps steady hiss or hum only.
- Changing what someone says, or re-singing: not possible.

Then measure. Write `/tmp/.scratch/sound-fixer/measure.json` with `{"input": "<file>"}` and run `python3 SKILL_DIR/scripts/sound_edit.py /tmp/.scratch/sound-fixer/measure.json`. The result has duration, sample rate, channels, integrated loudness in LUFS, loudness range, true peak, and `loudness_by_window` (average loudness for each 5 seconds). Use the windows to see where quiet and loud parts are, and to find a time range the user describes if they gave no exact times.

If the user gave no times for something like "the cough" and the windows do not show it, ask `media_analyze` to listen to the file and give the time. State the time you will use.

## Step 3: Write the change list

Turn the request into numbered operations, with every time in `mm:ss` or seconds as the user gave it, and repeat them in the reply. Decide the rest and say what you assumed.

| The user wants | Operation | Notes |
|---|---|---|
| Louder, quieter overall, "normalise", for YouTube, social, a podcast | `{"op":"normalize","target_lufs":-16}` | -16 LUFS for speech and podcasts, -14 for music and social, unless the user names a target. True peak limit -1.5 dBTP. |
| Even out: some parts too quiet and others too loud | `{"op":"even_out"}` then `normalize` | Follow `even_out` with `normalize`. It aims at the middle between the quiet and loud parts: quiet parts are raised by at most 20 dB, loud parts lowered by at most 12 dB, silence is left alone. Use it once only (a second run adds nothing). If `after.loudness_by_window` still shows a gap of more than 3 dB, say so in the reply; do not rebuild the file by hand. |
| Keep only part of it | `{"op":"trim","start":"0:03","end":"0:25"}` or `{"op":"trim","start":0,"duration":15}` | "Remove the first 3 seconds" is `trim` from 3 to the end. |
| Remove a section in the middle | `{"op":"cut","ranges":[{"start":"0:10","end":"0:14"}],"crossfade":0.05}` | Several ranges allowed. Crossfade 0.05 to 0.1 s avoids a click. |
| Fade in or out | `{"op":"fade","in":1,"out":2}` | Seconds. Either one may be left out. |
| Lower or raise one time range | `{"op":"volume","start":"1:20","end":"1:35","gain_db":-12}` | Short smooth ramps are added at both ends. No `start` and `end` means the whole file. |
| Silence one time range | `{"op":"mute","start":"0:45","end":"0:46"}` | |
| Hiss or hum | `{"op":"denoise"}` | Mild. Options `reduction_db` (default 12), `highpass_hz` (default 80). Always warn it is mild. |
| Faster or slower, pitch kept | `{"op":"speed","factor":1.1}` | 0.25 to 4. |
| Join a second file | `{"op":"join","file":"<path>","crossfade":2}` | The second file is added after the first. |
| Music under a voice | `{"op":"duck","file":"<music path>","music_gain_db":-14,"loop":true}` | The main input is the voice. Only when the user supplies the voice and the music as separate files. `loop` repeats short music. |
| Another format or bitrate | the `output` extension and `"bitrate":"192k"` | `.wav .mp3 .m4a .flac .ogg .opus` for audio. |

Order the operations like this: `denoise`, then `volume` and `mute` (times as in the original file), then `cut` or `trim` (original times too), then `join` or `duck`, then `speed`, `even_out`, `normalize`, and `fade` last. After a `cut`, `trim` or `speed`, times in later operations refer to the new, shorter timeline.

**Video files.** The picture is kept untouched and only the sound is replaced, so the length stays the same. The one exception is a single `trim`, which also trims the video (the picture is re-encoded, at quality 18). `cut`, `speed` and `join` are refused for video. If the user wants those, fix the sound, tell them the video itself needs cutting, and offer to do it as a separate step.

## Step 4: Run it

Write the edit list to `/tmp/.scratch/sound-fixer/edit.json`:

```json
{"input": "/tmp/.scratch/sound-fixer/<file>", "output": "/tmp/.scratch/sound-fixer/<name>-fixed.<same extension>",
 "ops": [ ... ]}
```

Run `python3 SKILL_DIR/scripts/sound_edit.py /tmp/.scratch/sound-fixer/edit.json`. The result is JSON with `ok`, `change_list`, `expected_duration`, `actual_duration`, `duration_ok`, `cut_points_in_output_seconds`, `warnings`, and `before` and `after` (loudness, true peak, loudness by window).

- The output has the same container and extension as the input unless the user asked for another. A video is delivered as a video.
- If `ok` is false, read `error`, fix the edit list once and run again. If it still fails, tell the user what failed.
- `duration_ok` must be true (the length matches the plan within 0.1 s). If not, say so.
- Never type a loudness number from memory: copy it from `before` and `after`.

## Step 5: Listen once

Ask `media_analyze` to listen to the output file once. Ask: is there a click, jump or abrupt change at each time in `cut_points_in_output_seconds` (and at each fade and muted range); does the voice sound natural; is anything cut off. Report what it says. If it hears a click at a cut, run again with `"crossfade":0.1`.

## Step 6: Deliver

Publish the output file with `publish_artifact`: `kind: "audio"` for audio, `kind: "video"` for a video. Then reply with:

1. **What I changed**: the numbered change list with the times as the user gave them, and anything you assumed.
2. **Before and after**: duration, integrated loudness (LUFS), true peak (dBTP), all from the script. For a file that was levelled, give the quietest and loudest 5-second windows before and after.
3. **Check**: the length found, and what `media_analyze` heard at the cut points. Say if you did not check something.
4. **Warnings** from the script, in plain words (for example that noise reduction is mild).
5. One offer: a different loudness target, another format, or a more careful cut.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. Run the edit again from the original file, not from the fixed one, so quality does not drop. Rebuild the same file type under the same name, and say in one line what changed.

## Hard rules

- Work from the user's file only. Never generate music, speech or sound effects, and never put anything in the recording that was not there, except the music file the user supplied for mixing.
- Every number in the reply is from the script or `ffprobe`. Do the arithmetic (for example expected length) in code.
- Say what cannot be fixed before you promise it, and never claim a noisy, echoing or clipped recording was repaired.
- Do not install anything. The script needs only `ffmpeg`, `ffprobe` and Python (it uses numpy for `even_out` if present).
- Final self-check: no invented numbers, times or contents; the file is the same type as the input; the reply starts with the result.
