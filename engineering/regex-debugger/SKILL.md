---
name: Regex Builder and Explainer
description: >
  Explains, fixes or writes a regular expression, with a plain-English breakdown and match results from running it for real.
  Use it for "explain this regex", "why doesn't my regex match", "write a regex for ...", "convert this regex to JavaScript".
---

# Regex Builder and Explainer

A good result is a pattern that has been run, not guessed: the reply explains it piece by piece, shows a table of real match results from the sandbox, names every flaw found, and gives a corrected pattern in the flavor the user works in.

## Step 1: Work out the job and the flavor

Decide which of these the user wants (it can be several):
- **Explain** a pattern they pasted.
- **Debug** a pattern that over-matches, under-matches or errors.
- **Write** a new pattern from a description.
- **Convert** a pattern between flavors.

Flavor: use the one the user names (Python, JavaScript, PCRE/PHP, Java, .NET, Perl, Go, grep). If they name none, assume Python `re` and JavaScript, give both, and say so in one line. Never ask a question first: state assumptions and deliver in this one reply. If the user gave no test strings, make your own in Step 3.

## Step 2: Read the pattern

Split it into parts: anchors, groups (capturing, non-capturing, named, lookaround), alternations, character classes, quantifiers and flags. Check for:
- unescaped specials, such as a bare `.` where a literal dot is meant;
- greedy quantifiers (`.*`, `.+`) that run past the intended end, and the lazy or negated-class fix (`.*?`, `[^"]*`);
- anchors missing or misplaced (`^`/`$` versus `\A`/`\Z`, and multiline flags);
- alternation that swallows too much without a group;
- character ranges that look right but are wrong (`[A-z]`, `[0-9]{1,3}` allowing 999);
- nested quantifiers like `(a+)+` or `(.*)*` that can backtrack catastrophically;
- features the target flavor lacks (named groups `(?P<n>)` versus `(?<n>)`, lookbehind, possessive quantifiers, atomic groups, `\d` matching non-ASCII digits in Python and .NET, no `re.VERBOSE` in JS).

## Step 3: Build test strings

Make three groups: strings that should match, strings that should not, and edge cases (empty string, leading or trailing whitespace, multi-line input, Unicode, a boundary value, the longest and shortest valid input). Include every string the user gave. For a "write a regex" job, build these first and the pattern second. Do not use real people's data; invent obviously fake values.

## Step 4: Run it, do not reason about it

Use `execute_code` (Python) for every match result. Never state a match result from memory. Run the original pattern and the fixed one against the same strings, and print a table with the string, whether it matched, the matched text and the capture groups.

```python
import re
pattern = r"<the pattern>"
flags = 0  # e.g. re.I | re.M
rx = re.compile(pattern, flags)
tests = ["<string 1>", "<string 2>"]
for s in tests:
    m = rx.search(s)  # use fullmatch if the user wants whole-string validation
    print(repr(s), bool(m), m.group(0) if m else None, m.groups() if m else None)
```

If the target is JavaScript (or the user's flavor differs from Python in a way that matters), run the same check with Node through `terminal`: write a small `.js` file under `/tmp/.scratch/regex-debugger/` and run `node file.js`, using `str.match(re)` and `re.exec`. Use `re.test` only with no `g` flag, or reset `lastIndex`, as the `g` flag makes it stateful. For other flavors (Java, .NET, PCRE, Perl, Go) Python or Node results are approximations: say that, and list the syntax that differs.

If a pattern raises an error, show the error text and fix that first. Time a suspected catastrophic-backtracking pattern on a long near-miss string (for example 30 repeated characters then a mismatch) and report the timing you measured, nothing invented.

## Step 5: Fix or write the pattern

Give the corrected pattern, then re-run it on the full test set and confirm every expected result in the table. If a requirement cannot be met by a regex alone (nesting, calendar validity such as day 30 of February, real email or URL validation, HTML parsing), say so plainly, give the best practical pattern, and name the follow-up check to do in code (a date parser, a URL parser, an HTML parser). Show that caveat in the table. Add at least one slipping-through string (for dates: `2024-02-30`) to the test list and run it. Put it in the Results table as a row with Expected "invalid (regex can't tell)" and Matched? "yes". Any string you name in Issues or Limits as slipping through or matching must be a row in the table, from the run.

Prefer the simplest readable pattern. Use non-capturing groups where the capture is not needed, and anchor validation patterns.

## Step 6: Reply in this shape

Put the whole answer in the reply. Skip a section that does not apply (for example, no "Issues found" for a pure explain job). For a write job where the user gave no pattern, "Issues found" lists only the limits of your own pattern, with no critique of a naive pattern the user never wrote. In "Results (run in ...)", name only the engines you actually ran in this turn. Write "Node" only if you ran `node` through `terminal`.

```
# Regex: `<pattern>` (<flavor>, flags: <flags or none>)

## What it does
<One or two sentences.>

## Breakdown
| Part | Meaning |
|---|---|
| `<token>` | <what it matches> |

## Results (run in <Python re / Node>)
| Test string | Expected | Matched? | Match | Groups |
|---|---|---|---|---|

## Issues found
1. <problem, why it happens, and the string that shows it>

## Fixed / new pattern
```<language>
<pattern in code form for the flavor>
```
<What changed and why. Re-run results for the fixed pattern in the same table format.>

## Other flavors
<Only the flavors the user asked for or that differ: the pattern as written for each, plus syntax notes (named groups, flags, escaping in string literals, \d and Unicode).>

## Limits and notes
<What a regex cannot guarantee here, performance notes, and assumptions you made (flavor, flags, test strings).>
```

## Rules

- Every match result in the reply comes from code you ran in this turn. If you could not run something, say so.
- Do the counting (match counts, lengths, timings) in code, not in your head.
- Claim JavaScript/Node results only if you ran `node` via `terminal` this turn. Otherwise say the JS behavior is unverified.
- Every string the reply says matches or slips through (in Issues, Limits or notes) appears as a row in a Results table.
- Show patterns in code form for the language: in Python use a raw string `r"..."`; in JavaScript use a literal `/.../flags` or `new RegExp("...")` with doubled backslashes; say which.
- Do not invent sample data that looks real (real people, companies, accounts). Use obviously fake values.
- Do not claim a pattern is "safe" or "complete" for email, URL, phone or date validation; state what it accepts and what it lets through.
