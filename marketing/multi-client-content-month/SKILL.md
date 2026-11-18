---
name: Multi-Client Content Month
description: Plans a month of social posts for one client at a time from their call notes, designs them in Canva on that client's brand kit and puts every post on a Trello board for the client to approve. Approved posts go out on Instagram, Facebook and LinkedIn at their set times, and a Slides report with real numbers is drafted at month-end. Just name the client and month, like "Bloom Bakery, December".
---

# Multi-Client Content Month

Runs a social media manager's month for one client: a brief from this month's client
call, a content calendar in Google Sheets, posts and carousels in Canva on the
client's brand kit, subtitled reels from the client's footage, a Trello approval board
with one card per post, scheduling of approved posts on Instagram, Facebook and
LinkedIn, and a month-end report in Slides built from Supermetrics. It works on one
client at a time and names that client at every step. It never publishes a post that
is not in the client's "Approved" list, never sends an email the user has not
approved, and never invents a number, testimonial or claim.

## When to Use

- "Plan Bloom Bakery's December content."
- "Do next month for Harbour Physio: 12 Instagram, 8 LinkedIn, 4 reels."
- "Check approvals for Bloom Bakery and make the changes they asked for."
- "Schedule everything Bloom Bakery approved."
- "Send Harbour Physio their November report."

## Start Here

When this skill is open, treat the user's message as the start of this pipeline, not
as a request for content ideas. "Bloom Bakery", "December for Harbour Physio" or "do
next month for my bakery client" all mean: run this pipeline for that client and
month. The user should not have to spell out the steps.

- Begin at step 1 straight away. Do not ask "do you want me to plan their posts?":
  that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. They protect the client relationship and the client's accounts, so
  never skip them, even if the user says "do everything" or "just post it".
- The only thing needed to start is the client's name. The month defaults to next
  month. If no client is named, ask "Which client, and which month?" in one short
  `clarify`, then go.
- Returning users jump in at a later step for that client: "check approvals" → step
  4b, "schedule what's approved" → step 5, "publish today's posts" → step 5, "send the
  report" → step 6. Do not start over.

## Prerequisites

Connected apps (check each with `search_connector_tools` at the step that needs it,
not all at the start; when a required one is missing, call
`report_missing_connector_access` for it instead of explaining in prose):

| App | For | Needed at step |
|---|---|---|
| Fathom | Goals and promotions from this month's client call | 1 (else the Fathom recap email in Gmail, pasted notes, or a recording via `audio_transcribe`) |
| Google Sheets | The client's sheet: profile and content calendar | 1 on |
| Canva | Posts and carousels on the client's brand kit | 3 |
| Trello | One approval board per client, one card per post | 4 |
| Gmail | Approval request, report email | 4, 6 |
| Instagram / Facebook / LinkedIn | Publishing approved posts (only the client's channels) | 5 |
| Supermetrics (`supermetrics_mcp_call`) | Organic numbers for the report and last month's best posts | 1 (optional), 6 |
| Google Slides | The monthly report (else `generate_design_slides`) | 6 |
| Google Drive | The client's brand guide, footage and past assets | Optional |

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Client name | Start | None: ask |
| Month | Never ask | Next month |
| Client's knowledge base: brand guide, tone, pillars, past winners, offers, products, words to avoid, country and time zone | Step 1, first run for this client only | None: ask once, store in the client's sheet |
| Canva brand kit for this client | Step 3, first run only | None: ask which kit |
| Channels and volume | Step 2 | Last month's mix from the client's sheet; first month: ask |
| Posting days and times | Never ask | Script defaults, or the times of last month's best posts |
| Client footage / approved stock for reels | Step 3 | None: ask when reels are planned |
| Approver name and email | Step 4, first run only | None: ask once, store in the sheet |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`
message, then continue.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing between them, except at every **Stop**. Start every update with the
client's name and month ("Bloom Bakery · December: calendar ready"). Templates for
the sheet, brief, captions, Canva and reel briefs, Trello cards, emails and the
report are in `references/templates.md`: read it before step 1.

One client per run. If the user names two clients, finish (or reach a Stop for) the
first, then start the second as a separate run with its own sheet, brand kit, board
and accounts.

## Procedure

### 1. Brief

Find the client's Google Sheet "Content: <Client>" (create it on the first run with
the tabs in `references/templates.md`). On the first run, ask for the knowledge base
in one `clarify` (or read the brand guide the user shares with `media_analyze` or
`read_file`) and write it to the "Profile" tab. Offer to remember the sheet link with
`memory` so the next month starts faster.

Then gather, for <Client> only:

- **This month's client call:** use the Fathom connector (`search_connector_tools`
  "fathom"); search for the latest meeting with the client's name. If Fathom is not
  connected, search Gmail for the Fathom recap email; else ask the user to paste the
  notes or upload the recording and transcribe it with `audio_transcribe`. Pull
  goals, promotions with dates, launches, and anything to avoid.
- **Key dates:** public holidays and observances in the client's country for the
  month, from `web_search` (keep the source link), plus launches and events from the
  call.
- **Last month's best posts:** top posts by engagements from Supermetrics; if it is
  not available, from the platform connector's insights; else write "not available".

Every goal, promotion and date must come from the call notes, the Profile tab or a
source read in this run, with where it came from noted. Never fill gaps from memory
and never hand this step to `delegate_task`. If there are no call notes at all, say
so and ask the user for the month's goals; do not invent them.

Write the brief (template in references) to the sheet's "Brief <Month>" tab.

**Stop.** Show the brief and ask the user to correct it. Then go straight on.

### 2. Calendar

Use the volume the user gave; else copy last month's mix from the sheet; on a first
month, ask for channels and volume (e.g. 12 Instagram, 8 LinkedIn, 4 reels). Write the
plan to a JSON file and lay out the dates:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/plan_calendar.py" --file plan.json
```

It spreads each channel's posts evenly over its posting days, interleaves formats,
rotates the client's pillars by weight, keeps posts off `avoid_dates`, and tags rows
that fall on key dates or inside a promotion. Read its `warnings` (too few slots, a
key date with no post) and fix the plan or tell the user. Use its dates and times as
they are; move a post by hand only for a reason in the brief (a launch day), and say
so.

Then write, for every row, the hook, caption, hashtags and call to action in the
client's voice from the Profile tab (rules in references). Promotions only on rows
inside their dates. No claims, prices or results the brief or Profile does not state.
Write the rows to a new "Calendar <Month>" tab with the columns in references,
status "Planned".

**Stop.** Show the calendar (link plus a short table) and wait for changes or a go.
Then go straight on through steps 3 and 4.

### 3. Make the posts

- **Posts and carousels:** in Canva, on <Client>'s brand kit only (find it with the
  Canva connector; ask which kit on the first run and store its name in Profile).
  One design per row from the design brief in references; export PNGs (one per
  carousel slide) and put each link in the row's "Media" column.
- **Reels:** from the client's footage or stock the client or user has rights to.
  Build each with `create_timeline` and `apply_timeline_edit` (cuts to the hook,
  burned-in subtitles, the client's fonts and colours, music only from a source the
  user confirms they may use). Use `video_sanitize` if a clip will not load. With no
  footage, ask for it; do not generate people or fake footage. AI-generated b-roll
  only if the user asks, labelled as AI where the platform requires.
- If Canva is not connected, call `report_missing_connector_access` for Canva. Offer
  `image_generate` with the Profile's colours and fonts only as a stopgap the user
  accepts, and mark those rows "Not on brand kit".

Set each row's status to "Made".

### 4. Approval

**4a. Send for approval.** On the first run, ask for the approver's name and email
and store them in Profile. Use Trello (`search_connector_tools` "trello") to find or
create the board "<Client> · Content approvals" with the lists in references. Create
one card per post in "For approval": title, caption, hashtags, call to action, date
and time as the due date, the media attached. Write each card's link into the sheet,
status "For approval".

Draft the approval email to the approver in Gmail (template in references) with the
board link.

**Stop.** Show the draft (and the board invite, if the approver is not on the board
yet). The user sends the email; send it or invite the approver only if the user says
so. Never write to the client from the skill on its own.

**4b. Check approvals** (when the user asks, or in the daily automation). Read every
card on the board (list, comments, content) and the sheet's rows into a JSON file,
then run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/approval_check.py" --file approvals.json
```

Act on each `action`: `record_approval` → write the `hash` into the row's "Approved
hash" column, status "Approved"; `changes_requested` → make the change the client
asked for (Canva, timeline or caption), update the card, clear the hash, move the card
back to "For approval" with a comment saying what changed; `needs_reapproval` → move
the card back to "For approval", clear the hash, tell the user; `out_of_sync` → make
the card match the sheet; `nudge` / `overdue` → list for the user. The script's
result is the only source for what is approved; never decide that from memory.

### 5. Schedule

Run `approval_check.py` again. Only posts with `ready_to_schedule` (or freshly
`record_approval`) can go out; everything else stays.

**Stop.** Show the list of posts that will be scheduled (date, time, channel, card)
and wait for the user's go.

Then, for each post on the client's own accounts (check the connector is the client's
page or profile, not another client's): if the Instagram, Facebook or LinkedIn
connector can schedule ahead, schedule it at the calendar time and mark the row
"Scheduled". If it can only publish now, mark the row "Approved, publish on the day";
when the user says "publish today's posts" on that day, rerun the check, show the
due list, and publish the unchanged approved posts after the user says go. Write the
live post link into the sheet and move the card to "Published".

### 6. Monthly report

For <Client> and last month, pull from Supermetrics (`supermetrics_mcp_call`), per
channel: reach, impressions, engagements, followers at start and end, and post-level
reach and engagements with links. Copy the numbers as returned into a JSON file and
run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/report_numbers.py" --file metrics.json
```

Use only its figures (it marks gaps "not tracked" and never rounds up). If
Supermetrics is unavailable or the client's accounts are not linked there, stop this
step and tell the user; never estimate. Build the deck (outline in references) in
Google Slides if connected, else `generate_design_slides`; charts with `render_chart`
from the script's numbers. "What we'll do next month" comes from next month's brief or
the user's notes.

**Stop.** Show the deck and the email draft (template in references). Send from Gmail
only after the user approves; otherwise leave the draft.

## Automation (offer at the end, never set up unasked)

Offer these, and create the ones the user accepts with `cronjob` (`action: create`,
`skills` set to this skill's name as you loaded it). Each prompt lists the clients by
name and their sheet links, and handles them one at a time, never mixing one client's
files, kit, board or accounts with another's. Cron runs have no one to ask, so they
only prepare and draft:

- **25th, 9:00:** for each client, run steps 1 and 2 for next month: the brief and a
  "Draft" calendar tab. Reply with the links for the user to review; designs and cards
  are made after the user approves the calendar.
- **Daily, 8:00:** for each client, run the approval check (step 4b, without making
  changes). Reply with: posts due today that are approved and not yet scheduled
  (ready for "publish today's posts"), cards waiting for approval due within 2 days,
  and change requests. Save a short reminder to the approver as a Gmail draft when
  cards are due within 2 days.
- **1st, 9:00:** for each client, build last month's report (step 6) and save the
  email as a Gmail draft for the user to send.

## Guardrails

- Publish nothing that is not in the client's "Approved" list with a matching
  approval hash. A change after approval needs approval again.
- One client at a time: never use one client's knowledge base, brand kit, board,
  sheet or social account for another. Name the client at every step.
- Report numbers come from Supermetrics only, through `report_numbers.py`. Never
  round up, estimate or fill a gap; write "not tracked".
- No made-up reviews, testimonials, statistics or claims about the client's product.
  Quote a customer only with the client's permission and the customer's words.
- Use only music, images and footage the client or the user has the rights to. No
  cloned faces or voices; label AI-generated media where the platform requires it.
- Emails to the client and board invites go out only when the user says so;
  automations save drafts.

## Pitfalls

- Using last client's brand kit or Canva folder. Check the kit name against the
  Profile tab before every design run.
- Editing an approved post "just a little". Any edit clears the approval hash and
  sends the card back for approval.
- Treating a card in "For approval" with no comments as approved. Only the "Approved"
  list counts.
- Writing captions with offers or prices the client never confirmed. Use only the
  brief and Profile.
- Posting a reel with music from a streaming service. Use licensed or client-supplied
  audio only.
- Asking for the brand kit, approver and footage at the start. Ask each at its step.

## Verification

- The calendar tab has one row per post with date, time, channel, format, pillar,
  hook, caption, hashtags, call to action and status, matching the script's dates.
- Every post has a card on <Client>'s board, and every card link is in the sheet.
- Every scheduled or published post was `ready_to_schedule` in the latest approval
  check, and its hash matches the sheet.
- Every number in the report appears in `report_numbers.py` output.
- No file, kit, board or account from another client appears in this client's run.
