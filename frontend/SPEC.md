# Spec: frontend

## Objective

React web application for the Planner SaaS. Renders the three planner page types — daily,
weekly, and monthly — with a visual style nearly identical to the physical spiral notebook
it replaces. All data is fetched from and saved to the proxy service; nothing is stored
client-side.

**Users:** Individual registered users, on desktop browsers (phase 1).

**Success:** A logged-in user can navigate to any day, week, or month; see their saved data
pre-filled in the correct fields; edit any field; and have changes saved automatically (or
on blur). The UI looks like a clean digital version of the paper planner.

## Tech Stack

- **Language:** TypeScript
- **Framework:** React 18
- **Build tool:** Vite (Node.js)
- **Routing:** React Router v6
- **HTTP:** Axios
- **Styling:** CSS Modules (plain CSS, no preprocessor)
- **Testing:** Vitest + React Testing Library
- **Containerization:** Docker (nginx to serve the built static files)

## Commands

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Type check
npm run typecheck

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run tests with coverage
npm run coverage

# Lint
npm run lint

# Build Docker image
docker build -t planner-frontend .

# Run via Docker (serves on port 80)
docker run -p 3000:80 planner-frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx                  ← React root, Router setup
│   ├── App.tsx                   ← Top-level route definitions
│   ├── api/
│   │   ├── client.ts             ← Axios instance (base URL, auth header injection)
│   │   ├── auth.ts               ← login(), logout() API calls
│   │   ├── planner.ts            ← getDaily(), updateDaily(), getWeekly(), etc.
│   │   └── accounts.ts           ← register() API call
│   ├── components/
│   │   ├── layout/
│   │   │   ├── PageShell.tsx     ← Outer chrome: nav, date picker, page type tabs
│   │   │   └── PageShell.module.css
│   │   ├── daily/
│   │   │   ├── DailyPage.tsx     ← Two-column layout: schedule + notes sidebar
│   │   │   ├── DailyPage.module.css
│   │   │   ├── TimeBlock.tsx     ← Single time-slot row (time label + text input)
│   │   │   └── NotesSidebar.tsx  ← Notes, Study Topic, Exercise Plan, Goals, To Do List
│   │   ├── weekly/
│   │   │   ├── WeeklyPage.tsx    ← Goals sections + week at a glance
│   │   │   ├── WeeklyPage.module.css
│   │   │   └── WeekAtAGlance.tsx ← 7-row table: day, date, one-line summary
│   │   ├── monthly/
│   │   │   ├── MonthlyPage.tsx   ← Goals sections scoped to a month
│   │   │   └── MonthlyPage.module.css
│   │   └── shared/
│   │       ├── SectionHeader.tsx ← Grey bar section divider (used on all page types)
│   │       ├── RuledField.tsx    ← Multi-line text area with ruled-line appearance
│   │       └── shared.module.css
│   ├── hooks/
│   │   ├── useAuth.ts            ← Auth state, login/logout actions
│   │   ├── useDailyPage.ts       ← Fetch + debounced save for daily page
│   │   ├── useWeeklyPage.ts      ← Fetch + debounced save for weekly page
│   │   └── useMonthlyPage.ts     ← Fetch + debounced save for monthly page
│   ├── pages/
│   │   ├── LoginPage.tsx         ← Username + password form
│   │   ├── RegisterPage.tsx      ← Registration form
│   │   ├── DailyView.tsx         ← Route wrapper: resolves date, renders DailyPage
│   │   ├── WeeklyView.tsx        ← Route wrapper: resolves year/week, renders WeeklyPage
│   │   └── MonthlyView.tsx       ← Route wrapper: resolves year/month, renders MonthlyPage
│   └── styles/
│       └── global.css            ← CSS reset, typography, CSS custom properties (tokens)
├── tests/
│   ├── components/               ← Component unit tests (RTL)
│   └── hooks/                    ← Hook tests (renderHook)
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── Dockerfile
└── nginx.conf                    ← Serves built files; proxies /api to proxy service in prod
```

## Routes

```
/login                    → LoginPage (public)
/register                 → RegisterPage (public)
/                         → redirect to /daily/today
/daily/:date              → DailyView  (e.g. /daily/2026-11-03)
/weekly/:year/:week       → WeeklyView (e.g. /weekly/2026/45)
/monthly/:year/:month     → MonthlyView (e.g. /monthly/2026/11)
```

All routes except `/login` and `/register` require an authenticated session. Unauthenticated
access to a protected route redirects to `/login`.

## Auth State

The JWT token is stored in memory only (a React context value). It is not written to
`localStorage`, `sessionStorage`, or any cookie. On page refresh the user must log in again.

```typescript
// src/hooks/useAuth.ts
interface AuthState {
  token: string | null;
  userId: string | null;
}
```

Token is attached to every API request via an Axios request interceptor:
```typescript
client.interceptors.request.use((config) => {
  const token = getToken(); // from in-memory auth context
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

## Page Designs

### Daily Page

Two-column layout, echoing the two-page spread in the physical planner.

**Left column — Daily Plan:**
- Header: "Daily Plan" (grey bar) with Month and day-of-week displayed
- Time-block rows from 07:00 to 21:00 in 30-minute increments (29 rows)
- Each row: time label (left, fixed width) + single-line text input (right, full width)

**Right column — Notes & Sections:**
- "Notes" section: large free-text area (grey header bar + tall ruled textarea)
- Sections below (each with grey header bar + ruled text area):
  - Study Topic
  - Exercise Plan
  - Goals for Today
  - To Do List

### Weekly Page

Single-column layout.

**Top half — Weekly Goals:**
- "Weekly Goals" header (grey bar)
- "Week of ___" date field
- Goal sections (grey header + multi-line ruled area each):
  - Study Topic
  - Educational Goal
  - Exercise Goal
  - Career Goal
  - Other Goals

**Bottom half — Week at a Glance:**
- "Week at a Glance" header (grey bar)
- 7-row table, one row per day (Monday–Sunday):
  - Date field (short, left-aligned)
  - Day label (Mon, Tue, etc.)
  - Single-line text input for the day's summary

### Monthly Page

Mirrors the weekly goals layout, scoped to a month.

- "Monthly Goals" header (grey bar)
- "Month of ___" field
- Goal sections (grey header + multi-line ruled area each):
  - Study Topic
  - Educational Goal
  - Exercise Goal
  - Career Goal
  - Other Goals

## Visual Style

The UI replicates the paper planner's minimalist look:

| Element | Style |
|---|---|
| Background | White (`#ffffff`) |
| Section headers | Light grey bar (`#d0d0d0` background), dark text, small caps |
| Section content | White background, horizontal ruled lines as bottom-borders on inputs |
| Input fields | No visible border box — just a bottom border line; no background color |
| Typography | Clean serif or neutral sans-serif (e.g. `Georgia` or `Inter`), modest size |
| Time labels | Monospace, right-aligned, fixed width |
| Layout | Max-width container centered, generous margins, no sidebar nav |

CSS custom properties (tokens) defined in `global.css`:

```css
:root {
  --color-bg: #ffffff;
  --color-section-header-bg: #d0d0d0;
  --color-rule: #cccccc;
  --color-text: #1a1a1a;
  --color-text-muted: #666666;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'Courier New', monospace;
}
```

## Save Behavior

Fields save automatically on blur (when the user clicks away from a field). No explicit
"Save" button. A debounced save (500ms) fires while typing for long-form text areas
(notes, to-do list). A subtle visual indicator (e.g. a fading "Saved" text) confirms
the save completed.

## Code Style

```typescript
// src/components/shared/SectionHeader.tsx
import styles from './shared.module.css';

interface SectionHeaderProps {
  label: string;
}

export function SectionHeader({ label }: SectionHeaderProps) {
  return <div className={styles.sectionHeader}>{label}</div>;
}
```

```typescript
// src/hooks/useDailyPage.ts
import { useEffect, useState, useCallback } from 'react';
import { getDaily, updateDaily } from '../api/planner';
import type { DailyPage } from '../api/planner';

export function useDailyPage(date: string) {
  const [page, setPage] = useState<DailyPage | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getDaily(date).then(setPage);
  }, [date]);

  const save = useCallback(async (patch: Partial<DailyPage>) => {
    setSaving(true);
    const updated = await updateDaily(date, patch);
    setPage(updated);
    setSaving(false);
  }, [date]);

  return { page, saving, save };
}
```

- All components are functional with hooks — no class components
- Props types are defined as interfaces, never inline `{}`
- CSS Modules only — no inline styles, no global class names except in `global.css`
- No `any` — use proper types or `unknown`
- One component per file; file name matches component name (PascalCase)

## Testing Strategy

- **Framework:** Vitest + React Testing Library
- **Coverage target:** 80% on `src/`
- **Test levels:**
  - Unit: component rendering and interaction (RTL)
  - Hook tests: `renderHook` with mocked API calls (via `vi.mock`)
  - No end-to-end tests in phase 1
- Tests live in `tests/` mirroring `src/` structure
- API calls are always mocked in tests — no live network calls

## Environment Variables

```bash
# .env.example (Vite exposes VITE_ prefixed vars to the browser)
VITE_API_BASE_URL=http://localhost:8000
```

## Boundaries

- **Always:**
  - Store the JWT in memory only — never `localStorage`, `sessionStorage`, or cookies
  - Save data server-side on every blur/debounced change — never rely on local state as
    the source of truth
  - Redirect to `/login` if a 401 is received from the proxy
  - Use CSS Modules — no global class names in component files

- **Ask first:**
  - Adding a new npm dependency
  - Adding a new page type or route
  - Changing the save behavior (e.g. moving from blur to explicit save button)
  - Adding offline support (out of scope for phase 1)

- **Never:**
  - Write the JWT or any user data to `localStorage`, `sessionStorage`, or `document.cookie`
  - Make API calls directly to internal services — always go through the proxy
  - Use `any` as a TypeScript type
  - Add phase 2 (iPhone) concerns to this codebase

## Success Criteria

- [ ] `/login` authenticates with valid credentials and redirects to `/daily/today`
- [ ] `/register` creates an account and redirects to `/login`
- [ ] `/daily/:date` renders a two-column daily page with all sections populated from the server
- [ ] Editing a time block and clicking away triggers a save; refreshing the page shows the saved value
- [ ] `/weekly/:year/:week` renders weekly goals and week-at-a-glance
- [ ] `/monthly/:year/:month` renders monthly goals
- [ ] Navigating between days/weeks/months loads the correct data
- [ ] Refreshing the page on a protected route redirects to `/login` (token is in-memory only)
- [ ] The visual style matches the paper planner: grey section headers, ruled lines, white background
- [ ] `npm run typecheck` passes with zero errors
- [ ] `npm run coverage` reports ≥ 80% coverage on `src/`

## Open Questions

- None — requirements are fully resolved.
