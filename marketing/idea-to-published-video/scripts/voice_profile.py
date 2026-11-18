#!/usr/bin/env python3
"""Measure a creator's writing voice from their past video scripts.

Usage:
    python3 voice_profile.py script1.txt script2.md [...]
    python3 voice_profile.py --dir past_scripts/

Reads plain-text or Markdown scripts (one video per file; at least 5 for a useful
profile) and prints one JSON object on stdout:
    {"scripts": n, "words_total", "words_per_script": {"median", "min", "max"},
     "sentence_length": {"median", "share_short_under_8_words"},
     "hook": {"median_words_first_15s", "openers": [first sentence of each script],
              "opens_with_question_share"},
     "person": {"i", "you", "we"} (per 1000 words),
     "contractions_per_1000", "questions_per_1000", "exclamations_per_1000",
     "signature_phrases": [[phrase, count], ...]  (3-4 word phrases used in 2+ scripts),
     "sign_offs": [last sentence of each script],
     "warnings": [...]}

"median_words_first_15s" assumes about 2.5 spoken words per second (38 words).
Stdlib only. Read-only.
"""

import collections
import json
import os
import re
import statistics
import sys

WORDS_PER_SECOND = 2.5
STOP = set("""a an the and or but of to in on at for with is it this that be are was
i you we my your our so just like it's i'm you're don't can if as do not have""".split())
CONTRACTION = re.compile(r"\b\w+'(s|re|ve|ll|d|m|t)\b", re.I)
MARKUP = re.compile(r"^\s*(#+|[-*>]|\[.*?\]|\(.*?\)|b-?roll:.*|\d{1,2}:\d{2}.*)\s*", re.I)


DROP_LINE = re.compile(r"^\s*(#+\s|\[.*\]\s*$|\(.*\)\s*$|b-?roll\b|\d{1,2}:\d{2})", re.I)


def clean(text):
    """Spoken words only: drop headings, [notes], (notes), b-roll and timestamp lines."""
    lines = []
    for line in text.splitlines():
        if DROP_LINE.match(line):
            continue
        line = MARKUP.sub("", line).strip()
        if line:
            lines.append(line)
    return " ".join(lines)


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if re.search(r"\w", p)]


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def ngrams(ws, n):
    ws = [w.lower() for w in ws]
    for i in range(len(ws) - n + 1):
        gram = ws[i:i + n]
        if all(w in STOP for w in gram):
            continue
        yield " ".join(gram)


def main(argv):
    paths = []
    if "--dir" in argv:
        d = argv[argv.index("--dir") + 1]
        paths = [os.path.join(d, f) for f in sorted(os.listdir(d))
                 if f.lower().endswith((".txt", ".md"))]
    else:
        paths = [a for a in argv[1:] if not a.startswith("--")]
    if not paths:
        print(__doc__, file=sys.stderr)
        return 2
    texts, warnings = [], []
    for p in paths:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError as exc:
            warnings.append(f"Could not read {p}: {exc}")
            continue
        if re.search(r"<!doctype html|<html\b", raw[:2000], re.I):
            warnings.append(f"{os.path.basename(p)} is a web page, not a script; skipped")
            continue
        t = clean(raw)
        if len(words(t)) < 50:
            warnings.append(f"{os.path.basename(p)} has under 50 words; skipped")
            continue
        texts.append(t)
    if not texts:
        print(json.dumps({"error": "No usable scripts (need text files with 50+ words)",
                          "warnings": warnings}))
        return 1
    if len(texts) < 5:
        warnings.append(f"Only {len(texts)} usable scripts; 5 or more give a steadier profile")

    all_words, sent_lens, hooks, openers, closers = [], [], [], [], []
    phrase_scripts = collections.Counter()
    q_open = 0
    for t in texts:
        ws = words(t)
        all_words.extend(ws)
        ss = sentences(t)
        sent_lens.extend(len(words(s)) for s in ss)
        openers.append(ss[0][:200])
        closers.append(ss[-1][:200])
        q_open += ss[0].rstrip().endswith("?")
        hooks.append(min(len(ws), round(15 * WORDS_PER_SECOND)))
        seen = set()
        for sent in ss:
            for n in (3, 4):
                seen.update(ngrams(words(sent), n))
        phrase_scripts.update(seen)

    total = len(all_words)
    lower = [w.lower() for w in all_words]
    joined = " ".join(texts)
    per_k = lambda n: round(1000 * n / total, 1)
    sig = sorted(([p, c] for p, c in phrase_scripts.items() if c >= 2),
                 key=lambda pc: (-pc[1], -len(pc[0].split()), pc[0]))[:60]
    # keep the longest phrase when a shorter one is inside it
    kept = []
    for p, c in sig:
        if not any(p in k[0] and p != k[0] for k in kept):
            kept.append([p, c])
    per_script = [len(words(t)) for t in texts]
    out = {
        "scripts": len(texts),
        "words_total": total,
        "words_per_script": {"median": int(statistics.median(per_script)),
                             "min": min(per_script), "max": max(per_script)},
        "sentence_length": {"median": statistics.median(sent_lens),
                            "share_short_under_8_words": round(sum(1 for s in sent_lens if s < 8) / len(sent_lens), 2)},
        "hook": {"median_words_first_15s": int(statistics.median(hooks)),
                 "openers": openers,
                 "opens_with_question_share": round(q_open / len(texts), 2)},
        "person": {"i": per_k(lower.count("i") + lower.count("i'm") + lower.count("my")),
                   "you": per_k(lower.count("you") + lower.count("your") + lower.count("you're")),
                   "we": per_k(lower.count("we") + lower.count("our") + lower.count("we're"))},
        "contractions_per_1000": per_k(len(CONTRACTION.findall(joined))),
        "questions_per_1000": per_k(joined.count("?")),
        "exclamations_per_1000": per_k(joined.count("!")),
        "signature_phrases": kept[:15],
        "sign_offs": closers,
        "warnings": warnings,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
