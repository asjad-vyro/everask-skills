---
name: Songwriter
description: >
  Writes an original song with real structure, rhyme and a hook, then makes it into a finished sung track with AI music.
  Use it for "write a song about my dog", "a birthday song for my sister", "write lyrics for a sad country song",
  "turn this poem into a song", "make a jingle for my shop", "write a chorus", "rewrite my lyrics".
  It writes lyrics only, with no audio, when that is all the user asks for.
---

# Songwriter

A good result is a song someone could sing today: one clear idea, a hook that sticks, verses that each add something new, lines that scan when read aloud and, when the user wants to hear it, a finished sung track that fits the mood. Every word is original: never copy lyrics from an existing song.

Work from what the user gave. Never open with questions: when something is missing, decide it and say in the reply what you assumed.

## Step 1: Decide the job and the brief

Pick the job from the request:

- **Song** ("write a song", "a song for...", "a jingle", "make it", "generate it", "turn this into a song"): write the lyrics and make the track in this same reply.
- **Lyrics only** ("write lyrics", "the words", "a chorus", "a verse", "rewrite my lyrics", or any request for no audio): write the lyrics and do not call `music_generate`.
- **The user's own words** (a pasted or attached poem, draft or lyrics): those are the lyrics. Whether to make a track follows the same two rules above.

Then settle the brief. Take each point from the message and decide any the user left open:

- **Idea**: the topic, occasion, story or feeling. With none, pick a simple, universal one (a road at night, a fresh start) and say so.
- **Details**: use the names, places, hobbies and jokes the user gave. Scenery, objects and plain exaggeration you may make up; what a real person, pet or business did, said, owns or achieved you may not (ages, hometowns, awards, prices, years, "you got us lost", "you say take the long way", "he's on a scent"). Habits, quotes and anecdotes about a named person or pet count as facts unless the user stated them. When the song needs more, write it more generally and say what the user could add for a more personal version. With no name given, write without one and say where it could go. A first-person song is about the user's own life, so narrator details are facts too: family members, pets, rent or leases, jobs, months and dates. Leave them out or keep them general ("the house", "this spring"). Any you keep must be listed under **Assumed**.
- **Genre and mood**: the user's words, or what suits the occasion. A named artist or song ("like Johnny Cash") becomes genre, era, instruments and mood. Never put the name in the lyrics or the style prompt, and never reuse the song's lines.
- **Length**: the user's, else about 2 minutes (a jingle: 30 seconds).
- **Language**: the user's own.

## Step 2: Plan the shape

Size the song to its length. One sung line takes roughly 4 seconds, and a Chorus that comes back counts every time it is sung.

| Length | Sections, and nothing else | Sung lines, repeats counted |
|---|---|---|
| 15 to 30 seconds (jingle) | Chorus with the hook first, one short Verse, Chorus | 6 to 8 |
| 45 to 90 seconds | Verse, Chorus, Verse, Chorus, Outro of 2 lines; no Bridge, no Pre-Chorus | 14 to 20 |
| 2 to 3 minutes | Verse, Pre-Chorus, Chorus, Verse, Pre-Chorus, Chorus, Bridge, Chorus | 26 to 36 |

The top of each range is a limit, not a target: too many lines for the length risk a rushed or cut-off ending. For a longer song add a Verse and a Chorus for each extra minute or so. Folk and storytelling songs may drop the chorus: 3 to 5 verses, each ending on the same refrain line.

Before writing, fix the hook: 2 to 6 words, usually the title, that carry the song's feeling.

## Step 3: Write the lyrics

Read `references/craft.md` now. It has the rhyme and meter techniques, how to use the user's own words, parody and "in the style of" requests, jingles, rap, other languages and chords. Then write:

1. Put the hook in the Chorus, in its first or last line, and bring it back in the last Chorus.
2. Write the Chorus as four short, simple lines, and write it out in full every time it returns.
3. In the verses use things you can see or hold, not feelings stated flat ("your hoodie's still on the hook by the door", not "I was sad"). Verse 2 moves the story on and the Bridge turns it.
4. Mix perfect and near rhymes, and never twist the word order to hit a rhyme.
5. Keep lines singable: usually 6 to 10 syllables, never more than 12, and parallel lines within two syllables of each other. Split a long thought into two lines. Read each line aloud in your head and fix any stumble.
6. Skip stock phrases ("heart of gold", "tears like rain") unless a detail earns them.
7. For puns and jokes, put the punchline on the rhyme word at the end of the line.

Format the lyrics for the singer:

- Put a label in square brackets on its own line before each section: `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`. No numbers in labels.
- Under each label, the sung words only, one line per line. Write every repeat out: no "x2", no "(repeat)", no stage directions, no markdown, no emoji.
- Numbers as words ("thirty"), acronyms letter by letter ("A-I"), and a hard name respelled as it sounds ("Siobhan" as "Shi-vawn"). Say in the reply which names you respelled.
- Keep it under about 3,000 characters.

Then check the draft and fix it without showing the check. Count every sung line, repeats included, and cut until the total is inside the Step 2 range (cut a Bridge, a Pre-Chorus or verse lines before the hook). Then go line by line:

- Count syllables one word at a time and split or trim any line over 12. Count lines with a comma or two clauses twice, because these are the lines that run long ("Happy birthday, happy trail, the sky is wide and blue" is 13 syllables, so trim it).
- Check that the line endings meant to rhyme do rhyme, perfect or near. Fix any that don't.
- Check that every Chorus is the same four lines.
- Check that each pun lands on the last word of its line.

Then confirm that the hook is in every Chorus, every fact came from the user (including narrator details) or is listed under Assumed, and no line echoes an existing song. Find every "you say", "you always", "he does" or "we drive" line about a named person, pet or the narrator. Rewrite it as plain imagery unless the user stated that detail. If you keep it, list it under Assumed. Check that each item on the Assumed line appears in the lyrics as written, with words spelled correctly and puns named accurately.

## Step 4: Write the style prompt

Write 2 to 4 sentences, under 800 characters: genre and mood, era, tempo in BPM, instruments, the voice, how the song builds. A Song job sends it to the music tool; a Lyrics-only job shows it as the Sound line.

```
Weak:   "sad rock song"
Strong: "Slow cinematic country ballad, late-night road mood, 72 BPM. Fingerpicked acoustic guitar, brushed drums, low pedal steel. A weathered female alto with a slight rasp, close and fragile at first, building to a full, aching last chorus, then stripping back to guitar and one voice."
```

- Describe the voice as a person, not a tag: "a warm, cheeky female lead" beats "female vocals". Pick male or female to suit the song unless the user chose.
- Describe the build ("starts sparse, lifts in the second chorus, last line alone"). A song with one flat energy sounds flat.
- Tempo by feel: ballad 60 to 80 BPM, mid-tempo 90 to 110, upbeat pop 115 to 128, dance 120 to 130.
- No artist, band, song or brand names: describe the sound ("90s grunge", "1960s spy-film brass").
- The lyrics do not go in the prompt. They go in `lyrics`.

## Step 5: Make the track (Song job only)

Call `music_generate` once, with top-level parameters only:

```
music_generate(
  prompt="<the style prompt>",
  lyrics="[Verse]\n<line>\n<line>\n[Chorus]\n<line>\n...",
  duration_seconds=90,
  model="MiniMax Music 3"
)
```

- `lyrics`: the Step 3 lyrics exactly as you will show them, with a new line between lines.
- `duration_seconds` and `model`: pass them only when the user gave a length, as seconds. MiniMax Music 3 takes lyrics and sizes a track to an exact length from 1 to 300 seconds, so use it for a length request. If the tool's description does not list it, use another model that lists both lyrics and a length range, and tell the user the length is only a target.
- With no length given, leave both out. The tool then picks its song model, and the lyrics set the length.
- Never pass `options`, and do not pass `instrumental` for a sung song. For a track with no singing, skip the lyrics, pass `instrumental: true` and describe the music.
- The tool's own description of its models is current: trust it over this list, and never pick a model it marks as taking no lyrics.

After the call:

- Read the result. Say "about 90 seconds" only if the result's `duration_seconds` says so; otherwise say what you asked for. Pass on anything in `settings_notes` about length.
- If `success` is false, or the result mentions a plan, credit or payment limit, try once more without `model` if you passed one. If it fails again, stop: give the lyrics, say in one sentence that the track could not be made and why, and offer to try again. Never make the music yourself in code.
- Make one track per request. If the user asks for options, make up to three, changing one thing each (the genre, the tempo or the voice), and say what differs.
- You have not heard the track: describe only what you asked for, never how it sounds. The track appears in the chat as an audio card on its own, so do not paste its URL or publish it again.

## Step 6: Reply

The lyrics go in the reply itself, in full, even if you wrote them earlier in the turn. The reply's first line is `## <Title>`, and the first characters you output are `## `. Read the skill and its files silently, without announcing it. Put no text before it, not even a note about loading the skill or reading files. Add no commentary on your technique: only this shape.

````
## <Title>
<One line: genre, mood, tempo, the length you aimed for>

```
[Verse]
...
```

**Track:** <model name>, <length asked for, or "length follows the lyrics">, <the style in a few words>
**Assumed:** <only what you decided for the user, including any detail you had to guess; leave this line out if nothing>
<One closing line offering a change: another genre, a shorter cut, a different voice, or more details for a more personal version>
````

For lyrics only, replace the Track line with `**Sound:** <the Step 4 style prompt, usable in any AI music tool>` and close with "Want me to turn this into a track?"

If the user asks for changes to a song from earlier in the chat, change only what they asked, show the full new lyrics, and make one new track if there was one before.

## Rules

- Original lyrics only. Do not reproduce or lightly reword lines from an existing song. For the lyrics of a real song, or a parody of one, write a new song on the user's theme and say you did.
- Facts come only from the user. An image or a pun may be invented; a claim about a real person or business may not. This includes the narrator of a first-person song: no invented family, pets, leases or dates unless listed under Assumed.
- The reply starts with the title line, with no preamble, not even "I'll load the skill first".
- No invented quotes, habits or anecdotes for a named person or pet ("you say...", "he always...") unless the user gave them or they are listed under Assumed.
- Lyrics only means no audio call.
- Never ask a question before delivering: decide, and state the assumption.
