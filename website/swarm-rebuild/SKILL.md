---
name: Swarm Rebuild Video
description: >
  Makes a video of a web page being rebuilt from scratch by a swarm of
  multiplayer cursors. The page dissolves, dozens of named cursors draw it
  back box by box while the view scrolls down, and then the live page fades
  back in. It's recorded in the sandbox with headless Chrome, with sound, as a
  1080p MP4 in landscape, vertical or square. Good for launch posts, portfolio
  reels and social teasers. Use it for "make a swarm video of my site", "swarm
  rebuild this page", "cursors building my website", "animate my landing page
  being built" or "a launch video of this URL".
---

# Swarm Rebuild Video

Turn a web page into a short video of a swarm of cursors building it.

The page goes blank. Cursors with name tags, like the ones in a multiplayer design tool, draw boxes with crosshairs, type the text, drag in the images and fill the page back in. The view scrolls down as they build. A badge says how many agents built it and how fast, and then the real page fades back in.

The animation is [Swarm Rebuild](https://github.com/DhvanilPatel/swarm-cursors) by Dhvanil Patel, a tribute to [Swarm](https://califa.github.io/swarm-site/) by Joel Califa. The skill has two scripts:

- `scripts/swarm.js` is Swarm Rebuild's page script, unchanged.
- `scripts/record.js` loads it into headless Chrome and records it one frame at a time, so the video stays smooth even when the sandbox is slow. A slow sandbox only makes the recording take longer.

Work in `/tmp/.scratch/swarm/` in the sandbox. Only the finished video goes to the user.

## Step 1: Get the page

- **A link**: use it as given. A bare domain such as `example.com` works too. The sandbox's Chrome isn't signed in to anything, so it can't record a page behind a login. For those, ask for a public page or the page's HTML.
- **An HTML file or a zipped site**: download it into the scratch folder with `curl -L` and unzip it if needed. Then pass the HTML file's path instead of a URL. Its images and styles must sit next to it or be online.

Settle these, from the message or by default:

- **Format**:
  - `landscape` (1920 by 1080) by default;
  - `vertical` (1080 by 1920) for Reels, TikTok and Shorts;
  - `square` (1080 by 1080) for feed posts.
- **Ending**: back on the live page by default. `--end hold` ends on the finished rebuild instead.
- **Sound**: on by default (clicks, whooshes and a closing chord). `--no-sound` makes a silent video.

Ask a question only if the user gave no page.

## Step 2: Find the scripts

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `record.js` under `~/.computer/skills` with `search_files`.

Both scripts need only what the sandbox already has: `node`, `ffmpeg`, and the headless Chrome and `puppeteer-core` that come with the HyperFrames CLI.

## Step 3: Preview the page

```bash
node SKILL_DIR/scripts/record.js --url https://example.com --preview /tmp/.scratch/swarm/preview.png
```

This takes about 15 seconds. It prints one line of JSON with:

- the page's `title`, its final `url` and the HTTP `status`;
- `page_height` in pixels;
- `overlays`: the fixed and sticky elements on screen. Each has a `selector`, where it sits, how much of the screen it covers, and its text.

Look at `preview.png` with `media_analyze`. Ask what page it shows, and whether a cookie banner, popup, chat bubble or app-install bar covers it. Then:

- **A banner or popup**: find it in `overlays` by its text, and run the preview again with `--hide "SELECTOR, SELECTOR"`. Hide only banners, popups, chat bubbles and install bars, never the site's own header or menu. Check the new preview.
- **The wrong page, a blank page, an error page or a "verify you are human" check**, or a `status` of 400 or more: don't record it. Tell the user what the sandbox saw, and ask for another link or the page's HTML.
- **A slow page** (images or text still loading in the preview): add `--wait 5000`.

## Step 4: Record

```bash
node SKILL_DIR/scripts/record.js --url https://example.com --out /tmp/.scratch/swarm/swarm-rebuild.mp4 --hide "#cookie-banner"
```

- Add `--format vertical` or `--format square` if needed, and the same `--hide` and `--wait` as the last good preview.
- Set the terminal `timeout` to 600. A small page takes under a minute and a big one up to 9.
- The script keeps its own time and always finishes within 9 minutes, encoding included. If time runs short, the swarm hands back to the live page early.
- Never run two recordings at once. Each one needs a whole Chrome.

It prints one line of JSON:

- `ok`, `out`, `seconds`, `size` (such as `1920x1080`) and `mb`.
- `rebuilt`: true if the swarm finished the whole page.
- `cut`: null, or why the swarm handed back early:
  - `max-seconds`: the video reached `--max-seconds` (75 by default);
  - `budget`: the 9 minutes ran short;
  - `chrome`: Chrome failed partway. The video fades back to the page from that point, and `warning` says when.
- `speed`: the build speed used. The script picks it from how many pieces (`layers`) the page has: 1 for up to 120, 2 for up to 350, and 3 above that. `--speed 1`, `2` or `3` forces one.
- `layers`, `built` and `agents`; and `sound`, the number of sound events mixed in.

If `ok` is false, the `error` says why:

- **"couldn't open"**: the link is wrong or the site is down.
- **"the swarm stopped early"**: the page can't be rebuilt. This usually means it's a single canvas, a PDF or an app that redraws itself. Tell the user.
- **"Chrome's tab crashed"**, **"Chrome stopped responding"** or **"gave up"**: run it once more with `--speed 3`. If it fails again, tell the user.

## Step 5: Check the video

1. **`ffprobe`**: check the length, the size and the audio track. A silent video has no audio track.
2. **A contact sheet**: put `seconds` from the JSON in place of `SECONDS`, then look at the sheet with `media_analyze`.

   ```bash
   ffmpeg -y -i /tmp/.scratch/swarm/swarm-rebuild.mp4 -vf "fps=8/SECONDS,scale=480:-1,tile=4x2" -frames:v 1 /tmp/.scratch/swarm/sheet.jpg
   ```

   The sheet should show, in order:
   - the real page first;
   - the page going blank, then cursors with name tags drawing boxes and filling them in, scrolling down as they build;
   - the real page again at the end, or the finished rebuild with `--end hold`.

   No frame should be all black, and no banner should cover the page.
3. If something is wrong, fix the cause and record once more. For a banner, add `--hide`. For a page that was still loading, add `--wait 5000`.

## Step 6: Deliver

Publish the video with `publish_artifact`, `kind: "video"`, and name it after the site, such as `swarm-rebuild-example-com.mp4`. Then reply with:

1. Its length and format.
2. Whether the swarm rebuilt the whole page or handed back early, and why.
3. The credit: "Animation: Swarm Rebuild by Dhvanil Patel, after Swarm by Joel Califa."

Offer a vertical or square version, one that ends on the rebuild, or a silent one.

## What not to do

- Don't edit `swarm.js` or `record.js` to make a page work. Use `--hide`, `--wait` or `--speed`.
- Don't run `swarm.js` on its own. It's the page script that `record.js` loads into Chrome.
- Don't record a page behind a login, and never ask for the user's password.
- Don't hide the site's own header, menu or content. Hide only banners, popups and chat bubbles.
- Don't rerun more than once after a failure.
- Don't show the user scratch files: previews, contact sheets or the JSON.
