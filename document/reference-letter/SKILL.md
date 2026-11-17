---
name: Reference and Recommendation Letter Writer
description: >
  Writes a complete, specific reference or recommendation letter, ready to sign, with a shorter version, for a colleague, student, employee or tenant.
  Use it for "write a reference letter", "recommendation letter for my intern", "character reference", "recommend her for a job, school or tenancy".
---

# Reference and Recommendation Letter Writer

A reference is believed when it is specific: concrete examples beat adjectives, and the reader can tell the writer really knows the person. The result is a full letter in the writer's voice that states who they are, endorses the person clearly and early, backs it with evidence, and is tailored to what the reader is deciding.

## Step 1: Read the brief and decide

Pull these from the user's message and anything pasted or attached:

- **Candidate** and what they are applying for (job, school or programme, grant, tenancy, other).
- **Writer's relationship**: how they know the candidate, in what capacity, for how long.
- **Strengths and evidence**: achievements, results, behaviours, moments, numbers.
- **Reader's priorities**: what the recipient is deciding, what matters to them.
- **Tone and length**: formal letter or email, any word limit. Default: formal letter, about 350 to 450 words.

Do not open with questions and do not stop to wait. If something is missing, write the letter anyway and handle the gap as in Step 2. State your assumptions in a short note after the letter.

## Step 2: Facts rule (no exceptions)

- Use only facts the user gave. Never invent an achievement, number, date, project, quote, job title, employer, grade, tenure or name.
- Where the letter needs a fact you were not given, insert a visible placeholder in square brackets that says what to put there, for example `[describe one project they led and its result]`, `[number of years]`, `[your phone number]`. Keep placeholders short and few; the letter must still read as a real letter around them.
- If the user gave little evidence, write the letter around the facts they did give, plus placeholders for the missing evidence. Never fill the gap with plausible-sounding anecdotes, and never hand back a hollow template of adjectives either: where there is no evidence, say so with a placeholder and add a one-line prompt for the kind of example that would work.
- Do not turn a number the user gave into a stronger claim ("increased sales 12%" must not become "doubled sales"). If you compare the candidate with others ("one of the strongest interns I have supervised"), use it only if the user said or clearly implied it; otherwise put it in as a bracketed option for the writer to confirm.
- Do any arithmetic (tenure from dates, percentages) with `execute_code`, not in your head.

## Step 3: Write the letter

Use this order. It is the shape of the letter, not headings to print.

1. **Opening**: who the writer is, their relationship to the candidate, how long and in what capacity. This establishes credibility to comment.
2. **Endorsement**: a clear recommendation in the first paragraph. Do not bury it.
3. **Evidence**: two or three specific examples (a result, a behaviour, a moment) that show the strengths that matter for this decision. Pick the strengths the reader cares about; leave out the rest. One paragraph per example, each one stating what the candidate did and what came of it.
4. **Comparative context**: where honest and supported, how the candidate stands out. Keep it concrete.
5. **Fit**: tie the strengths directly to what the reader is deciding (the role's duties, the programme's demands, what a landlord needs to know).
6. **Close**: a confident final recommendation, an offer to discuss, and the writer's contact details (placeholders if not given).

Adapt to the kind of reference:

- **Job**: reliability, results, how they work with others, why they are leaving if the user said.
- **School or programme**: intellectual curiosity, quality of work, growth, readiness for the next level.
- **Tenancy**: reliability on rent and communication, care of the property, only what the writer has seen first hand.
- **Character reference** (court, immigration, community): how long and how well the writer knows the person, what they have seen, no claims beyond first-hand knowledge, and no guess at legal outcomes.
- **Grant or award**: impact, track record, credibility with the funder's criteria.

## Step 4: Check before replying

- The writer's credibility is established (relationship, capacity, duration), with placeholders where not given.
- Every strength is shown with an example, not only adjectives such as "hardworking" or "dedicated".
- Every fact in the letter comes from the user's message; everything else is a bracketed placeholder.
- The praise is calibrated: honest, specific, not inflated until it means nothing.
- The recommendation is unambiguous and appears early.
- The length fits any limit the user gave.

## Output shape

The reply itself holds the letter in full. Do not build a file unless the user asks for a .docx or .pdf; then load the built-in `docx` or `pdf` skill with `skill_view` and follow it.

Reply in this order:

1. **The letter**, from the date and salutation (`Dear <name or "Admissions Committee" or "To whom it may concern">`) to the sign-off with `[writer's name, title, contact details]` unless given.
2. **Shorter version** of about 120 to 150 words, for an email or a form field with a limit.
3. **Before you sign**: a short list with (a) each placeholder to fill and what true detail goes there, and (b) any assumption you made (tone, length, relationship, reader). Keep it to a few lines.

## Hard rules

- Never present an invented example as real.
- Never write a one-size-fits-all letter: the evidence is chosen for this decision.
- Never overpraise past believability, and never claim more than the writer's first-hand knowledge covers.
- Letters carrying negative or mixed content (a lukewarm reference) stay truthful and fair; if the user asks for a letter that makes false claims, decline that part and write what can honestly be said.
- Nothing is sent anywhere. The letter is a draft for the writer to review, edit and sign.
