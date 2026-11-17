# Cutover and monitoring reference

Read this before writing the cutover and monitoring sections. Use the parts that fit the user's move; skip domain steps when the domain stays the same.

## Before cutover (T-7 days to T-1 day)

- Inventory complete and redirect map signed off by SEO and content owners.
- Destination built and tested on a staging site that mirrors production (same CDN, same redirect mechanism).
- A sample of redirects verified: the highest-traffic pages, the pages with most backlinks, and every edge case (query strings, trailing slashes, PDFs).
- Rollback plan written and tried on staging. Full backup of the source site.
- If the domain changes: lower DNS TTL a day or more ahead (for example 300 seconds), and verify both old and new domains in Search Console.
- Support team and stakeholders told the date and expected impact. Pick a quiet period, not a campaign or holiday peak.
- Content freeze on the source for the cutover window.
- Go/no-go call about two hours before. No-go if there is a critical bug on the destination, a key person is out, source data looks wrong, or the source platform has an outage.

## Switch day, in order

1. Final source backup; check it restores.
2. Deploy the destination to production and confirm it responds on its production address.
3. Deploy the redirect rules (htaccess, server config, CDN or edge rule, or the platform's redirect table) on the source side.
4. DNS change if the domain moves; check resolution from more than one resolver.
5. Submit the new sitemap in Google Search Console and Bing Webmaster Tools; add it to robots.txt; remove or update the old sitemap. If Google offers a change-of-address tool for the move, use it.
6. Update internal links, canonical tags and structured data to point at new URLs (crawlers follow canonicals even after redirects).
7. Update outside references: email templates, social bios, partner links, ad destination URLs, analytics goals that match on URL, CRM saved links.

## First hour

- Top 50 URLs from the inventory return the expected status.
- Redirects return 301, not 302, with a single hop.
- Critical flows work: sign-up, contact form, checkout if there is one.
- robots.txt and sitemap are reachable; analytics fire on new pages.
- Error logs clean of missing assets or broken integrations.

Commands for the developer to run (not run by the assistant): `curl -sI https://old.example/path` and check the status and `location` header; `curl -sIL` follows the chain and shows hop count; `dig +short new.example @8.8.8.8` checks DNS.

## Rollback

Roll back for: critical functionality broken, data corruption, a security issue, or indexing collapsing in a way that cannot be fixed forward. Do not roll back for a normal traffic dip, individual broken redirects, minor visual issues or slow pages: fix forward. Steps: reverse DNS, disable redirect rules, unlock the source, restore from backup if needed, tell stakeholders, hold a review within a week.

## Monitoring schedule

| When | Check | Tool | If it is off |
|---|---|---|---|
| Daily, week 1 | Organic traffic to the top 10 pages vs pre-move baseline | Analytics, Search Console | Check redirects, canonicals, indexing |
| Daily, week 1 | 404 and 5xx rate in logs and in Search Console | Server logs, Search Console | Add missing redirects, fix errors |
| Daily, week 1 | Conversion rate vs baseline | Analytics | Check tracking set-up and UX changes |
| Weekly to day 30 | Indexing of new URLs, crawl errors | Search Console | Resubmit sitemap, inspect stalled URLs |
| Weekly to day 30 | Rankings of the top 20 keywords | Rank tracker or Search Console | A sudden cliff points to a redirect or canonical fault |
| Day 30 | Total organic traffic vs baseline; pages with backlinks still resolving; 410 versus 404 for removed pages | Analytics, backlink tool | Add redirects from 404 patterns; fix missed internal links |
| Day 60 | Traffic recovery trend; indexed page count vs pre-move; any old URLs still ranking | Search Console | Investigate persistent gaps page by page |
| Day 90 | Full review against baseline; decide when to decommission the old platform | All of the above | Keep the old domain renewed long-term so redirects keep working |

Traffic often dips after a move and usually recovers over several weeks, but how much and how long depends on the site: judge against the user's own baseline, not a fixed number. A drop that persists well beyond the first month deserves an investigation.

## Common surprises

- Backlinks pointing at URLs missing from the inventory (old campaigns, archived posts): add them after cutover from 404 logs and a backlink report.
- `/page` and `/page/` treated differently: add a normalising rule.
- Old URLs stay in search results for weeks: normal; do not redirect them to the homepage to speed it up.
- URL-based analytics goals stop matching: update them.
- Cached sitemaps or a robots.txt that omits the new sitemap.
- Leaving the old site live alongside the new one: duplicate content; take it down once the destination is solid.

## Message templates (drafts only)

Internal: "The migration to <new platform or URL> is complete as of <time>. <N> redirects are in place and critical flows are verified. Watch <channel> for issues over the next 24 hours." Fill the placeholders from the user's facts only.

Customers: "We have moved to <new address>. Old links should redirect automatically. If you find a broken link, tell us at <contact>."
