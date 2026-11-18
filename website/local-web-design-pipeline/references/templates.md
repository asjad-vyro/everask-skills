# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## Prospect sheet columns

| Column | Content |
|---|---|
| Business | Name as on Google Maps |
| Address | Full address |
| Phone | As listed |
| Website | URL, or "None" |
| Public email | From their site's contact page, else blank |
| Contact form | URL of their site's contact form, else blank |
| WhatsApp link | Tap-to-send link from `whatsapp_links.py`, for businesses with no email |
| Rating | Google rating |
| Reviews | Review count |
| Maps link | Google Maps URL |
| Score | 0–10 from the audit (10 = most in need) |
| Reason | One line, e.g. "No HTTPS; not mobile friendly; copyright 2019" |
| Demo link | Filled in step 4 |
| Status | New → Demo built → Pitched (email / WhatsApp / form, date) or Called → Follow-up drafted → Replied → Client / Not interested / Opted out / Consent needed |
| Notes | Anything the user adds |

## Demo site prompt (for `sites` action: create)

```
Build a one-page website for <business>, a <type> in <city>. This is a DEMO to show
the owner what their site could look like.

Content (use only these facts):
- Services: <list from their site or Maps>
- Hours: <hours>
- Address: <address>, with an embedded map
- Phone: <phone> as a tap-to-call link
- What customers say: <2–3 themes reviewers praise, summarised in new words; no quotes,
  no reviewer names>

Design:
- A simple made-up logo mark: the business name in a clean typeface with a small
  abstract symbol. Do NOT use or imitate their real logo.
- Neutral, generic imagery that fits a <type>. Do NOT use their photos.
- Mobile first, fast, one clear primary button: "<Book an appointment / Call now>"
  linking to <their booking page or tel: link>.
- Sections: hero with the button, services, why choose us (from the review themes),
  hours and location, contact.
- Footer line, small: "Demo prepared for <business>. Not their official website."
```

## Pitch email (under 120 words)

```
Subject: A new website idea for <business>

Hi <first name, or "there">,

I was looking at <business> online and noticed <one specific, true problem from the
audit, e.g. "your site doesn't load properly on a phone">. That's often where new
<customers/patients> drop off.

So I put together a quick demo of what a new site could look like:
<demo link>

If it's useful, I'd be glad to walk you through it. You can pick a time here:
<booking link>

<sender name>
<signature>
<postal address>

If you'd rather not hear from me again, just reply "no thanks" and I won't email again.
```

## Follow-up (once, 4 days later, same thread)

```
Hi <first name>, just checking you saw the demo I made for <business>: <demo link>.
Happy to answer any questions, or book a time here: <booking link>.
<sender name>
(Reply "no thanks" and I won't follow up again.)
```

## WhatsApp pitch (under 60 words; becomes a tap-to-send link)

```
Hi, this is <sender name> from <studio>. I noticed <business>'s website <one specific,
true problem>, so I made a quick demo of a new one: <demo link>
Happy to show you round it: <booking link>
If you'd rather not hear from me, just reply "no thanks".
```

## Contact form message

Same as the pitch email body, without the subject line. Put the user's name, email and
phone in the form's own fields, not in the message.

## Call script (30 seconds)

```
Hi, is that <business>? I'm <sender name>, a local web designer. I'll be quick: I
noticed <one specific, true problem from the audit>, which can cost you
<customers/patients> who find you on their phone. I've built a free demo of a new site
for you. Could I send you the link by WhatsApp or email?
→ Yes: ask which, and to whom. Note it in the sheet.
→ Not interested: thank them, mark "Not interested". Do not call again.
```

## Proposal outline

1. Summary: what the client gets, in two sentences.
2. What we found: the audit points for their current site.
3. The new site: pages, features, the booking button, mobile and speed.
4. Timeline: from deposit to launch.
5. Price: build fee, deposit (%, amount), balance and when due.
6. Monthly retainer: amount and exactly what it includes (from the user's terms).
7. Next steps: sign the contract, pay the deposit, send domain access.

## Contract outline

Parties; scope of work; deliverables; timeline; fees and payment terms (deposit,
balance, retainer, late payment); what the retainer covers and excludes; client
responsibilities (content, domain access); ownership of the site and content on full
payment; cancellation (notice period for the retainer); limitation of liability;
governing law (the user's country). Add a note that the user should have the contract
checked by a lawyer; this skill does not give legal advice.

## Monthly report (one page)

```
<Client> · Website report · <Month Year>

Search performance (Google Search Console)
- Clicks: <n> (<+/- vs last month>)
- Impressions: <n>
- Average position: <n>
- Top queries: <top 5 with clicks>
- Top pages: <top 3>

Bookings: <taps on the booking button, or "not tracked">

What we did this month
- <from the user's notes>

Next month
- <from the user's notes>
```

Email: two lines saying the report is attached, with the headline number, from the
user's Gmail after approval.
