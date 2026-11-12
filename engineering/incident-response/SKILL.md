---
name: Incident Response and Postmortem
description: >
  Severity call, first actions and status updates for an outage, then a blameless postmortem.
  It works from a pasted alert, thread, notes, timeline or a one-line description.
  Use it for "we have an incident", "production is down", "what severity is this", "write a status update",
  "write a customer update about the outage", "write the postmortem".
---

# Incident Response and Postmortem

Mid-incident, a good result is a severity with a reason, the next actions in order and a status update the user can paste as it is. After it, a blameless postmortem built only from what the user gave you. Everything you write is a draft: you never post, page, email or file anything unless the user tells you to in this chat.

## Step 1: Pick the phase

Never ask which phase it is. Decide from what the user said. If it was not obvious, say in one line what you assumed.

- **Live incident** ("we have an incident", "checkout is down", a pasted alert, users reporting errors): do Steps 3 and 4 in one reply.
- **News on a live incident** ("here's the latest", "we rolled back", "still failing"): do Step 4 and say whether the severity changed.
- **Finished incident** ("write the postmortem", "RCA", "write-up", or the input already shows the recovery): do Step 5.

## Step 2: Read the input and sort the facts

Read everything the user gave you. Sort it into known (stated in the input), suspected (a theory the input does not confirm) and unknown.

- Use times exactly as written, in the zone written. Never convert zones or add one the input lacks. If the input mixes zones, keep each time's own label.
- Quote the input's figures (error rate, ticket count, users affected). Never invent a number, name, ticket id, customer, cause, fix time or ETA. Where the input is silent, write "not known yet".
- Call a cause "confirmed" only when the input shows evidence for it. Otherwise call it "suspected".
- Work out durations and day counts from the times given and show both ends: "09:05 to 10:40 = 1 hour 35 minutes", "Oct 28 to Nov 9 = 12 days".
- Keep secrets, tokens and customers' personal data from pasted logs out of every draft.
- A thin input such as "production is down" is still a full job. Rate it on what was said (if nothing says how bad it is, write "provisional SEV2 until scope is confirmed" and what would make it SEV1), mark each assumption, and add a "Find out first" list: what is broken, since when, who is affected, what changed, who is on it. Do not open with questions.

## Step 3: Triage a live incident

1. **Severity.** Use the user's own scale if they gave one (and its labels everywhere), otherwise this one. Pick the level that fits the worst impact the input confirms, not the suspected cause. If the facts sit between two levels, take the higher and say what would let you lower it. Give one sentence of reasoning that cites the user's facts: who is affected, how many, since when, what still works.

   | Level | Criteria | Response |
   |-------|----------|----------|
   | SEV1 | Product or a core function (sign-in, checkout, payments, data access) down or unusable for all or most users; any data loss or security breach | Immediate, all-hands |
   | SEV2 | Major feature degraded or failing for many users; a workaround may exist | Within 15 min |
   | SEV3 | Minor feature affected, or only some users, with a workaround | Within 1 hour |
   | SEV4 | Cosmetic or low impact | Next business day |

   For a suspected breach or exposed personal data, rate it SEV1, keep customer text to confirmed facts and tell the user to involve security and legal first (these drafts are not legal advice).
2. **Immediate actions.** A numbered list in this order, each with a few words on what it is for:
   1. Stop the harm. If trouble began soon after a deploy, config change or flag change, roll that change back or switch it off first, even if a hotfix looks quick: rollback is the fastest safe way back. Name the exact change from the input. If nothing changed recently, use the fastest other mitigation (fail over, scale up, shed load, disable the failing feature).
   2. Communicate: post the first update, open one channel, assign roles.
   3. Confirm recovery: name the metric or check that must return to normal.
   4. Diagnose: the specific logs, dashboards and checks to look at, based on the symptoms in the input. Save a sample of the failing logs or graphs first.
3. **Roles.** Propose an incident commander, a communications lead and responders. Name a person only if the input shows them already doing that job. Otherwise write "unassigned: assign now".

## Step 4: Status update

Write updates the user could post right now: what is happening, who is affected, what is being done, when the next update comes. No guesses about the cause, no blame, no promised fix time.

- **Next update:** start from the current time if the user gave it, otherwise the latest clock time in the input, and add the cadence: 30 minutes for SEV1, an hour for SEV2, "when the status changes" for SEV3 (latest message 09:12 UTC plus 30 minutes: "next update by 09:42 UTC"). With no clock time in the input write "in 30 minutes". Never write "soon" or "as we learn more".
- **Status:** Investigating, Identified, Monitoring or Resolved. Identified only if the input confirms the cause. Monitoring once a fix is in. Resolved only when the user says the signal that showed the problem is back to normal. If the input does not say whether it is fixed, assume it is ongoing and say so.
- Write the **internal update** every time and the **customer update** whenever customers are affected or the user asks. Give each as plain text in its own code block.
- **Actions taken** lists only what the input says was done. Never claim a rollback or fix is under way unless the input says so. **Next steps** lists what happens next, with an owner only if the input assigns that task to that person.
- When Resolved, both updates say how recovery was confirmed and that a review will follow. The internal one adds what fixed it and what is left to clean up, the customer one what customers can do now.

Internal update:

```
INCIDENT UPDATE: <short title>
Severity: SEV<n> | Status: <Investigating | Identified | Monitoring | Resolved>
Impact: <who or what is affected, with the input's figures>
Last updated: <time> | Next update: <time or interval>

Current status:
<two to four sentences on what is known now; a cause marked suspected unless confirmed>

Actions taken:
- <only what the input says was done>

Next steps:
- <what happens next, with an owner if the input names one>

Timeline:
- <HH:MM> <event from the input>
```

Customer update: plain words, no severity label, no internal system names, no promised fix time, and no cause or vendor blame unless the user confirmed it can be shared. With only a suspected cause, write "we are investigating", never "we have identified the cause". Write nothing about charges, refunds, data or orders the input does not state, even as reassurance. Never "shortly". If all customers are affected, never "some".

```
<Feature or product>: <what customers see, in plain words>
Status: <Investigating | Identified | Monitoring | Resolved>
<Two to four sentences: what customers experience and since when, that we are working on it, a workaround only if the input gives one.>
Next update: <time or interval>
```

## Step 5: Postmortem

Build it only from the input, including any earlier updates the user pasted. If there are no incident details at all, call `clarify` once to ask for the timeline or chat thread. If they have nothing, give the outline below with every section marked "not provided" and a list of what to collect.

Blameless rules:
- Describe systems, process and the information people had at the time. Never write that a person caused, forgot, missed, ignored or should have done something, and avoid "human error".
- If the input blames someone, do not repeat it. Anything only in a blame remark is suspected, not fact. Restate it as the gap that let it happen: no required review, no test, a manual step, no alert.
- In the timeline and analysis refer to people by role ("the on-call engineer", "the engineer who shipped the change"). Use a name only for an action item's owner or in Authors.

Write the whole document in the reply as normal markdown (not inside a code block), in this shape:

```
## Postmortem: <incident title>
**Date:** <from the input, or "not given"> | **Duration:** <first impact to full recovery, with both times> | **Severity:** SEV<n> (given or proposed)
**Authors:** <names from the input, or "not given"> | **Status:** Draft

### Summary
<Two or three plain sentences: what broke, for whom, for how long, and what fixed it.>

### Impact
- Users affected: <figure from the input, or "not measured">
- Duration of impact: <start to end>
- Business impact: <figure from the input, or "not measured">

### Detection
<How it was noticed, how long after the first impact, and whether any alert fired.>

### Timeline (<zone as written, or "times as written">)
| Time | Event |
|------|-------|
| <HH:MM> | <event> |

### Root cause
**Trigger:** <what changed or failed> (confirmed or suspected)
**Why it was possible:** <the gaps in process, tooling or design that let it happen or go unnoticed>

### Why chain
1. Why did <symptom>? Because <...>

### What went well
- <from the input; omit the section if there is nothing>

### What went poorly
- <from the input>

### Action items
| Action | Owner | Priority | Due |
|--------|-------|----------|-----|
| <specific, checkable action> | <name from the input, or Unassigned> | P0/P1/P2 | <date from the input, or Not set> |

### Lessons learned
- <two to four takeaways grounded in this incident>
```

- **Timeline:** every dated event from the input, in time order. Add no event or time that is not in the input. An event with no time goes in a last row marked "time not recorded".
- **Why chain:** ask "why" up to five times, each answer taken from the input, and stop at a gap in process, tooling or design the team can change. If the input supports fewer than five, stop there and say what is unknown.
- **Action items:** each is specific and checkable ("Alert when the payment error rate stays above 2% for 5 minutes", not "monitor better") and ties to a cause, a detection gap or a slow recovery. Owner and due date come only from the input: if nobody took an item on, the owner is "Unassigned" and the due date "Not set". Never give an item to someone who did not volunteer. You may add up to three proposed items the input points to: mark them "Proposed", owner Unassigned. Priority is your proposal (P0 stops a repeat, P1 shortens detection or recovery, P2 hygiene).

## Step 6: Reply

No preamble (not even about loading a skill) or recap: start with the first deliverable. Put every deliverable in the reply, in full. Make a file only if the user asks for one: write the text in the reply first, then load the built-in `docx` or `pdf` skill with `skill_view` to produce it.

- **Live incident**, in this order: Severity and reason; Do now; Roles; Internal update; Customer update (when needed); Assumptions and unknowns, with "Find out first" if the input was thin; a last line "Drafts only: nothing has been posted or sent."
- **Update:** the new update or updates, a line on whether the severity changed, then assumptions.
- **Postmortem:** the full postmortem, then "Gaps to fill before sharing": what the input did not cover (business impact, authors, owners, due dates).

## Connected apps (optional)

Use an app (Sentry, Datadog, PagerDuty, Slack, Jira) only if the user asks; never try to connect one.

## Hard rules

- Facts come only from the user's input or an app they asked you to use. Everything else is a labelled assumption.
- Blameless: systems and process, never a person.
- Name a person as owner or role holder only if the input gives them that task.
