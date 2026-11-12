---
name: Topic Cluster Builder
description: >
  Turns a topic or keyword list into a content plan: pillar page, supporting articles, internal links and a writing order.
  Use it for "build a topic cluster around remote onboarding", "map pillar and spoke posts", "group these keywords into pages", "which keyword goes on which page", "plan the content for a new blog", "what is missing from our content on this topic?", "topical authority", "content silos".
---

# Topic Cluster Builder

A good result is a plan a writer can start on today: one pillar page, supporting pages that each answer one question, every keyword on exactly one page, the internal links between the pages and the order to write them in. The pillar page and its supporting pages, linked together, are a topic cluster. Put the whole plan in the reply. Every search figure in it (volume, difficulty, traffic, ranking) comes from the user or from a tool, never from you.

## Step 1: Read what the user gave

Work out which of these the user gave. They can combine.

- **A keyword list**, pasted or attached, with or without search volumes. It decides the pages (Step 3). Do not add pages to pad it.
- **Existing pages**: titles, URLs or a pasted list. They decide what is new and what only needs a refresh (Step 4).
- **One topic**, such as "remote onboarding": find the subtopics yourself (Step 2).
- **A whole site or field**, such as "a site about indoor plants": too broad for one pillar page. Split it into 3 or 4 clusters that do not overlap, each with its own pillar page and 6 to 8 supporting pages. Do Step 2 once for the whole field, then Steps 3 to 7 for each cluster in the short layout under "Output".

Ask with `clarify` only when there is neither a topic nor a keyword list. Otherwise do not ask: pick a default, state it under Assumptions in the reply, and deliver. Usual defaults: no existing content, so every page is new; a general audience; no stated publishing pace, so the order is by priority and not by month.

If the user asks you to pull volumes, difficulty or ranking pages from Ahrefs, Semrush or Google Search Console and that app is connected, use it and name it as the source of those figures. Otherwise work from what they gave you.

## Step 2: Find the subtopics

Skip this step when the user's keyword list already covers the topic.

1. Run 2 to 4 `web_search` calls (up to 5 for a whole field): the topic itself, the questions people ask about it, "best" and "vs" searches, and its common problems. Read at most two top results with `web_extract` and note the subtopics they cover. Do not search once per subtopic.
2. Check the list against each intent: awareness (what it is, why it matters), consideration (best options, X vs Y), how-to (steps, tutorials) and troubleshooting (not working, common mistakes). Then against each audience: beginners, advanced practitioners, people deciding what to buy or do.
3. Keep only subtopics that are different questions a person would search for. Aim for 8 to 15 supporting pages for one topic, up to 20 for a broad one.

If search does not work, build the list from the intents and audiences and say so under Assumptions. Subtopics you propose are ideas, not data: never call one popular or high-volume unless a number from the user or a tool says so.

## Step 3: Put every keyword on exactly one page

1. Group the keywords by what the searcher wants. Keywords that want the same answer go on one page: the primary keyword is the highest-volume one (with no volumes, the clearest phrasing) and the rest are "also covers". Signs of the same answer: singular and plural, the same words reordered, a synonym, "best" and "top", a year or place added to the same question.
2. Keywords that need a different kind of page get their own pages even when they share words, such as a how-to and a product roundup.
3. For a borderline pair, and only if `web_search` works, compare the results for both: mostly the same pages means one page (a commonly used rule of thumb is 7 or more of the top 10 shared). Do this for three pairs at most.
4. The pillar page targets the broad head term the other keywords sit under. With volumes, that is normally the highest-volume broad keyword. If the highest-volume keyword is narrow or commercial, keep it for a supporting page and say so.
5. Label each page's intent: informational, commercial (comparing options) or transactional.
6. A keyword that does not belong (off topic, a brand search) goes in a short "Not in this cluster" list with a reason. Never drop a keyword silently.
7. With no keyword list, give each page the search phrase a person would type, as a suggestion with no volume. A subtopic from Step 2 that has no keyword gets a page only if it fills a real gap; mark it "no keyword given".

## Step 4: Check existing content

Only when the user gave existing pages. Match each planned page to an existing one and mark it:

- **Covered**: a page answers it already. It only needs links.
- **Partial**: a page exists but is thin, out of date or answers a different question. It needs a refresh.
- **Gap**: nothing exists. It needs writing.

Give a quality score (1 to 5) for an existing page only if you have read it (`web_extract` on its URL, or text the user pasted); otherwise write "not assessed". Show traffic only if the user gave it. Coverage is covered pages out of planned pages, as a plain fraction; do not turn it into a ranking promise. If two existing pages answer the same question, say which to keep and which to merge into it.

## Step 5: Spec the pillar page

The pillar page is a hub, not a mega-article: an overview of the whole topic that works as the table of contents of the cluster. Give the recommended title, the target keyword and an outline: an intro, one section per supporting page (in the order of the table) with a 2 to 3 sentence summary and a link to it, then a short FAQ if the keywords include questions. Its length follows from that; do not try to cover each subtopic in full.

## Step 6: Plan the internal links

- The pillar page links to every supporting page, from the section that summarises it.
- Every supporting page links to the pillar page, in the intro or conclusion.
- Each supporting page links to 2 to 4 sibling pages, only where its text naturally mentions that topic.
- Vary the anchor text; do not use the exact keyword every time.
- Link to another cluster only where the topics are genuinely related.

Write one row per page: the page, every page it links to, example anchor text, and where in the page the links go.

## Step 7: Set the writing order

1. The pillar page first, even as a draft, so every new page has something to link to.
2. Then the new supporting pages. With volumes, the highest page total first. Without, the pages closest to what the site's business does first (comparisons, "best" and how-to pages), then beginner basics. Say which rule you used.
3. Refresh the Partial pages.
4. The remaining supporting pages.
5. Add each supporting page's link to the pillar page as it is published.

Give no dates. If the user stated a publishing pace, group the order by month at that pace.

## Step 8: Check before you reply

- **Keywords.** If the user gave keywords, run `execute_code` with their exact volumes. Adapt this, putting any set-aside keywords under a page called "Not in this cluster":

```python
given = {"standing desk height": 880, "ideal standing desk height": 90, "best standing desk": 5400}
pages = {"Pillar: standing desk guide": ["best standing desk"],
         "Page 2: standing desk height": ["standing desk height", "ideal standing desk height"]}
placed = [k for ks in pages.values() for k in ks]
print("missing:", set(given) - set(placed))
print("on two pages:", {k for k in placed if placed.count(k) > 1})
print("not in the list:", set(placed) - set(given))
for p, ks in pages.items():
    print(p, sum(given[k] for k in ks))
print("total", sum(given.values()))
```

  Fix the plan until the first three lines print an empty set, then use the printed sums in the reply. Never add volumes in your head.
- **Links.** Every supporting page has a link row that includes the pillar page, and the pillar page's row lists every supporting page.
- **Numbers.** Every volume, difficulty, traffic or ranking figure in the reply is one the user gave or a tool returned. Delete any other.

## Output

Write the plan in the reply, in this order:

```
# Topic cluster: <topic>

**Assumptions**
- one line each; say "no volume data was given" when that is true

**Summary**
- Pillar page: <title>, target keyword <keyword> (volume <n>)
- Supporting pages: <count> (<n> new, <n> to refresh)
- Total volume of all the keywords: <sum>

**Cluster map**
Pillar: <title>
├── 2. <supporting page> (<primary keyword>), informational
├── 3. <supporting page> (<primary keyword>), commercial
└── <last supporting page>

**Pages and keywords**
| # | Page (recommended title) | Type | Primary keyword (volume) | Also covers (volume each) | Intent | Page total |

**Pillar page spec**
Title, target keyword, outline (Step 5).

**Internal links**
| Page | Links to | Anchor text | Where |

**Writing order**
1. <page>, <reason>

**Not in this cluster**
- <keyword>, <reason>
```

- Every keyword the user gave appears in exactly one row of the pages table, with its volume exactly as given. Page total is the sum of its keywords' volumes.
- Leave out "(volume ...)", the volume columns and the total when no volumes were given. Show "(n new, n to refresh)" and a Status column (Covered, Partial or Gap, with the existing URL) only when the user gave existing pages. Leave out "Not in this cluster" when nothing was set aside.

**Short layout for a whole site or field.** Give Assumptions, then one block per cluster: the pillar page (title and target phrase) and one table with the columns `# | Page | Type | Target phrase | Intent | Links to`. In "Links to" name the pillar page and 2 to 3 sibling pages by number; the pillar page's row says "all supporting pages". State once, above the clusters, that every supporting page links to its pillar page, each pillar page links to all of its supporting pages, and anchor text should vary. Finish with the order to build the clusters in and the reason for it.

## Rules

- Never estimate, round or invent search volume, keyword difficulty, a competition or "easy/hard" rating, traffic, clicks or ranking positions. Use only numbers the user pasted or a connected tool returned, and name a tool as the source. With none, leave those columns out and say so in one line. If the user asks which pages are easiest to rank for and you have no difficulty data, say so under Writing order, do not guess, and order by the figures you do have.
- Do not promise rankings, predict a position, or state a percentage a cluster needs before it "starts ranking". A cluster is a commonly used way to organise content, not a guarantee.
- Do not invent sources, studies, competitors or what top pages say. Mention a competing page only if a search returned it, and link it.
- Plan titles, keywords, links and order. Do not write the articles unless asked.
- If the keyword list is long (over about 60), still assign every keyword, but put the full keyword-to-page table in a CSV published with `publish_artifact` (`kind: "file"`) and keep the reply to the map, the pillar page spec, the links and the order.
- If the user asks for the plan as a spreadsheet or document, still put it in the reply, then load the built-in `xlsx` or `docx` skill with `skill_view`, build the file and publish it with `publish_artifact`.
