# planner-data

Planner data microservice. Stores and retrieves the three page types — daily, weekly, and monthly — per user. Uses MongoDB for flexible document storage.

Runs on **port 3003**. Internal-only — not exposed to the internet. The proxy forwards requests here after injecting the `X-User-ID` header; this service never touches JWTs.

## Setup

Requires MongoDB 7.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# MONGODB_URL and MONGODB_DB_NAME come from direnv — no .env needed unless overriding
.venv/bin/uvicorn app.main:app --reload --port $PLANNER_SERVICE_PORT
```

## Commands

| Command | Description |
|---|---|
| `pip install -r requirements.txt` | Install dependencies |
| `uvicorn app.main:app --reload --port 3003` | Start dev server |
| `pytest tests/` | Run tests (uses in-memory MongoDB — no live Mongo needed) |
| `pytest --cov=app --cov-report=term-missing` | Tests with coverage (target: ≥90%) |
| `docker build -t planner-data .` | Build Docker image |

## Endpoints

All endpoints require the `X-User-ID` header (injected by the proxy — never sent directly by clients).

```
GET  /daily/{date}              →  DailyPage document
PUT  /daily/{date}              →  updated DailyPage

GET  /weekly/{year}/{week}      →  WeeklyPage document
PUT  /weekly/{year}/{week}      →  updated WeeklyPage

GET  /monthly/{year}/{month}    →  MonthlyPage document
PUT  /monthly/{year}/{month}    →  updated MonthlyPage

GET  /health                    →  { status: "ok" }
```

GET endpoints always return 200. If no document exists yet for a date, an empty-but-valid document is returned (not 404). The empty document is only persisted on the first PUT.

## Examples

The `X-User-ID` header is normally injected by the proxy. When calling this service directly (dev/debug only), pass it manually.

```bash
# Health check
curl -s http://localhost:3003/health
# → {"status":"ok"}

USER_ID=550e8400-e29b-41d4-a716-446655440000

# --- Daily ---

# Get daily page (empty doc returned if not yet created — never 404)
curl -s http://localhost:3003/daily/2026-11-03 \
  -H "X-User-ID: $USER_ID"
# → {"user_id":"...","date":"2026-11-03","time_blocks":[...],"notes":"","study_topic":"", ...}

# Update daily page (partial update — only supplied fields are changed)
curl -s -X PUT http://localhost:3003/daily/2026-11-03 \
  -H 'Content-Type: application/json' \
  -H "X-User-ID: $USER_ID" \
  -d '{"notes":"Meeting at 9am. Prep deck.","study_topic":"TypeScript generics"}'
# → full updated DailyPage document

# Update a single time block
curl -s -X PUT http://localhost:3003/daily/2026-11-03 \
  -H 'Content-Type: application/json' \
  -H "X-User-ID: $USER_ID" \
  -d '{"time_blocks":[{"time":"09:00","text":"Standup"},{"time":"09:30","text":"Deep work"}]}'

# --- Weekly ---

# Get weekly page
curl -s http://localhost:3003/weekly/2026/45 \
  -H "X-User-ID: $USER_ID"
# → {"user_id":"...","year":2026,"week":45,"week_at_a_glance":[...],"study_topic":"", ...}

# Update weekly goals
curl -s -X PUT http://localhost:3003/weekly/2026/45 \
  -H 'Content-Type: application/json' \
  -H "X-User-ID: $USER_ID" \
  -d '{"study_topic":"Distributed systems","exercise_goal":"Run 5k three times"}'
# → full updated WeeklyPage document

# --- Monthly ---

# Get monthly page
curl -s http://localhost:3003/monthly/2026/11 \
  -H "X-User-ID: $USER_ID"
# → {"user_id":"...","year":2026,"month":11,"study_topic":"", ...}

# Update monthly goals
curl -s -X PUT http://localhost:3003/monthly/2026/11 \
  -H 'Content-Type: application/json' \
  -H "X-User-ID: $USER_ID" \
  -d '{"career_goal":"Ship the planner app","other_goals":"Read two books"}'
# → full updated MonthlyPage document
```

## Project layout

```
planner-data/
├── app/
│   ├── main.py
│   ├── database.py                 ← Motor client + Beanie initialization
│   ├── models/                     ← Beanie document models (daily, weekly, monthly)
│   ├── schemas/                    ← Pydantic request/response schemas
│   ├── routers/                    ← Endpoint handlers per page type
│   └── services/                   ← get_or_create / upsert logic per page type
└── tests/
    ├── conftest.py                 ← mongomock-motor fixture
    ├── test_daily.py
    ├── test_weekly.py
    └── test_monthly.py
```

## Collections

| Collection | Key | Description |
|---|---|---|
| `daily_pages` | `(user_id, date)` | Daily schedule + notes |
| `weekly_pages` | `(user_id, year, week)` | Weekly goals + week at a glance |
| `monthly_pages` | `(user_id, year, month)` | Monthly goals |

All collections have unique compound indexes on their key fields.

## Environment variables

```bash
MONGODB_URL=mongodb://localhost:27017  # set by direnv
MONGODB_DB_NAME=planner_data           # set by direnv
```

## Key notes

- **`user_id` always from header.** Every query is scoped by `X-User-ID`. A document from one user can never be returned to another.
- **GET never 404.** The service returns a zeroed-out document for any unseen date. Frontend components always receive a valid document and never need to distinguish "empty" from "not found".
- **Upsert semantics.** PUT is always an upsert keyed on `(user_id, <date fields>)`. Sending a subset of fields is safe — only the supplied fields are updated.
- **Testing.** Tests use `mongomock-motor` for an in-memory MongoDB. No live database is needed in CI. Dependency versions are pinned: `beanie==1.24.0` + `mongomock-motor==0.0.34` — beanie 1.27.0 breaks mongomock-motor.
