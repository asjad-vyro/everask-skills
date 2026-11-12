---
name: Brand Message Clarifier
description: >
  Turns a description of your business into a clear brand message: a brand script, a one-line pitch and homepage copy.
  The customer, not the company, becomes the hero of the story. Use it for "clarify my brand message",
  "write a one-liner for my business", "rewrite my homepage so it speaks to the customer", "build a brand script",
  "write my elevator pitch", "my messaging isn't landing". Once the message is clear, it can also turn it into a
  welcome email sequence, a sales-call outline or social posts.
---

# Brand Message Clarifier

A good result is a message a stranger understands in five seconds: the customer is the hero of the story, and the business is the guide who helps them win. Build three things from what the user told you and put all of them in one reply: a seven-part brand script, a one-liner, and homepage copy.

## Step 1: Take stock

1. Pull out of the user's message: what the business sells, who buys it, the offer and price, the proof they gave (real customer counts, results, years, awards, quotes), their tone, and any current copy. If they gave a website URL, read it with `web_extract` for the offer and the current wording.
2. Never open with questions and never wait for answers. Use `clarify` only if you cannot tell what the business sells at all. Otherwise decide, and list each assumption in the reply. You may assume the customer and how the product plainly works; never assume proof or promises (see the hard rules).
3. One hero per script. If the user names several audiences, write for the main one, say so, and note that each other audience would get its own script.
4. If the user pasted current copy, diagnose it before rewriting. Answer yes or no to each question, quote their words wherever the answer is no, and give the score out of 7. Before stating any count of their words (such as how many "we/our" lines), count it word by word in the pasted text; if unsure, quote the lines and give no number:
   1. Could a stranger grasp the offer in five seconds?
   2. Is the customer clearly the hero? (Does it talk about "you", or about "we" and "our"?)
   3. Is the internal problem named (how it feels), not only the external one?
   4. Does it show both empathy and authority?
   5. Is there a clear plan of about three steps?
   6. Is there one obvious call to action?
   7. Does it show both success and failure?

## Step 2: Write the brand script

Read `references/brand-script.md` now (use `skill_view` with `file_path`). It holds the template and the proof rules. Fill all seven parts:

1. **Customer (the hero).** Who they are, the one thing they want (a single, specific outcome in their words, not a list and not a feature), and who they want to become.
2. **Problem.** A specific, relatable villain (a situation or habit, not an abstract word like "complexity"), then three levels: external (the tangible problem), internal (how it makes them feel), philosophical (why it's wrong: "people shouldn't have to..."). Most brands stop at the external one; the internal one drives the purchase.
3. **Guide.** An empathy line ("We know what it's like to...") and authority: only proof the user gave, or a bracketed slot if they gave none. No origin story, and no invented credentials, vetting, safety checks or ratings.
4. **Plan.** A process plan of 3 steps (4 at most) with short action names, and an agreement plan of commitments that remove risk. List only commitments the user stated; mark any you suggest as "suggested, confirm it's true".
5. **Call to action.** One direct call (the main ask, in action words) and one transitional call for people who aren't ready (a lower-commitment ask such as a checklist or an intro call). The button text must match what happens on click: never call a paid action "free". Name a suggested lead magnet or intro call only by title, such as `[Tax-season checklist]`. Don't describe its contents, length, timing or what happens on the call unless the user did, and list it under "Fill in before publishing". Don't add "free", "no pitch", "no pitch deck", "find out if it's a fit" or a length ("15-minute") unless the user said it.
6. **Success.** What life looks like after: status, completeness, who they become. Concrete, with no invented figures.
7. **Failure.** What staying stuck costs them. A taste of the stakes, framed as lost time, money or peace of mind. No scare tactics and no fake urgency.

## Step 3: Write the one-liner

Read `references/one-liners.md` now. Write one sentence of 25 words or fewer, in the form "We help [customer] who [problem] [get the solution] so they can [result]." Run its four tests (repeatable after one hearing, makes people want more, specific enough that a competitor couldn't use it, a result people actually want) and rewrite until it passes. Give the main one-liner and two alternates in different forms; every version, alternates included, stays at 25 words or fewer. The one-liner may open with "We help"; headlines and body copy open with the customer.

## Step 4: Write the homepage copy

Read `references/homepage-copy.md` now. Write the actual words for each section, top to bottom, from the script: top of page (headline, subhead, button), stakes, benefits, guide, plan, testimonials, lead magnet, final call to action, footer. Headlines and body lines open with the customer or their problem, not "We". Voice is a guide's: empathy, authority and confidence, in plain words the customer would use. Cut jargon and hero language ("leading provider", "best-in-class", "solutions", "committed to excellence"). Describe only features the user gave; any other feature (scheduling, diary, profiles, messaging, matching, "pick your walker", "knows your dog", form fields) is a bracketed slot listed under "Fill in before publishing". No outcome promises stated as fact in headlines or closing lines ("Come home to a tired, happy dog", "You get your evenings back"). Never use "trusted", "safe" or "reliable" in the one-liner or copy unless the user did.

## Step 5: Check, then reply

Check and fix before replying: the customer is the hero everywhere; one desire; the internal problem is named; empathy and authority both show; the plan has 3 steps; the same direct call to action repeats through the page; the stakes are light; every one-liner is 25 words or fewer. Then scan the whole reply twice:

1. **Numbers.** Every digit or number word must be a figure the user gave, or the count of your own list. Delete the rest, including figures in advice and examples, clock times ("at three"), durations and time spans ("15-minute call", "in 15 minutes", "an afternoon", "next week", "another month", "last month"), counts in advice ("ask three customers": write "ask a few customers") and vague counts ("a couple of taps").
2. **Claims.** Go line by line through every benefit, stakes line, problem line, button, lead magnet and closing note. Every statement about what the business offers, promises, has done or is must come from the user. Examples to delete: a flat price turned into "the same price whatever happens"; "you'll always know where you stand"; problems the user never mentioned (such as "untracked invoices", "receipts in a bag or a drawer"); "no tiers, no packages to compare"; "no pitch"; "free" on a guide or call the user didn't call free; what happens on a call; what a checklist contains. Delete the claim, or turn it into a bracketed slot.
3. **Red flags.** Red-flag phrases from the hard rules ("cancel anytime", "no contracts" and the rest) never appear in the script's other parts or the homepage copy. They appear only in the agreement plan as "suggested, confirm it's true" and in "Fill in before publishing".
4. **Your own notes.** Any line explaining why the copy works must match what the reply actually contains. It must not assert unsupported facts about customers.

The reply holds the full deliverable. Do not publish a file, and never say you have prepared something without the content in the reply. The reply's very first characters are the first section heading below (for example "## Assumptions"). No preamble sentence such as "I'll start by loading the skill…" or "I'll load the Brand Message Clarifier skill". Write each assumption as one plain, specific statement. Use this shape:

1. **What's holding the current copy back**: only when they pasted copy. The diagnosis and score from Step 1.
2. **Assumptions**: 2 to 6 bullets on what you assumed (customer, how the product works, tone, anything missing). Leave it out only if the user gave everything.
3. **Brand script**: the seven parts, numbered, one line per element as the template shows.
4. **One-liner**: the main one in bold, the two alternates, and one line on why it works.
5. **Homepage copy**: each section with its actual text.
6. **Fill in before publishing**: every bracketed slot, every feature or commitment you assumed (so the user can delete what isn't true), and any other assumption worth confirming.

If the user asked for only one piece (a one-liner, say), give that piece in full, then a short "Behind it" block: the customer and what they want, their problem, and the plan, one line each.

## Other uses

- Emails, a sales call or social posts built from the message: read `references/email-sequences.md`, `references/sales-conversations.md` or `references/channel-adaptation.md` and write from the script (build the script first if there isn't one). Emails and posts are drafts for the user to review. Never send or post anything.
- A Word or PDF file wanted: load the built-in `docx` or `pdf` skill with `skill_view`, follow it to build the file from the same content, and publish it with `publish_artifact` (`kind: "document"`).

## Hard rules

- Use only what the user gave you or a tool returned. Everything else is an assumption: say so.
- No figures except the user's. Never invent customer counts, years in business, testimonials, reviews, logos, awards, guarantees, prices, percentages, speeds or results, in the copy or in your advice, not even as examples ("even over 300 beats a blank" is not allowed). Keep "since 2019" as it is; don't turn it into a number of years. Don't put a size on a problem the user didn't ("lose a week every spring").
- Never invent proof: vetting or safety checks, credentials, ratings, awards, response times, who founded the business or why. A thin request gets more slots, not invented proof.
- Never stretch a fact into a promise. "Flat $79 a month" is a price, not "no surprise invoices"; "monthly bookkeeping" is a cadence, not "always on time"; "for solo freelancers" is not "for solo freelancers only". Treat these as red flags unless the user said them: no hidden fees, no contracts, cancel anytime, guaranteed, refund, same-day, 24/7, vetted, certified, only, always. A commitment you want to suggest goes in the agreement plan as "suggested, confirm it's true" and in the fill-in list, never in the homepage copy. A lead magnet or intro call may be named, but don't describe its contents or what happens on it unless the user did.
- You may assume the customer and how the product plainly works; mark those as assumptions.
- Where the copy needs proof you don't have, write a bracketed slot such as `[number of clients you've served]` and list it under "Fill in before publishing". If the user gave no business name, write `[Business name]` instead of making one up.
- Clear beats clever. One message per asset. Lead with the outcome the customer wants, not with features.
- Don't manufacture fear or urgency. Deadlines, scarcity and guarantees appear only if the user said they are real.

Credit: the seven-part structure is adapted from Donald Miller's StoryBrand method (*Building a StoryBrand*). Use that name only if the user does.
