# Planner

Planner is a SaaS digital planner that brings the feel of a spiral notebook to your browser. It gives you dedicated daily, weekly, and monthly planning pages — each auto-saved as you type. No friction, no lost notes. Try it at [https://replace-me.matweaver.com](https://replace-me.matweaver.com). Phase 1 targets desktop browsers.

## Architecture

Five self-contained services in a monorepo:

```
planner/
├── auth/           Python/FastAPI · PostgreSQL · JWT authentication
├── accounts/       Python/FastAPI · PostgreSQL · user registration and profile
├── planner-data/   Python/FastAPI · MongoDB · daily/weekly/monthly page storage
├── proxy/          Python/FastAPI · public-facing gateway; routes + auth middleware
└── frontend/       React 18 · TypeScript · Vite · CSS Modules
```

The **proxy** is the only service exposed to the internet. Internal services communicate only with the proxy, never directly with the browser. See [ADR-001](docs/decisions/ADR-001-microservices-architecture.md) and [ADR-004](docs/decisions/ADR-004-proxy-auth-middleware.md).

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 20+
- PostgreSQL (for auth and accounts)
- MongoDB (for planner-data)

### Local development

```bash
# 1. Start databases (PostgreSQL + MongoDB via Docker)
docker compose up -d
# Wait for both to be healthy: docker compose ps

# 2. Allow direnv (sets connection vars from .envrc — one-time per directory)
direnv allow
direnv allow auth accounts planner-data proxy frontend

# 3. Auth service (also runs DB migrations)
cd auth && python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # add JWT_SECRET; DATABASE_URL comes from direnv
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --port $AUTH_SERVICE_PORT --reload

# 4. Accounts service
cd accounts && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port $ACCOUNTS_SERVICE_PORT --reload

# 5. Planner data service
cd planner-data && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port $PLANNER_SERVICE_PORT --reload

# 6. Proxy
cd proxy && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port $PROXY_PORT --reload

# 7. Frontend
cd frontend && npm install && npm run dev
# → http://localhost:$FRONTEND_PORT
```

**Environment variables** are layered: `docker-compose.yml` defines the database credentials; `.envrc` at the project root exports them (plus service URLs) for all services. Each service's `.envrc` inherits the parent and then loads its own `.env` on top, so a local `.env` file always wins. Only `auth/.env` needs to be created manually — it holds `JWT_SECRET`, which is intentionally not in `.envrc`.

## Commands

### Per service (Python)

| Command | Description |
|---|---|
| `pip install -r requirements.txt` | Install dependencies |
| `uvicorn app.main:app --reload` | Start dev server |
| `pytest tests/` | Run tests |
| `pytest --cov=app --cov-report=term-missing` | Tests with coverage |
| `alembic upgrade head` | Apply DB migrations (auth only) |
| `sqlc generate` | Regenerate `db/` from `sql/queries/` (auth + accounts) |

### Frontend

| Command | Description |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Start Vite dev server at localhost:5173 |
| `npm run typecheck` | TypeScript check (zero errors required) |
| `npm test` | Run Vitest tests |
| `npm run coverage` | Tests with coverage report (≥80% required) |
| `npm run build` | Production build to `dist/` |

## Coverage targets

| Service | Target |
|---|---|
| auth | ≥90% |
| accounts | ≥90% |
| planner-data | ≥90% |
| proxy | ≥90% |
| frontend | ≥80% |

## Key design decisions

| Decision | ADR |
|---|---|
| Why five services instead of a monolith | [ADR-001](docs/decisions/ADR-001-microservices-architecture.md) |
| Why PostgreSQL + sqlc + asyncpg for auth/accounts | [ADR-002](docs/decisions/ADR-002-postgresql-sqlc-asyncpg.md) |
| Why MongoDB + Beanie for planner data | [ADR-003](docs/decisions/ADR-003-mongodb-beanie-planner-data.md) |
| Why proxy is the only public service | [ADR-004](docs/decisions/ADR-004-proxy-auth-middleware.md) |
| Why JWT is stored in memory (not localStorage) | [ADR-005](docs/decisions/ADR-005-in-memory-jwt-storage.md) |
| Why GET planner pages never return 404 | [ADR-006](docs/decisions/ADR-006-planner-get-never-404.md) |
| Why auto-save uses blur + 500ms debounce | [ADR-007](docs/decisions/ADR-007-autosave-blur-debounce.md) |

## Known gotchas

- **respx version:** Use `respx==0.23.1`. Earlier versions are incompatible with `httpcore 1.0.x` (method bytes vs. string mismatch breaks all route matching in tests).
- **beanie version:** Use `beanie==1.24.0` + `mongomock-motor==0.0.34`. beanie 1.27.0 breaks mongomock-motor with an `authorizedCollections` keyword argument error.
- **sqlc plugin:** `sqlc-gen-python v1.1.0` WASM plugin must exist in the service root. It is not installed via pip.
- **coverage greenlet:** `auth` and `accounts` require `concurrency = greenlet` in `.coveragerc`. `planner-data` and `proxy` do not.
- **pip SSL:** If SSL certificate verification fails, add `--trusted-host pypi.org --trusted-host files.pythonhosted.org` to pip installs.

## Scope

**Phase 1 (current):** Desktop web app.  
**Out of scope:** iPhone app, payments/billing, shared planners, offline mode.
