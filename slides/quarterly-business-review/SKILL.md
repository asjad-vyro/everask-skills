---
name: Quarterly Business Review Deck
description: >
  Builds a quarterly business review (QBR) deck in EverAsk's slide maker from
  the quarter's numbers and notes: a spreadsheet, an export, a report or a few
  lines of text. Works out results against targets and the change from last
  quarter, then lays out the summary, scorecard, wins, misses, trends, risks,
  next quarter's plan and the asks. Makes a team QBR for leadership by default,
  or a customer QBR for an account. Uses only the figures provided and shows
  misses plainly. Use it for "QBR", "quarterly review deck", "business review
  slides", "end-of-quarter review" or "account review for a customer".
---

# Quarterly Business Review Deck

Turn a quarter's numbers into a review deck that says plainly what happened, why, and what comes next, built in EverAsk's slide maker.

A QBR earns trust by being straight: the misses sit next to the wins, and every number can be traced back to the data.

## Step 1: Pick the kind of review

- **Team QBR**, the default: a team or company reports its quarter to leadership.
- **Customer QBR**: an account manager reviews the quarter with a customer. Use it when the request names a customer or an account.

Use the quarter the user names. If they don't name one, use the quarter the data covers, and put it in the deck title.

## Step 2: Get the numbers right

Read the data the user gave: attached spreadsheets, CSV exports, reports or notes, and any file or app they point you to, such as Google Sheets, Google Drive, HubSpot, Salesforce or Stripe. If there is no data at all, ask for it in one question. Otherwise go ahead with what there is.

Work the figures out with code, not by eye:

- for each goal: the target, the actual and the status (hit, missed or partly hit);
- the change from last quarter, and from the same quarter last year when the data has it: as a percentage for amounts, and in percentage points for rates (churn going from 3.1% to 2.6% is down 0.5 points);
- totals and averages from the rows themselves, not from a summary line you can't check.

Then:

- Give every figure its period and unit: "$2.1M revenue in Q3 2026".
- With no target, there is no status: show the actual only.
- Never fill a gap with an estimate. Write a placeholder that says what goes there, such as `[ADD: Q3 target]`.
- If two sources disagree, use neither: write a placeholder, and tell the user which numbers clash.

## Step 3: Plan the slides

**Team QBR:**

1. **Title**: the team or company, and the quarter.
2. **Summary**: the quarter in one sentence, its 3 headline numbers, and whether things are on track, at risk or off track.
3. **Scorecard**: every goal with its target, actual and status, in one table.
4. **Wins**: 2 to 4, each with what it achieved.
5. **Misses**: what fell short, why, and what changes.
6. **Trends**: the 2 or 3 metrics that matter most, this quarter against earlier ones, one slide each.
7. **Customers and market**: notable wins, losses and feedback, if the data has them.
8. **Risks**: the top risks, each with an owner and what is being done about it.
9. **Next quarter**: 3 to 5 priorities, each with a target and an owner.
10. **Asks**: the decisions, budget or people needed from leadership.

**Customer QBR:**

1. **Title**: the customer's name, the quarter, and who is presenting.
2. **Your goals**: what the customer said they wanted to achieve.
3. **Results**: progress on each of those goals, with numbers.
4. **Usage**: adoption and activity trends.
5. **Support**: tickets, response times and anything still open.
6. **What's new**: releases that matter to them, from what the user gave you. No dates unless the user gave them.
7. **Recommendations**: 2 or 3 ways to get more value.
8. **Next quarter**: a joint plan with owners and dates.

Drop a slide the data can't support rather than pad it. At most 20 slides: that is the slide maker's limit.

Write each title as the takeaway: "Revenue up 12% on Q2, but 6% under target", not "Revenue". Use charts only where a trend matters, on 3 slides at most.

## Step 4: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck, with these changes:

- The request you pass to its outline step and its build step is the user's message, word for word, followed by this brief:

  ```
  QBR BRIEF
  Kind: <team QBR for leadership, or customer QBR for the customer's name>. Quarter: <for example, Q3 2026>.
  Figures (the only source for numbers):
  - <metric, period, value, target, status>
  Slide plan (follow exactly):
  1. <takeaway title>: <bullets>
  Rules: Use only the figures above. Keep every [ADD: ...] placeholder exactly as written. Do not invent plausible figures, customers, quotes or dates.
  ```

- Pass the same brief to both steps, so the slides keep the figures the outline had.
- If the user attached a report or notes, also pass its text as the deck's source, the way `design-slides` describes.

The outline appears in the chat for the user to approve or change before the slides are made. Don't repeat it in your reply.

## Step 5: Check the numbers

When the deck is ready, read back the summary, scorecard and trend slides, and compare every figure with the ones you worked out. Fix any that don't match, on those slides only.

Then reply in a few lines:

- the slide count and the look the slide maker picked;
- every placeholder still on a slide, by slide number;
- any numbers that clashed between sources.

## What not to do

- Don't round a miss into a hit, or leave a miss out.
- Don't invent targets, figures, customers, quotes or dates.
- Don't paste the slides or their code into the chat.
