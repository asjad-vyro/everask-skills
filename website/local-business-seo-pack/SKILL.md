---
name: Local Business SEO Pack
description: >
  Turns a local business's details into a ready-to-paste SEO pack: head tags with Open Graph, LocalBusiness JSON-LD, robots.txt and sitemap.xml, checked for valid JSON.
  Use it for "write schema markup for my business", "meta tags and sitemap for my cafe site", "LocalBusiness JSON-LD", "robots.txt and sitemap.xml".
---

# Local Business SEO Pack

The user gets files they can paste into their site: a `<head>` block, JSON-LD structured data, `robots.txt` and `sitemap.xml`, all built only from the facts they gave. Works for any country.

## Step 1: Collect the facts

Take everything from the user's message (and an attached file or a page they link: read it with `web_extract`). Do not ask questions; decide, and list assumptions at the end.

Needed: business name, what they do, city or suburb, phone, website URL. Useful if given: street address, postcode, region, country, opening hours, email, price range, social profile URLs, service areas, services, page list, logo or image URL, coordinates, tax or company number, FAQ questions.

Hard rules on facts:
- Never invent a phone number, address, hours, coordinates, rating, review count, price, founding year, social URL or FAQ answer. If a field was not given, leave the property out of the JSON-LD (do not write empty strings or "TBC").
- If the website URL is missing, use `https://www.example.com` and mark it as a placeholder to replace. Image URL missing: use `{SITE_URL}/og-image.jpg` style placeholder and say so.
- Opening hours that were given must be copied exactly. Days not mentioned are closed (omit them).
- Copy address parts exactly as given: do not add a county, region or postcode the user did not give. Titles and descriptions may only claim services, places, customer types, specialities and phrases the user stated (no "homes and businesses", "speciality coffee", "city centre", "family-run", "free quotes" unless given). If the user gave little, keep the copy plain and generic.
- Do not state typical prices or callout fees in FAQ answers unless the user supplied them.

## Step 2: Build the JSON-LD

Read `references/schema-guide.md` for the subtype table, property list and examples. Then:

1. Pick the most specific schema.org subtype (Plumber, Dentist, Restaurant, and so on), else `LocalBusiness`.
2. Build one `LocalBusiness` object for the homepage with `@context`, `@type`, `@id` (`{url}/#organization`), `name`, `url`, `telephone` in international format (+country code, digits, no spaces needed), `address` (PostalAddress with country as a 2-letter ISO code), plus every optional property the user supplied: `description`, `image`, `email`, `priceRange`, `geo`, `openingHoursSpecification`, `areaServed`, `sameAs`.
3. If the user listed services, add a `Service` object per service whose `provider` is `{"@id": "{url}/#organization"}`.
4. If the user gave FAQ questions with answers, or asked for FAQ schema and provided Q&A, add a `FAQPage`. If they asked for FAQ schema without answers, write 3 to 4 short questions with answers using only the given facts, and flag them as drafts to check.
5. Combine as one JSON array or `@graph` in a single script tag, or separate script tags, whichever is simpler.

## Step 3: Head tags

Fill the template in `references/head-template.html` for the homepage (and one extra block for each additional page the user named, with its own title, description and canonical URL).
- Title: 50 to 60 characters, `Service in Place | Brand` or `Brand - Tagline`.
- Meta description: 150 to 160 characters, naming the service, the place and a call to action. Include the phone number only if given.
- Drop the geo meta tags if no coordinates were given (keep `geo.region` and `geo.placename` if region and city are known). Region is ISO 3166-2, for example `GB-ENG`, `US-TX`, `AU-NSW`.
- Escape `&` and quotes inside attributes.

## Step 4: robots.txt and sitemap.xml

- `robots.txt`: `User-agent: *`, `Allow: /`, blank line, `Sitemap: {SITE_URL}/sitemap.xml` (absolute URL).
- `sitemap.xml`: one `<url>` per page the user listed, each `<loc>` an absolute URL on the given domain. If no pages were listed, use home, `/services/`, `/about/`, `/contact/` and say these are assumed. `<lastmod>` is today's date from `execute_code` (`datetime.date.today()`), format YYYY-MM-DD. Priority 1.0 home, 0.8 services, 0.6 others.

## Step 5: Verify with code

Run `execute_code`: parse every JSON-LD block with `json.loads`, check `@context`, `@type`, `name`, `telephone`, `address` exist; parse the sitemap with `xml.etree.ElementTree`; confirm every sitemap `<loc>` starts with the site URL and robots.txt names the sitemap; measure title and description lengths. Fix anything that fails before replying. Also write the files to `/tmp/.scratch/local-business-seo-pack/` and publish them: use `publish_artifact` with `kind: "file"` for `robots.txt` and `sitemap.xml`, and one `.html` file (`head-tags.html`) with the head block, using `kind: "file"`.

## Step 6: Reply

The reply must contain the full content, not just links:
1. One line on what was built.
2. The `<head>` block in an html code block (JSON-LD included).
3. `robots.txt` and `sitemap.xml` in code blocks.
4. "Checks" line: JSON parsed OK, number of URLs in sitemap, title and description lengths.
5. "Assumptions and placeholders": every value you made up or left as a placeholder.
6. "Next steps": paste the head into every page's `<head>` (change title, description and canonical per page), upload `robots.txt` and `sitemap.xml` to the site root, test the markup with Google's Rich Results Test and the schema.org validator, submit the sitemap in Google Search Console, and keep name, address and phone identical to the Google Business Profile.

Do not promise rankings. Do not use outdated markup claims: FAQ rich results in Google are limited, so say FAQ schema is optional.
