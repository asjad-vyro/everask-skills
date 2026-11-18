---
name: Weekly Ad Creative Engine
description: Reports last week's winning and tiring ads across Meta, TikTok and Google, scans what competitors are running and turns real customer words from Reddit and Instagram into new ad angles. Once you approve the brief, it makes a fresh batch of on-brand statics and subtitled videos and sets them up as paused tests. Just name your brand, like "run this week's ads for Glow Serum".
---

# Weekly Ad Creative Engine

Runs a DTC brand's weekly creative loop for one brand: pull last week's ad-level
results from Meta, TikTok and Google, mark the winners and the ads that are tiring,
scan competitors' long-running ads and price moves, mine Reddit and Instagram for how
customers really talk, and turn that into an angle matrix and a brief. After the user
approves the brief, it makes 20 new ads (statics, UGC-style and product videos,
subtitled, sized per platform) and, after a second approval, uploads them as
**paused** tests. It never launches an ad, changes a budget, bid or audience, pauses a
running ad, or posts to Slack without the user's say-so.

## When to Use

- "Run this week's ads for [brand]."
- "Which of our ads are winning and which are tired? Then make new ones."
- "Make 20 new test ads from what customers say on Reddit about [product]."
- "The brief looks good, make the ads." (re-enter at step 5)
- "Upload the approved ads as paused tests and post the summary to Slack." (step 6)

## Start Here

When this skill is open, treat the user's message as the start of the weekly run, not
as a question about ads. "Glow Serum ads", "run this week" or "what's working in our
ads" all mean: run this pipeline for that brand, starting at step 1.

- Begin at step 1 straight away. Do not ask "do you want me to pull your results?":
  that is what this skill is for.
- Carry on from one step to the next without waiting, and pause only at the steps
  marked **Stop**. Those pauses protect the user's ad spend, brand and accounts, so
  never skip them, even if the user says "do everything".
- The only thing needed to start is the brand (and the product, if the brand sells
  several). If it is missing, ask for it in one short `clarify` question, then go.
- A returning user re-enters where they are: "the brief is approved" → step 5;
  "upload the ads" → step 6; "just the report" → steps 1–2 only.

## Prerequisites

Check each app with `search_connector_tools` at the step that needs it, not all at the
start. When a required one is missing, call `report_missing_connector_access` for it
instead of explaining in prose.

| App | For | Needed at step |
|---|---|---|
| Supermetrics (`supermetrics_mcp_call`) | Last weeks' Meta, TikTok and Google Ads results in one pull | 1 (else the Meta Ads, TikTok Ads and Google Ads connectors, or an export the user uploads) |
| Google Sheets | The winners and fatigue report | 2 (else an .xlsx with `excel_*` tools, sent with `publish_artifact`) |
| Particl | Competitor product and price moves | 3, optional (else `web_extract` on competitor product pages) |
| Reddit | Customer language | 4 (`reddit_research` works without a connector) |
| Instagram | Comments on the brand's own posts | 4, optional |
| Google Docs | Angle matrix and brief | 4, optional (else `generate_document`) |
| Canva | Statics on the brand's templates | 5 (else `image_generate` on the brand guidelines) |
| Google Drive | Product footage in; the named Meta set out | 5 and 6 (else uploads in chat and a zip via `publish_artifact`) |
| TikTok Ads | New ads as paused tests | 6 |
| Google Ads | New ads as paused tests | 6 |
| YouTube | Hosting video ads for Google Ads, unlisted, only if the user agrees | 6, optional |
| Slack | The weekly summary | 6, optional (else the summary in the reply) |

## Inputs (ask each one only when its step needs it)

| Input | Asked at | Default |
|---|---|---|
| Brand (and product) | Start | None: ask |
| Ad accounts | Step 1 | Every Meta, TikTok and Google Ads account Supermetrics shows for the brand; ask only if it shows several brands |
| Main KPI | Never ask | Cost per purchase (the user may say ROAS, CTR or hook rate) |
| Winner threshold | Never ask | At least 2× the blended cost per purchase in spend, and 15% better than blended on the KPI |
| How many ads | Never ask | 20: 8 statics, 6 UGC-style videos, 6 product videos |
| Competitors (3–5) and their sites | Step 3 | None: ask |
| Brand guidelines: logo, colours, fonts, tone, words to avoid, claims allowed and not allowed | Step 4 | None: ask (upload or type) |
| Product photos and footage | Step 5 | None: ask (upload or a Drive folder) |
| Canva brand templates | Step 5 | The brand's templates in Canva if connected; else on-brand designs from the guidelines |
| Campaigns to test in, per platform | Step 6 | None: ask, listing the campaigns the connectors show |
| Slack channel | Step 6 | None: ask if Slack is connected; else the summary goes in the reply |

Use anything the user already gave and never ask for it again. When a step needs
something missing, ask for all of that step's missing inputs in one `clarify`
message, then continue. Offer to remember the brand guidelines, competitors and
channel with `memory` so next week's run asks nothing.

## How to Run

Plan the run with `todo` (one item per step), then work through the steps in order
without pausing between them, except at every **Stop**. Name the brand and the week
("Glow Serum, week of 9 Nov") in every update. Sheet columns, the brief, prompts,
scripts and the summary are in `references/templates.md`: read it before step 2.

## Procedure

### 1. Report

Pull the last three full weeks (Monday to Sunday) at ad level for Meta, TikTok and
Google Ads with `supermetrics_mcp_call`: `data_source_discovery` and
`accounts_discovery` to find the accounts, `field_discovery` for the field names, then
`data_query` split by week, ad and campaign. Fields: spend, impressions, clicks,
3-second video views (TikTok has 2-second views), purchases, purchase value,
frequency. Follow every page and async result until the connector says there are no
more. Last week is the report; the two before are only for the fatigue trend.

If Supermetrics is not connected, use the Meta Ads, TikTok Ads and Google Ads
connectors for the same fields, or ask the user to upload an ad-level export. If none
is available, call `report_missing_connector_access` for Supermetrics and stop. Never
fill in numbers from memory or estimate a missing metric. Do steps 1 and 2 yourself;
never hand them to `delegate_task`.

Save the rows as `results.json` (fields named as in the script's docstring, or the
platforms' own names) and run:

```
python3 "${COMPUTER_SKILL_DIR}/scripts/ad_report.py" --file results.json --kpi cpp --csv report.csv
```

The script decides every status (Winner, Fatiguing, Winner fatiguing, Steady, Low
spend) and writes the reason. Its output is the only source for these; never
overrule it with a judgement. A null metric or "could not check" stays as it is in
the report.

### 2. Winners and fatigue

Create a Google Sheet "Ad report: <brand> · week of <date>" with the report columns in
`references/templates.md`, one row per ad from `report.csv`, winners first. Fill the
**Hook** and **Angle** columns yourself: look at each ad's creative (thumbnail or
video through the connector, read with `media_analyze`) and its copy, and tag the
opening hook and the angle in a few words. If you cannot see an ad's creative, write
"not seen" and tag from the copy only. Add a top block: blended spend, KPI and the
counts per status. Share the link.

### 3. Competitor scan

Ask for the 3–5 competitors and their sites now if you do not have them. For each,
`ad_research` (`find_brands` by domain, then `brand_ads`) twice: newest live ads, and
live ads running 30+ days (`running_duration_min_days: 30`), which are likely
working. Note each ad's hook, angle, format, offer and days running, with its link.
`brand_trend` shows whether they are ramping up.

For product, price and offer changes, use Particl if `search_connector_tools` finds
it; otherwise `web_extract` each competitor's main product pages and record price,
offer and the URL with today's date. Never state a price you did not read in this run.

Write a "Competitors" tab: one row per ad or price point with its link, then 3–6
patterns (e.g. "two of four lead with a price-per-serving hook"). Patterns, not
copies: nothing from a competitor's copy, visuals or offer goes into the user's ads.

### 4. Customer language and brief

Ask for the brand guidelines now if you do not have them (upload or type; note the
claims the brand may and may not make). Then:

1. `reddit_research` on the category and on the brand (and the Reddit connector if
   connected, for specific subreddits). For Instagram, read recent comments on the
   brand's own posts through the connector, if connected.
2. Pull pains, desires, objections and the exact phrases people use, each with its
   source link. Keep usernames out of everything.
3. Write the **angle matrix** (angle × audience × hook × proof) and the **brief for
   20 ads** in Google Docs (else `generate_document`), using the outlines in
   `references/templates.md`. The brief leans on this week's winning hooks, replaces
   the fatiguing ones, and uses customer phrases only paraphrased.

Every pain, phrase and proof point must trace to a source read in this run. If
`reddit_research` and the connectors return nothing, say so and stop; never write
customer language from memory, and never source it through `delegate_task`.

**Stop.** Show the report link, the competitor patterns, the angle matrix and the
20-ad brief. The user cuts, edits or adds angles. Make nothing until they approve.

### 5. Make the ads

Ask for product photos and footage (upload or a Drive folder) now if you do not have
them, and whether to use Canva templates. Then:

1. Name every ad and get its sizes:
   `python3 "${COMPUTER_SKILL_DIR}/scripts/ad_names.py" --file ads.json --existing names.txt`
   (`names.txt`: last weeks' ad names from the report, so versions do not collide).
2. Write the copy per platform and check it:
   `python3 "${COMPUTER_SKILL_DIR}/scripts/check_copy.py" --file copy.json --rules rules.json`
   (`rules.json` from the brand guidelines: words to avoid, banned claims,
   competitor names). Fix every error; reread every warning against the brand's claim
   rules and the platform's policies.
3. **Statics:** fill the brand's Canva templates through the connector, one design
   per size. Without Canva, use `image_generate` with the product photo as the
   reference and the static prompt in `references/templates.md`.
4. **UGC-style videos:** `generate_ugc_ad` with the product and the script from the
   brief as `prompt` (9:16 first), or `video_generate` from a product photo. Any
   AI-generated person is labelled as AI-generated where the platform requires it and
   never presented as a real customer; no testimonial words in their mouth that no
   real customer said.
5. **Product videos:** cut the user's own footage in the video editor
   (`create_timeline` with the right `canvas`, then `apply_timeline_edit`,
   `read_timeline`), one cut per ad and size.
6. **Subtitles:** for every video,
   `python3 "${COMPUTER_SKILL_DIR}/scripts/make_subtitles.py" --file scripts.json --out subtitles/`
   (use `audio_transcribe` timings as `segments` when the video has a voice). Add the
   captions in the video editor from the frame timings; keep the `.srt` with the file.

**Stop.** Show every ad with its name, sizes, copy and the check results. The user
approves, cuts or asks for changes; remake only what they ask.

### 6. Upload as paused tests

Ask which campaigns to test in on TikTok Ads and Google Ads (list the campaigns the
connectors return) and the Slack channel, if not given. Then show the upload plan
(table in `references/templates.md`: ad → platform → campaign → new ad group or ad →
**Paused**) and the Slack summary.

**Stop.** Create nothing until the user confirms the plan. Then:

- **TikTok Ads:** in each chosen campaign, a new ad group or new ads with the
  approved creatives, status paused/disabled. Copy the existing ad group's targeting
  and budget unchanged; never edit the original.
- **Google Ads:** new ads (or a new ad group) in the chosen campaigns, status paused.
  Video ads must be hosted on YouTube: upload as **unlisted** through the YouTube
  connector only if the user agreed at this Stop; otherwise send only the statics to
  Google Ads and put the videos in the Drive folder.
- **Meta:** a Google Drive folder "Meta set: <brand> · <date>" with every approved
  file under its ad name and a copy sheet (template in references), ready for the
  user to upload in Ads Manager. Without Drive, a zip via `publish_artifact`.
- **Slack:** post the approved summary in the chosen channel.

Read back what the connectors created and confirm each one shows as paused. If any
did not, say so and leave it for the user; never change a live ad to fix it.

## Automation (offer at the end, never set up unasked)

Offer this, and create it with `cronjob` (`action: create`, `skills` set to this
skill's name as you loaded it) only if the user accepts. The prompt must be
self-contained (brand, accounts, KPI, competitors, guidelines location):

- **Mondays 7:00:** run steps 1–4: refresh the report sheet, the competitor tab, the
  angle matrix and next week's brief, and reply with the summary, the sheet and doc
  links, and "Reply 'make the ads' to approve the brief". It makes no ads (they cost
  credits and need an approved brief), uploads nothing and posts nothing to Slack;
  the user runs steps 5–6 from the reply.

## Guardrails

- Every test is created paused. Never launch an ad, change a budget, bid or audience,
  or pause, edit or delete a running ad.
- Report numbers come only from Supermetrics, the ad connectors or the user's export.
  Never estimate, round up or fill gaps; write "not tracked".
- No promises of lower costs or more sales in reports, briefs or summaries.
- Learn from competitor ads; never copy their copy, visuals, offers or claims, and
  never name a competitor in an ad.
- Customer language is paraphrased; never quote a username or a private person's
  post, and never present a paraphrase as a review.
- AI-generated people are labelled as AI where the platform requires it and never
  shown as real customers; no fake testimonials, reviews or before-and-after results.
- Follow the brand's claim rules and each platform's ad policies (health, finance,
  weight loss, before-and-after, personal attributes).
- Nothing is uploaded or posted without approval at the step 6 **Stop**.

## Pitfalls

- Calling an ad fatiguing from one bad week. Fatigue needs CTR or hook rate down two
  weeks running while frequency rises; the script checks this. "Could not check"
  (e.g. no frequency from Google) is not "fatiguing".
- Pulling daily rows. Weekly frequency is not the average of daily frequency; query
  by week. The script warns when it gets daily rows.
- Crowning a winner on tiny spend. Low-spend ads are "Low spend", not winners.
- Statics in one size only. Every ad goes out in every size `ad_names.py` lists for
  its platforms, or the platform crops it.
- Uploading into the user's best ad group. Tests go in new ad groups or as new ads,
  paused; the running ones stay untouched.

## Verification

- Every row in the report sheet traces to a row in the pulled data, and every status
  matches `ad_report.py`'s output.
- Every competitor pattern, price and customer phrase has a source link from this run.
- Every ad follows `date_angle_hook_format_v1`, exists in all its sizes, has subtitles
  if it is a video, and passed `check_copy.py` with no errors.
- Every ad created in TikTok Ads and Google Ads reads back as paused; the Meta folder
  holds exactly the approved set.
