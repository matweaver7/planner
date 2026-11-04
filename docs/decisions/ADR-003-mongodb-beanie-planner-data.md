# ADR-003: MongoDB + Beanie ODM for Planner Data

## Status
Accepted

## Date
2026-11-03

## Context

The `planner-data` service stores three types of documents: daily pages, weekly pages, and monthly pages. Each document belongs to a specific user and time period.

Key characteristics of this data:
- Schema is mostly stable but the set of fields on a page may grow (e.g. adding new sections to the daily page)
- Reads are overwhelmingly single-document lookups: one user, one date
- Writes are upserts: create or update the whole document for `(user_id, date)`
- No joins required — each page is self-contained
- The service never touches the auth schema

## Decision

Use **MongoDB** with the **Beanie** ODM (v1.24.0) over **Motor** (v3.7.0).

- One collection per page type: `daily_pages`, `weekly_pages`, `monthly_pages`
- Unique compound indexes: `(user_id, date)`, `(user_id, year, week)`, `(user_id, year, month)`
- GET returns a newly constructed empty document if none exists for that key — never 404
- PUT is always an upsert keyed on the compound index

## Alternatives Considered

### PostgreSQL (same as auth/accounts)
- Pros: One database technology to operate, team already knows it
- Cons: Planner page fields are likely to grow over time; each new field requires a migration. The `time_blocks` array on the daily page is variable-length and awkward in a relational model (junction table or JSON column, both with trade-offs).
- Rejected: Document model fits planner pages better than relational. The variable-length time block list and the distinct-but-similar structure of weekly vs. monthly pages benefit from flexible schemas.

### PostgreSQL with JSONB columns
- Pros: Single database, structured query support via JSONB operators
- Cons: Loses Beanie's ODM validation; queries against nested JSONB are verbose; indexing JSONB is less ergonomic than MongoDB's native compound indexes
- Rejected: JSONB is a workaround for document-shaped data in a relational store. MongoDB is the right tool.

### DynamoDB or another managed NoSQL
- Pros: Fully managed, scales automatically
- Cons: Local development requires mocking (DynamoDB Local or LocalStack), which is heavier than `mongomock-motor`; much higher operational complexity for a single-developer project; vendor lock-in
- Rejected: MongoDB with Docker is simpler to run locally and self-host

## Consequences

- **Positive:** Adding a new section to a planner page (e.g. a "Gratitude" field to the daily page) requires updating the Beanie model and the frontend — no migration file.
- **Positive:** `mongomock-motor` provides a lightweight in-memory MongoDB for tests; no Docker required in CI.
- **Negative:** Running two database technologies (PostgreSQL + MongoDB) increases local setup complexity. `docker-compose.yml` mitigates this.
- **Gotcha:** `beanie==1.27.0` is incompatible with `mongomock-motor` due to a `list_collection_names(authorizedCollections=...)` call that mongomock-motor doesn't support. Pin to `beanie==1.24.0` + `mongomock-motor==0.0.34`.
- **Gotcha:** Coverage does NOT need `concurrency = greenlet` for planner-data — Motor uses asyncio natively, unlike SQLAlchemy's greenlet-based async.
