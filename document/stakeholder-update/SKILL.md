---
name: Stakeholder Update Writer
description: >
  Turns rough notes into a status update written for its reader: executives, engineers, partners, customers or the board.
  Use it for "write my weekly update", "draft a status update for my VP", "announce this launch to customers",
  "escalate this slipped milestone", "turn these notes into a short exec summary" or "write the monthly board update".
  Works from what the user types or pastes, and also covers risk escalations and decision records.
---

# Stakeholder Update Writer

A good update tells the reader in its first lines where things stand and what is needed from them. The point comes first, bad news is never buried under good news, every fact comes from the user, and every ask says what is needed and by when. The finished update goes in the reply, ready to copy.

## Step 1: Decide the type and the audience

Choose both from the request. Do not ask the user which they want.

Type:
- **Weekly** (the default): progress, blockers, next steps.
- **Monthly**: higher level: milestones, trends the user gave, fit with goals.
- **Launch**: announcing something that shipped.
- **Ad hoc**: an escalation, a change of plan or a decision that is needed.

Audience:
- **Executives or leadership** (a VP, the CEO, "my boss"): outcomes, brief, strategic.
- **Engineering or the user's own team** ("my team", engineers): technical detail, owners, decisions.
- **Cross-functional partners** (design, marketing, sales, support): what affects them and what is needed from them.
- **Customers or other external readers**: benefits, clear timing, no internal jargon.
- **Board**: metrics first, strategic, risk-focused, very short.

If no audience is named, write for the user's own team and say so in the assumptions line. If the user wants several versions ("a customer announcement plus an exec summary"), write each in full under its own heading, with the same facts in every version: only the framing and the level of detail change.

## Step 2: Collect the facts

Work from what the user typed, pasted or attached. A connected tracker, chat, meeting-notes or docs app is an optional extra: if the user asks you to pull from one and it is connected, use it for what finished, what is at risk or blocked, decisions and action items. Otherwise work from what the user gave you, and say in the assumptions line that you could not pull from it. Never go looking in an app the user did not ask about.

Sort the facts into four piles: done, at risk or blocked, decisions made or needed, and next. Keep every date, number and name exactly as the user gave it. Keep vague dates vague: "end of Nov" stays "end of Nov", never "30 Nov".

- Use only facts from the user or a connected app. Never invent metrics, percentages, dates, owners, ticket numbers, links, customer names, quotes, causes or results. Simple arithmetic on the user's own figures (three weeks between two dates) is fine.
- Describe each item only in the user's words and verbs: "shipped" never becomes "live" or "in production". Add no status, schedule or plan the user did not state ("planned for this week", "still in progress", "carried over"), and no claims of absence ("nothing else is blocked"), knock-on effects, cadences or follow-up promises.
- If the reader would expect something the notes lack (a new date, an owner, a metric, a deadline), write the update without it and list it only under "To add before sending", never as a to-do in the update. Leave no placeholder such as [VP] in the update; write "you" instead.
- If two facts conflict, use the one the user stated most recently or most clearly, and list the conflict under "To add before sending".
- Leave out a section you have no facts for (no Coming up without next items the user gave) instead of padding it. Two facts make a short update.

Only if the user gave nothing at all to go on (no notes, no list, no topic), ask once with `clarify` for what got done, what is blocked or at risk, any decision made or needed, and what is next. In every other case do not ask: decide, state your assumption in one line, and write the update.

## Step 3: Set the status

Show a status colour on executive, board and escalation updates, and on others only if the user asks. Use the user's own status if they gave one. Otherwise choose from the facts and give the reason in a few words. The colour reflects what is true, not what the reader hopes to hear.

- **Green** (on track): progressing as planned, no significant risk or blocker. Not a default.
- **Yellow** (at risk): slower than planned, or a risk has become real; a mitigation is under way but the outcome is uncertain. A date that moved or a milestone that slipped is at least Yellow. Flag it at the first sign of risk.
- **Red** (off track): significantly behind, or a major blocker with no clear mitigation; commitments will be missed without intervention. Use it when help is genuinely needed.

If the user gave the previous status and this one differs, say why in the first lines: "Moved to Yellow because ...". Go back to Green only when the risk is resolved, not just paused.

## Step 4: Write the update

1. **Lead with the point.** The first lines say where things stand and what is needed. If anything slipped, is blocked or needs a decision, the first lines say what, the old date and the new date (when the user gave them), and the cause in a few words. Good news comes after.
2. **Use the layout for the audience** below, dropping any line you have no facts for. If a layout has no headline line, open with one: a single sentence with the most important thing, bad news first. If the user supplied their own template or a previous update, follow its layout and headings instead.
3. **Match the length.** Executives: under 200 words; count the body before replying and cut, merging any item repeated across Risks and Decisions, until it fits. Board: under 150. Customers: short and plain. Team and partners: as long as the reader needs, still easy to skim. A length the user asked for wins.
4. **Make every ask specific**: what is needed, from whom and by when ("Decision on X by 17 Nov", not "support needed"). Give the options, and a recommendation only if the user gave one; never add your own. If the notes give no deadline, do not invent one.
5. **Write each risk as**: what could happen and why; the impact if it does; how likely (only if the notes say); what is being done about it; what help is needed. List only risks the reader must know about or can help with, and give each one a mitigation or say plainly that there is none yet. Never write "there may be delays": say what, how long and why. For a risk review, label each risk Resolved (say how), Owned (name the owner and the plan), Accepted (say why we proceed) or Mitigated (say what reduced it).
6. **Format** for skimming: bold the key points, short bullets, no filler opening such as "I hope this finds you well". For email, begin with a Subject line that carries the headline. For a chat post, use plain text with short bullets and no tables.

### Executives or leadership

Frame everything as outcomes and goals, not activity ("we shipped X and it moved Y", not "14 standups and 23 tickets"). Put Risks above Progress when something slipped, is blocked or needs a decision; put Progress first when all is well.

```
Status: <Green | Yellow | Red>

TL;DR: <one sentence: the most important thing to know, bad news first>

Risks:
- <risk>: <mitigation>. <ask, if any>.

Progress:
- <outcome achieved, tied to a goal>
- <milestone reached, with impact>
- <metric movement, only if the user gave it>

Decisions needed:
- <decision>: <options; recommendation only if given>. Need by <date>.

Next milestones:
- <milestone>: <date>
```

### Engineering or the user's own team

Technical detail and owners. Link tickets and PRs only if the user gave the links. When priorities change, say why. Say plainly what is blocking the work and what is being done to unblock it. Leave out what does not affect their work.

```
Shipped:
- <feature or fix>. <link, if given>. <impact, if notable>.

In progress:
- <item>: <owner>. <expected completion>. <blocker, if any>.

Decisions:
- Made: <decision>. <rationale>.
- Needed: <context>. <options>. <recommendation>.

Priority changes:
- <what changed and why>

Coming up:
- <next item>: <why it is next>
```

### Cross-functional partners

Say what is coming that affects them, what is needed from them and by when, and where they can give input.

```
What's coming:
- <feature or launch>, <date>: <what it means for your team>.

What we need from you:
- <specific ask>: <context>. By <date>.

Decisions made:
- <decision>: <how it affects your team>.

Open for input:
- <topic>: <how to give feedback>.
```

### Customers or other external readers

Frame everything as what the customer can now do, not what was built. No internal jargon, ticket numbers or implementation detail. Be honest about timing without overcommitting: use the user's own wording ("later this quarter") and never turn it into a firm date. Mention a known issue only if it affects customers and there is a plan to resolve it.

```
What's new:
- <feature>: <benefit in the customer's terms>. <how to use it>.

Coming soon:
- <feature>: <timing as the user gave it>. <why it matters to you>.

Known issues:
- <issue>: <status>. <workaround, if there is one>.

Feedback:
- <how to share feedback or request features>
```

### Launch announcement

```
What launched: <one sentence>
Why it matters: <the benefit for this reader>
Details: <scope, who gets it and when, limitations>
Results so far: <only metrics the user gave>
Rollout: <phases and dates the user gave>
Feedback: <where to send it>
```

### Board

Metrics first, strategic, risk-focused, very short.

```
Status: <Green | Yellow | Red>
Headline: <one sentence>
Numbers: <metrics the user gave, with the period each covers>
Risks and asks: <the top one to three, each with its mitigation and what the board is asked to do>
Next milestones: <milestone>: <date>
```

### Decision records

If the user asks to write a decision down (an ADR) rather than announce it, write one page: Title; Status (Proposed, Accepted, Deprecated or Superseded by an earlier record); Context (the situation and the forces at play); Decision (stated clearly and directly); Consequences (positive, trade-offs accepted, what it enables or prevents); Alternatives considered (each with why it was rejected). Name who was involved and who made the final call only if the user said. Write it as if the reader has none of today's context.

## Step 5: Deliver

Open the reply with the update itself (a one-line title naming the audience and the type is fine). Put nothing before it, not even a line about loading the skill. After it, add these lines, leaving out any that has nothing to say:

```
Assumed: <the audience and type you chose; why you chose the status colour; any app you could not pull from>
To add before sending: <facts that were missing, such as a deadline, an owner, a metric or a new date>
```

Do not report a word count. Finish with one sentence naming another version you could write (for example a customer or Slack version), without asking a question.

- The update is a draft. Send or post it only if the user explicitly asks and the app is connected; otherwise the user sends it.
- Do not create a file unless the user asks for one. For a Word document or PDF, load the built-in `docx` or `pdf` skill with `skill_view`, build the file from the same text and publish it with `publish_artifact`, and still put the text in the reply.

## Rules

- The full update is in the reply, never only a summary of it or an offer to write it.
- Every fact is the user's or came from a connected app. Nothing is invented. Dates stay in the user's wording.
- Bad news comes first.
- Every ask says what is needed and by when; a deadline the user did not give is flagged, not made up.
