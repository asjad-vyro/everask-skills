---
name: Listing Launch Kit
description: Turns a new listing's photos and details into edited photos, a fact-checked description, a property page with viewing slots, a video tour, social posts, an open house flyer and a just-listed email. Then it drafts a reply to every inquiry and a weekly report for the seller. Just upload the photos and give the basics, like "3-bed semi, 12 Park Road, Leeds, £425,000".
---

# Listing Launch Kit

Launches one property listing for a real estate agent: edits the photos (exposure,
white balance, grey sky, upscale, optional virtual staging with a visible "Virtually
staged" label), writes a fact-checked description and feature sheet with real nearby
places, builds a property page with viewing slots, makes a narrated video tour and a
9:16 reel, and prepares the posts, an open house flyer and a just-listed email. Later it
answers inquiries with the page and viewing link and drafts a weekly report for the
seller. It never publishes the page, posts, emails, makes a video public or logs a lead
without the user's say-so, and it never edits away a permanent feature or defect.

## When to Use

- "Launch my new listing: 3-bed semi at 12 Park Road, Leeds, £425,000" (with photos).
- "Edit these listing photos and stage the empty living room, modern style."
- "Make the property page, video tour and just-listed posts for 41 Elm Street."
- "Answer the new inquiries on Park Road and log them in HubSpot."
- "Draft this week's report for the Park Road seller."

## Start Here

When this skill is open, treat the user's message as the start of the launch, not as
a single task. "New listing, photos attached, 41 Elm Street, $389k" means: run this
pipeline for that property. The user should not have to list the steps.

- Begin at step 1 straight away. Do not ask "do you want me to edit the photos?":
  that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. Those pauses protect the user's licence, reputation and contacts, so
  never skip them, even if the user says "do everything".
- To start you need the photos and the property basics (address, price, beds, baths).
  If either is missing, ask for it in one short `clarify` question, then go. Size,
  features and condition notes are asked in step 2, not now.
- If the user returns with "answer the inquiries" or "the seller report", jump to step
  6 or 7 for that property instead of starting over.

## Prerequisites

Check each app with `search_connector_tools` at the step that needs it, not all at the
start. When a required one is missing, call `report_missing_connector_access` for it
instead of explaining in prose.

| App | For | Needed at step |
|---|---|---|
| Cal.com | Viewing slots on the page and in replies | 3 (else any booking link the user has, or their listed viewing times) |
| YouTube | The video tour, uploaded unlisted | 4 (else deliver the MP4 with `publish_artifact`) |
| Instagram | Just-listed post and reel | 5 (else captions and files for the user to post) |
| Facebook | Just-listed post and reel | 5, optional |
| Gmail | Just-listed email; inquiry replies; seller report draft | 5 on |
| HubSpot | Contact list (optional source) and inquiries logged as leads | 5 and 6 (else a lead list in the reply) |
| Google Calendar | Booked viewings on the user's calendar | 6 |

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Listing photos (uploaded) and address, price, beds, baths | Start | None: ask |
| Rooms to virtually stage and the style | Step 1 Stop | No staging; offer it for empty rooms |
| Size, features, condition, what the seller wants said or not said | Step 2 | Ask once; leave out what is not given |
| Booking link (Cal.com or other) or viewing availability | Step 3 | None: ask |
| Branding (colours, logo, agency name) | Step 3 | Clean neutral design, agent name only |
| Contact list (CSV upload or a HubSpot list) | Step 5 | None: ask |
| Sender name, signature, business postal address | Step 5 | None: ask (marketing email carries a postal address) |
| Open house date and time | Step 5 | Flyer says "Viewings by appointment" |
| Seller's name and email | Step 7 or the weekly automation | None: ask |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing, except at every **Stop**. Name the property (street and town) in every
update. Prompts, outlines and message templates are in `references/templates.md`: read
it before step 1. Keep every file for this listing in one working folder named after the
street (`park-road-leeds/`), originals in `originals/`, edits in `edited/`.

## Procedure

### 1. Edit the photos

For each photo, run `media_analyze` with the photo check in `references/templates.md`:
room type, exposure and colour problems, whether the sky is grey or blown out, whether
the room is empty, and every permanent feature or defect visible (damp, cracks, power
lines, neighbouring buildings, the view). Record that list: it is what the edit must keep.

Then, per photo, with `image_generate` (pass the photo as `image_url`) and the edit
prompt in the templates:

1. Correct exposure and white balance. Replace the sky only when it is grey or blown
   out, and change nothing on the ground.
2. `image_upscale` the result.
3. Run `media_analyze` with the before/after check: if any permanent feature, defect,
   room size or the view changed, discard that edit and redo it more gently, or keep
   the original. Never ship an edit that fails this check.

Save the original next to each edit; never overwrite it.

**Stop.** Show every photo as a before/after pair, say what changed in each, and ask
which rooms (if any) to virtually stage and in what style. Offer staging only for rooms
that are empty or nearly empty.

For the rooms the user picks: stage with `image_generate` (staging prompt: furniture
and decor only; walls, floors, windows, fixtures and the view stay exactly as they are),
re-run the before/after check, download each staged image into `edited/` and stamp the
label:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/label_staged.py" --file staged.json
```

`staged.json` is `[{"in": "edited/living_staged.jpg", "out": "edited/living_staged_labelled.jpg"}]`.
Use only the labelled file from then on, and keep the unstaged edit next to it. If the
script reports an error (no ffmpeg), do not publish that staged photo: say so and
use the unstaged edit. Show the staged photos and wait for the user's OK before step 2.

### 2. Description

Ask in one `clarify` for anything missing: size, features, condition, anything the
seller wants said or not said. Then find what is nearby:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/nearby.py" --address "<full address>"
```

It returns the nearest schools, transport, parks and shops from OpenStreetMap, each
with a distance and a source link. Check `matched_address` is the property; if not,
rerun with `--lat`/`--lon` from the user's map pin. If it fails, use `web_search` for
each category and keep the source URL of every place. Distances come only from the
script or a cited source; never estimate one. School ratings or catchments only with
the official source and its date.

Write the description (portal-ready, 150 to 250 words) and the one-page feature sheet
from the outlines in the templates, using only the user's details and the sourced
places. Save the description as `description.txt` and the details as `details.json`,
then run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/check_copy.py" --text description.txt --details details.json --max-words 250
```

Rewrite every "avoid" phrase and every fact "mismatch" or "not_in_details"; raise each
"review" phrase and claim with the user. Rerun until `ok` is true. Build the feature
sheet with `generate_document`.

**Stop.** Show the description, the feature sheet and a facts table (fact, value,
source: "your details" or the link). Mark anything you could not confirm "Unconfirmed".
The user checks every fact; continue only once they approve.

### 3. Property page

Ask for the booking link or viewing availability (and branding, if they have any) in
one `clarify`. If Cal.com is connected, use the user's event link; any other booking
link works the same way; with only availability, list the times on the page.

Build one page with `sites` (`action: create`) from the page prompt in the templates:
the edited photos (staged ones labelled), the approved description, features, an
embedded map of the address, the viewing slots, an inquiry button that emails the
user, and the agent's name and contact.

**Stop.** Share the preview and ask the user to check every photo and fact. Publish
with `sites` (`action: publish`, `name: <street>-<town>`) only after they approve, and
note the public link.

### 4. Video

Write a 60 to 90 second voiceover from the approved description (template), run it
through `check_copy.py` like the description, and make it with `text_to_speech`. Open
the `motion-slideshow` skill with `skill_view` and follow it to build a 16:9 tour from
the edited photos in a sensible walk-through order, with the voiceover, the address
and price on the first slide and the page link on the last. Make a 9:16 reel (20 to
30 seconds, the best 6 to 8 photos, captions on screen) the same way. Staged photos keep
their label on screen.

Upload the tour to YouTube through the connector as **unlisted**, with the title and
description from the templates, and add the link to the page with `sites`
(`action: edit`). It stays unlisted until the user says go. Without YouTube, deliver
the MP4 with `publish_artifact`.

### 5. Spread the word

Ask in one `clarify` for the contact list (CSV, or which HubSpot list), the sender's
name, signature and business postal address, and the open house date and time.

Prepare, from the templates:

1. Instagram and Facebook just-listed posts (carousel caption, under 150 words) and the
   reel caption.
2. An open house flyer: one page with `generate_document` (hero photo, price, 3 to 5
   features, open house time or "Viewings by appointment", the page link, agent
   contact), delivered as a print-ready PDF with `publish_artifact`.
3. The just-listed email (under 120 words) with an unsubscribe line and the postal
   address. Clean the list (export a HubSpot list to JSON first):

```
python3 "${COMPUTER_SKILL_DIR}/scripts/contact_batches.py" --csv contacts.csv --batch-size 50
```

The script keeps only people with a recorded opt-in. If the list has no consent column,
ask the user to confirm everyone on it agreed to hear from them; only then rerun with
`--all-opted-in`. Never add an address yourself.

**Stop.** Show every post, the reel, the flyer, the email and the batch summary (kept,
excluded and why). Post only the posts the user approves, through the Instagram and
Facebook connectors (without a connector, hand over the files and captions). Send the
email from Gmail only after approval, one batch at a time, several minutes apart, each
person as their own recipient (never a visible list). Then ask whether to make the
YouTube tour public.

### 6. Answer inquiries

Search Gmail for messages about this property since the last check (the address, the
page link, "viewing"). For each new inquiry, draft a reply from the template: answer
only with facts from the approved description and details, the page link and the
viewing link. Never discuss offers, negotiate or say anything about the sale; pass
those questions to the user.

**Stop.** Show the drafts, send the ones the user approves, and on approval log each
person in HubSpot as a contact with the lead fields in the templates. Add booked
viewings (from Cal.com or confirmation emails) to the user's Google Calendar, without
inviting anyone.

### 7. Seller report

Ask for the seller's name and email if missing. Gather the week from real sources only:
page visits if `sites` reports them, YouTube views from the connector, inquiries from
Gmail or HubSpot, viewings booked from Google Calendar, and feedback from the user's
notes (ask for them). Anything with no source is "not tracked". Fill the report
template and save it as a Gmail draft to the seller. **Stop.** The user sends it.

## Automation (offer at the end, never set up unasked)

Offer these, and create the ones the user accepts with `cronjob` (`action: create`,
`skills` set to this skill's name as you loaded it). Cron runs have no one to ask, so
each prompt must be self-contained, name the property, its page link and booking link,
and leave sending for the user:

- **Every 15 minutes:** run step 6 for <property>: save a reply to each new inquiry as
  a Gmail draft and list them in the reply. Log each inquirer in HubSpot only if the
  user said yes to that when setting this up; otherwise list them. Add booked viewings
  to the user's Google Calendar without inviting anyone.
- **Fridays 16:00:** run step 7 for <property> and save the seller report as a Gmail
  draft to the seller.

## Guardrails

- Every virtually staged photo carries the visible "VIRTUALLY STAGED" label from the
  script, and its unstaged original is kept and offered with it.
- No edit misrepresents the property: never remove or hide permanent features or
  defects (damp, cracks, power lines, neighbouring buildings), change room sizes or
  alter the view. A sky change is the only outdoor change, and only for a grey sky.
- Describe the home, not who should buy it: no wording about the kind of person,
  family, age, religion or background it suits (fair housing). `check_copy.py` must pass.
- Facts (size, price, schools, distances) come from the user's details or a cited
  source read in this run; flag anything unconfirmed. Never fill a fact from memory and
  never hand fact-finding to `delegate_task`.
- Nothing goes out without approval: the page, posts, emails, the public video, leads.
- Replies give facts and viewing slots only; no price talk, no promises about the sale.
- Email only people who agreed to hear from the agent, each email with an unsubscribe
  line and the postal address. Anyone who unsubscribes is never emailed again.

## Pitfalls

- Letting an edit "tidy" the outside: a removed power line or a greener lawn is a
  misrepresentation. Run the before/after check on every edit.
- Asking an image model to write "Virtually staged": generated text is unreliable.
  Always stamp the label with `label_staged.py`.
- Trusting `nearby.py` blindly: a wrong `matched_address` makes every distance wrong.
- "Great schools" or "perfect for families" slipping back in during a rewrite: rerun
  `check_copy.py` after every change to the text, including the voiceover and captions.
- Sending to a whole spreadsheet: only the script's kept batches are mailed.

## Verification

- Every edited photo has its original saved next to it, and every staged one shows the
  label.
- `check_copy.py` returns `ok: true` for the final description and voiceover.
- The facts table shows a source for every number and nearby place.
- The page is published only after approval and links the tour and the booking link.
- Every post and email batch sent is one the user approved.
