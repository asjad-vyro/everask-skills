#!/usr/bin/env python3
"""Cross-check in-text citations against a reference list (standard library only).

Usage:
  python3 crosscheck.py TEXT_FILE [--refs REFS_FILE]

TEXT_FILE holds the body text followed by a heading such as "References" and the
reference list. With --refs, the list is read from REFS_FILE and TEXT_FILE is all body.
Handles author-year citations ("(Smith, 2020)", "Smith and Lee (2020)",
"(Smith et al., 2019; Lee 2018)", "García y López (2020)") and numeric citations
("[1]", "[1, 3]", "[2-4]", "[2]–[4]").
Prints JSON. It is a first pass: the caller must review every line.
"""
import json
import re
import sys
import unicodedata

HEAD = re.compile(
    r"^\s*#*\s*\**\s*(references?|reference list|bibliography|works cited|literature cited|sources)\s*\**\s*:?\s*$",
    re.I,
)
YEAR = r"(?:1[5-9]\d\d|20\d\d)[a-z]?|n\.d\."
# Any capital letter, not only A-Z, so names such as Çelik, Østergaard or Ünal are found.
UPPER = "[" + "".join(re.escape(c) for c in map(chr, range(0x10000)) if c.isupper()) + "]"
NAME = UPPER + r"[^\W\d_]+(?:[-'’][^\W\d_]+)*"
NAME_FULL = r"(?:(?i:van|von|de|der|den|di|da|del|la|le|al|el|bin|ibn|ter|ten)\s+)*" + NAME
# "and" between author names in common languages: and, &, y, e, et, und, en, og, och, i, ve.
AND = r"(?:and|&|y|e|et|und|en|og|och|i|ve)"


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("’", "'")).strip()


def split_doc(text, refs_text):
    if refs_text is not None:
        return text, refs_text
    lines = text.splitlines()
    idx = None
    for i, ln in enumerate(lines):
        if HEAD.match(ln):
            idx = i
    if idx is None:
        return text, ""
    return "\n".join(lines[:idx]), "\n".join(lines[idx + 1:])


def entries_from(refs):
    out = []
    for ln in refs.splitlines():
        if not ln.strip():
            continue
        # An indented line, or one starting in lower case, continues the entry above,
        # unless it starts with a surname particle and a name ("de Vries, J. ...").
        lower_start = ln.strip()[:1].islower() and not re.match(NAME_FULL, ln.strip())
        if out and (ln[:1] in " \t" or lower_start):
            out[-1] += " " + ln.strip()
        else:
            out.append(ln.strip())
    return out


def author_year_citations(body):
    found = []  # (surname, year, raw)
    # parenthetical groups containing a year
    for m in re.finditer(r"\(([^()]*?(?:%s)[^()]*)\)" % YEAR, body):
        for part in m.group(1).split(";"):
            part = re.sub(r"^\s*(?:e\.g\.,?|see also|see|cf\.|i\.e\.,?)\s+", "", part.strip(), flags=re.I)
            nm = re.match(r"(%s)" % NAME_FULL, part)
            years = re.findall(r"(%s)" % YEAR, part)
            if nm and years:
                for y in years:
                    found.append((nm.group(1), y, m.group(0)))
    # narrative: Smith (2020), Smith and Lee (2020), Smith et al. (2020)
    pat = r"(%s)(?:\s*%s\s*%s)*(?:\s+et al\.?)?(?:'s|’s)?\s*\(((?:%s)(?:\s*,\s*(?:%s))*)\)" % (
        NAME_FULL, AND, NAME_FULL, YEAR, YEAR)
    for m in re.finditer(pat, body):
        for y in re.findall(YEAR, m.group(2)):
            found.append((m.group(1), y, m.group(0)))
    seen, uniq = set(), []
    for s, y, raw in found:
        k = (norm(s), y.lower())
        if k not in seen:
            seen.add(k)
            uniq.append((s, y, raw))
    return uniq


def ref_key(entry):
    m = re.match(r"(%s)" % NAME_FULL, entry)
    surname = m.group(1) if m else entry.split(",")[0]
    ym = re.search(r"\((%s)\)" % YEAR, entry) or re.search(r"\b(%s)" % YEAR, entry)
    return surname, (ym.group(1) if ym else None)


def run_author_year(body, entries):
    cites = author_year_citations(body)
    refs = [(e,) + ref_key(e) for e in entries]
    cited_not_listed, year_mismatch = [], []
    used = set()
    def core(name):  # the surname without particles: "van der Berg" -> "berg"
        parts = norm(name).split()
        return parts[-1] if parts else ""

    for s, y, raw in cites:
        same = [i for i, (e, rs, ry) in enumerate(refs)
                if norm(e).startswith(norm(s) + " ") or norm(rs) == norm(s) or core(rs) == core(s)]
        exact = [i for i in same if refs[i][2] and refs[i][2].lower() == y.lower()]
        if exact:
            used.update(exact)
        elif same:
            used.update(same)
            year_mismatch.append({"cited": f"{s} {y}", "text": raw,
                                  "list_has": [{"entry": refs[i][0], "year": refs[i][2]} for i in same]})
        else:
            cited_not_listed.append({"cited": f"{s} {y}", "text": raw})
    listed_not_cited = [e for i, (e, rs, ry) in enumerate(refs) if i not in used]
    no_year = [e for e, rs, ry in refs if ry is None]
    seen, dups = {}, []
    for e, rs, ry in refs:
        k = (norm(rs), ry)
        if k in seen:
            dups.append([seen[k], e])
        else:
            seen[k] = e
    return {
        "style_guess": "author-year",
        "citations_found": [f"{s} {y}" for s, y, _ in cites],
        "entries_found": len(entries),
        "cited_not_listed": cited_not_listed,
        "year_mismatch": year_mismatch,
        "listed_not_cited": listed_not_cited,
        "entries_without_a_year": no_year,
        "possible_duplicates_same_first_author_and_year": dups,
    }


def expand(s):
    nums = []
    for part in re.split(r"\s*,\s*", s):
        r = re.match(r"(\d+)\s*[-–]\s*(\d+)$", part)
        if r and int(r.group(2)) >= int(r.group(1)) and int(r.group(2)) - int(r.group(1)) < 200:
            nums.extend(range(int(r.group(1)), int(r.group(2)) + 1))
        elif part.isdigit():
            nums.append(int(part))
    return nums


def run_numeric(body, entries):
    order = []
    for m in re.finditer(r"\[(\d+(?:\s*[-–,]\s*\d+)*)\]", body):
        for n in expand(m.group(1)):
            if n not in order:
                order.append(n)
    listed = {}
    for e in entries:
        m = re.match(r"\[?(\d+)[\].)]\s*(.*)", e)
        if m:
            listed[int(m.group(1))] = m.group(2)
    return {
        "style_guess": "numeric",
        "citation_numbers_in_order_of_first_use": order,
        "entries_found": len(entries),
        "cited_not_listed": sorted(n for n in order if n not in listed),
        "listed_not_cited": sorted(n for n in listed if n not in order),
        "first_use_order_is_sequential": order == sorted(order) and order == list(range(1, len(order) + 1)),
        "list_numbering_has_gaps": sorted(listed) != list(range(1, len(listed) + 1)),
    }


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    refs_path = None
    if "--refs" in args:
        i = args.index("--refs")
        refs_path = args[i + 1]
        del args[i:i + 2]
    text = open(args[0], encoding="utf-8").read()
    refs_text = open(refs_path, encoding="utf-8").read() if refs_path else None
    body, refs = split_doc(text, refs_text)
    # IEEE writes a range of sources as [1]–[3]: read it as [1-3].
    body = re.sub(r"\[(\d+)\]\s*[-–—]\s*\[(\d+)\]", r"[\1-\2]", body)
    entries = entries_from(refs)
    if not entries:
        print(json.dumps({"error": "no reference list found: add a 'References' heading or pass --refs"}))
        sys.exit(1)
    numeric = re.search(r"\[\d+(?:\s*[-–,]\s*\d+)*\]", body) and sum(
        bool(re.match(r"\[?\d+[\].)]", e)) for e in entries) >= max(1, len(entries) // 2)
    result = run_numeric(body, entries) if numeric else run_author_year(body, entries)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
