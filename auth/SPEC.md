# Spec: auth

## Objective

Authentication microservice for the Planner SaaS platform. Handles user login, JWT token
issuance, token validation, and logout. This is the only service that knows user passwords.
It owns the `users` table schema — other services (e.g. `accounts`) write to that table but
defer to this service for schema decisions.

**Users:** Internal service consumers (proxy, accounts). End-users interact indirectly via
the proxy.

**Success:** A client can log in with a valid username/password and receive a JWT. That JWT
can be validated by any internal service calling this service's `/validate` endpoint. An
invalid or expired token is rejected with a 401.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL 16
- **Data access:** sqlc (via `sqlc-gen-python`) + asyncpg — write pure `.sql` queries, sqlc generates type-safe async Python methods; no ORM overhead
- **Migrations:** Alembic (owned here; `accounts` defers to these)
- **Auth tokens:** JWT (HS256), signed with a secret key, 24-hour expiry
- **Password hashing:** `bcrypt` (direct Python package — replaces passlib, which is unmaintained and breaks on Python 3.13)
- **Server:** Uvicorn
- **Testing:** pytest + pytest-asyncio + httpx (AsyncClient)
- **Containerization:** Docker

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate type-safe DB code from SQL queries (re-run after editing any .sql file)
sqlc generate

# Run database migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --port 8001

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Build Docker image
docker build -t planner-auth .

# Run via Docker
docker run -p 8001:8001 --env-file .env planner-auth
```

## Project Structure

```
auth/
├── sql/
│   ├── schema.sql               ← Table definitions (source of truth for sqlc type generation)
│   └── queries/
│       ├── users.sql            ← Named queries: get_user_by_username, get_user_by_id
│       └── token_blocklist.sql  ← Named queries: add_to_blocklist, is_token_blocked
├── db/                          ← sqlc-generated output — do not edit by hand
│   ├── models.py                ← Generated dataclasses matching table columns
│   └── queries/
│       ├── users.py             ← Generated async functions for users.sql
│       └── token_blocklist.py   ← Generated async functions for token_blocklist.sql
├── app/
│   ├── main.py                  ← FastAPI app factory, router registration
│   ├── config.py                ← Settings from environment variables (pydantic-settings)
│   ├── database.py              ← asyncpg connection pool setup + dependency
│   ├── schemas/
│   │   ├── auth.py              ← Pydantic request/response models for auth endpoints
│   │   └── token.py             ← Token payload and response schemas
│   ├── routers/
│   │   └── auth.py              ← /login, /validate, /logout endpoints
│   └── services/
│       ├── auth_service.py      ← Business logic: verify password, issue token, validate token
│       └── token_service.py     ← JWT encode/decode utilities
├── migrations/                  ← Alembic migration files (owned here)
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py              ← Test DB setup, asyncpg pool fixture
│   ├── test_login.py
│   ├── test_validate.py
│   └── test_logout.py
├── sqlc.yaml                    ← sqlc configuration (engine, output path, plugin)
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Database Schema

`sql/schema.sql` — owned by this service. sqlc reads this to generate typed Python models.
Alembic migration files are generated from this schema.

```sql
-- sql/schema.sql
-- Owned by auth, written to by accounts
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(64) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE token_blocklist (
    token_jti  VARCHAR(36) PRIMARY KEY,  -- JWT "jti" claim (unique ID per token)
    blocked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Example query file (`sql/queries/users.sql`):

```sql
-- name: GetUserByUsername :one
SELECT id, username, email, password_hash, created_at, updated_at
FROM users
WHERE username = $1;
```

sqlc generates `db/queries/users.py` with a fully typed async function:

```python
# db/queries/users.py  (generated — do not edit)
async def get_user_by_username(conn: asyncpg.Connection, *, username: str) -> User | None:
    ...
```

## API Endpoints

```
POST /login
  Body:    { "username": str, "password": str }
  Returns: { "token": str, "expires_at": ISO8601 }
  Errors:  401 if credentials invalid

POST /validate
  Body:    { "token": str }
  Returns: { "valid": bool, "user_id": UUID | null }
  Errors:  never 4xx — always returns a response body

POST /logout
  Body:    { "token": str }
  Returns: { "success": true }
  Note:    Adds token to a blocklist in PostgreSQL; validate checks blocklist
```

## Code Style

```python
# app/services/auth_service.py
import bcrypt
import asyncpg
from db.queries.users import get_user_by_username  # sqlc-generated


async def verify_credentials(conn: asyncpg.Connection, username: str, password: str):
    user = await get_user_by_username(conn, username=username)
    if user is None:
        return None
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None
    return user


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
```

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(),
) -> LoginResponse:
    result = await auth_service.login(body.username, body.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return result
```

- Snake_case for all variables, functions, and file names
- PascalCase for classes and Pydantic models
- Type hints on every function signature — no bare `Any`
- One router per file; business logic lives in `services/`, not routers
- No business logic in `main.py` — it only wires things together
- All database calls go through sqlc-generated functions — no raw SQL strings in application code
- Never edit files under `db/` — they are regenerated by `sqlc generate`

## Testing Strategy

- **Framework:** pytest + pytest-asyncio
- **HTTP client:** `httpx.AsyncClient` with `ASGITransport` (no live network calls in unit tests)
- **Database:** A separate test PostgreSQL database; the asyncpg pool is created once per test session and rolled back per test using a transaction savepoint
- **Coverage target:** 90% line coverage on `app/`
- **Test levels:**
  - Unit: `services/` functions tested with a real asyncpg connection to the test DB (sqlc-generated functions are thin wrappers — no value in mocking them)
  - Integration: Router endpoints tested via `AsyncClient` + real test DB
- Tests live in `tests/` and mirror the `app/` structure
- The `db/` (generated) directory is excluded from coverage reporting

## Environment Variables

```bash
# .env.example
# asyncpg DSN format (no +asyncpg driver prefix — asyncpg uses its own DSN)
DATABASE_URL=postgresql://user:password@localhost:5432/planner_auth
JWT_SECRET=change_me_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
```

## Boundaries

- **Always:**
  - Hash passwords with `bcrypt` before storing — never store plaintext
  - Return 401 (not 403 or 404) for invalid credentials — do not reveal whether username exists
  - Validate all incoming request bodies via Pydantic before touching the database
  - Run `sqlc generate` after editing any `.sql` file before running the app or tests
  - Run `alembic upgrade head` before starting the server in Docker

- **Ask first:**
  - Changing `sql/schema.sql` — it affects `accounts` and requires a coordinated migration
  - Adding a new auth method (OAuth, magic links, etc.)
  - Changing the JWT algorithm or token structure
  - Adding new dependencies to `requirements.txt`

- **Never:**
  - Store passwords in plaintext or reversibly encrypted
  - Return the user's password hash in any response
  - Skip token blocklist check in `/validate`
  - Edit files under `db/` — they are generated by sqlc
  - Write raw SQL strings in `app/` code — add a named query to `sql/queries/` and regenerate
  - Commit `.env` files or secrets

## Success Criteria

- [ ] `POST /login` with valid credentials returns a JWT and expiry timestamp
- [ ] `POST /login` with invalid credentials returns 401 with no password hints
- [ ] `POST /validate` with a valid, unexpired, non-logged-out token returns `{ valid: true, user_id: <uuid> }`
- [ ] `POST /validate` with an expired token returns `{ valid: false, user_id: null }`
- [ ] `POST /validate` with a token that has been logged out returns `{ valid: false, user_id: null }`
- [ ] `POST /logout` invalidates the token so subsequent `/validate` calls return false
- [ ] All endpoints return JSON; no HTML error pages
- [ ] `pytest --cov=app` reports ≥ 90% coverage

## Open Questions

- None — requirements are fully resolved.
