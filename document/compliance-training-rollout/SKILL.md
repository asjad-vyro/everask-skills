---
name: Compliance Training Rollout
description: 'Turns a new procedure into training for every shift in every language: learning objectives, a short deck with knowledge checks, an avatar explainer video dubbed and subtitled per language, a quiz, a training portal and floor posters. It then tracks who has passed in Excel on SharePoint and drafts weekly reminders to managers. Just share the procedure, like "our new lockout/tagout SOP".'
---

# Compliance Training Rollout

Turns one new procedure into a complete training rollout for a large, multilingual
workforce: learning objectives the safety lead signs off, a deck, a three-minute avatar
explainer dubbed and subtitled per language, a 10-question quiz per language, a portal
with everything in each language, a floor poster with a QR code, a completion tracker
on SharePoint, and the announcement to managers with Q&A sessions across shifts. It
never publishes a translation a fluent speaker has not checked, never changes the
procedure's meaning, never sends an email or invite without approval, and never marks
anyone complete without a passing quiz response.

## When to Use

- "Roll out training on our new lockout/tagout procedure to all three shifts."
- "Turn this SOP into training in English, Arabic and Urdu."
- "Make a quiz and a tracker for the new forklift procedure."
- "Update the training tracker" / "Who still hasn't passed?"
- "Send this week's reminders to the managers."

## Start Here

When this skill is open, treat the user's message as the start of the rollout, not as
a plain question. "Our new hand-hygiene SOP", "train everyone on this" with a PDF
attached, or a SharePoint link all mean: run this pipeline for that procedure.

- Begin at step 1 straight away. Do not ask "do you want objectives first?": that is
  what this skill does.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. They protect workers' safety, translations and the user's name in
  front of every manager, so never skip them, even if the user says "do everything".
- The only thing needed to start is the procedure (an attached file or a SharePoint
  link or name). If it is missing, ask for it in one short `clarify` question, and say
  a recorded walkthrough (Teams recording) helps if there is one. Then go.
- Returning users: "update the tracker" or "who hasn't passed" → step 4's tracker
  update; "send the reminders" → the reminder part of Automation; "add Polish" → step 3
  onward for the new language only.

## Prerequisites

Check each app at the step that needs it with `search_connector_tools`, load the
actions with `expand_connector_tools`, and when a required one is missing call
`report_missing_connector_access` for it instead of explaining in prose.

| App | For | Needed at |
|---|---|---|
| SharePoint | Reading the procedure; storing the tracker, answer key and sign-off log | Step 1 (else an uploaded file), step 4 |
| Microsoft Teams | The walkthrough recording; Q&A meetings; private reminders to managers | Step 1 (optional), step 6, Automation |
| Typeform | One quiz per language | Step 4 |
| Excel | The completion tracker and dashboard (workbook on SharePoint) | Step 4 |
| Outlook | Manager announcement; Q&A invites | Step 6 |
| HeyGen | Only if the user wants their own HeyGen stock avatar; otherwise the built-in avatar video does the job | Step 3 (optional) |

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| The procedure (file, SharePoint link or name) | Start | None: ask |
| Recorded walkthrough (Teams recording) | Never ask again after the start | Use it if given; else the procedure alone |
| Who signs off objectives and script (the safety lead's name) | Step 1 Stop | The user |
| Staff list: name, work email or staff ID, manager, manager's email, shift, language | Step 3 | None: ask (languages are read from it) |
| Languages | Step 3 | The languages in the staff list |
| Deadline | Step 4 | None: ask |
| Pass mark | Never ask | 80% |
| Shift times and time zone for Q&A sessions | Step 6 | None: ask |
| Sender name and sign-off for the announcement | Step 6 | The user's name from their Outlook account |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`, then
continue.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing, except at every **Stop**. Name the procedure in every update ("LOTO
SOP: Arabic dub ready"). Templates, prompts and file shapes are in
`references/templates.md`: read it before step 1. Keep a sign-off log as you go (who
approved what, when) for the tracker workbook and the completion report.

## Procedure

### 1. Objectives

Read the procedure: from SharePoint through the connector, or the uploaded file with
`media_analyze` (PDF, scans) or `read_file`. If there is a recording, fetch it (Teams
recordings sit in OneDrive/SharePoint) and transcribe it with `audio_transcribe`.
Read them yourself; never hand this to `delegate_task`. If the procedure cannot be
opened or read, stop and say so (or `report_missing_connector_access` for SharePoint):
never write objectives from general knowledge of the topic.

Write, with the template: 4–6 learning objectives, and a plain-language summary of each
procedure step, each citing its section or page, with the safety-critical steps marked.
Keep the procedure's own terms (names of equipment, permits, signs); start a glossary of
them for translators. Where the recording and the document disagree, the document wins:
list every difference for the safety lead. Put this in a document with
`generate_document`.

**Stop.** Show the objectives and summaries, side by side with the original wording for
every safety-critical step, and ask the user (or the safety lead) to confirm nothing
changed meaning. Ask who signs off if not yet known. Log the sign-off.

### 2. Deck

Build a short training deck with `generate_design_slides` from the outline in
`references/templates.md`: one idea per slide, the procedure's own terms, a knowledge
check (one question) after each section, safety-critical steps called out. Use the
procedure's own diagrams where the file contains them as images; otherwise point to the
page ("See SOP 4.2, figure 3"). Never redraw a safety diagram from imagination.

### 3. Explainer video

1. Write a three-minute script from the deck (template in references) and check its
   length: put it in `script-en.json` and run
   `python3 "${COMPUTER_SKILL_DIR}/scripts/subtitles.py" --file script-en.json`.
   Cut or add until `length_note` says about right.

   **Stop.** Show the deck and the script to the safety lead (or user) for sign-off
   before anything is recorded. Log it.

2. Ask for the staff list now if you do not have it, and check it:
   `python3 "${COMPUTER_SKILL_DIR}/scripts/tracker.py" check --staff staff.csv --languages "<languages>"`.
   Show the problems it lists (no ID, no manager, a language not requested, duplicates)
   and carry on with what is clean; the user can fix the rest by step 4.
3. Presenter: make one clearly fictional presenter with `image_generate` (prompt in
   references), or use a stock avatar from the user's HeyGen if connected and asked for.
   Never use a photo of the real safety lead or any real person unless the user confirms
   that person's written consent.
4. For each language: translate the script with the glossary (keep meaning, not word
   order); voice it with `text_to_speech` in that language; make the avatar video with
   `video_generate` (the presenter image plus the voice file in `options.audio_url`). If
   the tool limits clip length, record one clip per section and join them with
   `create_timeline`. If no voice exists for a language, use the English video with that
   language's subtitles and say so.
5. Subtitles for each language from its script and the voice length in seconds:
   `python3 "${COMPUTER_SKILL_DIR}/scripts/subtitles.py" --file script-<code>.json --duration <seconds> --out-dir subs`.
6. Translate the deck into each language (one deck per language, right-to-left where
   needed) from the approved English deck.

**Stop.** For each language, a fluent speaker must watch the video with subtitles and
read the deck before either is used. Fix what they flag, then log who checked which
language.

### 4. Quiz and tracker

Write 10 multiple-choice questions from the objectives (template in references): each
tests one objective, every safety-critical step has at least one question, one correct
answer each. Translate them. For each language, create a Typeform with the same
questions in the same order, the same field refs and choice refs, a first required
question "Work email or staff ID" (ref `staff_id`), and a hidden field `language`.
Write the answer key (`key.json`, choice refs) and keep it on SharePoint with the
tracker, never on the portal.

Ask for the deadline if missing. Create the tracker workbook on the SharePoint site
through the Excel connector: a Tracker sheet with one row per person, a Dashboard sheet
with formulas by manager and by shift, and a Sign-offs sheet (layout in references). If
the connector cannot write formulas there, build the workbook with the `excel_*` tools
and save it to SharePoint through the SharePoint connector. Staff data never leaves
SharePoint: not on the portal, not in a `publish_artifact` download, not in a group
channel.

**Updating the tracker** (now, on request, and every Monday): pull every form's
responses through the Typeform connector, save each as JSON, then run
`python3 "${COMPUTER_SKILL_DIR}/scripts/tracker.py" update --staff staff.csv --responses <files, comma-separated> --key key.json --pass-mark 80 --deadline <YYYY-MM-DD> --out-dir tracker`
and write its rows into the Tracker sheet. Its output is the only source of who passed:
never mark anyone complete by hand, from a manager's word or from memory. Show
`unmatched_responses` (an ID nobody on the list has) to the user to resolve.

### 5. Portal and poster

Build the portal with `sites` (`action: create`, prompt in references): a language
picker, and per language the video with its subtitles, the deck, the quiz link, the
deadline and who to ask. The presenter is labelled "AI presenter". No staff names, no
scores, no answer key.

Prepare each language's poster text: the key steps from the approved summaries,
shortened (6 or fewer where possible), safety-critical ones marked, translated with the
glossary.

**Stop.** A fluent speaker checks each language's quiz, portal page and poster text,
and the user checks the portal, before anything is published. Then publish with
`sites` (`action: publish`).

Make each language's poster with the live portal link:
`python3 "${COMPUTER_SKILL_DIR}/scripts/poster.py" --file poster-<code>.json --out-dir posters`
(it lays out right-to-left languages correctly and adds the QR code). Deliver the HTML
posters with `publish_artifact` for A3 printing; scan one QR code before printing.

### 6. Announce

Ask for shift times and time zone if missing. Draft, with the templates:

- the Outlook announcement to every manager on the staff list: what, why, the deadline,
  the portal link, the Q&A times;
- one 30-minute Teams Q&A session per shift in the first week, inside that shift's
  hours, inviting that shift's managers and staff who have a work email.

**Stop.** Show the email, the recipient list and every session time. Send the email
from Outlook and create the invites only after the user approves all three. Then offer
the automations.

## Automation (offer at the end, never set up unasked)

Offer these and create the ones the user accepts with `cronjob` (`action: create`,
`skills` set to this skill's name as you loaded it). Cron runs have nobody to approve,
so each prompt must be self-contained and must leave sending to the user:

- **Every Monday 8:00 until everyone has passed:** update the tracker (step 4), then
  draft one private reminder per manager listing only their staff who have not passed,
  with the deadline (template in references). Reply with the drafts; when the user says
  "send the reminders", send each as a private Teams chat to that manager only, never
  to a group or channel.
- **When the tracker shows everyone passed:** build the completion report
  (`generate_document`, outline in references) from the tracker and sign-off log, save
  it to the SharePoint site, tell the user, and remove the Monday job with `cronjob`
  (`action: remove`).

## Guardrails

- A fluent speaker checks every translation, subtitle, dub, quiz and poster before it
  is published or used. Machine translation alone is never final.
- Simplifying never changes the procedure's meaning; the safety lead signs off the
  objectives and the script. When in doubt, quote the procedure.
- The avatar is a clearly labelled AI presenter, never the real safety lead. No cloned
  face or voice of a real person without their written consent.
- Staff data stays in the tracker on SharePoint. Reminders go privately to each
  manager about their own staff only.
- The tracker records what happened: "Passed" only from a matched quiz response at or
  above the pass mark, computed by `tracker.py`.
- Nothing is sent, published or scheduled without approval: announcement, invites,
  portal, reminders.
- Every fact in the training comes from the procedure or the recording; never add
  rules, limits or steps that are not in them.

## Pitfalls

- Relying on Typeform's own score. A form without scoring logic reports 0 for
  everyone; always pass `--key` so `tracker.py` scores the answers.
- Different choice refs per language. Then one answer key cannot score every form;
  keep refs identical (`q1_a`…`q10_d`) in every language.
- Staff typing their ID differently from the list. Matching ignores case and spaces;
  anything still unmatched goes to the user, never guessed.
- Translating the poster from the English poster instead of the approved summaries.
  Always translate from approved text with the glossary.
- Asking for the staff list, deadline and shift times at the start. Ask each at its
  step.

## Verification

- Every objective, summary and script line traces to a cited part of the procedure,
  and the sign-off log names who approved the objectives, the script and each language.
- Each language has a video, subtitle file, deck, quiz and poster, all checked by a
  fluent speaker, and the poster's QR code opens that language's portal page.
- The tracker's Passed count equals `tracker.py`'s `passed`, and the Dashboard formulas
  add up to the staff count.
- The announcement and invites went only to the approved recipients at the approved
  times.
