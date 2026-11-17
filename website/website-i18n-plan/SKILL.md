---
name: Website Localisation Plan
description: >
  Writes a complete plan for taking a website multi-language or multi-region: URL structure, a hreflang table with x-default, translation workflow, currency, date and RTL handling.
  Use it for "plan how to add German and French to my site", "subfolders or ccTLDs for my markets?", "audit my hreflang setup", "localise my website", "i18n plan".
---

# Website Localisation Plan

A good result is a plan the user can hand to a developer and a translator today: a clear pick on URL structure with the reasons, ready-to-paste hreflang markup, a translation workflow that survives content updates, and a per-locale checklist. It is delivered in the reply, in full. Never open with questions: if something is missing, assume it, say so in an "Assumptions" line, and go on.

## Step 1: Pin down the inputs

From the user's message (and a page, if they gave a URL), list:
- The locales in scope, as BCP 47 codes (`de-DE`, `fr-CA`, `ar`). If the user names only languages ("German and French"), keep language-only codes and say that region variants are a later option.
- The default (source) language and the site's platform, if stated (Shopify, WordPress, custom, and so on). If not stated, write "platform not given" and stay stack-agnostic.
- Business reason per locale, translation resources, and content volume. Anything not given is marked "assumed" or "not given". Do not invent traffic, revenue or word counts.

If the user gave a URL and the job is a plan or audit of that site, call `web_extract` on it once (at most two pages in total) to see the current structure, existing `hreflang` and `<html lang>`, and the language switcher. Report only what the page showed.

If the user pasted a URL list or hreflang markup for an audit, check it against the rules in Step 4 first, then deliver the audit findings above the plan.

## Step 2: Choose the URL structure (show the criteria, not only a pick)

Compare the patterns against the user's situation:

| Pattern | Example | Choose it when | Cost |
|---|---|---|---|
| Subfolder | example.com/de/ | Default for most sites. One domain, authority is shared, simplest to run. | Single hosting and one CMS; less legal or brand separation. |
| Subdomain | de.example.com | Separate infrastructure or team per market, large sites. | Treated more like a separate site; more setup. |
| ccTLD | example.de | Strong country focus, a local legal entity, local trust matters. | Separate domains to buy and maintain; authority is split per domain. |
| URL parameter | example.com?lang=de | Avoid. | Weak signal, easily dropped. |

Then decide and state:
1. The pattern, with two or three reasons tied to what the user told you. If the user asked "subfolder vs ccTLD", say which criteria would flip the answer (for example: separate legal entity, local payment or hosting rules, a marketing budget per country).
2. Language-only (`/de/`) or language plus region (`/de-de/`, `/de-at/`)? Use regions only when content, currency or legal terms differ by country.
3. Default locale at the apex or in a folder (`/en/`)? Apex is common but needs an `x-default` and care with canonicals.
4. Slugs: translated or kept identical across locales (either is fine; pick one and keep it consistent).

## Step 3: Choose the content structure

Pick one and say what is sustainable: **Mirror** (every page in every locale, best for marketing sites), **Subset** (some content only in some locales, for example products or blog posts), or **Local** (each locale largely independent). Name which pages go in the first release and which wait.

## Step 4: Build the hreflang table and markup

Read the rules in `references/locale-checklist.md` section "Search engine signals" if you need the full list. Produce:

1. A table with one row per locale: locale code, URL pattern for the homepage, and the `hreflang` value. Include a row for `x-default` (the fallback, normally the default-language version or a language chooser). Build the URLs from the user's real domain; if they gave none, use `https://www.example.com` and say it is a placeholder.
2. A ready-to-paste `<link rel="alternate" hreflang="..." href="...">` block for one sample page, covering every locale plus `x-default` and the page's own entry.
3. The rules, in brief: every page lists every equivalent including itself; links must be reciprocal; each page has a self-referencing canonical (never canonical a translation to the default language); use region codes (`es-ES` and `es-MX`) when more than one regional version of a language exists; for large sites put hreflang in the XML sitemap rather than the head.

## Step 5: Translation workflow

Describe, for the user's stated resources (or an assumed "AI draft plus human review" if none given):
1. Sources: in-house, agency, community, AI draft with human review. Machine translation is a starting point, not final copy for user-facing or brand-critical text.
2. Stages: source authored, translation requested, translated with translation memory, second-person review, localisation beyond translation (currency, units, examples), publish, update propagation.
3. Tooling: a spreadsheet with disciplined naming is enough for small volumes; a translation management system pays off as volume and locale count grow. Do not quote a word-count threshold as fact unless the user gave volumes; if you mention one, call it a commonly used rule of thumb.
4. Drift control: a rule for what happens when source content changes (flag the translated page as stale, a deadline for updating it, who owns it).

## Step 6: Localisation beyond translation

Read `references/locale-checklist.md` once, and select only the items that apply to the user's locales. Write a per-locale list covering: currency and number formats, dates and times, units, name and address forms, phone format, legal pages and consent (for example GDPR for EU audiences), payment methods, support hours, imagery, and text expansion (German is often longer than English). Give concrete examples for the user's actual locales (for instance `1,000.50` in en-US is `1.000,50` in de-DE). For RTL locales (Arabic, Hebrew, Persian, Urdu) add: mirrored layout, CSS logical properties such as `margin-inline-start`, flipped directional icons, and `dir="rtl"` on `<html>`.

When the user's request involves laws, tax or regulation, note that these change and tell the user to confirm the current rules for each market with a local specialist. This plan is not legal advice.

## Step 7: Language switcher, test plan, launch and maintenance

- Switcher: in the header or footer, locale names in their own language ("Deutsch", "Francais"), current locale marked, stays on the equivalent page, choice remembered, and never forces a redirect from the browser language (suggest a banner instead).
- Test plan: per locale, check rendering, hreflang validity and reciprocity, self-canonicals, currency and date formats, no untranslated strings (including form errors and emails), RTL layout, indexability.
- Monitoring: per-locale indexing, traffic from the target country, conversion compared with the default locale, translation freshness.
- Maintenance: update cadence, quarterly review, and a sunset rule (redirect a retired locale to the closest equivalent, do not leave 404s).

## Output shape (reply in this order)

1. **Summary**: two or three sentences with the recommendation.
2. **Assumptions**: each input that was not given, marked as assumed.
3. **Locales**: table of locale, priority, reason (reasons come from the user; otherwise "not given").
4. **URL structure**: the pick, the criteria, and what would change the decision.
5. **Content structure**
6. **hreflang plan**: the table and the markup block.
7. **Translation workflow**
8. **Localisation checklist** per locale
9. **Language switcher**
10. **Test plan** and **maintenance plan**
11. **First 30 days**: a short ordered list of actions (not dated unless the user gave dates).

For an audit of supplied markup or URLs, put a **Findings** section before the summary: each problem found, the URL or line it affects, and the fix. Common problems: missing reciprocal links, missing `x-default`, translation canonicalised to the default page, language without region where several regions exist, redirect by browser language, untranslated UI strings, currency baked into copy, hardcoded date formats.

## Hard rules

- Deliver the whole plan in the reply. Do not publish a file unless the user asks for one.
- Do not invent traffic, rankings, costs, or word counts. Write "not given" or mark an assumption.
- Do not copy the sample domain or locales from this skill: use the user's own.
- Do every count or sum in `execute_code`, never in your head.
- Keep to at most two `web_extract` or `web_search` calls.
