# Schema checklist

Run through this against the finished schema and fix any miss.

- Every table has a primary key; no meaningful (email, username) primary keys.
- Every relationship has a foreign key with an explicit ON DELETE choice; every FK column is indexed.
- Access-pattern columns (WHERE, ORDER BY) are indexed; composite index order matches the queries; no pointless extra indexes.
- Money is DECIMAL or integer minor units; timestamps in UTC; no dates as strings; no lists in a single column.
- Required fields are NOT NULL; UNIQUE and CHECK constraints cover the business rules.
- created_at and updated_at on mutable tables.
- Any denormalisation names the query it serves.
- Many-to-many uses a junction table; polymorphic links use a stated strategy.
- Migration has UP and a matching DOWN; new NOT NULL columns are added nullable first.
- Security: passwords hashed (never stored), PII identified for encryption or restricted access, least-privilege database roles.
- The ER diagram matches the DDL.
