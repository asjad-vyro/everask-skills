---
name: Stick Figure Scene
description: >
  Makes a small hand-drawn stick-figure animation for a landing page: a stick
  figure works a little machine or prop that shows what a product does (pulls
  a lever, pins a note, stamps a page). It idles quietly and plays one short
  action on click, hover or scroll into view. Every frame is checked in
  headless Chrome before delivery. You get a live preview page and an embed
  kit with the scene, its runtime and the font. Use it for "make a stick
  figure animation for my landing page", "show this feature as a doodle
  scene", "a little animated explainer for my hero section" or "a crew of
  stick figures that shows what my app does".
---

# Stick Figure Scene

A stick figure in Kamran Ahmed's ink-and-butter style ([stick-scene](https://github.com/nilbuild/stick-scene), MIT) does one job that shows what a product does. The scene idles (breathes, glances, scratches its chin) and plays one 5-8 second action when triggered, then settles back. It is one `<canvas>` inside a `<stick-scene>` element, with no dependencies. The patterns come from ~90 scenes on kamranahmed.info/story: start from them and do not invent a new drawing style.

This skill writes scene files by hand against the rig API, checks them frame by frame in headless Chrome, and ships a self-contained preview plus the files to embed. It does not make videos, GIFs or Lottie files.

## When to Use

- "Make a stick figure animation that shows what my product does", "a little animated doodle for the hero".
- "Show feature X as a scene: someone pulls a lever and ...", "a crew of stick figures for our landing page".
- Adding a scene to a site that already uses `stick.js`, or fixing a scene that glitches.

Not this skill: a narrated explainer video (`whiteboard-animation`), an MP4 or motion graphic (`motion-design`), a Lottie JSON (`text-to-lottie`), a full landing page design (`web-design`; a page from there can embed a scene from here).

## Prerequisites

- `terminal` with `node` (18+) and a Chrome binary. The sandbox image pre-caches chrome-headless-shell under `~/.cache/puppeteer`; `scripts/browser.mjs` finds it, or the one in `$STICK_CHROME`. Nothing is installed: no playwright, no puppeteer, no npm.
- `media_analyze` to look at the contact sheets and page screenshots.
- `publish_artifact` (needs R2) to deliver. If it errors, report the file paths instead.

## How to Run

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox; the scripts are in its `scripts/` folder. Put that path in `SK` in every command below. If `skill_view` gives no path, find `frames.mjs` under `~/.computer/skills` with `search_files`. Work in `/tmp/stick-scene/<id>/`. Every script runs with `node` through `terminal`.

```bash
SK=<skill_dir from skill_view>
W=/tmp/stick-scene/<id>
# contact sheet: the scene frozen at chosen moments, plus any page errors (exit 2)
node $SK/scripts/frames.mjs --scene <id> --src $W/<id>.js \
  --frames "idle:0,idle:2.5,s:0.8,s:1.6,s:2.4,s:3.2,s:4.0,s:5.0" --fw 400 --out $W/sheet.png
# motion: steps the scene at 60 fps and lists glitches a still frame hides (exit 2 when any)
node $SK/scripts/motion.mjs --scene <id> --src $W/<id>.js
# deliverables: one self-contained page + the embed kit
node $SK/scripts/bundle.mjs --scene <id> --src $W/<id>.js --title "<Product>: <feature>" \
  --out $W/<id>-preview.html --kit $W/kit
# the page as a visitor sees it, desktop and phone
node $SK/scripts/page.mjs --url $W/<id>-preview.html --out $W/page
```

## Quick Reference

| File | What it is |
|---|---|
| `runtime/stick.js` | The whole runtime: rig (figure, poses, easing, pen), prop kit, stage, the `<stick-scene>` element. Ship it unchanged. |
| `templates/scene.js` | Starting point for a new scene. |
| `references/craft.md` | API cheat sheet, pose cookbook, timing recipe, prop recipes, metaphor catalog, mistakes already made. Read it before writing a scene. |
| `references/scenes/diffity-review.js` | Cleanest full example (comment, agent fixes, approve; two figures, a board and a desk). `scenes-p3.js` / `scenes-p4.js` hold ~30 more; craft.md's catalog says which is which. |
| `scripts/frames.mjs`, `motion.mjs` | The two checks. `browser.mjs` is their Chrome driver. |
| `scripts/bundle.mjs`, `page.mjs` | Build the preview page and kit; screenshot a page at 1280 and 390 px. |
| `assets/balsamiq-sans-400.woff2` | The scene font (SIL OFL, `assets/OFL.txt`), used by the checks and inlined in the preview so nothing loads from Google. |

Frame specs: `idle:<sec>` freezes the resting loop, `s:<sec>` a moment in the action, `u:<0..1>` a fraction of it. Add `@<n>` for the nth play (`s:2.4@1`) so scenes that vary with `S.n` get every variant checked.

The element: `scene` (the id in `SCENES['<id>']`); `play` = `view` (plays once when half visible, then on click; the landing-page default), `click`, `hover` (loops while hovered, click on touch), `loop` (sparingly), `idle`; `no-floor` drops the grey band under the ground line, `no-ground` the line too; `zoom` scales the drawing; `label`/`aria-label` for screen readers (defaults to the scene's `label`); `no-font` skips loading Balsamiq Sans from Google. Size it with CSS: the drawing fits the height (230px native) and the scene's `width`, centred. Reduced motion shows one still frame. `STICK.theme({ butter: '#…', greenInk: '#…' })` swaps palette colours page-wide; prefer local colour constants when only one scene needs them.

Style rules:
- Ink `#141414`, white paper fills, one butter or accent highlight, lots of empty space. Balsamiq Sans at 8.5-11px, few words.
- The figure is the hero: never hide its head or active hand behind a prop. Draw props first, then figures, then things held or flying.
- One idea per scene. If it needs a caption to explain it, the metaphor is wrong. End on a result that changed state and stays for a beat.
- Physical objects over drawn animals or detailed characters. A helper figure gets one colour via `ink`/`far`.
- An AI agent is a robot: `fig(..., { ink: '#d97757', far: '#e8b7a3', bot: { col: '#d97757', dark: '#a8553a', glow, blink, happy } })`. A second agent goes teal (`#3d7a8c`, dark `#2a5866`, far `#a9c9d1`); a dark `col` gets a white visor automatically. Light `glow` while working, `happy` when done, a small label (`you`, `agent`) under each figure at `y = 16`.
- Agents don't react instantly: hold a beat (`thinking…`, a `hmm…` bubble, a hand to the chin) before the work starts.
- No other companies' logos. Product names as plain text on a prop are fine.

## Procedure

1. **Understand the product.** One line each: what the user does, what they get. Use `web_extract` on their landing page or README if they gave one.
2. **Pitch 2-3 metaphors** with `clarify` and let the user pick, unless they said to just go. Without `clarify` (a subagent has none), pick the strongest and name the runners-up in the reply. One line each: the prop, the action, the payoff. A good one is physical (lever, stamp, conveyor, pinboard, rail of frames, crate stack), reads in one glance without a caption, and ends on a visible result (a tick, a stamp, something rising or lighting up). See the catalog in craft.md.
3. **Read before writing.** `skill_view` with `file_path="references/craft.md"`, then `templates/scene.js` and `references/scenes/diffity-review.js` the same way. Those three hold the whole API; open `runtime/stick.js` only to check one helper's signature, never to read it through (it is 1,300 lines and burns turns).
4. **Write the scene** with `write_file` to `/tmp/stick-scene/<id>/<id>.js`, starting from the template. Lay out props in fixed world coordinates first, then the idle, then the action as a timeline over `T` seconds. Give `label` a plain sentence for screen readers. Write it yourself; do not hand it to `generate_code_preview`, whose separate model has never seen the rig API.
5. **Contact sheet.** Run `frames.mjs` and open every sheet with `media_analyze`. Fix and re-render until: nothing is cropped at the edges, no prop covers a face or the thing being explained, every beat reads on its own, text sits inside its box with room above and below, hands are in front of what they hold, held things meet the body where a real one would (a mic at the mouth, a handle in the palm), arrows are hand-drawn chevrons not filled triangles, and the last frame matches the idle. Two or three rounds is normal.
6. **Motion.** Run `motion.mjs` and fix every `jump` (blend the pose instead of switching it), `arm-through-face`, `head-covered`, `bent-back-elbow`, `elbow-out-back`, `squash`, `reach-short`, `start-pop` and `end-pop` until it prints "motion is clean". A short `skate` at the very start or end of a walk is fine. Re-run `frames.mjs` after motion fixes.
7. **Build and check the page.** Run `bundle.mjs` (several scenes: `--scene a,b --src a.js --src b.js`), then `page.mjs` on the preview and `media_analyze` both screenshots.
8. **Deliver.** `publish_artifact(path="/tmp/stick-scene/<id>/<id>-preview.html", kind="html_preview", title="<Product>: <feature>")` for the live scene. Zip the kit (`cd /tmp/stick-scene/<id> && zip -qr <id>-embed-kit.zip kit`) and `publish_artifact(..., kind="archive")` it. Reply with the two URLs, the metaphor in one line, and how to embed (the kit's `embed.html`). Sheets and screenshots are working files; do not publish them.
9. **Embedding into the user's own site** (when you can edit their project): copy `kit/stick.js`, the font and the scene file into the static folder, paste the markup from `embed.html`, and keep `stick.js` before every scene script in document order (deferred scripts run in order and scenes read `window.RIG` on load). In Astro use `<script is:inline ... defer>`. Give every scene on a page the same frame (the kit's `.stick-frame`: rounded card, 1px border, white, faint 14px dot grid, floor band on) and full content width. Then run `page.mjs --url <their dev or live URL>`.

## Pitfalls

- **Skipping the sheet.** Code that looks right routinely draws a prop over a face or crops a hand. Never call a scene done without looking at the sheet and getting "motion is clean".
- **Changing `stick.js`.** `motion.mjs` instruments the runtime at a fixed line; edit the scene, not the runtime.
- **Script order.** A scene script before `stick.js` (or not deferred alike) never registers; `page.mjs` reports "never started".
- **`</script` inside a scene string** ends the inlined script early; `bundle.mjs` refuses it. Split it as `'<' + '/script'`.
- **No Chrome found.** `browser.mjs` exits with where it looked. Point `STICK_CHROME` at a binary if you know one; otherwise say plainly that the frame and motion checks did not run. Do not claim they passed.
- **Over-busy scenes.** Several actions, a caption, a logo: cut back to one prop, one action, one result.

## Verification

1. `frames.mjs` exits 0 and the latest sheet was viewed with `media_analyze` and meets every step-5 criterion.
2. `motion.mjs` prints "<id>: motion is clean" (an edge-of-walk `skate` aside).
3. `page.mjs` exits 0, reports every scene drawn at 1280 and 390, and both screenshots were viewed.
4. The preview was published as `html_preview` and the kit as `archive`, or the paths were reported because publishing was unavailable.
