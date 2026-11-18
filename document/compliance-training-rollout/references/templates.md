# Templates: Compliance Training Rollout

Fill every <placeholder> from real data: the procedure, the recording, the staff list
and the user's answers. If a fact is missing, leave it out; never make one up.

## Objectives and summaries document (step 1)

```
<Procedure name> · <document number, version, date> · Training objectives (draft for sign-off)

Learning objectives (4–6). By the end, everyone can:
1. <action verb + what, e.g. "Isolate every energy source on their machine before work">
...

Step by step, in plain words
| # | Procedure says (section/page) | In plain words | Safety-critical |
| 1 | <exact wording, short> (§<n>) | <one or two short sentences, ~8th-grade reading level> | Yes / No |
...

Where the recording and the document differ: <each difference, or "none">
Terms to keep exactly (glossary): <term> – <meaning>; ...
Sign-off: ______________ (safety lead)   Date: ________
```

Rules: plain words, short sentences, active voice, "you". Keep numbers, limits, PPE and
equipment names exactly as written. Mark a step safety-critical when the procedure
says so, or when skipping it could hurt someone; list your reasons for the safety lead.

## Glossary (for every translation)

| Term (source) | Meaning | <Language 1> | <Language 2> | Checked by |
|---|---|---|---|---|

Translate each term once, have the fluent speaker confirm it, then use exactly that
term in the deck, script, subtitles, quiz and poster.

## Deck outline (step 2, `generate_design_slides`)

```
Title: <Procedure name>: what changes and what you must do
Audience: <shift workers / roles>, plain language, one idea per slide, large text.

1. Title slide: procedure name, effective date
2. Why this matters: <the risk the procedure controls, from the procedure>
3. What you will be able to do: the objectives
Section A: <first group of steps>
  - One slide per step: the step, why, the procedure's term; safety-critical steps in a
    red callout "Safety-critical"
  - Knowledge check: one multiple-choice question on this section (answer on next slide)
Section B, C ... same pattern
N-2. Who to ask: <role/contact from the procedure>
N-1. Your quiz: pass mark <80>%, deadline <date>, portal link
N. Summary: the key steps in one view
Diagrams: use the procedure's own figures (<page refs>); do not draw new safety diagrams.
```

## Explainer script (step 3, about 3 minutes, 380–450 words in English)

```
[Hook, 15 s] <what the procedure protects people from, in one or two sentences>
[What changes, 20 s] <what is new or different>
[The steps, 2 min] <each step in plain words, in order; say "This one is
safety-critical" before each critical step>
[Remember, 20 s] <the 2–3 things never to skip>
[What to do now, 15 s] Watch, then take the quiz on the training portal by <deadline>.
Questions? Ask <role> or join a Q&A session for your shift.
```

Write for the ear: short sentences, no brackets or abbreviations a voice cannot read.
`script-<code>.json`: `{"language": "<Language>", "code": "<ISO code>", "segments": ["<one paragraph per part>", ...]}`.

## Presenter image prompt (step 3, `image_generate`)

```
Photorealistic head-and-shoulders portrait of a friendly, professional training
presenter, mid-shot, facing camera, neutral expression with a slight smile, wearing
<workplace-appropriate clothing, e.g. a hi-vis vest>, plain softly lit <workplace>
background, even lighting, mouth closed, no text, no logos. A fictional person, not
resembling any real individual.
```

On screen and on the portal, label the presenter "AI presenter".

## Quiz (step 4, Typeform, one form per language)

- Title: "<Procedure name>: quiz (<Language>)". Intro: "10 questions. Pass mark
  <80>%. You can retake it."
- Q0 (required, short text, ref `staff_id`): "Your work email or staff ID".
- Hidden field `language` = <Language>.
- Q1–Q10 (required, multiple choice, single answer, refs `q1`…`q10`), choices with refs
  `q1_a`, `q1_b`, `q1_c`, `q1_d`; same order and refs in every language.
- Each question: one objective, one correct answer, three plausible wrong answers from
  real mistakes; no "all of the above", no trick wording. At least one question per
  safety-critical step.
- End screen: "Thank you. Your result is recorded. If you did not pass, review the
  video and try again."

`key.json`: `{"q1": "q1_c", ..., "q10": "q10_a"}` (choice refs, same for every language).

Question sheet for the safety lead:
| # | Objective | Question | Correct | Wrong 1 | Wrong 2 | Wrong 3 | Procedure ref |

## Tracker workbook (step 4, on SharePoint)

**Tracker** sheet, from `tracker.py update` (`tracker/tracker.csv`):
Name · Email · Staff ID · Manager · Shift · Language · Status (Passed / Failed (retake)
/ Not started) · Best score % · Attempts · Passed on · Last attempt · Overdue

**Dashboard** sheet, live formulas (Tracker rows 2–<n>):
| Manager | Staff | Passed | Failed | Not started | % passed |
| <name> | =COUNTIFS(Tracker!D:D,A2) | =COUNTIFS(Tracker!D:D,A2,Tracker!G:G,"Passed") | =COUNTIFS(Tracker!D:D,A2,Tracker!G:G,"Failed (retake)") | =COUNTIFS(Tracker!D:D,A2,Tracker!G:G,"Not started") | =IF(B2=0,0,C2/B2) |

The same table by Shift (column E), and a total row. Add a bar chart of % passed by
manager. Check the formulas match `tracker.py`'s `dashboard` numbers.

**Sign-offs** sheet: Item · Language · Approved by · Role · Date · Notes
(objectives, script, each language's video/subtitles/deck, quiz, poster, portal).

## Portal prompt (step 5, `sites` action: create)

```
Build a simple, fast training portal for "<Procedure name>" for <company>'s staff.
Mobile first (most people open it from the poster's QR code on a phone).
- Top: the procedure name, deadline "<date>", and a language picker: <languages, each
  written in its own language>. Each language has its own page at /<code>
  (right-to-left layout for <rtl languages>).
- Each language page, in that language only:
  1. The explainer video (<video link>) with subtitles (<subtitle file>) on by default,
     and the caption "AI presenter".
  2. "Read the slides": <deck link>.
  3. A big button "Take the quiz" to <Typeform link for that language>.
  4. Who to ask: <role / contact>, and the Q&A sessions <times>.
- No staff names, scores or answers anywhere. No login.
- Footer: "<procedure number, version>. Training material; the procedure document is
  the authority."
```

## Poster file (step 5, `poster.py`)

`poster-<code>.json`:
```
{"language": "<Language>", "code": "<ISO code>",
 "title": "<procedure name, translated>", "subtitle": "<one short line>",
 "steps": [{"text": "<step, under ~90 characters>", "critical": true|false}, ...],
 "critical_label": "<'Safety-critical' translated>",
 "scan_label": "<'Scan to start your training' translated>",
 "deadline_label": "<'Complete by <date>' translated>",
 "portal_url": "<live portal link for this language>",
 "footer": "<company · procedure number and version · month year>"}
```

## Manager announcement (step 6, Outlook, under 180 words)

```
Subject: Training needed by <deadline>: <procedure name>

Hi <manager first name, or "all">,

<Procedure name> takes effect on <date>. Everyone in your team needs to complete
short training and pass a 10-question quiz by <deadline>.

What: a 3-minute video, slides and a quiz, in <languages>.
Where: <portal link> (also on the QR posters going up on the floor).
Why: <one line on the risk, from the procedure>.

Q&A sessions on Teams (please share with your shift):
- <Shift>: <day, date, time, time zone>
...

Each Monday you will get a private note listing anyone in your team who has not
passed yet. Questions: <contact>.

<sender name>
<sign-off>
```

## Q&A invite

Title: "<Procedure name>: Q&A (<shift>)". 30 minutes, Teams meeting. Body: one line on
the purpose, the portal link, "Bring your questions; no preparation needed."

## Weekly manager reminder (private Teams chat, under 80 words)

```
Hi <manager first name>, <procedure name> training is due by <deadline>
(<n> days left / overdue since <date>). Not passed yet in your team:
- <name> (<Not started / Failed, best <score>%>)
...
Portal: <link>. Thank you for helping them finish.
```

## Completion report (`generate_document`)

1. Summary: procedure, version, effective date, staff trained, 100% passed on <date>.
2. Materials: languages; video, deck, quiz and poster versions; portal link.
3. Sign-offs: from the Sign-offs sheet.
4. Results: by manager and by shift (staff, passed, average best score, first and last
   pass dates); number of retakes.
5. Q&A sessions held: dates and shifts.
6. Records: where the tracker and answer key are kept on SharePoint.
