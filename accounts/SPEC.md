# Spec: accounts

## Objective

Account management microservice for the Planner SaaS platform. Handles user registration
and basic account operations (view, update, delete). Writes to the `users` table owned by
the `auth` service — shares the same PostgreSQL database but defers all schema and migration
decisions to `auth`.

**Users:** Internal service consumers only (proxy). End-users interact indirectly via the proxy.

**Success:** A new user can register with a username, email, and password. The account is
stored in PostgreSQL and the user can subsequently log in via the `auth` service.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL 16 (shared instance with `auth`, same `users` table)
- **Data access:** sqlc (via `sqlc-gen-python`) + asyncpg — write pure `.sql` queries, sqlc generates type-safe async Python methods; no ORM overhead
- **Migrations:** None — owned by `auth`. This service only writes `.sql` query files against the schema `auth` dictates.
- **Password hashing:** `bcrypt` (direct Python package — replaces passlib, which is unmaintained and breaks on Python 3.13; hashes are compatible with `auth`'s bcrypt calls)
- **Server:** Uvicorn
- **Testing:** pytest + pytest-asyncio + httpx (AsyncClient)
- **Containerization:** Docker

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate type-safe DB code from SQL queries (re-run after editing any .sql file)
sqlc generate

# Start dev server (auth must be running and DB migrated first)
uvicorn app.main:app --reload --port 8002

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Build Docker image
docker build -t planner-accounts .

# Run via Docker
docker run -p 8002:8002 --env-file .env planner-accounts
```

## Project Structure

```
accounts/
├── sql/
│   ├── schema.sql               ← Copy of auth's schema (read-only reference for sqlc; no migrations run here)
│   └── queries/
│       └── users.sql            ← Named queries: create_user, get_user_by_id, update_user_email,
│                                     update_user_password, delete_user
├── db/                          ← sqlc-generated output — do not edit by hand
│   ├── models.py                ← Generated dataclasses matching table columns
│   └── queries/
│       └── users.py             ← Generated async functions for users.sql
├── app/
│   ├── main.py                  ← FastAPI app factory, router registration
│   ├── config.py                ← Settings from environment variables (pydantic-settings)
│   ├── database.py              ← asyncpg connection pool setup + dependency
│   ├── schemas/
│   │   └── account.py           ← Pydantic request/response models
│   ├── routers/
│   │   └── accounts.py          ← /register, /users/{id} endpoints
│   └── services/
│       └── account_service.py   ← Business logic: create user, update user, delete user
├── tests/
│   ├── conftest.py              ← Test DB setup, asyncpg pool fixture
│   ├── test_register.py
│   └── test_account_management.py
├── sqlc.yaml                    ← sqlc configuration (engine, output path, plugin)
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Database Schema

This service does not own or run migrations. `sql/schema.sql` is a read-only copy of
`auth`'s schema, kept here solely so sqlc can generate correct Python types. It must be
kept in sync with whatever `auth` migrates to.

```sql
-- sql/schema.sql  (mirrors auth — do not migrate from here)
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(64) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Example query file (`sql/queries/users.sql`):

```sql
-- name: CreateUser :one
INSERT INTO users (username, email, password_hash)
VALUES ($1, $2, $3)
RETURNING id, username, email, created_at, updated_at;

-- name: GetUserById :one
SELECT id, username, email, created_at, updated_at
FROM users
WHERE id = $1;

-- name: UpdateUserEmail :one
UPDATE users SET email = $2, updated_at = now()
WHERE id = $1
RETURNING id, username, email, updated_at;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;
```

sqlc generates `db/queries/users.py` with fully typed async functions:

```python
# db/queries/users.py  (generated — do not edit)
async def create_user(conn: asyncpg.Connection, *, username: str, email: str, password_hash: str) -> User:
    ...

async def get_user_by_id(conn: asyncpg.Connection, *, id: UUID) -> User | None:
    ...
```

## API Endpoints

```
POST /register
  Body:    { "username": str, "email": str, "password": str }
  Returns: { "user_id": UUID, "username": str, "email": str, "created_at": ISO8601 }
  Errors:  409 if username or email already exists
           422 if validation fails (password too short, invalid email, etc.)

GET /users/{user_id}
  Returns: { "user_id": UUID, "username": str, "email": str, "created_at": ISO8601 }
  Errors:  404 if user not found

PUT /users/{user_id}
  Body:    { "email"?: str, "password"?: str }  (username is not changeable)
  Returns: { "user_id": UUID, "username": str, "email": str, "updated_at": ISO8601 }
  Errors:  404 if user not found, 409 if email already taken

DELETE /users/{user_id}
  Returns: { "success": true }
  Errors:  404 if user not found
```

## Code Style

```python
# app/services/account_service.py
import bcrypt
import asyncpg
from db.queries.users import create_user, get_user_by_id  # sqlc-generated
from app.schemas.account import RegisterRequest, AccountResponse


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def register_user(conn: asyncpg.Connection, body: RegisterRequest) -> AccountResponse | None:
    password_hash = hash_password(body.password)
    try:
        user = await create_user(
            conn,
            username=body.username,
            email=body.email,
            password_hash=password_hash,
        )
    except asyncpg.UniqueViolationError:
        return None  # caller raises 409
    return AccountResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )
```

```python
# app/routers/accounts.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.account import RegisterRequest, AccountResponse
from app.services.account_service import AccountService

router = APIRouter(prefix="/", tags=["accounts"])


@router.post("/register", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    account_service: AccountService = Depends(),
) -> AccountResponse:
    result = await account_service.register_user(body)
    if result is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")
    return result
```

- Snake_case for variables/functions/files; PascalCase for classes/schemas
- Type hints on every function signature — no bare `Any`
- Business logic lives in `services/`, not routers
- Password is hashed in `account_service.py` before writing to DB — never in the router
- All database calls go through sqlc-generated functions — no raw SQL strings in `app/` code
- `asyncpg.UniqueViolationError` is the correct exception to catch for 409 conflicts (not ORM-level exceptions)
- Never edit files under `db/` — regenerated by `sqlc generate`

## Testing Strategy

- **Framework:** pytest + pytest-asyncio
- **HTTP client:** `httpx.AsyncClient` with `ASGITransport`
- **Database:** Shared test PostgreSQL database (pre-migrated by running `auth`'s Alembic migrations against it); asyncpg pool created once per session, rolled back per test via transaction savepoint
- **Coverage target:** 90% on `app/`
- **Test levels:**
  - Unit: `account_service` functions tested with a real asyncpg connection to the test DB
  - Integration: Router endpoints tested via `AsyncClient` + real test DB
- The `db/` (generated) directory is excluded from coverage reporting

## Environment Variables

```bash
# .env.example
# asyncpg DSN format (no +asyncpg driver prefix)
DATABASE_URL=postgresql://user:password@localhost:5432/planner_auth
# Note: same database as auth service — no separate DB for accounts
```

## Boundaries

- **Always:**
  - Hash passwords with `bcrypt` (same library and default work factor as `auth`) before writing to DB
  - Validate email format and minimum password length (≥ 8 chars) in Pydantic schema
  - Catch `asyncpg.UniqueViolationError` and return 409 — never let constraint errors bubble as 500
  - Run `sqlc generate` after editing any `.sql` file before running the app or tests
  - Never expose `password_hash` in any response

- **Ask first:**
  - Any query that would require a schema change — coordinate with `auth` first
  - Adding fields to the `users` table
  - Adding new account management endpoints

- **Never:**
  - Run Alembic migrations from this service — migrations are owned by `auth`
  - Store or log plaintext passwords
  - Return the `password_hash` field in any API response
  - Edit files under `db/` — they are generated by sqlc
  - Write raw SQL strings in `app/` code — add a named query to `sql/queries/` and regenerate
  - Commit `.env` files or secrets

## Success Criteria

- [ ] `POST /register` with valid unique credentials creates a user and returns 201 with user data (no `password_hash` field)
- [ ] `POST /register` with a duplicate username returns 409
- [ ] `POST /register` with a duplicate email returns 409
- [ ] `POST /register` with a password shorter than 8 characters returns 422
- [ ] `GET /users/{id}` returns user data for an existing user (no `password_hash` field)
- [ ] `PUT /users/{id}` updates email or password and returns updated user data
- [ ] `DELETE /users/{id}` removes the user and returns `{ success: true }`
- [ ] A user registered via this service can subsequently log in via the `auth` service
- [ ] `pytest --cov=app` reports ≥ 90% coverage

## Open Questions

- None — requirements are fully resolved.
