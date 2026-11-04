# ADR-002: PostgreSQL + sqlc + asyncpg for Auth and Accounts

## Status
Accepted

## Date
2026-11-03

## Context

The `auth` and `accounts` services need a relational database. Key requirements:
- ACID transactions for token blocklist inserts and user mutations
- Async Python driver that integrates cleanly with FastAPI
- Type-safe database access without heavy ORM overhead
- A migration tool that auth can run independently

## Decision

Use **PostgreSQL** with the **sqlc** code generator (Python plugin v1.1.0) and **asyncpg** as the underlying driver via SQLAlchemy's async connection layer.

- `auth` owns the schema (`sql/schema.sql`) and Alembic migrations
- `accounts` reads the same schema but delegates all migrations to `auth`
- Both services use `sqlc generate` to produce typed async query functions in `db/`

## Alternatives Considered

### SQLAlchemy ORM (without sqlc)
- Pros: Familiar to most Python developers, active community, built-in migrations via Alembic
- Cons: ORM layer adds indirection; queries are less legible than raw SQL; lazy-loading traps are common in async contexts
- Rejected: We write SQL anyway when performance matters; sqlc keeps the SQL as the source of truth and generates the Python, rather than the other way around

### Tortoise ORM / async-first ORM
- Pros: Built for async from the ground up, simpler than SQLAlchemy async
- Cons: Smaller community, fewer features, non-standard query API
- Rejected: Marginal benefit over SQLAlchemy async, less documentation

### Databases (encode/databases)
- Pros: Thin async layer over SQLAlchemy core, explicit query strings
- Cons: Less type-safe than sqlc, no code generation, project is in maintenance mode
- Rejected: sqlc gives us the same explicit SQL with generated types, better tooling

### SQLite
- Pros: Zero configuration, embedded
- Cons: No concurrent writes from multiple processes, no managed hosting option
- Rejected: Multi-user SaaS requires a proper server-side database

## Consequences

- **Positive:** `db/` query functions are typed — no runtime surprises from mismatched column names.
- **Positive:** asyncpg is the fastest async PostgreSQL driver in Python; no connection pool overhead beyond SQLAlchemy's thin wrapper.
- **Positive:** SQL queries are visible in `sql/queries/` — easy to review and optimise.
- **Negative:** sqlc requires a code generation step (`sqlc generate`) whenever queries change. The generated `db/` files must be committed to the repository and re-generated locally after schema changes.
- **Gotcha:** `sqlc-gen-python v1.1.0` WASM plugin must be downloaded and placed in the service root. The URL is in `sqlc.yaml`. If the plugin is missing, `sqlc generate` fails silently or with a non-obvious error.
- **Gotcha:** Coverage requires `concurrency = greenlet` in `.coveragerc` for both `auth` and `accounts` because SQLAlchemy's async layer uses greenlet internally. Without it, async route handlers appear uncovered despite tests passing.
