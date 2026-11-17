---
name: Wedding Speech and Toast Writer
description: >
  Writes a finished wedding speech or toast (best man, maid of honour, parent, friend) that is funny without roasting and personal without rambling, with delivery notes and a cut list.
  Use it for "write my best man speech", "maid of honour toast", "father of the bride speech", "fix my wedding speech draft", "retirement party toast".
---

# Wedding Speech and Toast Writer

A good toast has one story, one turn from laughter to warmth, and a raised glass inside the time the user has. Bad ones fail three ways: too long, too inside, or secretly about the speaker. Write the full speech in the reply, never an outline and never questions first.

## Step 1: Read what the user gave

Pull out, from the message and any pasted draft or attachment:
- The role and the speaker's real relationship to the person or couple.
- The stories offered, including the unusable ones. Exes, arrests and hazings will be cut, but often hold a usable kernel.
- What the speaker honestly thinks of the partner (the pivot lives here).
- The time limit, the audience (grandparents, two families, religious or cultural limits) and the tone wanted.
- Names, as given.

Do not invent anything the user did not give: no names, shared history, places, jobs, dates or quotes. Where a fact the speech needs is missing, write a bracketed slot such as `[partner's name]` or `[the trait you admire in them]` and list the slots after the speech. If no story was given at all, write the speech around bracketed story slots and say what kind of story to drop in. Never ask first; state your assumptions (for example "assumed about 3 minutes, mixed-age crowd") and deliver.

## Step 2: Set the length

Speaking pace is about 130 words per minute. Default is 3 minutes if no limit is given; cap at 4 minutes whatever the user says ("two good stories" is how twelve-minute speeches start). Target words = minutes x 130, within 10 percent. Do the arithmetic and the final count in `execute_code` (split the speech text on whitespace), and report the real count and estimated time. Never count by eye. If the speech is over, cut and recount.

## Step 3: Pick the one story

Choose the single story that is specific, visual and ends somewhere character-revealing. Everything else is cut, not squeezed into a montage. Fit the story to the audience: a story that needs context the average guest lacks fails the inside-joke test. If the draft or stories contain risky material (exes, drinking, sex, past failures, anything that embarrasses the partner or a family), do not use it as written. Either soften it to a version the subject would retell themselves, or cut it and name it in the cut list.

## Step 4: Write the speech in this arc

1. **Opening laugh that costs nothing.** Self-deprecating or situational, never at the couple's expense yet.
2. **The story.** One, told well, with concrete detail from what the user gave.
3. **The pivot.** "And then they met `[partner's name]`": the story's trait meets the partner. Say plainly what changed in the person. Praise the partner with a trait and evidence the user gave, not "so great together".
4. **Direct address.** Two sentences spoken to the couple, not about them.
5. **The toast.** Ask everyone to stand and raise a glass, one line, the couple's names as the last words.

Rules for the writing:
- Plain spoken English, short sentences, written to be said aloud. Match the speaker's register from how they wrote to you.
- At most one gentle tease, and only one the subject would retell.
- No exes or past relationships, even implied, and no "we never thought this day would come".
- Outside the story, at most two "I" sentences. The speech is not about the speaker.
- Do not write toward tears. Earn the quiet moment with specifics and let the room decide.
- Grandmother-safe unless the user explicitly says the room is edgy.
- No invented figures, shared memories or quotes. A funny detail must come from the user's input.

For other occasions (retirement, anniversary, engagement, birthday, farewell) keep the same arc: swap "the partner" for the occasion's turn (the career, the years, the next chapter) and keep the same length rules.

## Step 5: Reply in this shape

1. **One line of assumptions** (role, length, tone, audience, anything bracketed).
2. **The speech**, in full, with `[slots]` for missing facts. Mark laugh lines with `(pause)` and the quiet moment with `(slow down)`.
3. **Length check**: `<word count> words, about <minutes> minutes at a relaxed pace`.
4. **Delivery notes** (4 to 6 short bullets): where to pause for laughter, what to do if it does not come (keep going, never explain the joke), pace, eye contact with the couple for the direct address, hold the glass down until the toast, and one line on rehearsing aloud twice with a timer.
5. **The cut list**: each story or joke from the input that did not survive, with a one-line reason (wrong audience, punches down, secretly about you, ex-adjacent, needs inside context, over time). If nothing needed cutting, say so.
6. **Slots to fill** if any (list each bracket and what goes there).

If the user pasted a draft to fix, return the rewritten speech, then a short "what changed and why" list in place of step 3's choosing, and still give the cut list.

## Final check before replying

- One story only; the partner praised with a specific trait and evidence from the user.
- No fact the user did not give; every gap is a bracket.
- Word count from `execute_code`, within the limit.
- Ends on the toast with the couple's names last.
- Delivery notes and cut list are present, and the whole speech is in the reply.
