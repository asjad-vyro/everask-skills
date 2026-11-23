---
name: Logo Maker
description: >
  Gives you three distinct logo concepts for your business as PNG images, each with the name spelled exactly, plus colours and fonts to match.
  Use it for "make me a logo", "logo ideas for my shop", "design a logo for...", "I need a brand mark".
---

# Logo Maker

A good result is three clearly different directions, each shown as a finished image with the business name set in real type (so it is spelled exactly), a symbol that fits the business, two or three hex colours and a font suggestion. These are concepts, not final artwork.

## Hard rules

- Write the reply in the language the user wrote in, unless they ask for another. Spell the business name, tagline and any other words exactly as the user gave them, with their accents and capitals, in every image. Never change the case of the name (no all-caps, no lower-casing, no `text-transform`) and never split or abbreviate it, except in the lettermark symbol itself.
- Never imitate an existing brand's logo or ask the image tool for "in the style of <brand>". Never name a real company as inspiration.
- Image models misspell text. The generated image is only the symbol (no letters, no words). The name is always typed in HTML.
- State plainly in the reply: these are concepts as PNG images, not vector files, and trademark availability is not checked.
- Never ask questions first. Decide, state your assumptions, deliver.

## Step 1: Brief

Write the brief in four lines, using only what the user gave, and an assumption (marked) where something is missing:
1. Name exactly as spelled, and tagline if given (no tagline if none given).
2. What the business does and who it serves.
3. The feeling (for example warm, modern, playful, premium): the user's words, or an assumption.
4. Colours to use or avoid: the user's, or an assumption. Never use a colour the user said to avoid.

## Step 2: Three directions

Pick three different directions that suit the brief, for example:
- **Symbol mark**: one simple picture that stands for the business, name beside it.
- **Lettermark**: the first letter or two inside a simple shape (the letter is typed in HTML on top of a plain shape image, or use a plain shape image plus the letter in the lockup).
- **Emblem**: the symbol inside a badge, circle or shield shape, name below.
Give each a short name of its own, a different symbol idea and a different arrangement and colour balance (the colours still come from the user's palette if given).

For each direction decide: 2 or 3 hex colours (main, accent, optional light) and a font style as a generic family only (for example "a rounded sans-serif", "a classic serif", "a bold geometric sans"). Do not claim any specific font is installed.

## Step 3: Make the symbols

Call `image_generate` three times, one per direction, with top-level parameters only. Prompt shape (fill the angle brackets):

`Flat vector style logo symbol, <the symbol idea>, <colours in words>, simple bold shapes, plain white background, centred with margin, no text, no letters, no words, no mock-up, no shadow`

For the lettermark direction ask only for the shape (for example a rounded square or circle) and no letter.

Check each image once with `media_analyze` for any letters, words or stray text and for a white background. If an image has text, regenerate it once with the same prompt plus "absolutely no text". If it still has text, keep it and say so in the reply. Copy each result to `/tmp/.scratch/logo-maker/symbol-1.png`, `symbol-2.png`, `symbol-3.png` (use `terminal` with `cp`, or `curl -L -o` if the tool returned a URL). If a generation fails after one retry, use a plain SVG shape of your own for that direction (a circle, rounded square or leaf-like path) and say so.

## Step 4: Build the lockups

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox; use the full path where it says `SKILL_DIR`. If it gives no path, find `lockups.html` under `~/.computer/skills` with `search_files`.
2. Read `SKILL_DIR/templates/lockups.html` with `read_file`.
3. Write `/tmp/.scratch/logo-maker/page.html` with `write_file`: the template with three `<section class="lockup">` blocks, ids `l1`, `l2`, `l3`, each with:
   - the `--c1`, `--c2`, `--bg` values in its `style` set to that direction's colours;
   - `<img src="symbol-N.png">` for its symbol;
   - the name exactly as given in `.name` (if the name is longer than 14 characters, add `style="font-size:72px"` to `.name`; if longer than 22, add class `stacked` to `.stage` too). The tagline in `.tag`, or delete that `div` if there is none;
   - the colour dots: set each `background` and each `#HEX` text to the direction's real hex values (delete a third dot if only two colours);
   - the label "Concept N: <direction name>" in the user's language.
   Set `lang` and `dir` on `<html>` (`rtl` for Arabic, Hebrew, Persian, Urdu).
4. Run: `python3 SKILL_DIR/scripts/render_lockups.py /tmp/.scratch/logo-maker/page.html /tmp/.scratch/logo-maker/out`. It finds headless Chrome (on PATH or under `/root/.cache/puppeteer` or `/root/.cache/ms-playwright`) and writes `lockup-01.png` to `lockup-03.png` (1200 x 900), printing OK or WRONG SIZE for each. Never install a browser or a PDF package (no playwright, puppeteer, weasyprint, no pip or apt installs). If it prints CHROME NOT FOUND, publish `page.html` as `html_preview` and also the symbol PNGs themselves, say the name is not set on them, and continue.
5. Look at one lockup with `media_analyze`: is the name spelled exactly as given and fully visible? Fix `page.html` once if not and re-run.

## Step 5: Publish and reply

1. Publish each lockup with `publish_artifact`, `kind: "file"`, named `<business>-logo-concept-1.png`, and so on.
2. Reply in the user's language with this shape:
   - **Brief**: the four lines, assumptions marked.
   - For each concept: its name, one sentence on the idea and why it fits, the hex colours, the font suggestion (generic family).
   - One line recommending which concept to start from and why.
   - The plain statement: these are PNG concepts, not vector files, and trademark availability is not checked.
   - One line offering changes ("other colours", "different symbol", "bigger name").

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. For a colour, text or layout change, edit `/tmp/.scratch/logo-maker/page.html` and re-render with the same script; regenerate a symbol with `image_generate` only if the user asks for a different symbol, and only for that concept. Publish the changed PNGs under the same names and say in one line what changed.
