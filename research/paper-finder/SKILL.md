---
name: arXiv Paper Finder
description: >
  Finds real arXiv papers by topic, author or ID and gives a reading list with a one-line summary and link for each.
  Also summarises one paper with related work to read next, and writes BibTeX entries.
  Use it for "find arXiv papers on ...", "latest research on ...", "papers by ... from the last two years",
  "summarise arXiv 1706.03762", "related work for this paper", "BibTeX for this paper".
---

# arXiv Paper Finder

A good result is a short, usable answer in which every paper is real: its title, authors, date and ID come from the arXiv or Semantic Scholar output you just retrieved, and each paper has its link. The whole answer goes in the reply. Do not stop at "I found some papers".

## Step 1: Decide what is being asked

Pick the path from the user's message. Do not open with questions: decide, state what you assumed in one line, and deliver. Use `clarify` only if the message has no topic, author, title or paper ID at all.

| The user wants | Path |
|---|---|
| Papers on a topic, "the latest", "a reading list" | Step 3, then the reading list in Step 6 |
| Papers by a person | Step 3 with `--author`, then the reading list in Step 6 |
| One paper summarised, given as an ID, link or title | Step 4, then the paper summary in Step 6 |
| Related work, or what to read next, for a paper | Steps 4 and 5, then the paper summary in Step 6 |
| BibTeX or a citation | the BibTeX part of Step 6 |

Defaults when the user did not say: 5 papers in a reading list (at most 15). Newest first when the user says latest, recent or new, or gives a time window such as "last two years"; otherwise most relevant first. A time window becomes `--since` in Step 3.

## Step 2: Find the scripts

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `search_arxiv.py` under `~/.computer/skills` with `search_files`.

Run commands with `terminal`, one at a time. arXiv allows about one request every 3 seconds. The search script keeps to that by pausing 3 seconds before it exits, so each command takes a little longer than the request itself. Never run several searches in parallel.

## Step 3: Search arXiv

Turn the request into 2 to 4 plain keywords (drop words such as "latest", "papers", "recent"), then run one of these:

| Job | Command |
|---|---|
| Topic, newest first | `python3 SKILL_DIR/scripts/search_arxiv.py "retrieval augmented generation" --phrase --sort date --max 15` |
| Topic, most relevant first | `python3 SKILL_DIR/scripts/search_arxiv.py "GRPO reinforcement learning" --max 15` |
| A person, in a time window | `python3 SKILL_DIR/scripts/search_arxiv.py --author "Yann LeCun" --since 2y --max 15` |
| A subject area | `python3 SKILL_DIR/scripts/search_arxiv.py --category cs.CV --since 30d --max 15` |
| A paper by its title | `python3 SKILL_DIR/scripts/search_arxiv.py --title "Attention Is All You Need" --max 3` |
| Papers by ID | `python3 SKILL_DIR/scripts/search_arxiv.py --id 1706.03762,1810.04805` |

`--phrase` needs the words together as one phrase: use it for a named technique or concept, and leave it off when the topic is several separate ideas. `--since` and `--until` take `2025-01-31`, `2025-01`, `2025`, `2y`, `6m` or `30d`. `--sort date` is newest first. Topic words, `--author`, `--title`, `--category` and the dates can be combined.

Then:

1. Ask for about three times as many papers as you need (`--max 15` for a list of 5). Keep the ones whose title or abstract is really about the topic; a title that names the topic always counts. Drop papers that only mention it in passing, duplicates, and any that print a WARNING about withdrawal (unless the user asked for that paper). When the user wants the latest, the list is the newest papers that pass this test: do not skip a newer one for an older one. The list shows only the first 600 characters of each abstract (a trailing `...` marks the cut), so write each one-line summary from the title and the part you can see, and do not guess what the cut-off hides. To read a full abstract, run `search_arxiv.py --id <ID>`.
2. If it says "No papers found", loosen the search (drop `--phrase`, use fewer words, widen `--since`) and run it again. Stop after three searches.
3. An ERROR line means arXiv could not be reached, and the script has already retried once. Run it one more time. If it fails again, use `web_search` for `site:arxiv.org <topic>`, read the `https://arxiv.org/abs/<ID>` pages you find with `web_extract` for title, authors and date, and tell the user the arXiv API was unavailable.
4. Read `references/query-syntax.md` when these options cannot express the search (leave out a subtopic, a title-only topic search, an OR of two phrasings) or when you are unsure of a category code.
5. Authors share names and arXiv has no author IDs. For a person search, keep papers whose Authors line has the full name, and say so if you cannot tell that they are all the same person.

## Step 4: Summarise one paper

1. Run `python3 SKILL_DIR/scripts/search_arxiv.py --id <ID>`. If the user gave only a title, run the `--title` command from Step 3 and take the matching paper. It prints the title, authors, dates, categories, full abstract and links.
2. Read the paper itself with `web_extract` on `https://arxiv.org/html/<ID>`. If there is no such page, use `https://arxiv.org/pdf/<ID>`. If a result says the PDF was binary or unreadable, or says it is "based on known content" or is otherwise written from memory, you have not read the paper: try `https://ar5iv.labs.arxiv.org/html/<ID>`.
3. If you still could not read the full text, write the summary from the abstract alone. Begin the summary with "Based on the abstract only" and leave out whatever the abstract does not state (training setup, layer counts, hyperparameters, ablations).
4. Write the summary in the paper-summary shape in Step 6. Every number, result and claim must be in the abstract or the paper text you read. If the paper does not say it, do not say it.

## Step 5: Related work

1. Run `python3 SKILL_DIR/scripts/paper_references.py <ID> --limit 8`. It lists what the paper builds on, from Semantic Scholar, with authors, citation counts and links. To save a round trip, run it in the same `terminal` call as the lookup in Step 4.1, one command after the other, joined with `;`.
2. For later or neighbouring work, run one arXiv keyword search on the paper's topic (2 or 3 key terms from its title or abstract, `--since` the paper's year, `--max 15`). Take 3 to 5 papers other than the paper itself, preferring ones whose abstract says they build on, extend or compare with this paper's method over ones that only share keywords.
3. If `paper_references.py` prints an ERROR (a rate limit, or the paper is too new for Semantic Scholar), wait about 10 seconds and run it once more. If it still fails, skip it, give only the keyword-search papers, and say Semantic Scholar was unavailable.
4. Say which list each related paper came from, and keep every "how it relates" clause to text you actually hold:
   - A "Builds on" paper: `paper_references.py` gives only its title, year, authors, citation count and link. Say only what the paper text you read in Step 4 says about it (a baseline in a results table, the mechanism it replaces, the data it uses). Do not describe that paper's own method or findings. If the text you read does not mention it, write "Cited by this paper." and nothing more.
   - A later or neighbouring paper: say only what its abstract from `search_arxiv.py` says. Make no claim about how influential it is or what it led to.
   - Do not add a paper from memory: if you know one worth including, look it up with `search_arxiv.py --title` and use only what the script returns.

## Step 6: Write the reply

Put the finished answer in the reply, in one of these shapes.

**Reading list**

```
**Reading list: <topic>** - from arXiv, <newest first | most relevant first>, <submitted <window>, if any>. Showing <N> of <total> matches. <One line stating any assumption.>

1. **<Title>** - <first author> et al., <YYYY-MM-DD>. <One line, at most 30 words, on what the paper does or shows, from its abstract.> [arXiv:<ID>](https://arxiv.org/abs/<ID>)
2. ...

Notes: <a withdrawn paper you left out, authors you could not tell apart, fewer papers than asked for, the arXiv API being unavailable. Leave this line out if there is nothing to say.>
```

**Paper summary**

```
**<Title>** (arXiv:<ID with version>, first submitted <YYYY-MM-DD>)
Authors: <the authors as printed, first 6, then "et al." if more>
Links: [abstract](https://arxiv.org/abs/<ID>) | [PDF](https://arxiv.org/pdf/<ID>)

- Problem: <one or two sentences>
- Approach: <two or three sentences>
- Results: <the main results, with numbers exactly as the paper gives them>
- Limits: <what the paper itself admits; if it says nothing, "the paper does not discuss limits">

**Related work**
Builds on (from Semantic Scholar's reference list):
- **<Title>** (<year>), <first author> et al., <N> citations. <What the paper text says about it, or "Cited by this paper."> [arXiv:<ID>](<link>)
  (3 to 5 items from `paper_references.py`; <N> is the count it printed; for a reference with no arXiv ID, give the DOI or Semantic Scholar link it printed)
Later or neighbouring work (from the arXiv keyword search or a title lookup):
- **<Title>** (<year>), <first author> et al. <One line from its abstract, saying how it connects to this paper only if the abstract does.> [arXiv:<ID>](<link>)
  (3 to 5 items)
```

Add the Related work block only when the user asked for related work or what to read next. End the reply with the last list, or the Notes line: no closing offer and no closing note about sources.

**BibTeX**: run `python3 SKILL_DIR/scripts/search_arxiv.py --id <ID>,<ID> --bibtex` and paste the entries unchanged in one `bibtex` code block. If the user gave only titles, run `--title "<title>" --bibtex --max 1` for each and check that the title in the entry is the paper they meant.

## Rules

1. Titles, authors, dates, IDs and links come only from tool output in this chat. Never write them from memory, never list a paper you did not see in a tool result, and never describe a paper beyond what its abstract or the paper text you read says.
2. No invented numbers. Quote results only as the abstract or the paper states them. Citation counts appear only where `paper_references.py` printed them.
3. arXiv papers are preprints and are not necessarily peer reviewed. Do not say a paper was accepted or published anywhere unless the script printed it under "Authors' note" or "Journal ref", and then call it the authors' note.
4. The date shown for a paper is its "Published" date (first submission). When the user wants a citation, give the version the script printed.
5. When you show only some of the matches, say how many matched, so the user knows the list is a selection.
6. Do not make files for these answers: the reply is the deliverable. Use another format only if the user asks.
