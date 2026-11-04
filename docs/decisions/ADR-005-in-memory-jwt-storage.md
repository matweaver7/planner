# ADR-005: JWT Stored in React Context (In-Memory Only)

## Status
Accepted

## Date
2026-11-03

## Context

The frontend needs to attach a Bearer token to every API request. The token must be available for the lifetime of the user's session, but the security implications of different storage mechanisms vary significantly.

Phase 1 is a desktop web app used by a single registered user. Phase 2 (iPhone app) is out of scope.

## Decision

Store the JWT in a **React context value** — a plain in-memory JavaScript variable, never written to `localStorage`, `sessionStorage`, `IndexedDB`, or a cookie.

```typescript
// src/hooks/useAuth.ts
interface AuthState {
  token: string | null;
  userId: string | null;
}
```

The token is attached to every Axios request via a request interceptor. On page refresh, the token is lost and the user must log in again.

## Alternatives Considered

### localStorage
- Pros: Survives page refresh and browser close, no re-login required
- Cons: Accessible to any JavaScript running on the page — vulnerable to XSS. Any third-party script (analytics, ads, compromised CDN) can exfiltrate the token.
- Rejected: The security trade-off is unacceptable. XSS-to-token-theft is a well-documented attack vector.

### HttpOnly cookie
- Pros: Not accessible to JavaScript, survives page refresh, automatic attachment to requests
- Cons: Requires CSRF protection (the cookie is sent with every request, including cross-site ones); adds server-side session management complexity; complicates the iPhone app (phase 2) because mobile apps don't share cookies with WebViews in the same way browsers do
- Rejected: Adds CSRF complexity without a clear phase-1 benefit. Reconsidered for phase 2.

### sessionStorage
- Pros: Cleared when the tab is closed, survives page refresh within a tab
- Cons: Still accessible to JavaScript, still vulnerable to XSS; survives page refresh so attacker has more time
- Rejected: Same XSS vulnerability as localStorage with fewer benefits

### Short-lived refresh token in HttpOnly cookie + access token in memory
- Pros: Best of both worlds — XSS can't steal the refresh token; re-login is automatic
- Cons: Significantly more complex: requires a dedicated token refresh endpoint, silent refresh logic, and coordination between auth service and proxy
- Rejected: Over-engineered for phase 1. Revisit for phase 2 or if session persistence becomes a user pain point.

## Consequences

- **Positive:** The token is never persisted anywhere that JavaScript from other origins can reach. XSS attacks cannot exfiltrate the token.
- **Positive:** No server-side session state required — the auth service is stateless except for the token blocklist.
- **Negative:** Page refresh ends the session. Users must log in again after every refresh. Acceptable for a planner app where the user is actively filling in pages.
- **Negative:** The token is lost if the tab is closed. If a user has the planner open in one tab and closes it, they must log in again. Acceptable trade-off for phase 1.
- **Implementation note:** The Axios 401 interceptor calls `setToken(null)` when a 401 is received. This clears the in-memory token so subsequent requests stop sending the expired/invalid header.
