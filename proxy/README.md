# proxy

Frontend proxy. The only backend service exposed to the internet. Routes all API requests from the React frontend to the correct internal microservice, validates JWT tokens on protected routes, and configures CORS.

Runs on **port 3000**. All browser traffic goes through here; internal services (`auth`, `accounts`, `planner-data`) are never contacted directly by the client.

## Setup

Requires all three internal services to be running for end-to-end use. For unit tests, internal services are mocked with `respx` — no live services needed.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# All service URLs and CORS_ORIGINS come from direnv — no .env needed unless overriding
.venv/bin/uvicorn app.main:app --reload --port $PROXY_PORT
```

## Commands

| Command | Description |
|---|---|
| `pip install -r requirements.txt` | Install dependencies |
| `uvicorn app.main:app --reload --port 3000` | Start dev server |
| `pytest tests/` | Run tests |
| `pytest --cov=app --cov-report=term-missing` | Tests with coverage (target: ≥90%) |
| `docker build -t planner-proxy .` | Build Docker image |

## Routing table

| Client path | Forwards to | Auth required |
|---|---|---|
| `POST /api/auth/login` | `localhost:3001/login` | No |
| `POST /api/auth/logout` | `localhost:3001/logout` | Yes |
| `POST /api/auth/validate` | `localhost:3001/validate` | No |
| `POST /api/accounts/register` | `localhost:3002/register` | No |
| `GET /api/accounts/users/{id}` | `localhost:3002/users/{id}` | Yes |
| `PUT /api/accounts/users/{id}` | `localhost:3002/users/{id}` | Yes |
| `DELETE /api/accounts/users/{id}` | `localhost:3002/users/{id}` | Yes |
| `GET /api/planner/daily/{date}` | `localhost:3003/daily/{date}` | Yes |
| `PUT /api/planner/daily/{date}` | `localhost:3003/daily/{date}` | Yes |
| `GET /api/planner/weekly/{y}/{w}` | `localhost:3003/weekly/{y}/{w}` | Yes |
| `PUT /api/planner/weekly/{y}/{w}` | `localhost:3003/weekly/{y}/{w}` | Yes |
| `GET /api/planner/monthly/{y}/{m}` | `localhost:3003/monthly/{y}/{m}` | Yes |
| `PUT /api/planner/monthly/{y}/{m}` | `localhost:3003/monthly/{y}/{m}` | Yes |

## Examples

These are the requests the browser (or any HTTP client) makes. The proxy handles auth and routing transparently.

```bash
# Register a new user (public — no token needed)
curl -s -X POST http://localhost:3000/api/accounts/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@example.com","password":"hunter2"}'
# → {"user_id":"...","username":"alice","email":"alice@example.com","created_at":"..."}

# Login — capture the token for subsequent requests
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"hunter2"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# No token → 401
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/planner/daily/2026-11-03
# → 401

# --- Daily ---

# Get daily page
curl -s http://localhost:3000/api/planner/daily/2026-11-03 \
  -H "Authorization: Bearer $TOKEN"
# → {"date":"2026-11-03","time_blocks":[...],"notes":"", ...}

# Update daily page
curl -s -X PUT http://localhost:3000/api/planner/daily/2026-11-03 \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"notes":"Meeting at 9am","study_topic":"TypeScript generics"}'
# → full updated DailyPage document

# --- Weekly ---

# Get weekly page
curl -s http://localhost:3000/api/planner/weekly/2026/45 \
  -H "Authorization: Bearer $TOKEN"

# Update weekly page
curl -s -X PUT http://localhost:3000/api/planner/weekly/2026/45 \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"study_topic":"Distributed systems","exercise_goal":"Run 5k three times"}'

# --- Monthly ---

# Get monthly page
curl -s http://localhost:3000/api/planner/monthly/2026/11 \
  -H "Authorization: Bearer $TOKEN"

# Update monthly page
curl -s -X PUT http://localhost:3000/api/planner/monthly/2026/11 \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"career_goal":"Ship the planner app"}'

# --- Account management ---

USER_ID=550e8400-e29b-41d4-a716-446655440000

# Get own profile
curl -s http://localhost:3000/api/accounts/users/$USER_ID \
  -H "Authorization: Bearer $TOKEN"

# Update email
curl -s -X PUT http://localhost:3000/api/accounts/users/$USER_ID \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"email":"alice2@example.com"}'

# Delete account
curl -s -X DELETE http://localhost:3000/api/accounts/users/$USER_ID \
  -H "Authorization: Bearer $TOKEN"

# --- Logout ---

curl -s -X POST http://localhost:3000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
# → {"success":true}

# Token is now blocked — further requests return 401
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/planner/daily/2026-11-03 \
  -H "Authorization: Bearer $TOKEN"
# → 401
```

## Auth middleware

For protected routes, the `require_auth` FastAPI dependency:

1. Extracts `Authorization: Bearer <token>` — returns 401 if missing.
2. Calls `POST localhost:3001/validate` with the token.
3. Returns 401 if `valid: false`; does not forward the request.
4. If valid, injects `X-User-ID: <user_id>` and forwards to the internal service.

Internal services receive only `X-User-ID` — never the raw JWT.

## Project layout

```
proxy/
├── app/
│   ├── main.py                     ← App factory, router registration, CORS middleware
│   ├── config.py                   ← Internal service URLs (pydantic-settings)
│   ├── middleware/auth_middleware.py ← require_auth FastAPI dependency
│   ├── routers/
│   │   ├── auth_routes.py          ← /api/auth/* forwarding
│   │   ├── account_routes.py       ← /api/accounts/* forwarding
│   │   └── planner_routes.py       ← /api/planner/* forwarding (protected)
│   └── services/proxy_service.py   ← Generic async HTTP forwarding
└── tests/
    ├── conftest.py
    ├── test_auth_middleware.py
    ├── test_auth_routes.py
    ├── test_account_routes.py
    └── test_planner_routes.py
```

## Environment variables

```bash
AUTH_SERVICE_URL=http://localhost:3001      # set by direnv
ACCOUNTS_SERVICE_URL=http://localhost:3002  # set by direnv
PLANNER_DATA_SERVICE_URL=http://localhost:3003  # set by direnv
CORS_ORIGINS=http://localhost:5173          # set by direnv
```

## Key notes

- **respx version.** Tests use `respx==0.23.1`. Earlier versions are incompatible with `httpcore 1.0.x` — method bytes vs. string mismatch breaks all route matching. Do not downgrade.
- **No greenlet coverage.** Unlike `auth` and `accounts`, this service does not use asyncpg. The `.coveragerc` does not include `concurrency = greenlet`.
- **Never log request bodies.** Login and register requests contain credentials in the body.
- **host header stripped.** The `forward()` function removes the `host` header before forwarding so internal services receive the correct host for their own URL, not the proxy's.
