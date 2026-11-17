# Design guide

## Normal forms
- 1NF: atomic values, no repeating groups (`product_ids = '1,2,3'` is a violation; use an items table).
- 2NF: no column depends on part of a composite key (customer name inside order_items).
- 3NF: no column depends on another non-key column (country derived from postal code).
- Denormalise only for a named read pattern: pre-calculated totals, cached counts, materialised views. Document the reason and how it is kept in sync.

## Data types
- Text: CHAR(n) for fixed codes (country_code CHAR(2)); VARCHAR(n) sized to the field; TEXT for long content. Do not use VARCHAR(255) everywhere.
- Numbers: INT for ids and counts, BIGINT for large tables, DECIMAL(p,s) for money, FLOAT only for approximate scientific data.
- Time: TIMESTAMP (PostgreSQL: TIMESTAMPTZ), stored in UTC. DATE for calendar dates.
- Boolean: BOOLEAN in PostgreSQL, TINYINT(1) in MySQL.
- Keys: auto-increment or identity for simple cases; UUID for distributed systems or ids exposed publicly. Do not use email or username as a primary key. Junction tables use a composite primary key.

## Foreign keys
- ON DELETE CASCADE: owned children (order lines). RESTRICT: references that protect history (product on a past order). SET NULL: optional links.
- ON UPDATE CASCADE is rarely needed with surrogate keys.
- Always index the FK column; the database does not do it for you (except MySQL InnoDB).

## Other constraints
UNIQUE (single or composite), CHECK (`price >= 0`, `discount BETWEEN 0 AND 100`, status in a fixed list), NOT NULL on required fields, sensible DEFAULTs.

## Indexing
- Always: foreign keys, WHERE columns, ORDER BY columns, unique constraints.
- Composite order: equality columns first, then range or sort columns; an index on (a, b) serves queries on a, or a and b, but not b alone.
- Types: B-tree for equality and ranges (default); hash for exact match only; full-text for text search; partial for a subset (`WHERE is_active`).
- Pitfalls: over-indexing slows writes; wrong column order leaves the index unused; missing FK indexes make joins and cascading deletes slow.
- Check plans with `EXPLAIN`: full table scan, no key used and high row counts are the warning signs.

## Relationship patterns
- One-to-many: FK on the many side.
- Many-to-many: junction table with composite PK and both FKs, plus extra columns (enrolled_at) as needed.
- Self-reference: `manager_id REFERENCES employees(id)`; for deep trees consider a closure table or path column.
- Polymorphic: prefer separate nullable FKs with a CHECK that exactly one is set (strong integrity); type + id columns are flexible but cannot be enforced.
- Soft delete: `deleted_at` column plus partial unique indexes on live rows.
- Multi-tenant: tenant_id on every tenant-owned table, in unique constraints and as the leading index column.
- Order lines: copy the unit price onto the line so later price changes do not rewrite history.

## NoSQL (document stores)
| Factor | Embed | Reference |
|---|---|---|
| Access | Read together | Read separately |
| Relationship | 1 to few | 1 to many, or unbounded |
| Size | Small and bounded | Could approach the 16 MB document limit |
| Updates | Rare | Frequent |
Rules: design for the queries, not for the entities; never embed an unbounded array (a feed's followers, comments); duplicate small, rarely-changing fields (author display name) and say how they are refreshed; use the fan-out-on-write or fan-out-on-read trade-off for feeds. Indexes: single field, compound (equality, sort, range order), text, 2dsphere for geo, unique where needed, TTL for expiring data.

## Migrations
- Always reversible (UP and DOWN), backward compatible, schema changes separate from data backfills, tested on a copy of production-like data.
- Add a column: add nullable, deploy code that writes it, backfill, then add NOT NULL.
- Rename a column: add new, copy, switch reads, switch writes, drop old.
- Wrap each script in a transaction where the database supports transactional DDL (PostgreSQL does, MySQL does not).
- Large tables: create indexes concurrently (PostgreSQL `CREATE INDEX CONCURRENTLY`), backfill in batches.
- Template:
```sql
-- Migration: <timestamp>_<description>
-- UP
BEGIN;
<statements>
COMMIT;
-- DOWN
BEGIN;
<exact reverse, in reverse order>
COMMIT;
```

## Performance notes
N+1 queries: fetch with a join or an IN list. Avoid SELECT *. Paginate with keyset (cursor) pagination for large tables. Consider caching, read replicas and partitioning only when a measured problem exists.
