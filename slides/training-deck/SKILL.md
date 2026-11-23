---
name: Training Deck Builder
description: >
  Builds a workplace training or safety briefing presentation: objectives, one rule or step per slide with do and
  don't, a scenario, a short quiz with answers and a summary, plus an optional one-page poster of the key points.
  Use it for "toolbox talk slides", "safety training deck", "onboarding session slides", "compliance refresher",
  "make a training presentation and a poster".
---

# Training Deck Builder

The user gets a staff training deck built in EverAsk's slide maker, and, when they ask for a poster or handout, a one-page PDF of the key points. Good training slides are short and concrete: one rule or step per slide, plain words, what to do and what not to do, then a quiz that checks the rules stuck.

## Hard rules

- Write the deck, the poster and the reply in the language the user wrote in, unless they ask for another. The audience is the workforce: short sentences (about 12 words or fewer), everyday words, no jargon without a plain explanation. Keep the user's names, terms and figures exactly as given.
- Take the content from the user's own procedure or rules first. Keep each rule they give, in their words, and add no extra steps or tips of your own to their rules: when they gave the rules, the Do and Don't lines only restate those rules.
- Never invent a regulation number, a legal limit, a statistic, a phone number, a date, a site name or an assembly point. Where a slide needs a site detail the user did not give, write a visible placeholder such as `<your assembly point>` and list it in the reply.
- Safety and compliance content is general good practice only. The last slide carries one line, in the user's language: this training does not replace the site's own procedures or local law.
- At most 20 slides (the slide maker's limit). Never ask the user a question: decide, state the assumptions, and finish.

## Step 1: Pin down the session

From the message and any attached or linked material, settle:
- **Topic and audience**: who is being trained (for example office staff, warehouse team, new hires) and in what setting.
- **Length**: if given, about one slide per 1.5 minutes of talking, but never fewer slides than the plan below needs (every rule gets its own slide); otherwise 10 to 12 slides in all.
- **Source of the rules**: (a) the user gave rules or a procedure: use them; (b) the user gave none: find them in Step 2.
- **Poster**: wanted only if the user asks for a poster, handout, one-pager or cheat sheet. Otherwise skip Step 4.

## Step 2: Source the content (only when the user gave no rules)

1. Use `web_search` at most three times, to find an official source for the topic: a national or regional safety or labour authority, a fire service, a standards body, or a recognised industry body. Read the best one or two with `web_extract`.
2. Take plain good-practice points from them. Do not copy long passages. Keep the page URLs, up to three.
3. If nothing useful comes back, use only well-established general practice you are sure of, and say so in the reply.
4. Do not quote numbers (distances, heights, weights, times) unless a page you read gave them; then note the page.

## Step 3: Plan the deck and the quiz

Write the plan now. Every sum, count and word-count check happens here, because the slide maker allows no code once loaded.

Slide plan, in this order:
1. **Title**: the topic, the audience, and the session if given.
2. **Objectives**: 2 to 4 lines, each "After this session you can <do something>".
3. **Why it matters**: two or three plain reasons. Use only facts the user gave or a page you read; otherwise reasons in plain words with no statistics.
4. **The rules**: 4 to 8 slides, one rule or step per slide. Each has a short title that is an instruction, one "Do" line and one "Don't" line, about 25 words in all. If the user gave a list, one slide per rule, in their order, wording kept. If you add steps of your own (no list given), they come from Step 2.
5. **Scenario**: one realistic situation in 2 to 3 sentences with the question "What would you do?". The answer is on the next slide and uses the deck's own rules.
6. **Quiz**: 3 to 5 questions, one per slide, each answerable from the rules in this deck. Multiple choice with 3 options works well; vary which letter is correct. Each answer goes on the slide after its question, with a one-line reason; or, to save slides, put all questions on slide A and all answers on slide B.
7. **Summary**: the rules in one line each, matched to the objectives.
8. **Close**: one line "Questions?" in the user's language, the placeholder lines you used, and the one disclaimer line from the hard rules. Add the source URLs here when Step 2 was used.

Word budget: title up to 8 words, body up to 25 words per slide. If a slide goes over, cut it, never shrink the text.

Write the quiz answers in a list for the reply (Step 6).

## Step 4: The poster (only when asked)

Build it before loading the slide maker, because the slide maker forbids code. Skip this step if no poster or handout was asked for.

1. Pick the 5 to 7 most important points from the plan: one short line each (up to 14 words), written as instructions. Words must come from the deck's rules.
2. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Read the template with `skill_view(name=<this skill's key>, file_path="templates/poster.html")`, or read `SKILL_DIR/templates/poster.html` with `read_file`. If `skill_view` gives no path, find `poster.html` under `~/.computer/skills` with `search_files`.
3. In `execute_code`, fill the template by plain text replacement and write it to `/tmp/.scratch/training-deck/poster.html`. Placeholders: `{{LANG}}` (language code such as `id`, `es`, `en`), `{{DIR}}` (`rtl` for Arabic, Hebrew, Persian and Urdu, otherwise `ltr`), `{{PAPER}}` and `{{PAGE_HEIGHT}}` (`A4` and `297mm`; use `Letter` and `11in` only if the user says Letter or is clearly in the US), `{{TITLE}}`, `{{SUBTITLE}}` (the audience or session), `{{POINTS}}`, `{{FOOTER}}` (the disclaimer line), `{{SOURCE_LINE}}` (the source names and URLs, or empty). Escape text with `html.escape`. Each point is:
   `<div class="point"><div class="num">N</div><div class="txt">TEXT</div></div>`
4. Find Chrome in `terminal`. It is usually not on the PATH, so try the PATH names first and then the usual cache folders:
   `CHROME=$(command -v google-chrome chromium chromium-browser chrome | head -1); [ -z "$CHROME" ] && CHROME=$(ls /root/.cache/puppeteer/chrome/*/chrome-linux64/chrome /root/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell /root/.cache/ms-playwright/chromium-*/chrome-linux*/chrome /root/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | tail -1); echo "$CHROME"`
   Then run (use the path printed above):
   `"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=/tmp/.scratch/training-deck/<name>.pdf file:///tmp/.scratch/training-deck/poster.html`
   Name the PDF after the topic, for example `<topic>-poster.pdf`. Never install a browser or a PDF package (no `pip install`).
5. Check in code with `pypdf` that the PDF has exactly one page. If it has two, shorten the longest points and render again, once.
6. Publish it: `publish_artifact` with `kind: "document"` and the PDF path.
7. If no Chrome is found after that lookup, do not install anything: publish `poster.html` with `publish_artifact` and `kind: "html_preview"`, and say in the reply that it is a web page the user can print to PDF.

## Step 5: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck, with these changes:

- The request you pass to its outline step and its build step is the user's message, word for word, followed by this brief:

  ```
  TRAINING BRIEF
  Audience: <who>. Setting: <setting>. Length: <minutes, or not given>.
  Language: <the user's language>. Short sentences, plain words, one rule per slide.
  Objectives:
  - <objective>
  Slide plan (follow exactly):
  1. <title>: <bullets>
  Quiz questions and answers (each answer on the slide after its question):
  - <question> / <answer>
  Rules: Use only the rules and facts given here. Do not invent regulation numbers, legal limits, statistics, phone numbers, extension numbers, clock times, room or site names, or sources. Where a detail is missing, show the placeholder. Keep placeholders such as <your assembly point> exactly as written. The last slide says this training does not replace the site's own procedures or local law.
  ```

- Pass the same brief to both steps.
- If the user attached a procedure, also pass its text as the deck's source, the way `design-slides` describes, so the slides keep its wording.
- If the deck is not in English, set the language the way `design-slides` describes.

The outline appears in the chat for the user to approve or change before the slides are made. Don't repeat it in your reply.

## Step 6: Reply

Short, in the user's language:

```
<Deck: slide count, who it is pitched at, and the look the slide maker picked.>
<Poster: one line and its link, or nothing if none was asked for.>
**Quiz answers:** <numbered list: question number, then the answer>
**Placeholders to fill:** <each <...> placeholder, or "none">
**Sources:** <linked pages from Step 2, or "your procedure">
**Assumptions:** <audience, length, anything you decided>
<One line: this does not replace the site's own procedures or local law.>
```

Do not paste the slides or their code into the chat.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. For the deck, use the slide maker's edit tool with one clear instruction, for example "on slide 4 change the Do line to ...". For the poster, change the point or text asked for, fill the template again with every other point unchanged, render it the same way, and publish the PDF under the same file name. Say in one line what changed.
