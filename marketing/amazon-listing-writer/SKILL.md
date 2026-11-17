---
name: Amazon Listing Writer and Optimizer
description: >
  Writes a copy-paste-ready Amazon listing (title, 5 bullets, description, backend search terms) with a keyword coverage check, or audits a pasted listing and rewrites it with the missing keywords.
  Use it for "write an Amazon listing", "optimize my Amazon listing", "audit this listing", "which keywords am I missing", "Amazon UK listing for my product".
---

# Amazon Listing Writer and Optimizer

A good result is a listing the seller can paste straight into Seller Central, with every target keyword placed on purpose and a coverage table whose numbers are counted by code, not guessed. The whole job is finished in one reply.

## Step 0: Pick the mode and the facts

- **Mode A, create:** the user gives product facts and, ideally, keywords. Build a new listing.
- **Mode B, optimize:** the user pastes an existing listing (title, bullets, description), or gives an Amazon URL. Audit it and rewrite it.
- If the user gives only an ASIN or URL, call `web_extract` on it once. If the page is blocked or empty, say so in one line, then work from whatever text the user did give. If there is none, treat it as Mode A from the product type named in the message and mark every product fact as an assumption.
- **Marketplace:** use the one named (US, UK, DE, FR, IT, ES, JP, CA, AU, IN, MX, BR); otherwise assume US and say so. The whole listing is written in that marketplace's language (DE German, FR French, JP Japanese, ES and MX Spanish, IT Italian, BR Portuguese, the rest English), whatever language the user wrote in. Use the local units and spelling.
- **Tone:** Professional (specs, trust; the default), Friendly (conversational, benefit-led), Urgent (problem-solving, action words) or Luxury (premium, sensory). Use what the user asked for.
- Never open with questions. Decide, state the assumptions in one short line, and deliver.

## Step 1: Build the keyword list

1. Use the user's keywords first. Keep their wording.
2. If competitor listings or ASINs are given, read them with `web_extract` (at most 3 pages) and take the repeated phrases from their titles and bullets as extra keywords. If a page can't be read, say so and move on.
3. If the user gave no keywords at all, derive 8 to 12 from the product facts and at most one `web_search`, and label them "derived, no volume data".
4. Search volumes: use a figure only if the user gave it. Otherwise leave the Volume column out. Never invent volumes.

Sort the keywords into tiers:

- **Primary** (the 2 to 4 strongest, most specific to the product): must be in the title. Put the first one near the front, after the brand.
- **Secondary**: each in a bullet, about one per bullet.
- **Tertiary and long-tail**: description, or backend search terms if they will not fit naturally.

## Step 2: Write the listing

Use only facts the user gave. If an attribute is missing (material, size, what is in the box, warranty), leave it out of the copy or write `<not given: add yours>` as a visible placeholder. Never invent specs, certifications, review counts, awards, guarantees or "tested by" claims.

**Title**
- Shape: Brand + primary keyword + key attributes (size, quantity, colour, material) + secondary keyword + one differentiator.
- Hard limit 200 characters. Aim for 150 or fewer, with the most important words in the first 80 so mobile does not cut them. Some categories allow less, so tell the seller to check theirs.
- Capitalise the first letter of each word. No ALL CAPS words except the brand. No "best", "#1", "top rated", prices, or promotional phrases. No repeating a word more than twice.

**Five bullets**
- Each starts with a short benefit header in CAPS, then a dash and one or two sentences. Under 500 characters each; aim for 200 to 300.
- Bullet 1: main feature and the primary keyword. 2: top use case and a secondary keyword. 3: quality or material. 4: what is included or what it fits. 5: care, support or the differentiator.
- Benefits first, specs second. Every bullet carries at least one target keyword, written naturally.

**Description**
- Under 2,000 characters. Open with the problem the product solves, expand on features as benefits without repeating the bullets word for word, and close with what is in the box and a calm call to action.
- Place the tertiary keywords here. Short paragraphs.

**Backend search terms**
- A single comma-free line of words, under 250 bytes in total, for keywords that did not fit. Do not repeat words already in the title or bullets, and leave out brand names of other companies, punctuation and filler.

**Compliance**
- No medical or health claims, no "FDA approved", "eco" or "organic" claims, and no competitor brand names unless the user supplied the proof or said it is theirs. Add a note listing any claim in the copy the seller must be able to prove.

## Step 3: Count, do not guess

Put the finished title, bullets, description and backend terms, plus the keyword list, into one `execute_code` call that prints:
- the character count of the title, each bullet and the description, and the byte count of the backend terms;
- for every keyword, whether it appears (case-insensitive, whole phrase) in the title, in any bullet, and in the description;
- the coverage figure: keywords found in title, bullets or description, divided by total keywords, as a percentage.

Copy the printed numbers into the reply. If a limit is broken or a primary keyword is missing from the title, fix the copy and run the check again. Do the same for before-and-after counts in Mode B. All arithmetic comes from code.

Coverage bands: 90% or more is excellent, 70 to 89% is good with minor gaps, under 70% needs work. A keyword that sits only in the backend terms counts as "backend only", not as covered in the visible copy.

## Step 4 (Mode B only): Audit before rewriting

Score what was supplied on the eight dimensions below. Only score a dimension if the user gave its data (images, A+ content, price and reviews are rarely pasted); otherwise write "not given, not scored" and give a recommendation instead. Show the score as points out of the total available for the dimensions that were scored.

| Dimension | Max | What to judge |
|---|---|---|
| Title | 15 | Primary keyword near the front, brand, attributes, length, no banned phrases |
| Bullets | 15 | All 5 used, benefit-first, keywords natural, lengths |
| Description | 10 | Keywords not already in the title and bullets, readable, problem-to-solution flow |
| SEO coverage | 10 | Keyword coverage percentage, long-tail present, no wasted repeats |
| Images | 15 | 7 or more, white-background main image, infographic, lifestyle, size reference |
| A+ content | 10 | Present, brand story, comparison chart |
| Pricing | 10 | Competitive, coupon or deal |
| Reviews | 15 | Rating and count, recent sentiment |

Keep what already works in the original (strong phrases, the brand voice) and say so. The rewrite must contain every missing keyword, placed by the Step 1 tiers.

## Output shape

The reply holds the full listing in the reply itself, never "I've prepared your listing" without the text. Use this order:

1. One line: marketplace, tone, mode and any assumptions.
2. `## Title`, with its character count in brackets.
3. `## Bullet Points`: five numbered bullets.
4. `## Description`.
5. `## Backend Search Terms`.
6. `## Keyword Coverage`: a table with Keyword, In Title, In Bullets, In Description, Status (use Yes and No), then the coverage percentage and the character counts from Step 3. Mode B shows Before and After columns.
7. Mode B only: `## Audit` (the score table from Step 4, with the key change per row) and `## What Changed` (original and optimized title, then each bullet that changed, naming the keywords added).
8. `## Seller To-Do`: things the copy cannot fix (images, A+ content, price, claims to verify, placeholders to fill, category title limits). Short.

## Hard rules

- No invented numbers, volumes, ratings, review counts, specs or claims. Missing facts are marked as assumptions or `<not given: add yours>` placeholders.
- Every coverage and length figure comes from the `execute_code` run.
- Do not stuff keywords: a phrase repeats at most twice across the title and bullets, and the copy has to read like a person wrote it.
- The listing is a draft for the seller to review. Nothing is posted to Amazon.
- Amazon's limits and category rules change. If the user asks about a specific policy, check it with `web_search` and link what you found.
