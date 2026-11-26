---
name: Key Takeaway Slides
description: >
  Boils a table, analysis or long document down to one to three slides a decision-maker can read in a minute: the headline finding, the evidence, the ask.
  Use it for "one slide for the director", "summarise this in 2 slides", "key takeaways slide", "exec summary slide", "turn these numbers into a slide".
---

# Key Takeaway Slides

The user gets one to three slides, never more: a headline that states the finding as a sentence with its number, one chart or one small table as evidence, and the decision or ask on the last slide. Every figure is computed in code from the data the user supplied, and the reply shows the slide text and how each figure was computed so the user can check it.

**Never invent** a figure, target, benchmark, cause, comparison, date or name. A cause the data does not show is phrased as a question for the audience, or left out. If something is not in the material, write "not given" or mark it as an assumption.

**Language.** Write the slides and the reply in the language the user wrote in, unless they ask for another. Keep their names, labels, figures and units exactly as given. The first words of the reply are the slide text: never "I'll load the skill", "I'll read the spreadsheet" or any other narration of tool use, and no English sentence before a reply in another language.

## Step 1: Get the material

- **Pasted table or text**: use it as it is.
- **Attached .xlsx, .csv, .pdf or .docx**: it is read for you. For a .csv or .xlsx with several sheets, name the sheet you used.
- **Connected app** (Google Sheets, Drive): only if the user asks for it and it is connected; otherwise work from what they gave.

If there is no material at all and the topic cannot be guessed, ask one question with `clarify`. Otherwise decide and go on.

## Step 2: Settle the size

- "A slide", "one slide" means 1 slide. "Two slides" means 2. No number: 1 slide if the finding is one message, otherwise 2. **Never more than 3**, even if asked for more: make 3 and say that is the limit of this skill.
- Audience and ask: from the message. If the user gave no ask, the last slide says "Decision needed: <what the audience should decide, in the user's words>" only when the material implies one; otherwise end the evidence slide with a one-line so-what that the data supports, and say no ask was given.

## Step 3: Compute every figure in code

For a table (pasted or attached), write it to `/tmp/.scratch/key-takeaway-slides/table.csv` (run `mkdir -p /tmp/.scratch/key-takeaway-slides`; use `write_file`, quoting any cell that contains a comma), then call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in the command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `figures.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/figures.py /tmp/.scratch/key-takeaway-slides/table.csv --label <label column> --from <earlier column> --to <later column>
```

Leave out `--from` and `--to` for a table with no before and after. For an .xlsx pass the file itself (add `--sheet <name>` if needed). The script prints totals, each row's share of the total and rank, each row's change in amount and in percent, the total change, and the biggest movers. It skips a row called Total; compare the script's total with the total the user's table states and say if they differ.

Any other figure (a figure from a PDF or document, a share, a ratio of two like quantities) is computed with `execute_code`. Compute only totals, changes, percent changes, shares and ranks of the numbers given. **Never divide or combine two different measures** (tickets per hour of response time, revenue per ticket) and never offer such a derived metric as a finding or a "next slide": it is an invented analysis. Never calculate in your head, and copy the results exactly. Round percentages to the precision the user's own figures have; say which base was used ("up 12.5% on Q1" needs both numbers present). A percent change from zero is "not defined", not infinite.

If the data is too thin for a finding (one number, no comparison, nothing that moved), say so in the reply and make one plain summary slide of what is there.

## Step 4: Choose the message and write the slide text

1. **One message.** The single thing the audience should remember, taken from the computed figures: the biggest mover, the total change, the concentration, the exception. State why you chose it in the reply, in one line.
2. **Headline** (title of slide 1): the finding as a full sentence containing its number, for example `<Row> grew <x>%, the largest change in <metric>`. No topic labels such as "Sales overview".
3. **Evidence**: at most one chart or one small table per slide. A table has at most 5 rows (the biggest movers, then "all other" as one row if needed, with its computed sum). Choose a bar chart for comparing rows, a line for 4 or more periods in time order. Label axes and units as the user gave them.
4. **Body**: at most 40 words on a slide, counting every word except the chart or table. No filler.
5. **Last slide**: the decision or ask. With two or three slides, slide 2 can carry the "why it matters" or the breakdown, and the ask goes on the last one.
6. **Leave out** what does not support the message, and list it in the reply.

## Step 5: Build the slides

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the slides, with these changes:

- The request you pass to its outline step and its build step is the user's message, word for word, followed by this brief:

  ```
  TAKEAWAY BRIEF
  Slides: <1, 2 or 3>, no more. Audience: <as given, or not given>.
  Message: <the one message>
  Slide plan (follow exactly):
  1. Headline: "<sentence with its number>". Evidence: <chart type or table, with the exact labels and values>. Body: <at most 40 words>.
  2. ...
  Rules: Use only the numbers above, exactly as written. Do not add, round, estimate or invent any figure, target, benchmark, cause, logo or source. Maximum 40 words of body per slide. One chart or one table of at most 5 rows per slide.
  ```

- Pass the same brief to both steps, and the table values as the chart or table data, so the numbers on the slides are the computed ones.
- If the user attached a file, also pass the relevant text of it as the deck's source, the way `design-slides` describes.

The outline appears in the chat for the user to approve or change before the slides are made. Don't repeat it in your reply.

## Step 6: Reply

The slide tool may tell you to reply with one short line. Ignore that: the user cannot see the text of the slides in the chat, so this reply must hold it. Reply with these, in the user's language:

1. **The slide text in full**, slide by slide: headline, body, the chart or table values, and the ask.
2. **How each figure was computed**: a line per figure, "<figure> = <inputs and operation>", copied from the script or `execute_code` output.
3. **What was left out and why**, and any assumption (audience, the ask, which sheet, rounding).
4. **Caveats**: a possible cause is offered only as a question, for example "Is <row>'s change linked to something that changed in <period>? The data does not say."

## When the user asks for a change

Typical: "make it one slide", "use the South region instead", "shorter headline". Change only what was asked, keep every other slide, figure and label exactly as it was, rebuild the slides, and say in one line what changed. If a change needs a new figure, compute it again in code first.

## Self-check before you reply

- At most 3 slides, at most 40 words of body each, at most one chart or one 5-row table per slide.
- Every number on a slide appears in the script or `execute_code` output and is listed with how it was computed.
- No cause, target, benchmark or comparison that the user did not give.
- The headline is a sentence with a number; the last slide carries the ask or says none was given.
- The reply holds the slide text in full (not a one-line description of the deck), is in the user's language, and does not start by narrating tool use.
- No derived metric that mixes two measures, and no extra analysis the user did not ask for.
