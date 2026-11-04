# frontend

React web app for the planner. Renders daily, weekly, and monthly planner pages styled to match the physical spiral notebook. All data is fetched from and saved to the proxy; nothing is stored client-side.

Runs on **port 5173** in development. In production, built static files are served by nginx.

## Setup

Requires Node.js 20+. The proxy must be running on port 3000 for API calls to work.

```bash
npm install

# VITE_API_BASE_URL comes from direnv — no .env needed unless overriding
npm run dev
# → http://localhost:5173
```

## Commands

| Command | Description |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Start Vite dev server at localhost:5173 |
| `npm run typecheck` | TypeScript check (zero errors required) |
| `npm test` | Run Vitest tests |
| `npm run coverage` | Tests with coverage (target: ≥80%) |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview production build locally |
| `docker build -t planner-frontend .` | Build Docker image (nginx) |

## Routes

```
/login                 → LoginPage         (public)
/register              → RegisterPage      (public)
/daily/:date           → DailyView         (protected)
/weekly/:year/:week    → WeeklyView        (protected)
/monthly/:year/:month  → MonthlyView       (protected)
/                      → redirect to /daily/<today>
```

Protected routes redirect to `/login` if there is no token in memory.

## Examples

The frontend is a browser app — its API requests go to the proxy at port 3000. See [`proxy/README.md`](../proxy/README.md) for full curl examples of every endpoint.

```bash
# Confirm the dev server is up
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
# → 200

# Confirm the production nginx build is serving (docker run -p 8080:80 planner-frontend)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
# → 200

# The app makes requests like these (shown here as curl; in the browser they go via Axios):

# Login (public)
curl -s -X POST http://localhost:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"hunter2"}'
# → {"token":"eyJ...","expires_at":"2026-11-04T12:00:00Z"}

# Load today's daily page (protected — token in Authorization header)
TOKEN=eyJ...
curl -s http://localhost:3000/api/planner/daily/2026-11-03 \
  -H "Authorization: Bearer $TOKEN"

# Auto-save a field on blur
curl -s -X PUT http://localhost:3000/api/planner/daily/2026-11-03 \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"notes":"Finish the planner README"}'
```

## Project layout

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts               ← Axios instance, token injection, 401 interceptor
│   │   ├── auth.ts                 ← login(), logout()
│   │   ├── accounts.ts             ← register()
│   │   └── planner.ts              ← getDaily/Weekly/Monthly, updateDaily/Weekly/Monthly
│   ├── hooks/
│   │   ├── useAuth.ts              ← Auth context + provider
│   │   ├── useDailyPage.ts         ← Fetch + debounced save for daily page
│   │   ├── useWeeklyPage.ts        ← Fetch + save for weekly page
│   │   └── useMonthlyPage.ts       ← Fetch + save for monthly page
│   ├── components/
│   │   ├── layout/PageShell.tsx    ← Nav tabs + prev/next + logout
│   │   ├── shared/                 ← SectionHeader, RuledField
│   │   ├── daily/                  ← DailyPage, TimeBlock, NotesSidebar
│   │   ├── weekly/                 ← WeeklyPage, WeekAtAGlance
│   │   └── monthly/                ← MonthlyPage
│   ├── pages/                      ← Route wrapper components
│   └── styles/global.css           ← CSS custom properties (tokens)
├── tests/                          ← Vitest + RTL tests mirroring src/
├── index.html
├── vite.config.ts
└── nginx.conf
```

## Auth

The JWT is stored in memory only — never in `localStorage`, `sessionStorage`, or a cookie. On page refresh the token is lost and the user must log in again. This is intentional (see [ADR-005](../docs/decisions/ADR-005-in-memory-jwt-storage.md)).

The Axios request interceptor attaches `Authorization: Bearer <token>` to every request. A 401 response clears the in-memory token.

## Save behavior

All fields save on blur. Long-form text areas (Notes, To Do List) additionally debounce-save 500ms after the user stops typing. A "Saved" indicator appears for 2 seconds after each successful save. No explicit save button — see [ADR-007](../docs/decisions/ADR-007-autosave-blur-debounce.md).

## Environment variables

```bash
VITE_API_BASE_URL=http://localhost:3000  # set by direnv; Vite also proxies /api → 3000 in dev
```

## Key notes

- **CSS Modules.** All component styles use CSS Modules (`.module.css`). No global class names in component files except `global.css`.
- **No `any`.** TypeScript `any` is banned. Use proper types or `unknown`.
- **`vite-env.d.ts`.** Required for `import.meta.env` and CSS module imports to type-check. Do not delete it.
- **Mock isolation in tests.** Call `vi.clearAllMocks()` in `beforeEach` — Vitest does not reset mock call history between tests by default.
