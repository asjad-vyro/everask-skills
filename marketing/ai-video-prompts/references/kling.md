# Kling 3.0 Pro and Kling 4.0

Kling handles strong physical motion and stylised and anime looks well. Kling 3.0 Pro renders 3 to 15 seconds at 1080p, with its own sound. Kling 4.0 runs 3 to 30 seconds in one generation, at 720p or 1080p, takes reference images and clips, and can edit an existing clip. Both are optional models in EverAsk, used when the user asks for Kling.

## Structure

- Write plain, direct sentences in this order: subject, motion, scene, camera. Aim for 40 to 100 words.
- Put actions in time order with "first", "then" and "finally".
- Use concrete camera verbs, one move per shot: "the camera tracks alongside her", "slow push in", "crane up to reveal the city".
- Kling 3.0 Pro takes a negative prompt in `negative_prompt`. Keep it short ("blur, distorted hands, extra limbs"), and still describe what you want in the prompt itself.

## From a still

- The still's shape sets the video's shape, so crop it to the target aspect ratio first.
- Describe only the motion; the image already shows the look.
- With a closing frame, describe the movement between the two frames.

## References (Kling 4.0)

- Cite them in the prompt as `@Image1` and `@Video1`, counting from one, in the order they're passed.
- Say which traits must stay the same (face, outfit, logo) and which may change (pose, setting).

## Editing a clip (Kling 4.0)

- Pass the clip as `video_url` with a short instruction: "change the season to winter; keep the people, the camera and the timing the same".
- Make one change per pass.

## Fixing misses

| Problem | Fix |
|---|---|
| Motion too fast or chaotic | Fewer actions and calmer verbs ("slowly", "gently") |
| The wrong camera move | One move, stated plainly, then "the rest of the shot is steady" |
| Lip sync on the wrong face | Keep one clear face in the frame |
| Refused by the safety filter | Change the prompt or the image; the same request fails again |
