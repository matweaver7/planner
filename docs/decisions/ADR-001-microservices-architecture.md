# ADR-001: Five-Service Microservices Architecture

## Status
Accepted

## Date
2026-11-03

## Context

We need a backend for a multi-user SaaS planner. Core requirements:
- User authentication with token-based sessions and explicit logout
- User account management (register, update, delete) independent of auth
- Structured planner data (daily, weekly, monthly pages) per user
- A single public endpoint the browser talks to — internal services must not be reachable from the internet
- Phase 1 is desktop web only; an iPhone app is planned for phase 2

The team is a single developer. Operational overhead must be low enough for one person to run.

## Decision

Split the backend into five self-contained services:

| Service | Responsibility |
|---|---|
| `auth` (port 8001) | Issue and validate JWTs, maintain token blocklist |
| `accounts` (port 8002) | Register users, manage profile fields |
| `planner-data` (port 8003) | Store and retrieve daily/weekly/monthly planner pages |
| `proxy` (port 8000) | Single public surface: authenticate requests, route to internal services |
| `frontend` (port 5173 dev) | React SPA served from nginx |

Internal services (`auth`, `accounts`, `planner-data`) are never exposed publicly. The proxy is the only entry point.

## Alternatives Considered

### Monolith
- Pros: Simpler to run locally, no network hops between services, one test suite
- Cons: Auth logic entangled with planner logic; harder to replace the storage layer later; forces a single database type for all data (relational and document)
- Rejected: Different data access patterns for auth (relational + token blocklist) and planner pages (document store, flexible schema) benefit from being separated. The proxy also gives us a clean security boundary.

### Three services (auth+accounts merged, data, proxy)
- Pros: Fewer services to run
- Cons: Auth and accounts have genuinely different responsibilities. Keeping them separate lets auth remain stateless except for the token blocklist, and lets accounts evolve independently (e.g. adding profile fields or email verification without touching auth logic).
- Rejected: The separation maps cleanly to two different bounded contexts.

## Consequences

- **Positive:** Each service has a single, well-defined responsibility. The auth service can be swapped without touching planner data, and vice versa.
- **Positive:** The proxy provides a clear security boundary. Internal services never need to implement CORS, TLS termination, or auth middleware themselves.
- **Positive:** Different data models (PostgreSQL for auth/accounts, MongoDB for planner pages) without compromise.
- **Negative:** Local development requires running five processes. A `docker-compose.yml` mitigates this.
- **Negative:** Network hops between proxy and internal services add latency. Acceptable for a desktop planner where sub-100ms response times are not critical.
- **Trade-off:** The accounts service shares the auth PostgreSQL schema but owns no migrations. This is a deliberate coupling — they describe the same `users` table — and is acceptable as long as auth continues to own the migration lifecycle.
