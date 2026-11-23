---
name: Infographic Maker
description: >
  Turns a topic, a set of facts or your data into a one-page infographic, a finished PNG and PDF with big numbers, icons, steps and a simple chart.
  Use it for "make an infographic", "turn these figures into a visual", "one-page visual summary", "infographic for my school project".
---

# Infographic Maker

A good infographic is mostly pictures and numbers and very few words: 4 to 7 blocks, about 120 words in total, every number exactly as the user gave it. You build it from a ready template, render it, check it once and publish it, all in one reply.

## Hard rules

- Write the infographic in the language the user wrote in, unless they ask for another. Keep their names, figures and terms exactly as given. For Arabic, Hebrew, Persian and Urdu set `dir="rtl"` and the matching `lang` on the `<html>` tag.
- Use only facts the user gave or a search returned. Every figure must appear in a search result you actually received, and its source is the page that gave it: never put a figure from memory on the page, never attach a source to a figure that source did not return. Never invent a statistic, percentage, date, source or quote. Qualitative lines (what something does) need no figure but must not carry one either. If a number is missing, leave that tile out or write "not given" in the reply and ask nothing.
- All arithmetic (bar widths, percentages, totals) is done in `execute_code`. Never by head.
- Never ask questions first. Decide, state your assumptions in the reply, deliver.
- No external images, fonts or scripts. Icons and charts are inline SVG or CSS.

## Step 1: Plan the blocks (in your head, then in one line of the reply)

1. If the user gave facts or a data file, use them. If they gave only a topic, run at most 3 `web_search` calls for 3 to 5 figures with a clear source; keep each source's name and link for the footer. If the topic needs no figures (a process, a how-to), use steps only.
2. Choose 4 to 7 blocks from: title, big-number tiles (2 to 4), steps or timeline (3 to 5), bar chart (3 to 6 bars), one-line takeaway, sources footer. Use a chart only when the user's data compares several values.
3. Word budget: title at most 8 words, each label at most 5, each step at most 8, whole page about 120 words. Cut words before you cut a picture.
4. Pick a colour pair that fits the topic (assumption, unless the user named colours): one main colour and one accent. School projects: simpler words, and add a name/class line in the header only if the user asked for it, using placeholders the user fills.

## Step 2: Build the page

1. Call `skill_view` on this skill. Its result has `skill_dir`. If it gives no path, find `infographic.html` under `~/.computer/skills` with `search_files`. Read `SKILL_DIR/templates/infographic.html` with `read_file` (only this file).
2. Make `/tmp/.scratch/infographic-maker/` and write your page to `/tmp/.scratch/infographic-maker/page.html` with `write_file`. It is the template with these changes, nothing else restructured:
   - Replace every placeholder text (INFOGRAPHIC TITLE, NUM, short label, SECTION HEADING, Step text, CHART HEADING, Name, VALUE, SOURCE LINE). Tile numbers: at most 6 characters; put the unit in the label.
   - Delete any block you do not use (a whole `<section>` inside `<main>`); the rest spreads out by itself. Copy a `.tile`, `.step` or `.bar` to add one. Keep tiles at 2 to 4.
   - Set the four colours in `:root`. Change the icon `stroke` colour to match `--main`. Pick icons that fit the topic from simple shapes (circle, bars, heart, leaf, drop, arrow) drawn as 24x24 SVG paths; the three icons in the template are examples.
   - Bar `width` = value / largest value x 100, computed in `execute_code`; the VALUE text is the user's figure verbatim.
   - Footer: "Source: <name and link>" for searched facts, or the same sentence translated for "Figures as given by the user". Translate the footer word "Source" into the user's language.
   - Set `lang` and `dir` on `<html>` and a fitting `<title>`.
3. Never let text run past the page: the page is fixed 1080x1920 and clips overflow. If you have more text than fits, cut words.

## Step 3: Render and check

1. Run: `python3 SKILL_DIR/scripts/render.py /tmp/.scratch/infographic-maker/page.html /tmp/.scratch/infographic-maker <topic>-infographic` (`SKILL_DIR` from `skill_view`; if it gives no path, find `render.py` under `~/.computer/skills` with `search_files`). It finds headless Chrome (on PATH or under `/root/.cache/puppeteer` or `/root/.cache/ms-playwright`), writes the 1080 x 1920 PNG and the PDF, and prints OK or WRONG SIZE / WRONG PAGE COUNT for each. Do not make the PNG larger than 1080 x 1920.
2. Look at the PNG once with `media_analyze`: is any text cut off, overlapping or missing, and are all the user's numbers there? For right-to-left pages, check that numbers, ranges and percentages read in the right order (wrap each in `<span dir="ltr">`). If something is wrong, fix `page.html` once, re-run and go on. Do not loop.
3. Never install a browser or a PDF package (no playwright, puppeteer, weasyprint, wkhtmltopdf, no pip or apt installs): they are not needed and waste minutes. If the script prints CHROME NOT FOUND, publish `page.html` as `html_preview`, say that no PNG or PDF could be made, and still give the reply below.

## Step 4: Publish and reply

1. Publish with `publish_artifact` (never reply "made" without publishing): the PNG with `kind: "file"`, the PDF with `kind: "document"`, and `page.html` with `kind: "html_preview"`. Use meaningful names such as `<topic>-infographic.png`.
2. Reply in the user's language with this shape and nothing longer:
   - One line: what you made and its size (1080 x 1920 PNG, one-page PDF).
   - The block list in one line.
   - "Sources:" the links you used, or "Figures as you gave them".
   - "Assumptions:" colours, anything you left out and why.
   - One line offering changes ("bigger numbers", "other colours", "fewer words").

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was: edit your existing `/tmp/.scratch/infographic-maker/page.html` (re-create it from the template only if it is gone), re-render the same file types under the same names, publish them again and say in one line what changed.
