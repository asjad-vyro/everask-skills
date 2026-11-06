---
name: Music and Soundtrack Maker
description: >
  Makes music that fits a video or a brief: background beds cut to the exact
  runtime, intros and outros, logo stings and seamless loops, with the mood,
  tempo and hits placed where the picture changes. Writes precise music
  prompts, picks the model for the job, trims and fades the track, mixes it
  under a voiceover at the right loudness and puts it on the video. Use it for
  "background music for my video", "make a soundtrack", "music for this ad",
  "a 30-second music bed", "intro music for my podcast", "a seamless loop" or
  "add music to this video".
---

# Music and Soundtrack Maker

Make music that serves the picture or the moment it's for: the right mood, the right length, and changes where the content changes.

Generated music usually goes wrong in one of three ways. It doesn't fit the length, so it stops dead or is chopped mid-phrase. It fights the voice for attention. Or it's generically "upbeat", with nothing tied to the edit. This skill plans the music against a cue sheet, asks for it in musical terms, then trims, mixes and checks it.

For a song with lyrics, load the built-in `songwriting-and-ai-music` skill with `skill_view` instead.

Work in `/tmp/.scratch/music/` in the sandbox. Only the finished files go to the user.

## Step 1: Get the brief

Settle these from the message and any files:

- **What it's for**: a video, an ad, a podcast intro or outro, a logo sting, a loop for an app, game or website, or a track on its own.
- **The length**, or the video it has to fit.
- **The mood and genre**, any tempo or instruments the user wants, and anything to avoid.
- **Whether a voice plays over it.** Music under speech has to stay out of the way.
- **Vocals**: none by default. Background music is instrumental unless the user asks otherwise.

If the user names an artist or a song ("like Hans Zimmer"), describe that sound in musical terms instead: genre, era, instruments, tempo and mood. Never put an artist's name, a song title or lyrics in the prompt.

Ask a question only if you can't tell what the music is for.

## Step 2: Map the video

If there's a video, download it and build a cue sheet: the moments the music should follow.

```bash
cd /tmp/.scratch/music
# Length in seconds
ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4
# Cuts
ffmpeg -hide_banner -i video.mp4 -an -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2
# Pauses in the speech
ffmpeg -hide_banner -i video.mp4 -vn -af silencedetect=noise=-35dB:d=0.4 -f null - 2>&1 | grep -E 'silence_(start|end)'
```

If the scene check finds too many cuts in fast or animated footage, raise the threshold to 0.4 or 0.5. Then ask `media_analyze` for the video's changes of mood, its key moments (a reveal, the logo, the call to action) and where people speak, with times.

Write the cue sheet as a table of time, what happens, and what the music does. For example: 0:00, open on the product, soft intro; 0:04, the voice starts, steady bed; 0:24, the logo, one clean hit; 0:24 to 0:30, the chord rings out.

## Step 3: Pick the model

The `music_generate` tool's description lists the models available now, with their lengths. Trust it over this list:

- **An exact length** (a bed under a cut, a sting, a loop): MiniMax Music 3 (1 to 300 seconds) or ElevenLabs Music v2.5 (3 seconds to 10 minutes, with the most finished mix). Pass `duration_seconds`.
- **A quick draft, or a mood to try out**: Lyria 3.5, the default. Its length is only a hint in the prompt, so plan to trim it. It can also take a picture whose mood the track should match, as `image_url` in `options`.
- **Longer than one model's maximum**: several sections in the same key, tempo and instruments, joined with a crossfade (Step 6).

## Step 4: Write the prompt

Write it in this order, in plain sentences:

1. **Purpose and length**: "Instrumental background music for a 30-second app demo with a voiceover."
2. **Genre and era**, in musical terms: "warm minimal electronic", "1970s soul", "modern cinematic hybrid".
3. **Tempo, meter and key**: "120 BPM, 4/4, G major".
4. **Instruments by role** (lead, rhythm, bass, pads): "soft Rhodes chords, muted synth plucks, round sub bass, light shaker".
5. **Structure, tied to the cue sheet**: "Rhodes alone for 4 seconds; bass and shaker enter at 0:04 and stay steady; a gentle lift from 0:20; one clean hit at 0:24; the chord rings out to silence by 0:30." On Lyria, time ranges such as `[0:00-0:04]` work well.
6. **Vocals**: "Instrumental only: no vocals, choir, humming, spoken words or vocal chops." Pass `instrumental: true` as well.
7. **Its place in the mix**: under a voice, ask for a "background bed" with "steady energy", and leave out busy hi-hats, big drops and risers, which compete with speech.
8. **The ending**: "ends on a held chord", "clean ending, no fade" or, for a loop, "ends exactly where it starts, with no intro or outro".

**Tempo by feel:**

| Feel | BPM |
|---|---|
| Calm, meditation, luxury | 60 to 80 |
| Explainer, corporate, tutorial | 90 to 115 |
| Upbeat ad, product launch | 115 to 128 |
| Sports, action, hype | 128 to 150 |

Major keys sound bright (C, G) or triumphant (D, B flat); minor keys sound serious (D, A), mysterious (E, B) or sad (F, C).

**Hits on the beat**: a bar of 4/4 lasts 240 ÷ BPM seconds. For a hit to land on a bar line, pick a tempo at which the hit time is a whole number of bars. At 120 BPM a bar lasts 2 seconds, so a hit at 12 seconds starts bar 7. Name both the tempo and the hit time in the prompt.

## Step 5: Generate

Call `music_generate` with `prompt`, `model`, `instrumental: true` and, for the models that take it, `duration_seconds`. Make one track per piece. If a result is wrong, change one thing in the prompt (the instruments, the tempo or the energy) rather than everything, and say what you changed.

Download the result into the sandbox: `curl -L -o music.mp3 URL`.

## Step 6: Fit, mix and finish

Work on WAV files, and encode only at the end.

```bash
cd /tmp/.scratch/music
# Fit to a 30-second video: trim at a bar line, fade in over 0.5 s, fade out over the last 3 s
ffmpeg -y -loglevel error -i music.mp3 -af "atrim=0:30,asetpts=N/SR/TB,afade=t=in:d=0.5,afade=t=out:st=27:d=3" -ar 48000 bed.wav
# Join two sections with a 2-second crossfade (one bar at 120 BPM)
ffmpeg -y -loglevel error -i part1.wav -i part2.wav -filter_complex "[0:a][1:a]acrossfade=d=2:c1=qsin:c2=qsin" -ar 48000 joined.wav
```

- **Trim at a bar line**, not mid-phrase, and fade out over the last 2 to 3 seconds unless the track's own ending fits. Never stretch music to fit; trim it, or generate it again at the right length.
- **Joins**: make the crossfade a whole number of bars, and start the second section on its first downbeat.
- **Loops**: check the seam by playing the loop twice in a row (`ffmpeg -y -stream_loop 1 -i loop.wav -c copy twice.wav`) and asking `media_analyze` whether the join halfway through can be heard.

**Under a voice**, duck the music whenever someone speaks. The voice is a voiceover file, or the video's own speech (`ffmpeg -i video.mp4 -vn -ar 48000 voice.wav`):

```bash
ffmpeg -y -loglevel error -i bed.wav -i voice.wav -filter_complex \
  "[1:a]asplit[vo][k];[k]apad[key];[0:a]volume=-10dB,equalizer=f=3000:t=q:w=1:g=-4[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=80:release=600[d];[d][vo]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -ar 48000 mix.wav
```

While someone speaks, the music should sit about 18 to 20 dB below the voice, rising in the gaps. If the words are hard to follow, lower the bed's `volume` further.

**Loudness for music on its own**: `ffmpeg -y -i bed.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 final.wav`. Use −14 LUFS for social and YouTube, and −16 for podcasts.

**On the video**:

```bash
ffmpeg -y -loglevel error -i video.mp4 -i mix.wav -filter_complex "[1:a]apad[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest video-music.mp4
```

## Step 7: Check it

- **Length**: the track or the mix matches the video to within a frame (`ffprobe`).
- **Listen with `media_analyze`**: ask about the opening, each hit on the cue sheet, every join or loop seam, and the ending. It should confirm that there are no vocals or spoken words, no clicks and no abrupt stops, and that each hit lands where planned.
- **Loudness**: `ffmpeg -hide_banner -nostats -i final.wav -af ebur128=peak=true -f null - 2>&1 | grep -E '^ +(I|Peak):'`. The integrated loudness (I) should be within 1 LU of the target, and the true peak at −1.5 dBTP or lower.
- **With a voice**: ask `media_analyze` whether the music covers any words.

## Step 8: Deliver

Publish the files with `publish_artifact`: the music (`kind: "audio"`), and the video with music (`kind: "video"`) if you made it. Then reply with:

- what you made: the length, tempo, key and model;
- the cue sheet, with where each hit lands;
- the prompt you used, so the user can ask for variations;
- one offer: another take in a different mood, a cut-down (15 or 6 seconds), or a version without the hit.

Before the user puts generated music in an ad or a monetised video, suggest they check EverAsk's terms for commercial use.

## What not to do

- Don't name artists, bands or songs in a prompt, or ask for a sound-alike.
- Don't stretch, speed up or slow down a track to fit; trim it or generate it again.
- Don't let the music cover the voice.
- Don't hand over a track you haven't checked with `media_analyze`.
- If generation fails or keeps missing the brief after three tries, say what went wrong and offer to try again later. Don't build the music yourself in code.
- Don't show the user scratch files.
