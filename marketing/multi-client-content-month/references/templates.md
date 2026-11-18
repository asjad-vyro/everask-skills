# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## Client sheet: "Content: <Client>"

One Google Sheet per client. Never put two clients in one sheet.

### Tab "Profile" (two columns: Field | Value)

| Field | Value |
|---|---|
| Client | Name as the client uses it |
| Country, time zone | e.g. United Kingdom, Europe/London |
| Channels | Instagram / Facebook / LinkedIn handles or page names |
| Brand guide | Link to the file |
| Canva brand kit | Kit name in Canva |
| Tone of voice | 3–5 short rules, e.g. "warm, plain words, no exclamation marks" |
| Pillars (weight) | e.g. Educate (2), Show the work (1), Offer (1), Community (1) |
| Offers and products | What can be promoted, with prices only if the client gave them |
| Words to avoid | From the client |
| Past posts that did well | Links |
| Hashtag sets | Per channel |
| Approver | Name, email |
| Trello board | Link |
| Music and footage sources | Client folder / licensed library the user named |

### Tab "Calendar <Month YYYY>"

| Column | Content |
|---|---|
| ID | Row number from `plan_calendar.py` (`n`) |
| Date | YYYY-MM-DD, client's time zone |
| Time | HH:MM |
| Channel | instagram / facebook / linkedin |
| Format | post / carousel / reel |
| Pillar | From the script |
| Key date / Promotion | From the script |
| Hook | First line, under 12 words |
| Caption | Full caption |
| Hashtags | From the Profile's sets, 3–8 |
| Call to action | One action |
| Media | Canva export or reel links |
| Card | Trello card link |
| Approved hash | From `approval_check.py`; blank until approved, cleared on any change |
| Status | Planned → Made → For approval → Changes requested → Approved → Scheduled / Approved, publish on the day → Published |
| Post link | Live post URL |

## Brief: "Brief <Month YYYY>" tab

```
<Client> · <Month YYYY> brief

Goals this month (from the <date> call):
- <goal> (source: <Fathom meeting / notes>)
Promotions:
- <name>: <start> to <end>, <offer as stated> (source)
Launches and events:
- <what, date> (source)
Key dates:
- <date>: <holiday or observance> (source link)
Avoid this month:
- <topics, words, competitor mentions> (source)
Last month's best posts:
- <link>: <engagements> engagements (Supermetrics), or "not available"
Mix: <n> per channel and format (<"as last month" / "as asked">)
```

## Caption rules

- In the client's voice from Profile; use none of the "Words to avoid".
- Hook first, under 12 words. Instagram caption under 150 words; LinkedIn under 200,
  first two lines carry the point; Facebook under 80.
- One call to action per post. Promotion details only on rows inside its dates.
- No invented facts, prices, results, reviews or testimonials. No health, money or
  legal promises.

## Canva design brief (one per post)

```
Client: <Client> · Brand kit: <kit name> (use only this kit's fonts, colours, logo)
Format: <post 1080x1350 / carousel 1080x1350, <n> slides / story 1080x1920>
Channel: <channel> · Date: <date>
Headline on image: <hook, max 8 words>
Slides (carousels): <slide 1 hook> / <points, one per slide> / <last slide CTA>
Imagery: <client photo from <folder> / Canva stock / brand illustration>
Do not: other clients' assets, fake reviews, stock photos of "customers" with quotes
```

## Reel edit brief (for `create_timeline` / `apply_timeline_edit`)

```
Client: <Client> · Reel for <date> · <length 15–45 s> · 9:16
Footage: <file names or folder> (client-supplied / licensed stock: <source>)
Cut: hook in the first 2 seconds: <hook>; then <beats>; end card with <CTA>
Subtitles: burned in, <client font>, <colour>, max 2 lines, centred lower third
Music: <track> from <licensed source the user confirmed>, or none
```

## Trello board "<Client> · Content approvals"

Lists, in order: For approval · Changes requested · Approved · Scheduled · Published.

Card:

```
Title: <date> <time> · <Channel> · <format> · <hook>
Description:
  Caption:
  <caption>

  Hashtags: <hashtags>
  Call to action: <CTA>
  Sheet row: <ID>
Due date: <date> <time>
Attachments: <media>
```

To approve, the client moves the card to "Approved". To ask for a change, the client
comments on the card (or moves it to "Changes requested"). After a change, comment
"Updated: <what changed>. Back for approval." and move it to "For approval".

## Approval request email (under 120 words, the user sends it)

```
Subject: <Month> posts for <Client> ready for your approval

Hi <approver first name>,

<Client>'s <Month> posts are ready: <n> posts across <channels>.

Board: <Trello board link>

Move a card to "Approved" when you're happy with it, or leave a comment on the card
with any change and I'll update it. The first post goes out on <first date>, so
approvals by <date 2 days before> keep everything on time.

Thanks,
<user's name>
```

## Approval reminder (under 60 words, saved as a draft)

```
Subject: <n> <Client> posts waiting for approval

Hi <approver first name>, a quick reminder: <n> posts on the board are due on
<dates> and still need a look: <board link>. Move them to "Approved" or comment with
changes. Thanks, <user's name>
```

## Monthly report (Slides, 6–8 slides)

1. Title: "<Client> · Social report · <Month YYYY>"
2. Headline: 3 numbers from `report_numbers.py` (e.g. engagements, follower growth,
   reach on the main channel), each with its change vs last month
3. Per channel: reach, impressions, engagements, engagement rate, followers (value,
   last month, change); "not tracked" where the script says so
4. Follower growth chart (`render_chart`, from the script's numbers)
5. Top posts: up to 5, thumbnail, date, channel, engagements, link
6. What we did this month: posts published by channel and format (count from the
   sheet's Published rows), promotions run
7. What we'll do next month: from next month's brief or the user's notes
8. Source line: "Numbers from Supermetrics, <date pulled>. Engagement rate =
   engagements / reach."

## Report email (under 80 words)

```
Subject: <Client> social report · <Month YYYY>

Hi <approver first name>,

Here's <Month>'s report: <deck link>.
Headline: <one real number with its change, e.g. "engagements up 2.8% to 1,532 on
Instagram">.

Next month we'll focus on <one line from the plan>. Happy to talk it through.

<user's name>
```
