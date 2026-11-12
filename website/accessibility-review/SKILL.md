---
name: Accessibility Audit (WCAG AA)
description: >
  Audits a web page, pasted HTML or screenshot against WCAG 2.1 AA, with each problem's criterion, severity and fix.
  Colour contrast is calculated, and the report says what could not be checked.
  Use it for "audit accessibility", "check a11y", "is this accessible?", "does this meet WCAG AA?", "check the colour contrast", or a review before launch or design handoff.
---

# Accessibility Audit (WCAG AA)

A good audit is one a developer or designer can act on today. Every problem names the element at fault, the WCAG 2.1 criterion it breaks, how serious it is and a concrete fix. Contrast ratios are calculated, never guessed, and the report says plainly what could not be checked from the material given. The whole report goes in the reply.

## Step 1: Get the material

Work from what the user gave you. Do not open with questions. Only if there is nothing at all to audit (no URL, code, screenshot or description) ask once, with `clarify`, for the page URL or its HTML.

- **Pasted HTML, CSS or component code:** for a whole page, save it exactly as given with `write_file` to `/tmp/.scratch/accessibility-review/page.html` (keep every line, including blank ones, and end with a newline), then run `wc -l` on it for the line count and `head -3` and `tail -3` to confirm the file starts and ends like the paste. For a snippet of a few lines, skip the file and read it directly, and cite no line numbers unless you save it and use `grep -n`.
- **A URL:** in `terminal` run `mkdir -p /tmp/.scratch/accessibility-review && curl -sL --max-time 40 -A "Mozilla/5.0" -o /tmp/.scratch/accessibility-review/page.html "THE_URL"`, then check the size with `wc -c`. If the file is empty, or is mostly script tags with almost no text, render the page instead: `google-chrome --headless --no-sandbox --disable-gpu --virtual-time-budget=8000 --dump-dom "THE_URL" > /tmp/.scratch/accessibility-review/page.html` (find the browser with `command -v google-chrome chromium chromium-browser`). If both fail, use `web_extract`, audit the text it returns, and say at the top of the report that only the page text could be read, not its markup or styles.
- **A screenshot or other image:** look at it with `media_analyze`. Ask for text and background colours, form fields and whether each has a visible label, icons with no text, and anything shown by colour alone. Contrast read from a picture is an estimate: write "estimated from the image".
- **A design description, or a Figma link you cannot open:** review the design as described, using "Reviewing a design" in the checklist, and say the review is of the description. If a Figma tool is available and the user gave a Figma link, read colours, text sizes and component sizes from the file.

## Step 2: Scan the HTML

Skip this step for a screenshot, a description or a snippet of a few lines.

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `a11y_scan.py` under `~/.computer/skills` with `search_files`.

`python3 SKILL_DIR/scripts/a11y_scan.py scan /tmp/.scratch/accessibility-review/page.html --base "THE_URL"`

Leave off `--base` for pasted code. The scan prints page facts, findings with their WCAG criterion, text colour pairs with ratios, the stylesheets it did not read, and what it cannot check.

- If it lists linked stylesheets that were not read, download the two or three main ones with `curl -sL -o` into the same folder and run the scan again with the CSS file names after the HTML file name.
- Every scan line is a lead, not a verdict. Confirm it in the code before you report it (a later rule such as `background: transparent` or `color: ... !important` can change a colour, and text that is hidden until focused is not a contrast failure). Leave out leads you could not confirm, and do not mention them in the report.
- If the script fails, do the checks by reading the code and say the automatic scan did not run.

## Step 3: Work through the checklist

Read `references/wcag-aa-checklist.md` now. It has the criterion names and numbers to cite, what a read of code can and cannot prove, how to review a design, and fix patterns.

Go through the scan results and the material itself. For each criterion in the checklist decide: failed (you can quote the evidence), checked and fine, or cannot be confirmed from this material. Add what the scan cannot see: unclear link text, headings or labels that do not describe their content, instructions that rely on colour or position, unhelpful error messages, missing captions or transcripts. Group repeats: one finding per pattern, with the count and up to three examples.

Take every count and line number from the scan output or from a command you run on the saved file: `grep -n 'pattern' FILE` for line numbers, `grep -o -i 'pattern' FILE | wc -l` for counts (`grep -c` counts lines, not matches), `wc -l FILE` for the total number of lines. Run `grep -n` for the quoted code of every finding and copy the line number it prints; never count lines by eye. A number you did not measure becomes a word such as "several", or is left out. This includes element counts ("ten tables") and word counts ("~200-word alt"): measure with `grep -o -i` or `wc -w`, or drop the number. For pasted code, line numbers are lines of the code as pasted.

Describe attributes exactly as the quote shows them: `alt=""` is an empty alt, not "no alt".

## Step 4: Calculate every contrast ratio

Run the script, text colour first, then its background, with the colours quoted:

`python3 SKILL_DIR/scripts/a11y_scan.py contrast "#999999" "#ffffff" "#555555" "#f4efe9"`

- Start from the scan's colour pairs. Add any text or UI pair you see in the code that it missed. If a colour cannot be worked out (set by script, an unread stylesheet, an image behind text), say so instead of guessing it.
- Needed: 4.5:1 for normal text; 3:1 for large text (24px, or 18.66px bold, and up) and for UI component borders, meaningful icons and focus indicators. Placeholder text counts as text.
- For each failing pair, propose a replacement colour and check it with the script before writing it.

## Step 5: Rate each finding

- **Critical:** a user cannot finish a task or reach content at all. Examples: a control that cannot be used with a keyboard, a form field or button with no accessible name, an informative or linked image with no alt text, a keyboard trap, essential video with no captions, text under 2:1 contrast.
- **Major:** fails AA and makes the page hard or error-prone to use, but there is a way round. Examples: normal text between 2:1 and 4.5:1 contrast, no lang attribute, no visible focus indicator, placeholder-only labels, no page title, a missing heading structure on a long page, errors that are not announced. Contrast on text that is essential to finish a task (labels, buttons, errors) is Critical.
- **Minor:** low impact, advisory or best practice. Examples: a generic link with clear context nearby, redundant alt text, small touch targets (a Level AAA matter). Missing autocomplete on a field already reported goes in that finding's fix, never as its own numbered finding.

## Step 6: Write the report

Put the whole report in the reply, in this shape. The first characters of the reply are `## Accessibility audit` (no opening line about loading the skill or what you will do). Number findings continuously across the severity groups, and leave out a severity heading with no findings. Each numbered finding stands alone: do not fold one finding into another finding's fix. A small advisory add-on (such as autocomplete on a field already reported) goes inside its parent finding's fix and is not numbered or counted separately.

```markdown
## Accessibility audit: <page or component name>
**Standard:** WCAG 2.1 AA | **Audited:** <what was read and how: "HTML fetched from the URL, scripts not run", "pasted HTML", "screenshot, visual check only">

### Summary
<One-sentence verdict, for example "Fails WCAG 2.1 AA: 7 problems found, the worst being ...">
**Issues:** <n> | **Critical:** <n> | **Major:** <n> | **Minor:** <n>

### Findings
#### Critical
1. **<short title>** - WCAG <number> <name> (Level <A or AA>)
   - Where: `<the element or code, quoted>` (<line number or location>)
   - Problem: <what is wrong and who it affects, one sentence>
   - Fix: <the specific change; corrected code where the fix is code>

#### Major
2. ...

#### Minor
3. ...

### Colour contrast
| Element | Text on background | Ratio | Needed | Result |
|---|---|---|---|---|
| <what it is> | `#999999` on `#ffffff` | 2.85:1 | 4.5:1 | Fail |

<One line: ratios were calculated with the script, or are estimated from the image.>

### Could not be confirmed from this material
- <area> - how to check: <a one-line manual test>

### Checked, no failure found
- <what you checked that looked fine>

### Priority fixes
1. <the fix with the biggest user impact> - <why it comes first>
2. ...
3. ...

_This is a technical review against WCAG, not legal advice or a certificate of compliance._
```

Write the Findings section first, then the Summary. Before replying, list the finding numbers under each severity heading as written (for example "Critical: 1; Major: 2, 3, 4; Minor: 5, 6"), count them, and make the Summary's verdict number and its Issues, Critical, Major and Minor counts match that recount exactly (Issues = Critical + Major + Minor). Check every finding's line number against the `grep -n` output once more. Any line count in the Audited line is the `wc -l` result.

In the contrast table list every failing pair and the main passing ones (body text, buttons), at most about ten rows. For "Could not be confirmed", list the items from the scan's "not checked" list and the checklist that apply to this page, such as keyboard use and focus order, screen-reader output, zoom and reflow, and captions, each with a one-line manual test (for example "Tab through the page: can every control be reached and can you see where focus is?").

## Hard rules

- Report only what is in the material. Do not invent elements, selectors, colours, ratios, line numbers or page content. Quote the code or element for every finding.
- Counts, line numbers and quotes must be measured or copied, never estimated (see Step 3). The Summary tally must equal the numbered findings as written.
- A contrast ratio that the script did not calculate does not go in the report. Colours read off an image are "estimated".
- You have not heard a screen reader. Say what one may announce, not exactly what it says.
- Never write that keyboard use, focus order, focus traps, screen-reader output, zoom, reflow, text spacing, captions or motion "pass" unless the material shows it. They go under "Could not be confirmed".
- Never call the page "compliant" or "accessible". Say "no failures found in what was checked".
- Cite criterion numbers and names from the checklist. 2.5.5 Target Size is Level AAA, not AA. If the user asks for WCAG 2.2, use the additions in the checklist and write "Standard: WCAG 2.2 AA".
- Every finding has a fix. If you cannot say what the fix is, say what to investigate.
- Plain words for severity. No emoji.

## Optional extras

Use an app only if the user asks for it and it is connected. Otherwise work from what the user gave you.

- Figma: if the user asks you to audit a Figma file and Figma is connected, read colour values, text sizes and component sizes from it.
- Jira, Linear or Asana: if the user asks for tickets, draft one per finding in the reply (title, WCAG criterion, severity, how to see it, fix). Create them in the app only if the user says to.
- GitHub: if the user points to a repository, branch or pull request and GitHub is connected, read the files from it and cite file and line.
