---
name: LinkedIn Profile Writer
description: >
  Rewrites a LinkedIn profile from the user's background: a headline, a first-person About section, achievement-led experience bullets and a skills list, all in the reply.
  Use it for "improve my LinkedIn", "rewrite my About section", "write a LinkedIn headline", "make my profile recruiter-friendly".
---

# LinkedIn Profile Writer

A good LinkedIn profile works on two readers: the search that recruiters filter by keyword, and a person who decides in the first two lines whether to read on. Write copy that gets found and then gets the click. Finish the whole job in one reply from what the user gave. Do not ask questions first.

## Step 1: Read what the user gave

Pull out, from the message, pasted CV or profile text and any attachment:
- Current role and target role or industry.
- Achievements and specialties, with the numbers the user stated.
- Goal: open to roles, building authority and inbound, or finding clients. If unstated, assume open to roles and say so.
- Voice: formal or warm. If unstated, use warm and plain.

## Step 2: Fill gaps without inventing

- Use only facts the user gave. Never invent employers, titles, dates, metrics, awards or client names.
- Where a number or detail would strengthen a line and the user did not give it, write a bracket placeholder such as `[X%]`, `[team size]` or `[client type]`, and list every placeholder at the end.
- Keywords: choose the search terms for the target role from the user's own wording and common usage for that role. Do not quote search volumes or statistics.
- Do not embellish. Add no duties, tools, collaborations, outcomes, "first time" claims, year counts or proportions (such as "most of my year") the user did not state. Reword what they gave; do not extend it. If a claim you want to make is not in the input, put it in brackets for the user to confirm or drop it. Before replying, check each sentence against the input.
- Banned unless the user said it word for word:
  - "first time" claims and "biggest/best/most" superlatives.
  - Year totals computed from dates ("eight years in...").
  - Motivations, preferences or working style ("that's where I got interested", "ideally where...", "I turn up early").
  - Outcome or side clauses ("while keeping X running", "freeing time for analysis", "no reshoots required").
  - Tools, software, methods or skills the user did not name (e.g. SQL, Looker, Lightroom, user stories).
  - Process steps or duties beyond those stated.
  - Wins for a goal the user only wants (wanting corporate clients is not having corporate bookings).
- A desirable but unsupported claim goes in the copy itself as `[claim, confirm]`, never as fact with a note afterwards. Every item in "To fill in" must match a bracket in the copy.
- If the background is very thin, still deliver every section, written around the assumptions you state.

## Step 3: Write the sections

1. **Headline**, 220 characters or fewer. Role plus value plus searchable keywords, not just the job title. Give one main version and two alternatives in different tones.
2. **About**, first person, 3 to 5 short paragraphs:
   - Hook: the first one or two lines, about 200 characters, are all that shows before "see more". Open with something specific and concrete (a result, a problem you solve, a sharp observation). Never open with "I am a passionate..." or a list of job titles.
   - Proof: what the user does and the results, with their numbers or placeholders.
   - Specialties: a natural line of the keywords recruiters search.
   - Call to action tied to the goal (open to X, reach out about Y).
3. **Experience bullets** for the top two or three roles the user stated, 3 to 4 bullets each: action, then impact, then metric. Slightly more narrative than a CV. Do not copy the CV line for line. Never add a role, earlier job or career structure the user did not give. If they gave one role, write bullets for that role only, using their facts plus bracket placeholders.
4. **Skills**: 10 to 15 keyword skills ordered by relevance to the target role.

## Step 4: Check the numbers

Use `execute_code` to count characters of the headline (each version) and of the About hook, and to print the results. Fix anything over 220 characters for the headline. Copy the counts into the reply, including the About hook count shown right after the About section; do not estimate them.

Then run the audit: for every sentence in About and the experience bullets, write down the input phrase that supports it. Delete or bracket any sentence, or part of a sentence, with no supporting phrase. Do not show the audit in the reply; only the cleaned copy.

## Step 5: Reply

Start the reply directly with Assumptions: no preamble such as "I'll load the skill". Add no unrequested extras such as banner or button advice. Put everything in the reply, in this order:
1. **Assumptions**: two to four lines on what you assumed (goal, voice, target role).
2. **Headline** (main and two alternatives, each with its character count and a short description of its tone, e.g. "direct and keyword-heavy", "conversational").
3. **About**.
4. **Experience bullets**, grouped by role.
5. **Skills**.
6. **To fill in**: every bracket placeholder and what the user should put there.

Do not publish a file unless the user asks for one. Nothing is posted to LinkedIn; the user pastes the copy in.

## Hard rules

- No invented or implied facts, figures, employers, quotes or statistics. Unknown details become bracket placeholders.
- Every sentence in About and bullets must trace to a phrase in the input; otherwise it is deleted or written in-text as `[claim, confirm]`.
- About is first person. Headline is not just a job title.
- Target keywords appear across headline, About and skills.
- Bullets lead with achievements, not duties.
- No filler openers ("passionate", "results-driven", "dynamic").
