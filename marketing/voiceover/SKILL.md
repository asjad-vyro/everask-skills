---
name: Voiceover Producer
description: >
  Turns a script, a brief or a video into a finished voiceover. Rewrites the
  text so it sounds natural read aloud, fits it to the time you have, casts a
  voice that suits the job, gets names and numbers said right, and delivers
  one consistent MP3 or WAV at the right loudness, laid onto your video if you
  want. For ads, explainers, product demos, narration, training, phone menus
  and other languages. Use it for "make a voiceover", "narrate this script",
  "text to speech", "voiceover for my video", "read this in a British accent"
  or "record this ad read".
---

# Voiceover Producer

Make a voiceover that sounds directed, not just read out: a voice that suits the job, a natural pace, every name said correctly, and a length that fits.

Most weak voiceovers go wrong before any audio is made. The script was written to be read rather than heard, the voice doesn't fit the brand, or there are too many words for the time, so the read is rushed. Fix those first, then generate, then check what came back.

Work in `/tmp/.scratch/voiceover/` in the sandbox. Only the finished files go to the user.

## Step 1: Get the brief

Settle these from the message and any files:

- **The words**: a finished script, notes to turn into one, or a video to narrate.
- **The job**: an ad, explainer, product demo, documentary narration, training course, phone menu or podcast intro.
- **The length**: a time limit, or the video it has to fit. For a video, download it, measure it with `ffprobe`, and ask `media_analyze` for its scenes with start times, so each line can land on its scene.
- **The voice**: gender, age, accent and tone, or a voice the user named.
- **The language**, and the names, brands and terms that must be said a certain way.
- **The file**: MP3 by default, WAV if it's going into a video editor.

Ask a question only if there's nothing to read and no topic to write about. Otherwise make the calls yourself and state them.

## Step 2: Write it for the ear

Rewrite the script so it sounds natural aloud. Keep its meaning, its claims and any wording the user needs exactly (prices, offers, legal lines).

- **Short sentences** of 10 to 20 words, one idea each, with contractions.
- **Numbers as they should be said**: "twenty-nine ninety-nine", "March the third", "five thousand". Digits are read unpredictably.
- **Abbreviations**: write letters that are spelled out with hyphens ("A-P-I"), keep words said whole as they are ("NASA"), and expand the rest ("for example", not "e.g.").
- **Links and handles**: say them simply ("acme dot com slash start"), or leave them to the screen.
- **Hard names**: respell them the way they sound ("Siobhan" becomes "Shiv-awn"), and keep a list of every respelling. With ElevenLabs v4 you can write the IPA between forward slashes instead.
- **Pauses**: a comma is a short pause, a full stop a longer one, and a new paragraph longer still. Don't use "..." for a pause, since it can come out as a sound. For an exact gap, generate the parts separately and set the silence when joining (Step 5).
- **Emphasis**: put the key word at the end of its sentence, where the voice lands naturally.

Then check the length. Count the words with `wc -w` in the sandbox, rather than estimating, and divide by the pace:

| Delivery | Words per minute | 15 seconds | 30 seconds | 60 seconds |
|---|---|---|---|---|
| Calm: technical, meditation, luxury | 120 to 130 | 30 words | 60 words | 125 words |
| Conversational: explainers, demos | 145 to 155 | 37 words | 75 words | 150 words |
| Energetic: ads, promos | 165 to 180 | 42 words | 85 words | 170 words |

If the script is too long for its slot, cut words. Don't plan to speed the voice up; a rushed read sounds worse than a shorter script.

## Step 3: Cast the voice

Pick the model:

- **Inworld TTS-1.5 Max**, the default: natural, and much cheaper per character. Right for almost everything.
- **ElevenLabs v4**: when the user names an ElevenLabs voice, wants the delivery steered with audio tags such as `[whispering]` or `[excited]`, or needs a word said exactly, written as IPA between forward slashes. It costs about eight times as much per character.

Then pick one voice that suits the job, and say why in a line. Pass Inworld voices with their language code, as in `Ashley (en)`:

| Job | Inworld voices |
|---|---|
| Brand, explainer, product demo | Ashley (warm), Lauren (confident, upbeat), Brian (friendly), Nate (conversational) |
| Corporate, training, finance | Derek (steady), Elizabeth (professional), Simon (articulate), Anjali (Indian English, professional) |
| Documentary, premium brand | Graham (British, authoritative), Elliot (calm), Deborah (warm, calm) |
| Ad, promo, trailer | Carter (announcer), Timothy (lively), Tessa (Australian, upbeat), Rupert (British, commanding) |
| Tech explainer | Tyler (authoritative), Ethan (precise), Jason (clear) |
| Meditation, sleep, wellness | Luna, Serena, Gareth, Celeste (whispery) |
| Phone menu, support | Kelsey (reassuring), Evan (friendly), Derek |
| British | Olivia (young, friendly), Clive (calm), Craig (older, refined), Wendy (posh) |
| Australian, Indian English, US South | Pippa, Callum, Hamish; Saanvi, Arjun, Priya; Loretta, Hank |

For other languages, Inworld has Spanish `Diego (es)`, `Miguel (es)`, `Lupita (es)`; French `Alain (fr)`, `Mathieu (fr)`, `Hélène (fr)`; German `Josef (de)`, `Johanna (de)`; Italian `Gianni (it)`, `Orietta (it)`; Portuguese `Heitor (pt)`, `Maitê (pt)`; Dutch `Lennart (nl)`, `Lore (nl)`; Japanese `Satoshi (ja)`, `Asuka (ja)`; Korean `Seojun (ko)`, `Minji (ko)`; Chinese `Yichen (zh)`, `Xinyi (zh)`; Russian `Nikolai (ru)`, `Elena (ru)`; Hindi `Manoj (hi)`, `Riya (hi)`; Arabic `Omar (ar)`, `Nour (ar)`; Hebrew `Oren (he)`, `Yael (he)`; and Polish `Szymon (pl)`. For any other language, use ElevenLabs v4.

ElevenLabs v4 voices include George (warm, British), Daniel (authoritative, British), Lily (warm, British), Alice (confident, British), Bill (older, American), Matilda (friendly, American), Jessica (expressive, American), Laura (upbeat, American), Will (friendly, American) and Charlie (Australian).

- `media_models` with `category: "tts"` shows the models and settings available now. If a voice name is rejected, choose another from these lists; don't retry the same name.
- Keep one voice per speaker for the whole job, on one model.
- For anything over about a minute, or an ad that will run as paid media, first make a 10-to-15-second sample in two or three voices and let the user choose, unless they named a voice.

## Step 4: Generate

Call `audio_generate` with `text` and `voice`, plus `model: "ElevenLabs v4"` if you chose it.

- **Up to about 1,500 characters** (roughly a minute and a half): one call, even when the read will be cut into scenes later. One read keeps the pace and the voice even, and each call adds a card to the chat.
- **Longer scripts**: split at paragraph ends into parts of at most 1,500 characters. Generate every part with the same model and voice, and keep them in order (`part01`, `part02` and so on).
- **Several speakers**: generate each line in its speaker's voice, in order.
- **Audio tags** work on ElevenLabs v4 only. Put the tag just before the words it colours, as in `[whispering] Don't tell anyone.`, and use a few, where the delivery matters. Leave tags out of Inworld scripts, which may read them aloud.

Each call returns an audio URL. Download every part into the sandbox with `curl -L -o part01.mp3 URL`.

If the call is refused because the user's plan doesn't include voice generation, still give them the final script, the respellings and the voice you'd use, so the work isn't lost.

## Step 5: Join and finish

Trim each part's edges, join the parts with set pauses, and even out the loudness:

```bash
cd /tmp/.scratch/voiceover
TRIM="silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
for f in part*.mp3; do ffmpeg -y -loglevel error -i "$f" -af "$TRIM" -ar 48000 -ac 1 "${f%.mp3}.wav"; done
# 0.6 s between paragraphs; use 1.2 s between sections
ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=48000:cl=mono -t 0.6 gap.wav
: > list.txt
for f in part*.wav; do [ -s list.txt ] && echo "file 'gap.wav'" >> list.txt; echo "file '$f'" >> list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c:a pcm_s16le joined.wav
ffmpeg -y -loglevel error -i joined.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -ac 1 voiceover.wav
ffmpeg -y -loglevel error -i voiceover.wav -c:a libmp3lame -b:a 160k voiceover.mp3
```

Set the loudness (`I`) for where it will be heard: −16 LUFS for voice on its own or a podcast, −14 for social and YouTube video, and the broadcaster's own figure (usually −23 or −24) for TV and radio.

**Timed to a video's scenes**: write one paragraph per scene and generate them as one read. Cut the read at the pauses between paragraphs, then start each piece at its scene's time. Check that each piece ends before the next scene starts; if one runs over, shorten that paragraph and generate the read again.

```bash
# The pauses between paragraphs: each silence_end is where the next one starts
ffmpeg -hide_banner -nostats -i read.mp3 -af silencedetect=noise=-40dB:d=0.4 -f null - 2>&1 | grep -E 'silence_(start|end)'
# Cut the read at those times, for example
ffmpeg -y -loglevel error -i read.mp3 -af "atrim=0:5.3,asetpts=N/SR/TB" -ar 48000 -ac 1 part01.wav
ffmpeg -y -loglevel error -i read.mp3 -af "atrim=6.1:11.4,asetpts=N/SR/TB" -ar 48000 -ac 1 part02.wav
ffmpeg -y -loglevel error -i read.mp3 -af "atrim=12.2,asetpts=N/SR/TB" -ar 48000 -ac 1 part03.wav
# Then place them: part01 at 0 s, part02 at 6.4 s, part03 at 14.2 s, in a 30-second video
ffmpeg -y -loglevel error -i part01.wav -i part02.wav -i part03.wav -filter_complex \
  "[1:a]adelay=6400:all=1[b];[2:a]adelay=14200:all=1[c];[0:a][b][c]amix=inputs=3:duration=longest:normalize=0,apad=whole_dur=30,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -ar 48000 -ac 1 voiceover.wav
```

**On the video**: either replace its sound, or keep its sound lowered under the voice. Use the first command if the video has no sound.

```bash
# Replace the video's sound with the voiceover
ffmpeg -y -loglevel error -i video.mp4 -i voiceover.wav -filter_complex "[1:a]apad[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest video-voiceover.mp4
# Keep the video's own sound, ducked under the voice
ffmpeg -y -loglevel error -i video.mp4 -i voiceover.wav -filter_complex \
  "[1:a]asplit[vo][k];[k]apad[key];[0:a]volume=-8dB[bed];[bed][key]sidechaincompress=threshold=0.03:ratio=6:attack=80:release=600[duck];[duck][vo]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 video-voiceover.mp4
```

## Step 6: Check it

- **The words**: publish the finished file with `publish_artifact` (`kind: "audio"`, `as_input: true`) and call `audio_transcribe` with the URL it returns. Compare the transcript with the script: look for missing, repeated or extra words, tags read aloud, and numbers said wrongly. Ignore differences of form, such as "$29.99" against "twenty-nine ninety-nine".
- **The delivery**: ask `media_analyze` about the file: whether each name on your list is said correctly, whether the pace is even, and whether there are glitches, clicks, odd breaths or a change of voice between parts.
- **Length and loudness**: `ffprobe -v error -show_entries format=duration -of csv=p=0 voiceover.wav` gives the length, and `ffmpeg -hide_banner -nostats -i voiceover.wav -af ebur128=peak=true -f null - 2>&1 | grep -E '^ +(I|Peak):'` gives the integrated loudness (I) and the true peak.

Fix only what failed: respell the word, move the pause or shorten the line, regenerate that part, and join again. If one word still comes out wrong after three tries, tell the user and offer the other model.

## Step 7: Deliver

Publish the final file with `publish_artifact` (`kind: "audio"`), and the video too (`kind: "video"`) if you put the voice on one. Say which file is the finished one, since the parts also appear in the chat. Then reply with:

- the voice and model, the length and the loudness;
- the script as it was read, with the respellings, so the user can change a line and ask again;
- one offer: another voice, a different pace, or the same script in another language.

## What not to do

- Don't change what the script claims, add claims, or reword lines the user needs exactly.
- Don't speed a long read up to make it fit; cut words instead.
- Don't switch voice or model partway through one speaker's lines.
- Don't present a voice as a real person's, or try to imitate a real person.
- Don't show the user scratch files.
