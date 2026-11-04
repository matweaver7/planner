# ADR-004: Proxy as Sole Public Surface with Per-Route Auth Middleware

## Status
Accepted

## Date
2026-11-03

## Context

Internal services (`auth`, `accounts`, `planner-data`) must not be reachable directly from the internet. The frontend needs a single base URL to talk to.

Auth validation is required on some routes but not others (e.g. `POST /api/auth/login` is public; `GET /api/planner/daily/:date` is protected). The proxy needs to apply authentication without adding code to every route.

## Decision

The `proxy` service is the **only** publicly exposed backend service. It:

1. Accepts all browser traffic on port 8000
2. Applies a FastAPI `Depends(require_auth)` dependency to protected routes — not globally
3. `require_auth` calls `auth:8001/validate` with the Bearer token, extracts `user_id`, and raises HTTP 401 on failure
4. On success, injects `X-User-ID: <user_id>` into the forwarded request
5. Internal services read `X-User-ID` directly — they never touch JWTs

CORS is configured on the proxy only (`CORS_ORIGINS` env var), not on internal services.

## Alternatives Considered

### Global auth middleware (applied to all routes)
- Pros: Simpler — one place to configure auth
- Cons: Login and validate routes must be public; a global middleware would need an exception list that grows as public routes are added
- Rejected: FastAPI's `Depends()` pattern is more explicit. Each protected route declares its own dependency; no hidden exception lists.

### Auth sidecar / service mesh (e.g. Envoy + ext_authz)
- Pros: Language-agnostic, handles auth at the infrastructure level
- Cons: Massive operational complexity for a single-developer project; requires running Envoy, configuring ext_authz, and debugging at the infrastructure layer
- Rejected: FastAPI proxy is simpler and sufficient for phase 1

### Each internal service validates the token itself
- Pros: True service autonomy — no single auth bottleneck
- Cons: Every internal service must know the JWT secret (or call auth), adding coupling. The proxy pattern means only one service holds the secret.
- Rejected: Centralising token validation in the proxy keeps the secret in one place

### Forwarding the raw JWT to internal services
- Pros: Internal services could independently validate tokens
- Cons: Requires every internal service to import JWT validation logic and know the secret
- Rejected: `X-User-ID` is a simpler, already-validated claim. Internal services are fully trusted once the proxy injects this header; they never need to re-validate.

## Consequences

- **Positive:** Internal services are simple — they read a plain header, no crypto.
- **Positive:** Auth logic is in exactly one place (the proxy middleware). Changing the token format only touches `auth` and `proxy`.
- **Positive:** CORS is configured once, on the proxy.
- **Negative:** The proxy is a single point of failure. If the proxy is down, all services are unreachable. Acceptable for phase 1; horizontal scaling of the proxy is straightforward later.
- **Security note:** `X-User-ID` is injected by the proxy and must be stripped from incoming client requests before forwarding. The `forward()` function strips headers the client sends but does not add `X-User-ID` unless `require_auth` has successfully validated the token.
