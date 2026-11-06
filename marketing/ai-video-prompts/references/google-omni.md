# Google Omni Flash 1.1

Use it for clips that contain design (on-screen text, titles, lower thirds, hand-drawn looks and motion graphics) and for changing an existing clip by instruction. For cinematic hero shots, or anything longer than it allows, use Seedance or Kling.

## New clips

- Write prose covering the scene, camera, light, motion and sound, in about 40 to 100 words.
- It may cut on its own. For one take, write "a single continuous shot, no cuts".
- Time the beats with ranges: `[0-3s] the title "SPRING SALE" draws on in white brush strokes; [3-6s] the camera drifts right to the product`.
- On-screen text renders well. Quote it exactly, keep it short, and give it time to be read: about a second for each word on screen.
- It always makes sound, so direct it: "light acoustic guitar, no voice".
- There's no negative prompt, so write exclusions as sentences: "No people appear."
- In EverAsk, cite references as `#Image1` and `#Video1`, counting from one, in the order they're passed, and say what each is: the product, the character, the style or the background.

## Changing a clip

Pass the clip as `video_url` and keep the instruction short:

- Name only the change, and end with "Keep everything else the same."
- Make one change per pass: the light, then the camera, then the action, then the sound.
- Say the result, not the method: "make the phone invisible", not "mask the phone and fill in the background".
- Don't describe the scene again, which invites other changes.
- It's good at restyling, relighting, adding or removing a prop, changing the words on a sign, and changing the weather or season.
- Chain edits: each pass's result is the input for the next.

## Limits

- Speech is most reliable in English.
- Very short reference clips (3 seconds or less), or several input clips at once, give poor results.
- Some recognisable people, and children, are blocked.

## Fixing misses

| Problem | Fix |
|---|---|
| Unwanted cuts | "A single continuous shot, no cuts" |
| An edit changed other things too | A shorter instruction that names only the change, ending "Keep everything else the same." |
| "Make it move" did little | Name the motion: "the leaves sway to the left as the camera drifts right" |
| Text misspelled | Shorter text, in quotes, with more time on screen |
