---
name: Idea to Published Video
description: Picks your next YouTube video from your channel's analytics and the questions your audience asks, writes the script in your own voice, and turns your recording into a rough cut with filler, pauses and retakes removed. Then it adds b-roll, subtitles and music, makes three thumbnails, titles and chapters, and schedules the video and its Shorts. Just say "plan my next video".
---

# Idea to Published Video

Takes a YouTuber from "what should I make next?" to a scheduled upload: research the
channel's analytics and the audience's questions, rank ten topics with evidence,
script the chosen one in the creator's own voice, cut their recording, finish it
with b-roll, subtitles, music and thumbnails, and schedule the video, 2-3 Shorts and
an Instagram reel. It never uploads, schedules or posts anything until the user has
confirmed every detail, never publishes straight away unless asked, and uses only
music, footage and images the user has the rights to.

## When to Use

- "Plan my next video." / "What should I make next on my channel?"
- "Write a script for [topic] in my voice."
- "Here's my recording, cut out the ums and pauses."
- "Make thumbnails, a title and chapters for this video and schedule it for Friday 5pm."
- "How did last week's video do?"

## Start Here

When this skill is open, treat the user's message as the start of the pipeline, not
as a one-off question. "Plan my next video", "next video" or just "video ideas" all
mean: run this pipeline for their channel. The user should not have to spell out the
steps.

- Begin at step 1 straight away. Do not ask "do you want me to look at your
  analytics?": that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. Those pauses protect the user's channel, voice and reputation, so
  never skip them, even if the user says "do everything".
- Nothing is needed to start except a connected YouTube channel (checked in step 1).
  If the user named a niche or topic, use it; otherwise infer the niche from the
  channel's top videos.
- Re-entry: "write a script for X" starts at step 3 with that topic; a recording or
  "here's my footage" starts at step 4; "make thumbnails / schedule this" starts at
  step 5 or 6; "how did it do?" runs the retention report from Automation.

## Prerequisites

Check each app at the step that needs it with `search_connector_tools`, then load
the tools with `expand_connector_tools`. When a required one is missing, call
`report_missing_connector_access` for it instead of explaining in prose.

| App | For | Needed at step |
|---|---|---|
| YouTube | Channel analytics, retention, search terms; upload and schedule the video and Shorts | 1 and 6 |
| Reddit | Audience questions (`reddit_research` works without a connector) | 1 (optional connector) |
| Google Sheets | The ranked topic list | 2 |
| Google Docs | Script, titles, description and chapters (else `generate_document`) | 3 and 5 |
| Instagram | Reel cross-post | 6 (optional) |

Descript and Splice are not needed: the built-in video editor does the transcript and
rough cut, and music comes from the user's own licensed library (Splice downloads
included) or is generated.

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Channel niche in a sentence | Never ask | Inferred from the top 10 videos |
| Topics the channel won't cover | Step 2 (only if the user mentions limits) | None |
| Past scripts, 5 or more (files or Docs links) | Step 3 | A saved voice profile from `memory`, if one exists; else ask |
| The recording of the new video | After step 3 | None: ask |
| Thumbnail style references | Never ask | The channel's last 6 thumbnails |
| Music | Never ask | The user's own tracks if they share them; else a generated instrumental |
| Upload day, time and time zone | Step 6 | None: ask (suggest the slot the analytics show their viewers are most active, if available) |
| Shorts | Never ask | 3 Shorts, one every 2 days at 12:00 after the main video |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`
message, then continue.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing, except at every **Stop**. Name the channel and the video topic in
every update. Templates for the topic sheet, script, thumbnails, metadata, Shorts
and reports are in `references/templates.md`: read it before step 2. Scripts run with
`terminal`; write their JSON inputs with `write_file`.

## Procedure

### 1. Research

Pull from the YouTube connector, for the last 90 days: top 10 videos by views and by
watch time (with average view percentage), traffic sources, YouTube search terms
that brought views, the median views of the last 20 videos, and the audience
retention curve (`elapsedVideoTimeRatio`, `audienceWatchRatio`) for the three best
videos. Run each curve through:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/retention_report.py" --file retention_<video>.json
```

Note what the best videos share where viewers stayed (hook length, when the first
payoff lands, where they dropped). Its output is the only source for those numbers.

Then find what the audience is asking: `reddit_research` for the niche (or the
Reddit connector), and `web_search` / `web_extract` for forums and Q&A sites. Keep
every question's URL. Comments on the channel's own videos (YouTube connector) count
too.

Every video, number and question must come from a live source read in this run, with
its link or "YouTube Analytics" kept next to it. If YouTube is not connected, stop and
call `report_missing_connector_access`; if no web or Reddit tool works, say so and
rank on analytics alone. Never fill gaps from memory, and never hand steps 1 and 2 to
`delegate_task`.

### 2. Rank topics

Group the evidence into candidate topics, write them to `topics.json` (shape in the
script's docstring, every evidence item with its `url` or `source`), and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/rank_topics.py" --file topics.json --top 10
```

The score (0-10) is the script's, not yours. Drop topics the user won't cover. Create
a Google Sheet "Video topics: <channel>" with the columns in
`references/templates.md`, best first, and share the link.

**Stop.** Show the top 10 with each one's evidence and working title, and ask which
to make. As soon as they pick, go on to step 3.

### 3. Script

Voice: if `memory` holds a voice profile for this channel, use it. Otherwise ask for
5 or more past scripts in one `clarify`, save them as files and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/voice_profile.py" past_script_1.txt past_script_2.txt ...
```

Offer to keep the profile with `memory` so the user never uploads them again. If they
have no written scripts, transcribe 5 past videos with `audio_transcribe` and use those.

Write the script (outline in `references/templates.md`) in a Google Doc, or with
`generate_document`: a hook that pays off the title within the first 15 seconds (about
as many words as the profile's `median_words_first_15s`), the structure that held
retention on the best past videos, the user's sentence length, person ("I"/"you"),
contractions and signature phrases, and `[B-ROLL: ...]` notes. Use only facts from
sources found in step 1 or the user; cite them in the Doc's notes.

**Stop.** Ask the user to edit the script, read it aloud, and record. They come back
with the recording (a file or link). Never treat the draft as final.

### 4. Rough cut

Transcribe the recording with `audio_transcribe` (`timestamps: true`), save the result
as `transcript.json`, and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/cut_list.py" --file transcript.json --duration <seconds> --srt captions.srt
```

It cuts long pauses, filler-only lines ("um", "uh, so, basically") and retakes
(keeping the last take), and returns `clips` in editor frames (30 fps) plus captions
remapped to the cut. Open the editor with `create_timeline` (the recording as one
`video` clip, landscape canvas), then `read_timeline` and `apply_timeline_edit` to
replace that clip with one clip per `clips` entry (same media, its `from`,
`durationInFrames`, `sourceInFrames`).

**Stop.** Show the rough cut in the editor with the numbers from `cut_list.py` (time
cut, retakes removed, fillers left in) and ask the user to check every retake. Make the
changes they ask for.

### 5. Finish

- **B-roll** where the script has `[B-ROLL: ...]`: the user's own footage first; else
  short cutaways from `video_generate` or `image_generate`, matched to the shot with
  `read_timeline_frames`, on a lane added above the talking head. Note every
  realistic AI-made person, place or event for the disclosure in step 6.
- **Subtitles:** the captions from `cut_list.py` as text clips on the captions lane;
  keep `captions.srt` for YouTube.
- **Music and sound effects:** the user's own licensed tracks, or `music_generate`
  (instrumental, under the voice) and `audio_generate` for effects. Never a
  commercial song they do not hold a licence for.
- **Thumbnails:** three variants with `image_generate` (prompt in
  `references/templates.md`), 16:9, in the style of their last 6 thumbnails, using a
  real frame from `read_timeline_frames` as the reference for the creator's face.
  Each must show what the video delivers.
- **Metadata:** 3-5 title options, a description and chapters (from the cut's section
  starts). Check them with
  `python3 "${COMPUTER_SKILL_DIR}/scripts/publish_kit.py" --file kit.json` and fix
  anything in `problems`. Put the result in the Google Doc.
- **Shorts:** choose 2-3 self-contained 20-50 second moments from the cut (rules in
  `references/templates.md`) and write their start and end times.

Ask the user to export the finished video from the editor. Then rework the same
timeline into each Short (vertical 1080x1920, captions on) and have each exported in
turn, so the long video is never lost.

### 6. Schedule

Ask for the upload day, time and time zone if missing, put them in `kit.json` and run
`publish_kit.py` again for the exact UTC publish times of the video and the Shorts.

**Stop.** Show the confirmation summary from `references/templates.md`: the final
file, chosen title, thumbnail, description with chapters, tags, publish time (local and
UTC), each Short and its time, the reel and its caption, and whether the "altered or
synthetic content" disclosure applies. Upload nothing until the user confirms all of
it.

Then, through the YouTube connector: upload the video as **private with a scheduled
publish time** (never public now unless the user says so), set the thumbnail, upload
`captions.srt`, and set the altered-content flag if the connector offers it; if it
does not, tell the user to tick it in YouTube Studio before the publish time. Upload
and schedule each Short the same way. If the connector cannot schedule, upload as
private and give the user the exact time to set in YouTube Studio.

Instagram cannot schedule through the connector (it posts at once). Deliver the reel
file and caption with `publish_artifact` for the user to schedule in Instagram, or
post it through the Instagram connector only if the user says "post it now".

## Automation (offer at the end, never set up unasked)

Offer this, and create it with `cronjob` (`action: create`, `skills` set to this
skill's name as you loaded it) if the user accepts. Cron runs have no one to ask, so
the prompt must be self-contained and must not upload, post or change anything:

- **7 days after each video goes live:** pull its retention curve and the channel's
  average from the YouTube connector, run `retention_report.py`, and reply with the
  retention report (template in references): where viewers dropped and what was on
  screen there, how it compares with the channel average, and the next three topics
  from steps 1-2 with their evidence links.

## Guardrails

- The script must sound like the user; they edit and approve it before recording.
- Use only music, footage and images the user has the rights to: their own, licensed
  (Splice, stock they hold), or generated with the built-in music tool.
- Set YouTube's "altered or synthetic content" disclosure when the video includes
  realistic AI-made people, places or events. Never clone the creator's or anyone
  else's face or voice without written consent.
- Thumbnails and titles must match what the video delivers; no misleading claims or
  fake reactions to things that do not happen in the video.
- Schedule, never publish straight away, unless the user says so. Nothing is uploaded
  or posted before the step 6 confirmation.
- No promises of views, subscribers or revenue in scripts, titles or reports.
- Every number and question comes from a tool result with its source; script
  outputs are the only source for scores, cuts, chapter times and publish times.

## Pitfalls

- **Inventing analytics or audience questions.** If YouTube or web tools are not
  available, stop and report it; never write "people often ask..." without a link.
- **Writing in a generic YouTube voice.** Re-read the voice profile before writing;
  match sentence length and signature phrases, and keep the user's sign-off.
- **Trusting retakes blindly.** `cut_list.py` keeps the last take of a repeated line;
  ask the user to check each one at the step 4 Stop.
- **Losing the long cut.** The editor holds one timeline per chat: export the finished
  video before reworking the timeline into Shorts.
- **Wrong publish time.** Always pass the user's time zone to `publish_kit.py`;
  daylight saving shifts UTC by an hour.
- **Uploading as public.** Set private plus the scheduled time; check the connector's
  response shows the scheduled status.

## Verification

- The topic sheet has 10 rows, each with at least one evidence link or "YouTube
  Analytics", and scores that match `rank_topics.py`.
- The rough cut's length equals `result_seconds` from `cut_list.py`, and the user
  checked the retakes.
- `publish_kit.py` reports no `problems` for the chosen title, description, tags and
  chapters.
- YouTube shows the video and each Short as scheduled (private) at the confirmed UTC
  times, with the chosen thumbnail and captions.
- The user received the reel file and caption, or confirmed it was posted.
