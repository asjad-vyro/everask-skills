---
name: Site Migration and Redirect Map Planner
description: >
  Turns a list of old URLs and a description of the new site into a redirect map (CSV) plus a migration plan with keep/merge/drop decisions, cutover checks and 30/60/90-day monitoring.
  Use it for "build a redirect map", "plan our WordPress to Shopify migration", "we're changing domains, what do we redirect?", "merge two blogs without losing SEO".
---

# Site Migration and Redirect Map Planner

A good result is a redirect map the developer can load as it stands (every old URL has one final destination, no chains, no homepage dumping) and a short plan that says what to keep, merge or drop, how to cut over, and what to watch afterwards. Finish in one reply: do not wait for the user to supply more.

## Hard rules

- Use only URLs, traffic, backlink and platform facts the user gave or a tool returned. Never invent traffic numbers, backlink counts, rankings or URLs. Where data is missing write "not given" and say what it affects.
- Every figure in the reply (counts, percentages) comes from `execute_code` output, never mental arithmetic.
- Do not use real expected-drop numbers as promises: say traffic often dips after a move and usually recovers over weeks, and that this depends on the site.
- The plan is advice for a technical team, not a guarantee of search results.
- Proposed destination URLs that the user did not provide are marked "proposed" in the notes column.

## Step 1: Read what the user gave

Work out, from the message, pasted URLs, sitemap text or attachments:
1. Old URLs (pasted list, sitemap XML, CSV). If only a domain is given and the user wants a real map, use `web_extract` on `<domain>/sitemap.xml` once (at most two calls). If that fails, say so and build the plan with the pattern rules in Step 3.
2. New structure: the new URL scheme, platform and domain. If only the platform is named (for example WordPress to Shopify), apply that platform's standard URL patterns, mark them "assumed", and tell the user to confirm them. Search for the current patterns with one `web_search` if unsure; do not rely on memory for platform-specific paths.
3. Goal and constraints: reason for the move, date, who does the work.

Write a three-line "Assumptions" list for anything you had to decide. Do not ask questions with `clarify` unless there is neither a URL list nor a platform or domain to work from.

## Step 2: Classify every old URL

In `execute_code`, load the old URLs into a table, normalise them (lower-case host, strip tracking parameters, pick one trailing-slash form, strip fragments) and drop exact duplicates, keeping a count of what was dropped. Give each URL a type (home, article, product, category, landing page, document/PDF, image, feed, tag/archive, utility such as login or search, other) and a decision:

- **Keep**: has a direct new equivalent.
- **Merge**: several old pages become one new page.
- **Redirect**: no equivalent, point to the closest related page.
- **Drop**: intentionally gone, low value, serves 410.

If the user gave traffic or backlink data, rank by it: pages with traffic or backlinks must get a specific destination, never a catch-all. If they gave none, say priority could not be ranked and suggest pulling it from analytics, Search Console and a backlink tool.

## Step 3: Build the redirect map

Columns: `old_url, new_url, status_code, decision, reason, priority, notes`.

- 301 for content with a new home. 410 for intentionally deleted content (new_url blank). Use 302/307 only for genuinely temporary moves, and say why.
- Never send unrelated pages to the homepage. Use the closest related page or category.
- For a domain-only move, default to 1:1 path mapping (`old.com/page` to `new.com/page`) and list only the exceptions.
- Pattern rules are fine for low-priority bulk (for example `/blog/<slug>` to `/articles/<slug>`): write the rule once and list a few expanded examples.
- Cover non-HTML URLs (PDFs, images, downloads, feeds) and query-string variants.
- Pick one canonical trailing-slash form and add a normalising rule for the other.

Then run these checks in `execute_code` and print the results: (a) chains and loops: any `new_url` that is itself an `old_url` must be collapsed so the old URL points to the final destination; (b) duplicate old URLs with different targets; (c) old URLs with no row; (d) rows sending more than a handful of different old URLs to the same destination, which are merge candidates or a sign of dumping; (e) any destination that is a homepage for a non-homepage source. Fix what you find, then report the counts: total rows, by status code, by decision, chains fixed, orphans flagged.

Save the map as `redirect-map-<site or domain>.csv` under `/tmp/.scratch/site-migration-redirect-plan/` and publish it with `publish_artifact` (`kind: "file"`). Also include the full map in the reply when it has 40 rows or fewer; for longer maps show the first 25 rows, all exceptions and orphans, and the pattern rules.

## Step 4: Spot-check (optional, small)

If the old site is live and the user gave real URLs, use `web_extract` on up to three of the highest-priority old URLs to confirm they resolve and to see their title, so the destination choice is sound. If the new site is live, check up to two destinations. Report what you checked. If you could not check, say the map is untested. For the developer's own testing list the commands in `references/cutover-and-monitoring.md`; do not claim they were run.

## Step 5: Write the plan

Read `references/cutover-and-monitoring.md` before writing the cutover and monitoring sections. Reply with these sections in order:

1. **Summary**: what is moving, from where to where, and the assumptions.
2. **Inventory and decisions**: table of counts by type and by decision, plus the pages that need a human call (listed with the reason).
3. **Redirect map**: the CSV link and the table or sample as in Step 3, then the check results.
4. **Orphans and risks**: URLs with no good destination, high-value pages, URLs that need the owner's input.
5. **Cutover plan**: pre-cutover, switch day, first-hour checks, rollback triggers. Tailor to the platform and to whether the domain changes.
6. **Monitoring plan**: first week, 30, 60 and 90 days, with what to check, the tool to use, and the action if it is off.
7. **Owners and timeline**: roles (migration lead, tech, SEO, content, comms, support) with owner "to assign" and relative dates (T-7 days, T-0, T+30 days), not invented calendar dates.
8. **Open items**: what the user must confirm or supply for the map to be final.

Keep the plan tight: bullets and tables, no filler. If the user asked only for the redirect map, give sections 1, 3 and 4 and a short note on cutover.
