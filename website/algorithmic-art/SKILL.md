---
name: Generative Art Studio
description: >
  Makes original generative art as a live, interactive page: change the seed, tweak sliders and colours, save a PNG.
  Use it for "make generative art", "algorithmic art", "a flow field", "a particle animation", "art from code", "a p5.js sketch", "album art that moves", "a piece I can re-seed until I like it".
  Not for photos or illustrations from a text prompt.
---

# Generative Art Studio

A good result is an original piece of generative art that opens in the chat as a live page. It looks finished the moment it loads, the same seed always draws the same picture, and the user can change the seed, the settings and the colours, and save a PNG. The art comes from an algorithm (noise, particles, forces, geometry), not from an image.

Do the whole job in one reply. Never ask a question first. If the request is thin, choose the subject, mood and palette yourself and say what you chose.

## Step 1: Read the request

Note the subject or feeling, any colours the user named, whether it should move, and the format. A square 1200 x 1200 canvas suits album art and avatars, 1600 x 900 suits a wallpaper or banner, and square is the default. If the user names a living artist or a specific artwork, take only the general technique, say so in one line, and make the piece original.

## Step 2: Write the philosophy

Name the piece in one or two words ("Organic Turbulence"). The name is the page title and the heading of your reply. Write three to five sentences: what the system is made of, how it moves, and what emerges. Say it through computation (noise fields, particles, forces, recursion, interference, seeded variation), not as a picture, and mention each idea once. Describe the process, never how the finished picture looks: you have not seen it, so say nothing about where colours land or what it resembles. It steers the algorithm and goes at the top of your reply.

If the request names no technique, or you are unsure where to start, read `references/movements.md` and take a direction from it. It also holds palette starting points.

Then find the conceptual thread: one real idea from the request that shapes a rule, a parameter or the palette instead of appearing literally (for ocean currents, a slow tide-like drift in the noise field). Someone who knows the subject should feel it, and everyone else just sees a good piece. Let the philosophy hint at it and do not explain it separately.

## Step 3: Write the sketch and the spec

Read `templates/generator_template.js` first (`skill_view` with that file path). It shows what the sketch must define, the rules that keep the page working, and helpers to copy. Run `mkdir -p /tmp/.scratch/algorithmic-art`, then write two files there.

**`sketch.js`** is the p5.js code. It defines `initializeSystem()` (seed first, then rebuild everything) and, for an animated piece, `draw()`. A static piece has no `draw()` and draws everything in `initializeSystem()`. It reads `params.seed`, `params.<slider id>` and `params.colorPalette[i]`. It has no `setup()` and no `createCanvas()`: the page supplies both.

**`spec.json`** lists the page's controls, as strict JSON. This example only shows the shape: write your own title, subtitle, sliders and colours for this request.

```json
{
  "title": "Lantern Field",
  "subtitle": "Sparks rise and fade over a dark field.",
  "seed": 2718,
  "canvas": [1200, 1200],
  "params": [
    {"id": "sparks", "label": "Number of sparks", "min": 200, "max": 3000, "step": 100, "value": 1200},
    {"id": "rise", "label": "Rise speed", "min": 0.2, "max": 3, "step": 0.1, "value": 1, "live": true}
  ],
  "colors": [
    {"label": "Background", "value": "#140a0a"},
    {"label": "Ember", "value": "#c0392b"},
    {"label": "Glow", "value": "#f6b93b"}
  ]
}
```

- `seed` is any whole number from 1 to 999999. It is the seed the piece opens on. `canvas` is optional.
- Offer four to eight sliders in `params`, plus every setting the user asked for. `id` is a plain word (letters, digits, underscore). `value` is the best-looking setting and must sit on the slider grid (min plus a whole number of steps). Set `"live": true` only for a slider the sketch reads every frame and that needs no rebuild, such as speed.
- Offer three to six `colors`. The first is normally the background.

What makes the sketch good:

- **Palette**: three to six colours that belong together, such as one hue family plus one contrasting accent. No pure black or white, no random RGB.
- **Composition**: layer broad calm structure with fine detail. Vary size, weight or opacity by something meaningful (speed, age, distance). Leave a margin or a focal area so the piece reads as composed rather than noisy.
- **Visible marks**: soft trails come from laying a low-alpha wash of the background over the last frame (alpha 10 to 30), but the marks themselves must be clearly visible: stroke alpha of at least 80 or opaque, and never below 40 except for halos. `blendMode(ADD)` makes single marks dim, so use it only on a dark background with every mark at alpha 60 or more. A faint or nearly empty picture is the most common failure, and it is not finished.
- **Settings**: sliders change the character of the piece (counts, scales, speeds, probabilities, thresholds). Every combination inside the ranges must still look good. Never add a slider the sketch ignores.
- **Motion**: slow and continuous. A piece meant to flow keeps running, and the Pause button freezes it. A piece that builds up a picture can settle: call `noLoop()` inside `draw()` when it is finished.
- **Seeds**: all randomness comes from `random()`, `noise()` and `randomGaussian()` after `randomSeed(params.seed)` and `noiseSeed(params.seed)`. Keep your own `tick` counter and reset it in `initializeSystem()`.
- **Weight**: at most about 5,000 moving elements at 1200 x 1200, and no full-canvas `loadPixels()` every frame. `initializeSystem()` runs again whenever a slider is released or a colour changes, so keep it quick: no warm-up of more than about 30 frames.
- **Care**: choose every number on purpose (counts, scales, alphas, speeds, line weights) and balance density against empty space. A piece that is too sparse, too noisy or all one colour is not finished.

## Step 4: Build the page

The `skill_view` result that loaded this skill has `skill_dir`, the skill's folder in the sandbox (call `skill_view` on this skill again if you no longer have it). Use it in place of `SKILL_DIR` below. If it gives no path, find `build_art.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/build_art.py --spec /tmp/.scratch/algorithmic-art/spec.json --sketch /tmp/.scratch/algorithmic-art/sketch.js --out /tmp/.scratch/algorithmic-art/<piece-name>.html
```

Use a meaningful file name such as `tidal-drift.html`. The script checks the spec and the sketch (syntax, seeded randomness, every slider is read, no `setup()`), then fills `templates/viewer.html` to make one self-contained page with the seed box (Go, Prev, Next, Random), your sliders and colour pickers, and Regenerate, Reset, Pause and Download PNG. If it prints ERROR lines, fix the file it names and run it again. Fix any WARNING it prints too. Do not edit the built HTML by hand.

The script then loads the page in a headless browser, when the sandbox has one, and prints one RENDER line. If it says RENDER PROBLEM, change the sketch as the line says and run the script again, at most twice. A RENDER NOTE or a skipped check needs no action.

## Step 5: Publish

Publish the built file with `publish_artifact`, kind `html_preview`. It shows live in the chat.

## Step 6: Reply

First reread your philosophy against `sketch.js` and change any sentence the code does not do (do not mention depth if nothing uses depth, or a tide if nothing drifts). Then reply in this shape, under about 250 words, with no code:

```
**<Piece title>**
<three to five sentences of philosophy>

Published above as a live preview: <file name>.

How to use it:
- Seed: type a number and press Go, or use Prev, Next and Random. The same seed always draws the same picture. It opens on seed <N>.
- Settings: <each slider and what it changes, a few words each>.
- Colours: <each picker and what it colours>.
- Regenerate replays the current seed, Reset returns to the opening look, Pause freezes the frame, and Download PNG saves the picture (if the preview blocks the download, right-click the picture and choose Save image).

Assumptions: <anything you decided that the user did not say: size, theme, palette, motion>.
```

For a static piece leave out the Pause mention. If the user asks for "a few variations", say that every seed is a different variation and point to Prev, Next and Random.

## Rules

- The deliverable is the one published HTML page. Do not give the user separate `.md` or `.js` files, and do not paste the sketch into the reply.
- Never ask a question before making the piece. State assumptions at the end instead.
- The only outside thing the page loads is p5.js 1.7.0 from its CDN. No other libraries, images, fonts or network calls.
- Original work only: never copy a living artist's style or a named artwork.
- Do not say you watched the piece run or tested it in a browser. In the reply, claim only what the sketch does and what you decided: for example, do not promise that a light background or other colours will look good.
