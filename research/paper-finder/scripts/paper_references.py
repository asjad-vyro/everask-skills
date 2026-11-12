#!/usr/bin/env python3
"""List the papers an arXiv paper cites (what it builds on).

References that Semantic Scholar flags as influential for the paper come first, then the
rest by citation count. Data comes from the Semantic Scholar open API. Standard library only.

Examples (use the full path to this file):
    python3 paper_references.py 1706.03762
    python3 paper_references.py 1706.03762 --limit 10

Semantic Scholar rate-limits its open API, so the script retries twice before giving up.
Exit codes: 0 ok, 1 bad input, 2 network or server error, 3 rate-limited,
            4 Semantic Scholar has no reference list for this paper (often a very new paper).
"""
import argparse
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.semanticscholar.org/graph/v1/paper/arXiv:%s/references"
FIELDS = "isInfluential,title,year,citationCount,externalIds,authors"
USER_AGENT = "paper-finder-skill/1.0"
RETRY_WAITS = (4, 8)  # seconds before the 2nd and 3rd attempt


def fail(code, message):
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(code)


def clean_id(text):
    m = re.search(r"\d{4}\.\d{4,5}", text) or re.search(r"[a-z]+(?:-[a-z]+)*(?:\.[A-Za-z]{2})?/\d{7}", text)
    return m.group(0) if m else None


def get_json(url):
    last = "unknown problem"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code == 404:
                fail(4, "Semantic Scholar does not know this paper (very new papers are often missing).")
            last = "HTTP %d" % err.code
            if err.code not in (429, 500, 502, 503, 504):
                fail(2, "Semantic Scholar answered %s." % last)
            rate_limited = err.code == 429
        except (OSError, http.client.HTTPException, ValueError) as err:
            last = "network error: %s" % err
            rate_limited = False
        if attempt < len(RETRY_WAITS):
            time.sleep(RETRY_WAITS[attempt])
    if rate_limited:
        fail(3, "Semantic Scholar is rate-limiting requests right now (%s)." % last)
    fail(2, "could not get a reply from Semantic Scholar (%s)." % last)


def author_text(authors):
    if not authors:
        return "authors not listed"
    if len(authors) <= 3:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + ", et al."


def link(ref):
    if ref["arxiv"]:
        return "arXiv:%s | https://arxiv.org/abs/%s" % (ref["arxiv"], ref["arxiv"])
    if ref["doi"]:
        return "DOI:%s | https://doi.org/%s" % (ref["doi"], ref["doi"])
    if ref["pid"]:
        return "https://www.semanticscholar.org/paper/%s" % ref["pid"]
    return "no link"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arxiv_id", help="arXiv ID, e.g. 1706.03762 (a URL or 'arXiv:' prefix also works)")
    ap.add_argument("--limit", type=int, default=8, help="how many references to show (default 8)")
    args = ap.parse_args()

    paper_id = clean_id(args.arxiv_id)
    if not paper_id:
        fail(1, "'%s' does not look like an arXiv ID" % args.arxiv_id)
    url = (API % urllib.parse.quote(paper_id, safe="")) + "?" + urllib.parse.urlencode(
        {"fields": FIELDS, "limit": "1000"})
    data = get_json(url)

    refs = []
    for row in data.get("data") or []:
        cited = row.get("citedPaper") or {}
        title = " ".join((cited.get("title") or "").split())
        if not title:
            continue
        ext = cited.get("externalIds") or {}
        refs.append({
            "title": title,
            "year": cited.get("year"),
            "cites": cited.get("citationCount") or 0,
            "influential": bool(row.get("isInfluential")),
            "authors": [a.get("name") for a in (cited.get("authors") or []) if a.get("name")],
            "arxiv": ext.get("ArXiv"),
            "doi": ext.get("DOI"),
            "pid": cited.get("paperId"),
        })
    if not refs:
        fail(4, "Semantic Scholar has no reference list for arXiv:%s yet." % paper_id)

    refs.sort(key=lambda r: (not r["influential"], -r["cites"]))
    shown = refs[:max(1, args.limit)]
    print("Semantic Scholar lists %d references for arXiv:%s. Shown: %d, influential ones first, then most cited." % (
        len(refs), paper_id, len(shown)))
    print()
    for i, r in enumerate(shown, 1):
        flag = " - flagged influential" if r["influential"] else ""
        print("%d. %s (%s) - %s - %s citations%s - %s" % (
            i, r["title"], r["year"] or "n.d.", author_text(r["authors"]),
            format(r["cites"], ","), flag, link(r)))
    print()
    print("Citation counts and the influential flag are from Semantic Scholar and can differ from other sources.")


if __name__ == "__main__":
    main()
