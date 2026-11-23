---
name: Social Carousel Maker
description: >
  Makes a swipeable Instagram or LinkedIn carousel as finished slide images (PNG) with your exact text, plus the caption.
  Use it for "make a carousel", "turn this into Instagram slides", "LinkedIn carousel about...", "swipe post with these tips".
---

# Social Carousel Maker

A good carousel has 5 to 8 slides: a hook, one point per slide (at most 25 words), a recap and a call to action. The slides are real PNG images built from a template, so the text is exactly the user's words. The reply also holds the caption. You never post anything; the user posts it.

## Hard rules

- Write everything in the language the user wrote in, unless they ask for another. Keep their names, figures and terms exactly as given. For Arabic, Hebrew, Persian and Urdu set `dir="rtl"` and the right `lang` on `<html>`.
- Use the user's wording for their points. Never invent a statistic, quote, customer or result. If the user gave only a topic, write points that are advice or explanation, not claims with numbers; mark any figure from a search with its source.
- Never ask questions first. Decide, state assumptions, deliver. Never post or schedule; no login is needed or used.
- Explanation lines under a point restate or gently explain it in plain words. They carry no number, quantity, frequency, time span, percentage or study (no "two inches", "every few weeks", "in 2 weeks") unless the user gave it. The same goes for the closing call-to-action slide and the caption: no "start with 5 minutes", "in 7 days" or similar invented amounts.
- Text lives in the HTML, never inside generated images.

## Step 1: Plan the slides

1. Format: 1080 x 1350 (Instagram portrait) by default; 1080 x 1080 if the user says square or LinkedIn square. State the choice.
2. Count the user's points. Slides = hook + one per point + recap + call to action, so 3 points give 6 slides and 5 points give 8. Never exceed 8 slides: if the user gave more than 5 points, merge or drop the weakest and say which in the reply. If they gave only a topic, write 3 to 5 points.
3. Write all the text in a list first: hook title (max 10 words), promise line (max 14), each point title (max 8 words) and text (max 25 words), recap items (3 to 5, max 8 words each), call to action (max 8 words).
4. Colours: use the brand colours if the user gave any (hex or names), else pick three that fit the topic: background, main, accent. Handle or brand tag: only if the user gave it; otherwise use the topic as the tag.

## Step 2: Build the slides

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox; the files are under `templates/` and `scripts/`. Use the full path where it says `SKILL_DIR`. If `skill_view` gives no path, find `carousel.html` under `~/.computer/skills` with `search_files`.
2. Read `SKILL_DIR/templates/carousel.html` with `read_file`.
3. Write `/tmp/.scratch/social-carousel/page.html` with `write_file`. It is the template with:
   - the three colours set in `:root` (and `--h:1080px` for square);
   - one cover slide (`id="s1"`), then one `point` section per point (copy the block, ids `s2`, `s3`, ...), then one `recap` section and one `cta` section, each with the next id; slide ids run s1, s2, ... without gaps;
   - every placeholder replaced (BRAND OR TOPIC TAG, titles, texts, items, HANDLE IF GIVEN). Empty a span you do not need instead of leaving a placeholder. The big number on a point slide is the point's number;
   - every `n / TOTAL` replaced with the real count, for example `2 / 7` with the real numbers, and the "SWIPE" word translated;
   - `lang`, `dir` and `<title>` set.
4. Do not change the slide structure or CSS sizes. If a slide's text does not fit, cut words.

## Step 3: Render and check

1. Run: `python3 SKILL_DIR/scripts/render_slides.py /tmp/.scratch/social-carousel/page.html /tmp/.scratch/social-carousel/out 1080 1350` (use `1080 1080` for square). It finds headless Chrome (on PATH or under `/root/.cache/puppeteer` or `/root/.cache/ms-playwright`), writes `slide-01.png`, `slide-02.png`, ... and prints each size with OK or WRONG SIZE. Never install a browser or a PDF package (no playwright, puppeteer, weasyprint, no pip or apt installs). If it prints CHROME NOT FOUND, publish `page.html` as `html_preview`, say that no images could be made, and give the caption anyway.
2. Check in `execute_code` that the number of PNGs equals the number of slides you planned and every one is the right size.
3. Look at one text-heavy slide and the cover with `media_analyze`: is text cut off, overlapping or too small? Fix `page.html` once, re-run the script and go on. Do not loop.

## Step 4: Caption

Write one caption in the user's language: a first line that works as a hook, 2 to 4 short lines of value taken from the slides, and the call to action. Add 3 to 6 hashtags only if the user asked for them or the platform is Instagram; for LinkedIn use at most 3. No invented numbers, no tags of real accounts the user did not give.

## Step 5: Publish and reply

1. Publish each PNG with `publish_artifact`, `kind: "file"`, named like `<topic>-slide-01.png`. If there are more than 5 slides, first zip them in `execute_code` with `zipfile` into `<topic>-carousel.zip` and publish the zip as well (`kind: "file"`).
2. Reply in the user's language:
   - One line: N slides, size, order (hook, points, recap, call to action).
   - The slide texts as a short numbered list so the user can proofread them.
   - The caption, ready to paste.
   - "Assumptions:" format, colours, anything merged or dropped.
   - One line: you have not posted anything; the user posts the slides in this order.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was: edit `/tmp/.scratch/social-carousel/page.html` (re-create it from the template only if it is gone), re-render with the same script, publish the PNGs again under the same names and say in one line what changed. If the change is to the caption only, give just the new caption.
