# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## Report sheet: "Ad report: <brand> · week of <date>"

Top block: week, blended spend, blended <KPI>, counts per status (from `ad_report.py`),
the minimum spend used for winners.

| Column | Content |
|---|---|
| Platform | Meta / TikTok / Google |
| Ad | Ad name as in the account |
| Ad ID | From the data |
| Campaign | From the data |
| Hook | Opening beat in a few words, tagged by you ("POV unboxing", "price anchor") or "not seen" |
| Angle | The reason to buy it leads with ("no sticky residue", "cheaper per cup") |
| Spend | Last week |
| Impressions | Last week |
| CTR % | From the script |
| Hook rate % | 3-second views ÷ impressions (TikTok: 2-second); blank for statics |
| Cost per purchase | From the script |
| ROAS | From the script |
| Frequency | From the script; blank if the platform does not report it |
| Status | Winner / Winner, fatiguing / Fatiguing / Steady / Low spend |
| Why | The script's reason, one line |

## Competitors tab

| Column | Content |
|---|---|
| Competitor | Brand |
| Type | Ad / Price / Offer / Product |
| Hook | For ads: the opening, described, not copied |
| Angle | For ads |
| Format | Static, UGC, product video, carousel |
| Running | Days live, and "live" or "stopped" |
| Price / offer | As read on the page, with currency |
| Link | Ad link or page URL |
| Checked | Date read |

Then **Patterns** (3–6 lines): what several competitors do, e.g. "3 of 4 long runners
open on a problem close-up", "BrandA dropped its bundle price from <x> to <y>". No
copy lifted from any ad.

## Customer language (in the doc, before the matrix)

| Type | In their words (paraphrased) | How often | Source links |
|---|---|---|---|
| Pain | <paraphrase> | <n threads/comments> | <links> |
| Desire | | | |
| Objection | | | |
| Phrase to echo | <short phrase, paraphrased, no username> | | |

## Angle matrix

| Angle | Audience | Hook | Proof | Based on |
|---|---|---|---|---|
| <reason to buy> | <who it speaks to> | <first 2 seconds / headline> | <real proof the brand can show: a feature, a demo, a number the brand provided> | <winning hook / customer pain / competitor gap> |

Proof is only what the brand can back. No invented stats, reviews or awards.

## Brief for 20 ads (Google Doc or `generate_document`)

1. **This week in one paragraph:** winners, what is tiring, what competitors are doing.
2. **Keep:** winning hooks and angles to build on (with their numbers from the report).
3. **Replace:** fatiguing ads and what replaces each.
4. **New angles:** from customer language, each with its source.
5. **The 20 ads:** a table: # | Angle | Hook | Format (static / UGC / product video) |
   Platforms | Main line of copy | Proof | Notes. Default mix 8 static, 6 UGC, 6 product.
6. **Rules:** the brand's claim rules and words to avoid, and the platform policy
   points that apply (health, before-and-after, personal attributes).

## Static prompt (for `image_generate`, when Canva is not used)

```
A clean, scroll-stopping <ratio> social ad for <brand>'s <product>.
Use the attached product photo exactly as the product; do not redraw the packaging.
Layout: <headline area top / product centre / CTA bottom>.
Headline text: "<headline, from the checked copy>"
Brand colours <hex list>, font style <from the guidelines>, logo space bottom-right
(leave empty; the real logo is added after).
Mood: <from the angle>. No people unless the brief says so; no extra text, no fake
badges, ratings, reviews or prices.
```

Check every generated static for spelling and for the product looking like the real
one; remake any that do not.

## UGC-style video script (15 seconds)

```
0–3 s  HOOK: <the hook from the brief, said to camera or on screen>
3–7 s  PROBLEM: <the customer pain, paraphrased>
7–12 s PRODUCT: <what it does, shown, with the proof the brand can back>
12–15 s CTA: <"Tap to try it" / the offer the brand gave>
On-screen label where the platform requires it: "AI-generated"
```

The presenter speaks as themselves ("I tried…" only if the brand approves that style
and the claim is true of the product); never "I'm a customer" or a made-up review.

## Product video cut plan (user footage)

```
<ad name> · <ratio> · <length> s
0–2 s  <strongest shot of the product in use> + headline caption
2–8 s  <2–3 feature shots matching the angle>
8–<end> <product + CTA card in brand colours>
Captions: from make_subtitles.py; burned in, bottom third, safe from the platform UI.
```

## Copy per platform (checked by `check_copy.py`)

- Meta: primary text (shows ~125 characters), headline (~40), description (~30).
- TikTok: ad text (≤100, no emoji), display name.
- Google: headlines (≤30 each), long headline (≤90), descriptions (≤90), business
  name (≤25).

## Upload plan (shown at the step 6 Stop)

| Ad name | Platform | Campaign | Ad group | Sizes | Status |
|---|---|---|---|---|---|
| <name> | TikTok | <campaign> | New: "Test <date> <angle>" | 9:16 | Paused |
| <name> | Google | <campaign> | New: "Test <date> <angle>" | 1:1, 1.91:1, 4:5 | Paused |
| <name> | Meta | Drive folder | n/a | 9:16, 4:5, 1:1 | Ready to upload |

## Meta copy sheet (in the Drive folder)

Columns: Ad name | File names | Primary text | Headline | Description | CTA | Landing
URL (from the user) | Notes (e.g. "AI-generated presenter: label in Ads Manager").

## Slack summary (under 150 words)

```
<brand> · ads week of <date>
Winners: <ad names with KPI from the report>
Tiring: <ad names, one reason each>
Competitors: <1–2 patterns>
New angles: <3–4 angle names>
New tests: <n> ads, all paused: TikTok <link>, Google Ads <link>, Meta set <Drive link>
Report: <sheet link> · Brief: <doc link>
```

No predictions of results.
