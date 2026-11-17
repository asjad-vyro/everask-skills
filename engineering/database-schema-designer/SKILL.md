---
name: Database Schema Designer
description: >
  Turns a description of your data into a complete database schema: tables or collections, keys, constraints, indexes, an ER diagram and a migration script.
  Use it for "design a schema for...", "model the data for...", "create tables for...", "NoSQL schema for...", "review my schema", "normalise this table".
---

# Database Schema Designer

A good result is a schema someone can run today: correct types, enforced relationships, indexes that match the queries, and a short note on why each choice was made. Finish in one reply from what the user gave; never open with questions.

## Step 1: Pin down the requirements

From the message (and any attached file), list:
- Entities and the relationships between them (1:1, 1:many, many:many).
- Access patterns: the 4 to 6 queries the app will run most. If the user gave none, infer them from the domain and label them "assumed".
- Scale hints (rows, traffic, read/write ratio). If none, say "not given" and design for a small to mid-size OLTP app.
- Database: use what the user named. If none, use PostgreSQL for SQL. Choose NoSQL (MongoDB-style documents) only when the user asks for it or the access pattern is clearly document-shaped; say why.

Write the assumptions as a short list in the reply. Do not invent figures, customer names or volumes the user did not give.

## Step 2: Design

For SQL, read `references/design-guide.md` (normal forms, data types, key and ON DELETE choices, indexing, relationship patterns, zero-downtime migrations). For a NoSQL request read its NoSQL section. Then:

1. Normalise to 3NF. Denormalise only for a named access pattern and say so.
2. Every table: primary key, NOT NULL on required fields, UNIQUE where the business needs it, CHECK for simple rules (price >= 0, status values), `created_at` and `updated_at`.
3. Every relationship: a foreign key with an explicit ON DELETE choice and a one-line reason (CASCADE for owned children such as line items, RESTRICT for things that must not vanish such as products on past orders, SET NULL for optional links).
4. Money is DECIMAL (or integer minor units), never FLOAT. Store timestamps in UTC. Do not store lists in one column. Snapshot prices on order lines so history survives price changes.
5. Index every foreign key, plus the columns in the access patterns' WHERE and ORDER BY. Composite index order follows the query: equality columns first, then range or sort. Say which query each non-obvious index serves.
6. Multi-tenant requests: put a tenant id on every tenant-owned table, include it in unique constraints and leading index columns.
7. NoSQL: for each relationship decide embed or reference with the reasoning (read together, bounded size, update frequency). Show example documents with placeholder values, the collections, indexes, and what is deliberately duplicated.

For a review request (user pasted a schema), list findings ranked by severity, each with the problem, why it hurts and the fixed DDL; then give the corrected schema.

## Step 3: Check the SQL actually runs

Use `execute_code` with Python's `sqlite3` (the sandbox has it). Translate the DDL to SQLite in the test only (BIGSERIAL or identity to INTEGER PRIMARY KEY, TIMESTAMPTZ to TEXT, DECIMAL stays, drop PostgreSQL-only features), run `PRAGMA foreign_keys = ON`, create all tables and indexes, insert a few made-up rows, and confirm a foreign key violation is rejected. If it fails, fix the schema and rerun. Report in one line what was tested ("created N tables, M indexes; FK violation rejected") and which parts could not be tested in SQLite (for example partial indexes or PostgreSQL-specific types). Skip this step for NoSQL.

## Step 4: Deliver

Put the whole deliverable in the reply, in this order:

1. **Assumptions**: bullets, each marked given or assumed.
2. **ER diagram**: a Mermaid `erDiagram` code block with entities, key columns and relationship cardinality.
3. **Schema**: one fenced `sql` block with all CREATE TABLE and CREATE INDEX statements (or the collections and example documents for NoSQL).
4. **Design notes**: a table with columns Table or index, Decision, Reason. Cover keys, ON DELETE choices, denormalisation and every index.
5. **Migration**: an UP script and a DOWN script that reverses it exactly. For changes to an existing table, add nullable first, backfill, then add the constraint.
6. **Next steps**: two or three scaling or risk notes (partitioning, soft delete, audit trail, PII handling), clearly marked as suggestions.

If the user wants a file, also write `schema.sql` and publish it with `publish_artifact` (`kind: "file"`), but still show the schema in the reply.

## Hard rules

- Never use FLOAT or DOUBLE for money. Never store dates as strings in the real schema.
- Every foreign key is declared and indexed.
- Every migration has a working DOWN.
- Do not invent business facts, volumes or benchmarks; write "not given" or mark an assumption.
- Before sending, run the checklist in `references/checklist.md` against your schema and fix any miss. Read that file only if the schema has more than five tables or the user asked for a review; otherwise rely on the rules above.
