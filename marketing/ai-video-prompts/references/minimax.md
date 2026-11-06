# MiniMax H3 Max

EverAsk's default video model: quick and inexpensive, 5 to 15 seconds, up to 768p, with sound made with every clip. Use it for b-roll, social clips, product motion and drafts. For clips longer than 15 seconds or at 1080p, use Seedance; to change an existing clip, use Google Omni Flash.

## Structure

Write one paragraph, in this order: subject, action, camera path, setting, light, sound. Aim for 60 to 120 words.

- **The camera path** is its strength. Describe the move from start to finish: "starts wide on the table, then slowly pushes in to a close-up of the cup".
- **Ask only for the motion the length can hold**: one or two actions in 6 seconds, and three beats at most in 15.
- **Sound** comes with the picture, so describe it: "soft café ambience, and a cup set down on its saucer at 3 seconds". Write "no music" if music will be added later.
- **Text-to-video needs an aspect ratio.** Image-to-video takes the image's shape, so crop the image first.

## From a still

- Image-to-video is faster than text-to-video. Supply the opening frame and describe only the motion; the image already shows the look.
- Pass a closing frame as `end_image_url` for a move from one frame to another, and spend the prompt on what happens between them.

## References

- It takes up to 9 images, 3 clips and 3 audio files (audio up to 15 seconds), 12 files in all. Audio can't be the only reference; pair it with an image or a clip.
- In EverAsk, cite them in the prompt as Image 1, Image 2, Video 1 and Audio 1, counting from one, in the order they're passed, and say what each one is.

## Fixing misses

| Problem | Fix |
|---|---|
| The camera move is ignored | Put the camera sentence earlier, and keep it to one move |
| Too much happening, or rushed motion | Fewer actions, or split the idea into two clips |
| Unwanted music or speech | Say exactly what should be heard: "only wind and footsteps" |
| The look changes from the still | Describe only motion in the prompt, not the subject's appearance |
