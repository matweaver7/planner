# Spec: proxy

## Objective

Frontend proxy microservice. The only backend service directly reachable by the client.
Routes all API requests from the React frontend to the appropriate internal microservice
(`auth`, `accounts`, `planner-data`). Validates JWT tokens on protected routes by calling
the `auth` service's `/validate` endpoint before forwarding requests.

**Users:** The React frontend (and eventually the iPhone app in phase 2).

**Success:** The client has a single base URL. Any request to the proxy is authenticated
(if required), forwarded to the correct internal service, and the response is returned
transparently. The client never needs to know internal service URLs or ports.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **HTTP client (internal calls):** `httpx` (async)
- **Server:** Uvicorn
- **Testing:** pytest + pytest-asyncio + httpx + `respx` (mock internal service calls)
- **Containerization:** Docker

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start dev server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Build Docker image
docker build -t planner-proxy .

# Run via Docker
docker run -p 8000:8000 --env-file .env planner-proxy
```

## Project Structure

```
proxy/
├── app/
│   ├── main.py              ← FastAPI app factory, router registration, CORS config
│   ├── config.py            ← Internal service URLs, settings (pydantic-settings)
│   ├── middleware/
│   │   └── auth_middleware.py ← Validates JWT on protected routes via auth service
│   ├── routers/
│   │   ├── auth_routes.py   ← Forwards /api/auth/* → auth service
│   │   ├── account_routes.py← Forwards /api/accounts/* → accounts service
│   │   └── planner_routes.py← Forwards /api/planner/* → planner-data service (protected)
│   └── services/
│       └── proxy_service.py ← Generic async HTTP forwarding logic
├── tests/
│   ├── conftest.py          ← Mock internal service fixtures (respx)
│   ├── test_auth_routes.py
│   ├── test_account_routes.py
│   └── test_planner_routes.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Routing Table

| Client path                      | Forwards to                              | Auth required |
|----------------------------------|------------------------------------------|---------------|
| `POST /api/auth/login`           | `auth:8001/login`                        | No            |
| `POST /api/auth/logout`          | `auth:8001/logout`                       | Yes           |
| `POST /api/auth/validate`        | `auth:8001/validate`                     | No            |
| `POST /api/accounts/register`    | `accounts:8002/register`                 | No            |
| `GET  /api/accounts/users/{id}`  | `accounts:8002/users/{id}`               | Yes           |
| `PUT  /api/accounts/users/{id}`  | `accounts:8002/users/{id}`               | Yes           |
| `DELETE /api/accounts/users/{id}`| `accounts:8002/users/{id}`               | Yes           |
| `GET  /api/planner/daily/{date}` | `planner-data:8003/daily/{date}`         | Yes           |
| `PUT  /api/planner/daily/{date}` | `planner-data:8003/daily/{date}`         | Yes           |
| `GET  /api/planner/weekly/{y}/{w}`| `planner-data:8003/weekly/{y}/{w}`      | Yes           |
| `PUT  /api/planner/weekly/{y}/{w}`| `planner-data:8003/weekly/{y}/{w}`      | Yes           |
| `GET  /api/planner/monthly/{y}/{m}`| `planner-data:8003/monthly/{y}/{m}`   | Yes           |
| `PUT  /api/planner/monthly/{y}/{m}`| `planner-data:8003/monthly/{y}/{m}`   | Yes           |

## Auth Middleware Behavior

For every route marked "Auth required":

1. Extract the `Authorization: Bearer <token>` header. If missing → 401.
2. Call `POST auth:8001/validate` with `{ "token": "<token>" }`.
3. If `valid: false` → 401, do not forward.
4. If `valid: true` → attach `X-User-ID: <user_id>` header and forward the original request
   to the internal service.

The internal service never receives the raw JWT — only the resolved `X-User-ID`.

## Code Style

```python
# app/routers/planner_routes.py
from fastapi import APIRouter, Depends, Request, Response
from app.middleware.auth_middleware import require_auth
from app.services.proxy_service import forward

router = APIRouter(prefix="/api/planner", tags=["planner"])


@router.get("/daily/{date}")
async def get_daily(
    date: str,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        target_url=f"{settings.PLANNER_DATA_URL}/daily/{date}",
        extra_headers={"X-User-ID": user_id},
    )
```

```python
# app/services/proxy_service.py
import httpx
from fastapi import Request, Response

async def forward(
    request: Request,
    target_url: str,
    extra_headers: dict[str, str] | None = None,
) -> Response:
    headers = dict(request.headers)
    headers.pop("host", None)
    if extra_headers:
        headers.update(extra_headers)
    async with httpx.AsyncClient() as client:
        upstream = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
        )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(upstream.headers),
    )
```

- The proxy does minimal transformation — it forwards, it doesn't rewrite payloads
- Auth middleware is a FastAPI `Depends()`, not a global middleware, so it can be
  selectively applied per route
- Never log request bodies (may contain passwords on `/login` and `/register`)

## Testing Strategy

- **Framework:** pytest + pytest-asyncio
- **HTTP client:** `httpx.AsyncClient` with `ASGITransport`
- **Internal services:** mocked with `respx` (no live internal services in tests)
- **Coverage target:** 90% on `app/`
- **Test levels:**
  - Unit: auth middleware tested in isolation with mocked auth service responses
  - Integration: full route tests with all internal services mocked via respx

## Environment Variables

```bash
# .env.example
AUTH_SERVICE_URL=http://auth:8001
ACCOUNTS_SERVICE_URL=http://accounts:8002
PLANNER_DATA_SERVICE_URL=http://planner-data:8003

# CORS: comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:5173
```

## CORS Configuration

The proxy is the only backend the browser talks to, so CORS is configured only here.
In development: allow `http://localhost:5173` (Vite dev server).
In production: allow only the deployed frontend domain.

## Boundaries

- **Always:**
  - Validate tokens with the auth service before forwarding protected requests
  - Strip internal headers (e.g. `host`) before forwarding
  - Inject `X-User-ID` on all forwarded requests to protected services
  - Configure CORS to allow only known frontend origins

- **Ask first:**
  - Adding a new internal service to the routing table
  - Adding request body transformation (currently proxy passes through as-is)
  - Changing the auth header format (`Bearer` token is the assumed standard)

- **Never:**
  - Expose internal service URLs or ports to the client
  - Log request bodies — login and register requests contain credentials
  - Forward a request to a protected route without a valid `X-User-ID`
  - Commit `.env` files

## Success Criteria

- [ ] `POST /api/auth/login` forwards to auth service and returns its response
- [ ] `POST /api/accounts/register` forwards to accounts service without requiring a token
- [ ] `GET /api/planner/daily/{date}` with a valid Bearer token is forwarded with `X-User-ID` header
- [ ] `GET /api/planner/daily/{date}` with no token returns 401
- [ ] `GET /api/planner/daily/{date}` with an invalid/expired token returns 401
- [ ] `POST /api/auth/logout` with a valid token is forwarded and the token is invalidated
- [ ] CORS headers are present on responses for the configured frontend origin
- [ ] `pytest --cov=app` reports ≥ 90% coverage

## Open Questions

- None — requirements are fully resolved.
