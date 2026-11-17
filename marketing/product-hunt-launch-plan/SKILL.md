---
name: Product Hunt Launch Plan
description: >
  Builds a dated, personalized Product Hunt launch plan: assets, support-list targets, hour-by-hour launch day and post-launch follow-up.
  Use it for "make a Product Hunt launch plan", "launch-day checklist for Product Hunt", "draft my Product Hunt tagline and first comment", "where else should I launch besides Product Hunt?".
---

# Product Hunt Launch Plan

A good result is a plan the user can follow tomorrow: real dates, the user's own product named throughout, support-list targets sized to their actual reach, copy-paste drafts, and an honest read of their ranking odds. The whole plan goes in the reply itself, in full, in one turn.

## Step 1: Read the guide
Read `references/ultimate_product_hunt_launch_guide.md` with `skill_view(name=<this skill's key>, file_path="references/ultimate_product_hunt_launch_guide.md")` before writing. It holds the three phases, the asset specs, the launch-day timeline, the tips and the alternative platforms. It is the only file to read.

## Step 2: Collect what the user gave
From the message and any attachment, list: product name, one-liner, who it is for, product type (dev tool, B2B SaaS, AI product, consumer app, other), launch date or timeframe, email list size, social following, communities, assets ready, landing page, Product Hunt account status, helpers, goal, constraints, timezone.

Never open with questions and never stop to ask. Never open with a line about loading or reading the skill; the reply starts with the plan's title. For anything missing, pick a sensible default, mark it "Assumption:" and carry on. Defaults: a Tuesday, Wednesday or Thursday at least 4 weeks from today; self-hunted; goal is signups and validation; audience size "not given" (plan for a small audience); assets not ready; product type inferred from the description. Never invent traction figures, customers, quotes or results for the user's product. Also never invent product features, differentiators, benefit figures (for example "3 days faster"), customer segments, founder or cofounder backstory, or personal anecdotes. Where a draft needs one, write a bracketed placeholder such as [your main differentiator], [how feature X works] or [your origin story, 1 sentence].

## Step 3: Check the current rules (one search at most)
Product Hunt's rules and mechanics change. Run one `web_search` for the current Product Hunt launch guidelines (launch time reset, rules on asking for upvotes, any change to ranking or vote visibility). Use what it returns, link the source, and where it disagrees with the guide, follow the search. If the search fails, say the rules were not re-checked.

## Step 4: Do the maths in code
Use `execute_code` for every date and number: today's date, the weeks between today and launch, the date of each milestone (for example 4 weeks, 2 weeks, 1 week, 1 day before), the weekday of launch day, and support-list targets. Copy the results into the reply; never compute them in your head.

Support-list target: work from the user's own reach. Typical conversion is a small share of an email list or following (assume roughly 5-15%, never call a higher figure conservative), so state the percentage you assume and show the sum. Compute each table row in code, then compute the low and high totals and the gap to 500 in code from those same row values. Copy the row values, totals and gaps exactly; the totals must equal the sum of the rows and match the stated percentage. Do not split reach into channels the user did not give unless each split is marked "Assumption:". A rule of thumb for a top-5 finish is about 500 engaged supporters (commonly quoted, not guaranteed). Show the gap between the user's estimated reach and that figure.

Rate four things: support strength (weak under 100, moderate 100-300, strong 300-500+), asset readiness, timeline (rushed under 2 weeks, tight 2-4, ideal 4+), audience reach.

## Step 5: Write the plan
Use exactly this structure. Replace each `<...>` with the real content.

```
# Product Hunt Launch Plan: <product name>

## Executive Summary
**Product:** <name> - <one-liner>
**Recommended launch date:** <date> (<weekday>), 12:01 AM Pacific, in <user's timezone> that is <local time>
**Ranking potential:** <honest assessment from the four ratings; no promise of #1, no predicted rank band or signup count>
**Critical success factor:** <the one thing to get right>
**Assumptions:** <bullet list of everything you assumed>

## Phase 1: Pre-Launch (<n> weeks out)
<one "Week of <date>: <focus>" block per week, with checkbox actions>

## Phase 2: Launch Week
### <date> to <date>: Final preparations
### Launch day, hour by hour (<user's timezone>)
<time - action, covering hour 0, hours 1-4, 5-12, 13-24>

## Phase 3: Post-Launch
### Days 1-3
### Week 1

## Launch assets
<table: asset, spec, status (Ready / Needed), and drafts of the tagline (60 characters max, count each candidate's length in execute_code and show the count), a short description and the maker's first comment. Use only facts the user gave; any missing feature, benefit or story is a [bracketed placeholder]>

## Support list targets
<table: category, current estimate, target, how to reach them>

## Ready-to-use drafts
<supporter DM, launch-day post, email to subscribers, reply scripts for comments; each names the product and never asks directly for upvotes. Features, backstory, numbers and customer segments come only from the user; otherwise use [bracketed placeholders]>

## Tips for your situation
<5 to 8 tips from the guide that fit this user, each tied to their facts>

## Where else to launch
<table of platforms prioritized for the product type, split into "same week" and "next week">

## Risks and honest notes
<timeline, asset or reach gaps, and what to do about each; suggest moving the date if the timeline is too tight>
```

## Step 6: Personalize
- Audience under 500: lean on community engagement and reciprocity (supporting other launches first). Audience of 5,000+: coordinate a staged outreach and keep momentum across time zones.
- Dev tool: add Hacker News, DevHunt, GitHub. AI product: add the AI directories. B2B SaaS: LinkedIn and professional communities. Consumer app: X and strong visuals.
- If assets are weak, put fixing them first in the schedule.
- If the timeline is under 2 weeks, say so and offer a later date alongside the rushed one.

## Hard rules
- Facts about the product come only from the user. Anything else is marked as an assumption.
- Drafts (tagline, description, first comment, posts, threads, DMs, image ideas, reply scripts) never invent features, differentiators, benefit figures, customer segments, founder backstory or anecdotes; use [bracketed placeholders] instead.
- Every total and gap in the support table is computed in execute_code from the table rows, never by hand.
- No fake accounts, paid upvotes, mass automated messages or public "please upvote" asks; the drafts say "check it out" and ask for honest feedback.
- Do not guarantee a rank. Figures from the guide are rules of thumb: say "commonly quoted".
- Drafts are drafts: nothing is posted or sent for the user.
- If the user asks for a file (for example a checklist as a spreadsheet), load the built-in `xlsx` skill with `skill_view` and follow it, otherwise keep everything in the reply.
