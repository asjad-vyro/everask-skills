# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## Photo check (for `media_analyze`, before editing)

```
Look at this property photo and answer in JSON:
{"room": "<kitchen / living room / front exterior / ...>",
 "exposure": "<ok / dark / overexposed / uneven>",
 "white_balance": "<ok / too warm / too cool / mixed>",
 "sky": "<none / blue / grey / blown out>",
 "empty_room": <true/false>,
 "keep": ["<every permanent feature or defect visible: damp patches, cracks, power
          lines, pylons, neighbouring buildings, road, railway, the view, fixtures>"]}
```

## Edit prompt (for `image_generate` with the photo as `image_url`)

```
Edit this real estate photo. Correct the exposure so the room is bright and even, and
fix the white balance so whites look neutral.<If sky is grey or blown out: " Replace
the grey sky with a natural soft blue sky with light clouds; change nothing below the
roofline or horizon.">
Keep everything else exactly as it is: the same room, walls, floors, windows, fixtures,
furniture, size and layout; the same view through the windows; and every one of these
exactly as photographed: <keep list>. Do not add, remove or move anything. Photographic,
natural, no HDR look, no text.
```

## Staging prompt (for `image_generate`, only rooms the user picked)

```
Virtually stage this empty <room> in a <style, e.g. "warm modern Scandinavian"> style:
add furniture, a rug, lamps, plants and simple wall art that suit a <room> of this size.
Keep the room exactly as it is: walls, wall colour, floors, windows, doors, radiators,
sockets, ceiling, light fittings, the view and every one of these: <keep list>. The
furniture is to scale for the room; do not make the room look bigger. Photographic and
natural. No text, no watermark.
```

## Before/after check (for `media_analyze`, both images)

```
Image 1 is the original property photo, image 2 the edit. Answer in JSON:
{"same_room_and_size": <true/false>,
 "features_changed": ["<any permanent feature or defect from this list that is
                      missing, hidden or altered: <keep list>>"],
 "view_changed": <true/false>,
 "only_allowed_changes": <true if the only differences are light, colour, sharpness,
                         <the sky> <and added furniture/decor>>,
 "notes": "<one line>"}
```

An edit passes only when `same_room_and_size` and `only_allowed_changes` are true,
`view_changed` is false and `features_changed` is empty.

## Description (150 to 250 words, portal-ready)

1. Opening line: property type, beds, the one best feature of the home itself.
2. Inside: room by room, in walk-through order, with sizes only if the user gave them.
3. Outside: garden, parking, outbuildings.
4. Location: 3 to 5 nearby places with distances, from `nearby.py` or a cited source.
5. Practical facts the user gave: tenure, council tax band / HOA, EPC, chain, heating.
6. Close: "Book a viewing: <booking link>."

Describe rooms and features, never the buyer. Prefer "primary bedroom", "step-free
entrance", "south-facing garden" over who it suits.

## Feature sheet (one page, `generate_document`)

```
<Street address>, <town>                         <Price>
<Hero photo>
<Beds> bedrooms · <baths> bathrooms · <size, if given>
Key features (6 to 10 bullets, from the user's details)
Nearby (name, type, distance; source noted in small print)
Practical facts: <tenure, tax band / HOA, EPC, heating, parking>
Viewings: <booking link>   <Agent name>, <agency>, <phone>, <email>
Small print: "Distances are straight-line. Virtually staged images are marked."
```

## Facts table (shown at the step 2 Stop)

| Fact | Value | Source |
|---|---|---|
| Price | <value> | Your details |
| <Nearby place> | <distance> | <OpenStreetMap or web link> |
| <Anything unconfirmed> | <value> | Unconfirmed: please check |

## Property page prompt (for `sites` action: create)

```
Build a one-page property listing website for <street address>, <town>.

Content (use only these facts):
- Headline: <beds>-bedroom <property type>, <street>, <town> · <price>
- Photo gallery, in this order: <edited photo files/links>. Staged photos keep their
  "VIRTUALLY STAGED" label; under each one add a caption "Virtually staged. Original
  photo:" with a link to the unstaged photo.
- Description: <approved description, word for word>
- Key features: <bullets>
- Location: an embedded map of <full address>, and the nearby list: <name, distance>
- Video tour: <YouTube link, added after step 4>
- Viewings: <Cal.com or booking link embedded / or the listed times: "<times>">
- Inquiries: a button "Ask about this home" that opens an email to <agent email> with
  the subject "Inquiry: <street address>"
- Agent: <name>, <agency>, <phone>, <email>, <logo if given>

Design: <brand colours or "clean, light, neutral">, large photos, mobile first, fast.
Primary button: "Book a viewing". No buyer-profile wording.
Footer: "Details provided by the agent. Distances are straight-line and approximate.
Virtually staged images are marked."
```

## Voiceover (60 to 90 seconds, about 150 to 220 words)

```
Welcome to <street>, <town>: a <beds>-bedroom <property type> <offered at price>.
<Walk-through: one or two sentences per room, in the photo order.>
<Outside space.>
<Two or three nearby places with distances.>
To book a viewing, visit <short page link> or contact <agent name> at <agency>.
```

## YouTube (unlisted)

- Title: `<Beds>-bed <property type>, <street>, <town> | Video tour`
- Description: first two lines of the description, the page link, the booking link,
  "Virtually staged images are marked on screen." (if any), agent name and agency.

## Instagram / Facebook just-listed post (under 150 words)

```
Just listed: <beds>-bed <property type> on <street>, <town>. <Price>.
<Two lines on the best features of the home.>
<One line on location with a real distance.>
Book a viewing: <link in bio / page link>
<"Some photos are virtually staged." if any>
<5 to 8 hashtags: #justlisted #<town>homes #<town>property ...>
```

Reel caption: the first line and the booking line above, plus the hashtags.

## Open house flyer (one page, print-ready PDF)

Top: "OPEN HOUSE" with <date, time> (or "VIEWINGS BY APPOINTMENT"). Hero photo. Address
and price. 3 to 5 features. The page link in large type. Agent name,
agency, phone, email. Small print: "Virtually staged images are marked." if any. Size
A4 for the UK and Europe, US Letter for the US and Canada.

## Just-listed email (under 120 words)

```
Subject: Just listed: <beds>-bed <property type> on <street>, <town>

Hi <first name, or "there">,

I've just listed <street address>: a <beds>-bedroom <property type> with <one or two
best features>, <price>.

Photos, the video tour and viewing times are here: <page link>
<Open house: <date, time>, or omit.>

If you or someone you know might be interested, I'd be glad to show you round.

<sender name>
<signature>
<postal address>

You're getting this because you asked to hear about new listings from me. To stop,
reply "unsubscribe" and I won't email you again.
```

## Inquiry reply (under 100 words)

```
Subject: Re: <their subject>

Hi <first name>,

Thanks for your interest in <street address>. <Answer their question with facts from
the approved details only; if you cannot answer from them, say "<agent name> will
come back to you on that.">

Everything about the home, including the video tour, is here: <page link>
You can pick a viewing time here: <booking link>

<sender name>, <agency>, <phone>
```

Questions about offers, price flexibility, the seller's situation or how the sale
will go: never answer; flag them to the user.

## HubSpot lead (logged after approval)

| Field | Value |
|---|---|
| Email, first name, last name, phone | As given in the inquiry; blank if not given |
| Lifecycle stage | Lead |
| Lead source | "Listing: <street address>" |
| Note | Date, channel (email or page), their question in one line, viewing booked yes/no |

## Seller report (weekly, one page)

```
<Street address> · Weekly update · week ending <date>

This week
- Page visits: <n or "not tracked">
- Video tour views: <n from YouTube or "not tracked">
- Inquiries: <n> (<new this week>)
- Viewings booked: <n>, <dates>
- Feedback from viewings: <from the user's notes; quote nothing they did not give>

Next week
- <from the user's notes: open house, price review discussion, etc.>

<Agent name>, <agency>
```

Email to the seller: two lines with the headline numbers, the report attached or
pasted below, saved as a Gmail draft for the user to send.
