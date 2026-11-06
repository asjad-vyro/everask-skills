# Seedance 2.5

Seedance is the model for the finished piece: cinematic motion, believable physics, and long takes of up to 30 seconds in one generation, with its own sound and lip-synced dialogue. It can cut between several shots in one generation. It is slow and costs the most per second, so draft on MiniMax H3 Max first when the user is still exploring.

Its weak spots are faces that drift between shots, extra people who appear from nowhere, and a plastic, computer-generated look when the prompt doesn't fix the style.

## Structure

Write the prompt in labelled sections, in this order. Always keep Style, Shots and Audio; use the others when the scene needs them.

1. **Style**: genre, era, film stock or grade, as in "1990s documentary on 16mm film, muted greens, natural grain, real photography".
2. **Scene**: one sentence on what happens.
3. **Characters**: each person's fixed description, word for word from the continuity sheet. State the count: "exactly two people in the frame".
4. **Location**: the place, time of day and weather, and landmarks that stay in place.
5. **First frame**: what the opening frame shows and where each person stands, as in "the courier on the left third, facing right; the door on the right".
6. **Shots**: one line each, as in `Shot 1 (0-4s): medium shot, she unlocks the door. Hard cut.` For one take, write "One continuous shot, no cuts."
7. **Camera**: one move per shot, written as a plain instruction ("slow dolly in", "locked-off tripod, no zoom"), and the lens by focal length ("35mm", "85mm").
8. **Physics**: how things move and react, such as wind direction, cloth, liquid and weight. Changes only move forward: wet stays wet, and broken stays broken.
9. **Light**: the source and its direction.
10. **Audio**: the ambience, sound effects with their timing, and dialogue. Music is usually better added in the edit, so write "natural sound only, no music" unless the user wants music.

## Shots and length

- In a multi-shot prompt, shots of 2 to 5 seconds cut cleanly.
- When the scene is continuous, use one long generation rather than stitching clips together.
- Give each shot one action and one camera move.

## Dialogue and voices

- Write dialogue as `The courier says: "Sign here, please."` and keep each line short: about 6 words on fast cuts, and 10 at most.
- Describe each speaker's voice once, in a fixed sentence (age, accent, pace and manner), and repeat it word for word wherever they speak.
- Singing and long speeches are unreliable.

## References

- In EverAsk, cite references in the prompt as `@Image1`, `@Image2` and `@Audio1`, counting from one, in the order they're passed. The `video_generate` tool's description has the current limits.
- Give each reference one job, and say what it is: "@Image1 is the courier's face; @Image2 is the red bike."
- For a face, use a front-on, evenly lit photo with nothing covering it, and reuse the same photo in every shot.
- To carry a character into the next clip, pass the previous clip as a reference rather than chaining last frames, which carries any drift forward.

## Fixing misses

| Problem | Fix |
|---|---|
| Faces change between shots | Repeat the character description word for word, add "the same person throughout, no change to the face", keep only the steadiest references, and use longer shots |
| Extra people appear | State the count: "exactly two people in the frame" |
| The place changes between shots | Name fixed landmarks and positions in the frame, and keep the direction of movement ("moving left to right") |
| A plastic, computer-generated look | Name the medium: "real photography, 35mm film, natural skin texture, not 3D, not cartoon" |
| A "no ..." is ignored | Say what should be there instead |
| An unwanted cut | "One continuous shot, no cuts" |
| A camera move you didn't ask for | "Locked-off camera, no zoom, no dolly" |

Change one thing per retry, and judge the whole clip, not a single frame.
