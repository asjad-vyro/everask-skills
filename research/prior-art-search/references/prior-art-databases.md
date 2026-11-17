# Prior art databases and classification guide

Read this in Step 1 when forming queries and guessing classes.

## Free patent sources (reach them with `web_search` or `web_extract`)

- **Google Patents** (patents.google.com): best free full-text search. Covers US, EP, CN, WIPO, JP, KR and many more; machine-translates non-English patents and groups families. It may lag official offices, and it shows no authoritative legal status. Query operators in the page search: `inventor:`, `assignee:`, `CPC:`, `before:`, `after:`. Through `web_search`, use `site:patents.google.com <terms>`. Open a patent page with `web_extract` on its URL, for example `https://patents.google.com/patent/<number>`.
- **Espacenet** (worldwide.espacenet.com): very broad coverage, machine translation, legal-status events via INPADOC. The interface is awkward for `web_extract`; use it for a specific number if Google Patents lacks the page.
- **WIPO PATENTSCOPE** (patentscope.wipo.int): PCT international applications (WO publications).
- **USPTO Patent Center** (patentcenter.uspto.gov): US prosecution history. Often not readable by `web_extract`.
- **CNIPA** (China): the authoritative source for CN applications, in Chinese only. For CN inventions, search Google Patents with Chinese keywords first.

## Papers and other non-patent literature

Papers, theses, product manuals, web pages and talks published before the priority date are all prior art.

| Source | Use |
|---|---|
| Google Scholar | Broadest academic coverage; use `site:scholar.google.com <terms>` |
| arXiv | Preprints; `site:arxiv.org <terms>` |
| Semantic Scholar, OpenAlex, CrossRef | Pages are readable with `web_extract` when a search result points to them |
| Company sites, product pages, news | Existing products and announcements |

## IPC/CPC classification

A code reads Section, class, subclass, group, subgroup: for example a section letter, two digits, a subclass letter, then `group/subgroup`. Sections: A human necessities, B operations and transport, C chemistry and metallurgy, D textiles, E construction, F mechanical engineering, G physics, H electricity.

Common classes for software and electronics inventions:

- G06F: digital data processing
- G06N: computing models (AI and machine learning)
- G06T: image data processing
- G06Q: business, finance and administration data processing
- H04L: digital information transmission (networking)
- H04N: pictorial communication (video, images)

For other fields, guess from the invention (for example A61 for medical, G01 for measuring, H01 for basic electric elements) and state that the code is a guess. Confirm a code from a fetched patent page before relying on it. To widen a search, try the parent class; to narrow it, add a subgroup or combine the class with keywords.

## Search protocol

1. Keywords: core concept terms, then problem terms, then advantage or feature terms.
2. Classification: the guessed classes, then related ones.
3. Assignees: companies or universities known to work in the area.
4. Citations: if a close patent is found, look at what it cites and what cites it (the Google Patents page lists both).
5. Families: group the same invention filed in several countries and analyse one member.

## Per-reference record

Reference ID, type (patent, paper, other), title, date (publication or priority), assignee or authors, class codes, key teaching in two or three sentences, relevant claims, overlap rating (HIGH, MEDIUM, LOW), and relationship (anticipating, relevant, background). Write "not shown" for any field the page did not show.
