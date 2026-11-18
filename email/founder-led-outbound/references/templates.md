# Founder-Led Outbound: templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never make
one up.

## Account sheet ("Outbound: <profile>")

| Column | What goes in it |
|---|---|
| Company | Company name |
| Domain | Company website domain |
| Staff | Staff count or range, from the prospecting app or a linked page |
| Industry | As the source states it |
| Region | Country (and city if known) |
| Contact | Decision-maker's full name |
| Role | Their title |
| Email | Work email from a prospecting app or a page that publishes it, else blank |
| Contact source | Link to where the contact and email came from |
| Score | 0–10 from `score_accounts.py` |
| Fit / Signal | The two halves of the score, e.g. "5 / 4" |
| Signal | The best signal, e.g. "Series A, $12M (2026-07-01)" |
| Signal source | Link to the announcement, job post or news |
| Personal line | The one personal line used in the email |
| Personal line source | Link to the post or news it came from, or "Nothing personal found" plus the signal link |
| Status | New → Emailed → Follow-up drafted → Followed up → Replied → Booked → Called → Deal / Not now / No reply / Opted out / Consent needed / No email |
| Emailed on | Date of the first email (YYYY-MM-DD) |
| Gmail thread | Link or id of the thread |
| Next step | From replies or the call, with a date |
| Notes | Anything the user adds |

## accounts.json (input to score_accounts.py)

```json
{
  "icp": {"min_staff": 10, "max_staff": 200,
          "industries": ["<from the user>"], "regions": ["<country>", "<short form>"],
          "roles": ["<buyer role>", "<other titles for it>"],
          "signals": ["funding", "hiring", "new_leader"]},
  "exclude_domains": ["<domains already in the sheet or opted out>"],
  "accounts": [
    {"company": "<name>", "domain": "<domain>", "staff": "<n or 51-200>",
     "industry": "<industry>", "region": "<country>",
     "contact_name": "<name>", "contact_role": "<title>", "contact_email": "<email or empty>",
     "signals": [{"type": "funding", "detail": "<Series A, $12M>",
                  "date": "<YYYY-MM-DD>", "source": "<url>"}]}
  ]
}
```

Signal types: `funding`, `hiring`, `new_leader`, `tool` (they use a tool that matters),
`other`. Give `regions` and `roles` in the words the sources use ("UK" and "United
Kingdom"; "CTO" and "Chief Technology Officer").

## batch.json (input to check_batch.py)

```json
{"booking_link": "<url>", "postal_address": "<exact address as in the emails>",
 "daily_cap": 20, "sent_today": <emails already sent today>,
 "opted_out": ["<emails or domains marked Opted out>"],
 "emails": [{"to": "<email>", "company": "<name>", "region": "<country>",
             "entity_type": "<company | sole_trader | partnership>",
             "consent": false, "subject": "<subject>", "body": "<full body>",
             "personal_source": "<url behind the personal line or signal>"}]}
```

## Cold email (under 100 words, not counting the address)

```
Subject: <3–6 words about their situation, e.g. "Hiring your first data team">

Hi <first name>,

<Personal line: one true, specific sentence about their post or news.>

<One sentence on the problem this usually brings for a <role> at a company like theirs.>
<One proof point from the user's own proof, e.g. "We helped <customer they may name>
<result they can back up>." Leave this line out if there is none.>

Worth a 20-minute chat? Pick any time here: <booking link>

<sender name>
<signature>
<postal address>

If you'd rather not hear from me, just reply "no thanks" and I won't email again.
```

No attachments, no images, no tracking pixels, one link. Plain text.

## Follow-up (once, 3 days later, same thread, under 50 words)

```
Hi <first name>, a quick nudge on my note about <the signal or their post, in 3–6
words>. If it's not a priority, no worries. If it is, here's my calendar: <booking link>
<sender name>
(Reply "no thanks" and I won't follow up again.)
```

## Reply drafts (under 80 words each)

**Interested**
```
Thanks <first name>, glad it's useful. Here's my calendar, pick whatever suits:
<booking link>. If none of those work, send me two times and I'll fit in.
<sender name>
```

**Question**
```
Good question. <Short, true answer using only what the user has told you.>
Happy to go deeper on a call: <booking link>
<sender name>
```
If the answer is not in what the user gave you, ask the user before drafting.

**Not now**
```
Understood, thanks for letting me know. I'll leave it there<, and check back in
<the month they suggested> if that's alright>. Good luck with <their signal, e.g. the
new team>.
<sender name>
```

**Opt-out** (mark "Opted out" before drafting)
```
Understood, I've taken you off my list and won't email again. Sorry for the bother.
<sender name>
```

**Out of office**: no reply. Note the return date in "Next step".

## Pre-call brief (one page, `generate_document`)

1. **Call**: <date, time, attendees>, booked via <calendar link or email thread>.
2. **Company**: what they do, staff, region, funding stage (each with a source link).
3. **Person**: role, time in role, what they have posted or said recently (with links).
4. **Signals**: each signal, date and link.
5. **Likely pains** (our guesses, to test on the call): 2–3, each tied to a signal.
6. **Questions to ask**: 5, open-ended, about their current process, who else is
   involved, timing and what "good" looks like.
7. **Proof to mention**: the 1–2 most relevant proof points from the user's own list.
8. **Goal of the call**: the next step to aim for.

## Deck tailoring (edit_pptx operations on the user's deck)

1. Title slide: add "Prepared for <company>" under the existing title.
2. After the problem slide, add one slide "<Company>: where we can help" with 3 bullets:
   their likely use case, tied to their signals (as questions or "we heard" points,
   not claims about their business).
3. Move the most relevant proof slide (closest industry or size) right after it.
4. Leave every other slide, the design, fonts and colours exactly as they are.
5. Name the file "<Original deck name> - <Company>".

## Recap email (under 150 words, within the hour of the call)

```
Subject: Recap: <company> and <user's company>, <date>

Hi <first name>,

Thanks for the time today. Here's what I took away:

What we heard
- <2–4 points from the transcript, in their words where possible>

What we agreed
- <each agreement from the transcript>

Next step
- <action, owner, date> <"(proposed)" if no date was agreed on the call>

<sender name>
```

## HubSpot update (show as a table before writing)

| Object | Action | Fields |
|---|---|---|
| Company | Find by domain; create only if missing | Name, domain, industry, staff, region |
| Contact | Find by email; create only if missing | Name, email, title, company, lead source "Outbound" |
| Emails | Log on the contact | The cold email, follow-up, replies and recap (dates and subjects) |
| Note | Create on contact and deal | Call summary from the transcript: pains, agreements, next step |
| Deal | Create or update | Name "<company> - <product>", pipeline and stage from the user's HubSpot, close date only if agreed, amount only if the user gives one |
