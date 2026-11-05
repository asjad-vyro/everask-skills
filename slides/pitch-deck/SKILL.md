---
name: Pitch Deck Builder
description: >
  Builds an investor pitch deck in EverAsk's slide maker from what the founder
  shares: a description of the company, a one-pager, a memo, notes or numbers.
  Plans the story investors expect (problem, solution, why now, product,
  traction, market, business model, competition, go-to-market, team and the
  ask), fitted to the company's stage. Uses only the founder's real figures and
  leaves a visible placeholder wherever one is missing. Use it for "make a
  pitch deck", "investor deck", "seed deck", "fundraising deck", "demo day
  slides" or "turn this one-pager into a deck".
---

# Pitch Deck Builder

Turn what a founder knows about their company into an investor deck they can present, built in EverAsk's slide maker.

A pitch deck has one job: to get the investor to take the next meeting. It does that with a clear story and real numbers. A deck with invented traction is worse than no deck, because the founder may present it.

## Step 1: Gather the facts

Read everything the founder gave: the message, attached files (a one-pager, a memo, a financial model, an old deck), and any file or page they point you to in a connected app such as Google Drive or Notion.

Note every fact you can use, in their words and numbers:

- what the company does and for whom, in one sentence;
- the problem, and any evidence for it (a figure, a customer quote);
- the product and how it works;
- traction: revenue, growth, users, pilots, letters of intent or a waitlist, each with its date;
- the business model: pricing, contract size, margins;
- the market: who buys, and how many of them there are;
- competitors and alternatives the founder named;
- the team: names, roles and relevant experience;
- the ask: how much they are raising, and what it pays for;
- the stage: idea, pre-seed, seed, Series A or later.

Ask a question only if you can't tell what the company does, or the founder mentions a file that isn't attached. Everything else that's missing becomes a placeholder (Step 2), and the outline the slide maker shows is where the founder fills the gaps.

## Step 2: Plan the slides

Start from this order:

1. **Title**: the company name and its one-line description.
2. **Problem**: who has it and what it costs them.
3. **Solution**: what the product does about it.
4. **Why now**: what changed that makes this possible or urgent now.
5. **Product**: how it works, with the founder's screenshots if they gave any.
6. **Traction**: the strongest proof, with dates.
7. **Market**: who buys and how big the opportunity is.
8. **Business model**: how the company makes money.
9. **Competition**: the alternatives, including doing nothing, and why this one wins.
10. **Go-to-market**: how customers are found, and what already works.
11. **Team**: why these people will win.
12. **The ask**: the amount, the milestones it reaches and how it's spent.

Then fit it:

- **Idea or pre-seed**: call traction "early signals" (interviews, a waitlist, pilots), and lean on the problem, the insight and the team.
- **Series A or later**: split traction into growth and retention or unit economics, and add a financial plan slide if the founder gave one.
- **A slide count from the founder** (a demo day often allows 8 to 10): merge slides to fit, keeping the title and the ask.
- **At most 20 slides**: that is the slide maker's limit.

Write each slide title as the takeaway, not a label: "Clinics lose 1 in 5 appointments to no-shows", not "Problem". Give each slide 2 to 4 short bullets.

**Every number, name and quote comes from Step 1.** Where a slide needs a fact you don't have, write a placeholder in square brackets that says what goes there, such as `[ADD: monthly revenue and date]`. Never estimate traction, revenue, customers, team history or the raise.

- **Market size**: use the founder's figures. If they ask you to size the market, use web search, put the source and year on the slide, and prefer a bottom-up count (buyers times price) with its inputs shown.
- **Competitors**: only ones the founder named or that you found with web search, and no claims about them you can't back up.

## Step 3: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck, with these changes:

- The request you pass to its outline step and its build step is the founder's message, word for word, followed by this brief:

  ```
  PITCH DECK BRIEF
  Stage: <stage>. Audience: <for example, seed investors>.
  Facts (the only source for figures, names and quotes):
  - <fact>
  Slide plan (follow exactly):
  1. <takeaway title>: <bullets>
  Rules: Use only the facts above for numbers, names, customers and quotes. Keep every [ADD: ...] placeholder exactly as written. Do not invent plausible figures.
  ```

- Pass the same brief to both steps, so the slides keep the facts the outline had.
- Screenshots and a logo the founder attached: use them the way `design-slides` describes for uploaded material.

The outline appears in the chat for the founder to approve or change before the slides are made. Don't repeat it in your reply.

## Step 4: Check the numbers

When the deck is ready, read back the slides that show figures (traction, market, business model and the ask) and compare each number with your facts. Fix any figure that isn't in them, on those slides only, by putting its placeholder back.

Then reply in a few lines:

- the slide count and the look the slide maker picked;
- every placeholder still on a slide, by slide number, so the founder knows what to fill in.

Offer one next step: a shorter version for a demo day, or changes to any slide.

## What not to do

- Don't invent traction, revenue, customers, logos, quotes, team history or market figures.
- Don't ask more than one question before the outline. The outline is where the founder corrects you.
- Don't paste the slides or their code into the chat.
