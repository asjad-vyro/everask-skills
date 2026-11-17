# SQL review checks

Go through the input against each section. Report only what is present.

## Security

- **Injection.** String concatenation, f-strings, `format`, template literals or `+` that put user input into SQL. Dynamic SQL inside procedures (`EXEC('...' + @x)`, `EXECUTE IMMEDIATE`, `PREPARE` from a built string). Fix: bind parameters.
  - Bad: `query = "SELECT * FROM users WHERE id = " + user_input`
  - Good: `cursor.execute("SELECT id, name FROM users WHERE id = %s", (user_id,))`
  - SQL Server: `EXEC sp_executesql N'SELECT id FROM users WHERE id = @id', N'@id INT', @id = @user_id;`
  - Identifiers (table or column names) cannot be bound: use an allow-list in code, or `QUOTENAME` (SQL Server) / `format('%I', ...)` (PostgreSQL).
  - Parameters protect values, not `ORDER BY` direction or `LIMIT` built from text: allow-list those too.
- **Privileges.** `GRANT ALL`, `GRANT ... TO PUBLIC`, application using an owner or admin account, `WITH GRANT OPTION`, `SECURITY DEFINER` / `EXECUTE AS OWNER` routines that take user input. Fix: least privilege, roles, a dedicated app role.
- **Data exposure.** `SELECT *` on tables with passwords, tokens or personal data; hashes or secrets returned to clients; credentials written in scripts; sensitive columns without a view or mask. Plain-text password columns.
- **Auditing.** Sensitive deletes or updates with no audit trail, when the context suggests one is needed.

## Correctness

- `UPDATE` / `DELETE` with no `WHERE`, or a `WHERE` that matches more than intended; no transaction around multi-step changes.
- Missing join condition (Cartesian product); implicit comma joins that hide it.
- Join that multiplies rows, then `SUM` / `COUNT` over the result (double counting).
- `NOT IN (subquery)` when the subquery column can be NULL: use `NOT EXISTS`.
- `= NULL` instead of `IS NULL`; `LEFT JOIN` whose right-side filter in `WHERE` turns it into an inner join (move the filter to `ON`).
- Non-deterministic `LIMIT` / `TOP` without `ORDER BY`.
- `GROUP BY` that selects non-grouped columns (error in strict modes, arbitrary values in MySQL without `ONLY_FULL_GROUP_BY`).
- Integer division, `BETWEEN` on timestamps that drops the last day, time zone assumptions.

## Performance

- **Non-sargable filters** (the column is wrapped, so an index on it cannot be used):
  - Bad: `WHERE YEAR(order_date) = 2024`
  - Good: `WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`
  - Also: `LOWER(col) = ...` (use a functional index or a case-insensitive collation), `col + 0`, arithmetic on the column.
- **Leading wildcard** `LIKE '%term'` or `'%term%'`: cannot use a normal B-tree index. Options: full-text search, a trigram index (PostgreSQL `pg_trgm`), or accept the scan if the table is small.
- **Implicit type conversion**: comparing a number column to a string or a `VARCHAR` column to an `NVARCHAR` parameter (SQL Server), which can stop index use.
- **Missing indexes**: foreign key columns used in joins, columns in frequent `WHERE`, `ORDER BY` and `GROUP BY`. Suggest composite indexes with the equality columns first, then the range or sort column. Say which query each index serves. Whether an index is really missing depends on the user's schema: if it was not given, say so.
- **Redundant indexes** (one is a prefix of another) and over-indexing on write-heavy tables, if the schema is shown.
- **`SELECT *`**: reads unneeded columns, blocks covering indexes, breaks when columns change. List the columns.
- **`SELECT DISTINCT`** used to remove duplicates produced by a bad join. Fix the join, or use `EXISTS` when only checking for a match. Do not swap `DISTINCT` for `GROUP BY` and call it a fix: it is the same work.
- **Correlated subquery** run per row (for example a `COUNT(*)` subquery in the select list): rewrite as a join with `GROUP BY`, or a window function.
  - Bad: `SELECT o1.user_id, (SELECT COUNT(*) FROM orders o2 WHERE o2.user_id = o1.user_id) FROM orders o1 GROUP BY o1.user_id`
  - Good: `SELECT user_id, COUNT(*) AS order_count FROM orders GROUP BY user_id`
- **N+1** in application code (a query inside a loop): fetch with one join or `WHERE id IN (...)`, selecting the needed columns.
- **Unbounded result sets** and deep `OFFSET` pagination: suggest keyset pagination (`WHERE id > :last_id ORDER BY id LIMIT n`).
- **`OR` across different columns, `UNION` where `UNION ALL` is enough, `COUNT(*)` to test existence** (use `EXISTS`).
- **Row-by-row loops or cursors** where a set-based statement would do.

## Migrations and schema changes (large tables)

- Adding a column with a default, changing a column type, adding `NOT NULL`, adding a foreign key or check, or creating an index can lock or rewrite the table. Behaviour depends on the dialect and version: say that, and name the safer pattern.
- Safer patterns: add a nullable column, backfill in batches, then add the constraint (PostgreSQL: `ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT`; `CREATE INDEX CONCURRENTLY`; MySQL 8: `ALGORITHM=INPLACE, LOCK=NONE` where supported; SQL Server: `ONLINE = ON` where the edition allows).
- Dropping or renaming a column the application still reads: split into deploy steps.
- Large `UPDATE` / `DELETE` in one transaction: batch it.
- Check for a rollback path and for running inside a transaction where the dialect allows DDL in one.

## Schema design

- Missing primary key, missing foreign keys, missing `NOT NULL` or `CHECK` where the data clearly needs them.
- Wrong types: money as float (use `DECIMAL`/`NUMERIC`), dates as strings, booleans as text, oversize `VARCHAR`, `TIMESTAMP` without time zone where zones matter.
- Repeated groups of columns (`phone1`, `phone2`), comma-separated lists in a column, over-normalisation that forces many joins, missing junction tables.
- Reserved words as identifiers; mixed naming styles (`userId`, `user_id`); vague names (`data`, `temp`).

## Maintainability

- Format: one clause per line, upper-case keywords, aligned columns, explicit `JOIN ... ON` (not comma joins), table aliases that mean something.
  - Bad: `select u.id,u.name,o.total from users u left join orders o on u.id=o.user_id where u.status='active'`
  - Good: one select item per line, `FROM`, `LEFT JOIN ... ON ...`, `WHERE` each on its own line.
- Comments on non-obvious logic; deeply nested subqueries that would read better as CTEs; error handling and transactions in procedures.

## Dialect notes (use only for the dialect in the input)

- **PostgreSQL**: `JSONB` plus a GIN index for JSON containment queries; `TIMESTAMPTZ`; `GENERATED ... AS IDENTITY` over `SERIAL`; `CREATE INDEX CONCURRENTLY`; `EXPLAIN (ANALYZE, BUFFERS)` shows the real plan (it runs the query, so careful with writes).
- **MySQL**: InnoDB; `utf8mb4`; implicit conversions when comparing strings to numbers; check `ONLY_FULL_GROUP_BY`; `EXPLAIN` / `EXPLAIN ANALYZE`.
- **SQL Server**: `NVARCHAR` vs `VARCHAR` parameter mismatch; `DATETIME2`; `sp_executesql` and `QUOTENAME`; included columns in indexes; `SET STATISTICS IO ON` and the actual execution plan.
- **Oracle**: `VARCHAR2`, `NUMBER`; sequences or identity columns; bind variables; empty string is NULL; `EXPLAIN PLAN` / `DBMS_XPLAN`.
- **SQLite**: loose typing; foreign keys are off unless `PRAGMA foreign_keys = ON`; limited `ALTER TABLE`.
