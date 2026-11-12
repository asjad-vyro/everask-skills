#!/usr/bin/env python3
"""Search arXiv and print clean, readable results. Standard library only.

Examples (use the full path to this file):
    python3 search_arxiv.py "retrieval augmented generation" --phrase --sort date --max 15
    python3 search_arxiv.py "GRPO reinforcement learning" --max 10
    python3 search_arxiv.py --author "Yann LeCun" --since 2y --max 10
    python3 search_arxiv.py --category cs.CV --since 30d --max 10
    python3 search_arxiv.py --title "Attention Is All You Need"
    python3 search_arxiv.py --id 1706.03762
    python3 search_arxiv.py --id 1706.03762,1810.04805 --bibtex
    python3 search_arxiv.py --raw 'ti:"diffusion" AND cat:cs.CV' --sort date

arXiv asks for at most one request every 3 seconds; this script waits when needed.
Exit codes: 0 done (also when nothing matched), 1 bad input, 2 arXiv unreachable.
"""
import argparse
import calendar
import datetime as dt
import http.client
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

try:
    import fcntl
except ImportError:  # not on Unix: skip the lock that queues parallel runs
    fcntl = None

API = "https://export.arxiv.org/api/query"
NS = {
    "a": "http://www.w3.org/2005/Atom",
    "o": "http://a9.com/-/spec/opensearch/1.1/",
    "x": "http://arxiv.org/schemas/atom",
}
USER_AGENT = "paper-finder-skill/1.0"
MIN_GAP = 3.0  # seconds between arXiv requests
ABSTRACT_CHARS = 600
STOP = {"a", "an", "the", "of", "for", "in", "on", "and", "or", "to", "with", "by",
        "from", "at", "as", "is", "are", "via"}
NEW_ID = re.compile(r"\d{4}\.\d{4,5}(?:v\d+)?")
OLD_ID = re.compile(r"[a-z]+(?:-[a-z]+)*(?:\.[A-Za-z]{2})?/\d{7}(?:v\d+)?")


def die(message, code=1):
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(code)


# ---------- request handling ----------

def hold_turn():
    """Make parallel runs queue up by locking this script file; no file is created.

    The lock is released when the process exits. main() sleeps MIN_GAP seconds before that,
    so two requests to arXiv are never closer together than MIN_GAP seconds.
    """
    if fcntl is None:
        return None
    try:
        handle = open(os.path.abspath(__file__), "rb")
        fcntl.flock(handle, fcntl.LOCK_EX)
        return handle
    except OSError:
        return None


def fetch(url):
    problem = "unknown problem"
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            problem = "HTTP %d" % err.code
            if err.code not in (429, 500, 502, 503, 504):
                break
        except (OSError, http.client.HTTPException) as err:
            problem = "network error: %s" % err
        if attempt == 1:
            time.sleep(5)
    die("could not get a reply from the arXiv API (%s)." % problem, 2)


# ---------- building the query ----------

def clean_words(text, drop_stop=True, min_len=1):
    text = re.sub(r"[-_/\"():\[\]]", " ", text)
    words = []
    for w in text.split():
        if drop_stop and w.lower() in STOP:
            continue
        if len(w.strip(".")) < min_len:
            continue
        words.append(w)
    return words


def parse_when(text, end_of_period):
    """2025, 2025-03, 2025-03-31, 2y, 6m or 30d -> a date."""
    t = text.strip().lower()
    today = dt.date.today()
    m = re.fullmatch(r"(\d+)\s*([ymd])", t)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "d":
            return today - dt.timedelta(days=n)
        months = n * 12 if unit == "y" else n
        year, month = divmod(today.year * 12 + today.month - 1 - months, 12)
        month += 1
        return dt.date(year, month, min(today.day, calendar.monthrange(year, month)[1]))
    m = re.fullmatch(r"(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", t)
    if not m:
        die("cannot read the date '%s'; use 2025-01-31, 2025-01, 2025, 2y, 6m or 30d" % text)
    year = int(m.group(1))
    try:
        if m.group(2) is None:
            return dt.date(year, 12, 31) if end_of_period else dt.date(year, 1, 1)
        month = int(m.group(2))
        if m.group(3) is None:
            return dt.date(year, month, calendar.monthrange(year, month)[1] if end_of_period else 1)
        return dt.date(year, month, int(m.group(3)))
    except (ValueError, calendar.IllegalMonthError):
        die("'%s' is not a real date" % text)


def date_clause(since, until):
    if not since and not until:
        return None
    start = parse_when(since, False) if since else dt.date(1991, 1, 1)
    end = parse_when(until, True) if until else dt.date.today()
    if start > end:
        die("--since is later than --until")
    return "submittedDate:[%s0000 TO %s2359]" % (start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))


def build_query(args, words):
    parts = []
    if args.raw:
        raw = args.raw.strip()
        parts.append("(%s)" % raw if " OR " in raw else raw)
    if words:
        if args.phrase:
            parts.append('all:"%s"' % " ".join(clean_words(" ".join(args.query), drop_stop=False)))
        else:
            parts.extend("all:%s" % w for w in words)
    if args.title:
        parts.append('ti:"%s"' % " ".join(clean_words(args.title, drop_stop=False)))
    if args.author:
        names = clean_words(args.author, min_len=2)
        if not names:
            die("--author needs a name")
        parts.extend("au:%s" % w for w in names)
    if args.category:
        if not re.fullmatch(r"[A-Za-z-]+(\.[A-Za-z-]+)?", args.category):
            die("'%s' is not an arXiv category such as cs.CL or stat.ML" % args.category)
        parts.append("cat:%s" % args.category)
    clause = date_clause(args.since, args.until)
    if clause:
        parts.append(clause)
    return " AND ".join(parts)


def normalize_id(text):
    m = NEW_ID.search(text) or OLD_ID.search(text)
    return m.group(0) if m else None


# ---------- reading the answer ----------

def text_of(el, tag):
    found = el.find(tag, NS)
    return " ".join(found.text.split()) if found is not None and found.text else ""


def paper_from(entry):
    raw_id = text_of(entry, "a:id")
    summary = text_of(entry, "a:summary")
    if not raw_id or "/api/errors" in raw_id:
        return {"error": summary or text_of(entry, "a:title") or "arXiv reported an error"}
    full_id = raw_id.split("/abs/", 1)[-1]
    m = re.match(r"^(.+?)(v\d+)?$", full_id)
    primary_el = entry.find("x:primary_category", NS)
    primary = primary_el.get("term") if primary_el is not None else ""
    cats = [c.get("term") for c in entry.findall("a:category", NS) if c.get("term")]
    if primary:
        cats = [primary] + [c for c in cats if c != primary]
    return {
        "title": text_of(entry, "a:title"),
        "id": m.group(1),
        "version": m.group(2) or "",
        "published": text_of(entry, "a:published")[:10],
        "updated": text_of(entry, "a:updated")[:10],
        "authors": [text_of(a, "a:name") for a in entry.findall("a:author", NS)],
        "cats": cats,
        "summary": summary,
        "comment": text_of(entry, "x:comment"),
        "journal": text_of(entry, "x:journal_ref"),
    }


def clip(text, n):
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " ..."


def author_line(authors, limit):
    if len(authors) <= limit:
        return ", ".join(authors)
    return "%s, ... (+%d more)" % (", ".join(authors[:limit]), len(authors) - limit)


def show(n, p, full, author_limit):
    print("%d. %s" % (n, p["title"]))
    print("   ID: %s%s | Published: %s | Updated: %s" % (p["id"], p["version"], p["published"], p["updated"]))
    print("   Authors: %s" % author_line(p["authors"], author_limit))
    print("   Categories: %s" % ", ".join(p["cats"]))
    if p["comment"]:
        print("   Authors' note: %s" % clip(p["comment"], 200))
    if p["journal"]:
        print("   Journal ref: %s" % clip(p["journal"], 200))
    if re.search(r"\b(withdrawn|retracted)\b", p["summary"] + " " + p["comment"], re.I):
        print("   WARNING: the abstract or note mentions withdrawal - check before listing it")
    print("   Abstract: %s" % (p["summary"] if full else clip(p["summary"], ABSTRACT_CHARS)))
    print("   Links: https://arxiv.org/abs/%s | https://arxiv.org/pdf/%s" % (p["id"], p["id"]))
    print()


def ascii_alnum(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]", "", text)


def bibtex(p):
    year = p["published"][:4]
    last = ascii_alnum((p["authors"][0].split() or [""])[-1]) if p["authors"] else ""
    key = "%s%s_%s" % (last or "arxiv", year, p["id"].replace(".", "").replace("/", ""))
    names = " and ".join(p["authors"][:20]) + (" and others" if len(p["authors"]) > 20 else "")
    fields = [
        ("title", "{%s}" % p["title"]),
        ("author", names),
        ("year", year),
        ("eprint", p["id"]),
        ("archivePrefix", "arXiv"),
        ("primaryClass", p["cats"][0] if p["cats"] else ""),
        ("url", "https://arxiv.org/abs/%s" % p["id"]),
    ]
    lines = ["  %-13s = {%s}," % (name, value) for name, value in fields if value]
    lines[-1] = lines[-1].rstrip(",")
    return "@misc{%s,\n%s\n}" % (key, "\n".join(lines))


# ---------- main ----------

def report(args, header, data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        die("arXiv sent a reply that is not valid XML (starts with %r)" % data[:120], 2)
    total_el = root.find("o:totalResults", NS)
    total = int(total_el.text) if total_el is not None and (total_el.text or "").strip().isdigit() else None
    papers = [paper_from(e) for e in root.findall("a:entry", NS)]
    good = [p for p in papers if "error" not in p]

    if not args.bibtex:
        print(header)
    for p in papers:
        if "error" in p:
            print("ERROR from arXiv: %s" % p["error"], file=sys.stderr)
    if not good:
        print("No papers found. Loosen the search: fewer words, drop --phrase, or widen the dates.")
        return

    if args.bibtex:
        print("\n\n".join(bibtex(p) for p in good))
        return
    if total is not None and not args.id:
        print("Found %d papers; showing %d.\n" % (total, len(good)))
    else:
        print()
    full = args.full or bool(args.id) or bool(args.title)
    author_limit = 60 if args.author else 10
    for i, p in enumerate(good, 1):
        show(i, p, full, author_limit)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="*", help="topic words; every word must appear in the paper record")
    ap.add_argument("--phrase", action="store_true", help="the topic words must appear together as an exact phrase")
    ap.add_argument("--author", help="author name; every part of the name must match")
    ap.add_argument("--category", help="arXiv category such as cs.CL, cs.CV, stat.ML")
    ap.add_argument("--title", help="exact phrase that must appear in the title")
    ap.add_argument("--since", help="first submitted on or after: 2025-01-31, 2025-01, 2025, 2y, 6m or 30d")
    ap.add_argument("--until", help="first submitted on or before (same forms as --since)")
    ap.add_argument("--id", help="arXiv IDs, comma separated; URLs and 'arXiv:' prefixes are accepted")
    ap.add_argument("--raw", help="a ready-made arXiv search_query string")
    ap.add_argument("--sort", choices=["relevance", "date", "updated"],
                    help="date = newest first. Default: relevance with a topic or title, date otherwise")
    ap.add_argument("--max", type=int, default=10, help="how many results to show (default 10, at most 50)")
    ap.add_argument("--full", action="store_true", help="print complete abstracts in lists")
    ap.add_argument("--bibtex", action="store_true", help="print BibTeX entries instead of the list")
    args = ap.parse_intermixed_args()

    words = clean_words(" ".join(args.query))
    if args.id:
        ids = []
        for chunk in re.split(r"[,\s]+", args.id.strip()):
            if not chunk:
                continue
            found = normalize_id(chunk)
            if not found:
                die("'%s' does not look like an arXiv ID (expected 1706.03762 or hep-th/0601001)" % chunk)
            ids.append(found)
        if not ids:
            die("--id needs at least one arXiv ID")
        params = {"id_list": ",".join(ids), "max_results": str(len(ids))}
        header = "arXiv lookup: " + ", ".join(ids)
    else:
        query = build_query(args, words)
        if not query:
            die("give topic words, --author, --category, --title, --id or --raw")
        sort = args.sort or ("relevance" if (words or args.title or args.raw) else "date")
        sort_by = {"relevance": "relevance", "date": "submittedDate", "updated": "lastUpdatedDate"}[sort]
        sort_label = {"relevance": "most relevant first", "date": "newest first",
                      "updated": "most recently updated first"}[sort]
        params = {"search_query": query, "start": "0", "max_results": str(max(1, min(50, args.max))),
                  "sortBy": sort_by, "sortOrder": "descending"}
        header = "arXiv search: %s (%s)" % (query, sort_label)

    lock = hold_turn()  # keep the handle: the lock lasts until this process exits
    data = fetch(API + "?" + urllib.parse.urlencode(params, safe=",/"))
    try:
        report(args, header, data)
    finally:
        sys.stdout.flush()
        time.sleep(MIN_GAP)  # the next arXiv request must be at least MIN_GAP seconds away
    del lock


if __name__ == "__main__":
    main()
