---
name: SQL Code Review
description: >
  Reviews pasted SQL (queries, migrations, schemas, or app code that builds SQL) and returns findings ranked by severity, each with a rewritten fix.
  Use it for "review this SQL", "is this query safe?", "check for injection and missing indexes", "is this migration safe to run on a big table?".
---

# SQL Code Review

A good review finds the real problems in the SQL the user gave, ranks them, and shows the corrected SQL for each. It covers injection and data exposure, performance and indexes, correctness, and maintainability. It works for PostgreSQL, MySQL, SQL Server, Oracle and SQLite. Deliver the whole review in the reply.

## Step 1: Read the input

1. Take the SQL from the message, pasted text or attached files. If the user gave no SQL at all, ask once with `clarify` for the SQL to review. Otherwise do not ask anything.
2. Work out the dialect from the syntax (`TOP`, `NVARCHAR`, `SERIAL`, `AUTO_INCREMENT`, `NUMBER`, `JSONB`). If the user named one, use that. If it is unclear, say "Assumed dialect: <name>" and write fixes that run on it.
3. Note what is missing: no schema, no indexes listed, no row counts, no execution plan. Never invent table sizes, timings or index lists. Where a finding depends on something not given, say "depends on <the missing fact>" and say how to check it (for example the dialect's `EXPLAIN`).
4. If the input is application code (Python, JS, Java and so on) that builds SQL, review the SQL it produces and quote the offending line.

## Step 2: Find issues

Read `references/checks.md` once. It holds the checklist by category, the known bad-to-good rewrites, and dialect notes. Go through every statement in the input against it. Only report what is actually in the SQL: do not pad the review with generic advice.

Severity levels:

- **Critical**: injectable SQL, `UPDATE` or `DELETE` with no `WHERE`, a migration that locks or rewrites a large table, wrong results (a join that multiplies rows, `NOT IN` against a nullable column), exposure of secrets or personal data.
- **High**: a query that cannot use an index (function on a column, leading wildcard, implicit type conversion), a foreign key or join column with no index, an N+1 pattern, an unbounded result set on a large table.
- **Medium**: `SELECT *`, `DISTINCT` hiding a bad join, implicit comma joins, missing constraints, poor data types, missing transaction around multi-step changes.
- **Low**: formatting, naming, reserved words, missing comments.

Rules for findings:

- Each finding cites the exact statement, line or object it is about.
- Call something a security risk only if the input shows it (string concatenation, formatted strings, dynamic SQL, broad `GRANT`). A static query with literal values is not an injection risk.
- A performance finding says why it is slow in general terms. Give a measured impact only if the user supplied measurements.
- Leave out a checklist item that the input does not touch.

## Step 3: Write the fixes

For every Critical, High and Medium finding, write the corrected SQL in a fenced `sql` block, in the user's dialect. Keep the meaning of the query the same unless the finding is about wrong results, and then say what changed in behaviour. Include `CREATE INDEX` statements for index findings, naming the columns and the reason (the join or filter it serves). For parameterised queries, use the placeholder style of the user's language or driver (`?`, `$1`, `:name`, `@name`).

For a migration or schema change, give the safe order of steps: for example add the column as nullable, backfill in batches, add the constraint without validating then validate, create the index with the online option the dialect offers. State the lock behaviour as dialect and version dependent, and tell the user to check their version's documentation.

If the input is long, report the 10 most important findings in full and list the rest in one line each.

## Step 4: Write the reply

Use this shape, in this order:

```
## SQL review

**Dialect:** <name, stated or assumed>
**Reviewed:** <what was reviewed, for example "2 queries and 1 migration">
**Verdict:** <one sentence: safe to ship / fix before shipping / do not run>

### Findings
| # | Severity | Category | Where | Issue |
|---|----------|----------|-------|-------|
| 1 | <level> | <Security / Performance / Correctness / Maintainability> | <statement or line> | <one line> |

### Details
#### 1. <title> (<severity>)
**Why it matters:** <one or two sentences>
**Before:** ```sql ... ```
**After:** ```sql ... ```
**Note:** <what changed in behaviour, what to verify, what depends on missing facts>

(repeat for each finding)

### Assessment
- Security: <Low / Medium / High risk> - <one-line reason>
- Performance: <Low / Medium / High risk> - <one-line reason>
- Maintainability: <Good / Fair / Poor> - <one-line reason>

### Do these first
1. <most important action>
2. <next>
3. <next>

### Assumptions and what I could not check
- <dialect, schema, indexes, data volumes, anything not given>
```

If the SQL is clean, say so, show the Verdict, list any Low items, and still fill in Assessment and Assumptions. Do not invent problems.

## Hard rules

- Everything in the reply is about the SQL the user gave. Do not invent table names, columns, indexes, row counts, timings, percentages or "expected speed-up" figures. Use the user's own names in fixes; if a name is missing, write `<column>` and say so.
- Do not run or connect to a database. Never claim a query was tested or timed.
- A fix must be valid in the dialect and must not change results without saying so.
- If a fix changes data (a backfill, a `DELETE`), tell the user to run it on a copy or inside a transaction first.
- This review is guidance from reading the SQL, not a substitute for testing against real data or for a security audit.
