# Patterns and databases

Use these as starting points. The user's stated scale, team and constraints always override a default.

## Architecture patterns

| Pattern | Fits | Typical team | Cost |
|---|---|---|---|
| Monolith | Simple domain, new product, fast iteration | one small team | Hard to scale parts independently; one deploy unit |
| Modular monolith | Growing complexity, clear module boundaries | several small teams | Boundaries need discipline; still one deploy |
| Microservices | Complex domain, several teams, different scaling needs per part | many teams | Network failures, eventual consistency, heavy operations (tracing, deploy pipelines, on-call) |
| Serverless | Spiky or low load, event-driven work | any | Cold starts, vendor lock-in, harder local debugging |
| Event-driven (queue or log) | Async work, decoupling, fan-out, audit trail | any | Eventual consistency, ordering and duplicate handling, harder debugging |
| CQRS | Reads and writes with very different shapes or load | experienced teams | Two models to keep in sync; use only when one model clearly strains |

Guidance:
- New product or small team: start with a monolith or modular monolith; extract a service only when a measured reason exists (independent scaling, a separate team, a different failure domain).
- Microservices before the team and operations can support them is the most common over-engineering. Name the operational cost in the ADR.
- Queue choice: a simple managed queue for task offloading and retries; a log-based broker (Kafka-style) when you need replay, multiple independent consumers or ordering at high throughput. Always specify the handling of duplicates (idempotent consumers) and a dead-letter path.
- Caching: add it for a measured hot read path, with an invalidation rule stated; a cache is never the source of truth.
- Real-time features: say whether polling, server-sent events or websockets, and why.

## Database selection

| Type | Examples | Good for | Avoid when |
|---|---|---|---|
| Relational | PostgreSQL, MySQL | Transactions, joins, integrity, most products by default | Truly schemaless data, or write volume beyond one primary with no sharding plan |
| Document | MongoDB, Firestore | Evolving schemas, nested documents, content | Many cross-document transactions or heavy joins |
| Key-value | Redis, DynamoDB | Sessions, caching, counters, rate limits, very high throughput by key | Ad hoc queries, relational data |
| Time-series | TimescaleDB, InfluxDB | Metrics, IoT, events with timestamps, analytics | Frequent updates to old rows, non-time access patterns |
| Graph | Neo4j, Neptune | Deep relationship traversal | Simple relations that joins handle |
| Search | Elasticsearch, Meilisearch, Postgres full-text | Full-text and faceted search, log search | Primary system of record |
| Columnar / warehouse | BigQuery, ClickHouse | Analytical scans over large history | Low-latency transactional reads |

Decision questions, in order:
1. Does the data need multi-row transactions or strong integrity? If yes, relational.
2. Is access mostly by one key at very high throughput? Key-value.
3. Is it append-only events queried by time or aggregated? Time-series or a warehouse; keep the transactional store separate.
4. Is search the main read path? Add a search index fed from the system of record, not as the record itself.
5. Only then consider document or graph, and only if the access pattern demands it.

A single relational database with a cache and a search index covers most products for a long time; say so when it is true, and list what would trigger a change (measured read load, write limits, query latency).
