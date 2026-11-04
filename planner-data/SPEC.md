# Spec: planner-data

## Objective

Planner data microservice. Stores and retrieves the three planner page types — daily,
weekly, and monthly — on a per-user basis. Each page is a structured document that mirrors
the sections in the physical spiral notebook this app replaces.

**Users:** Internal service consumers only (proxy). The proxy validates the user's JWT with
the `auth` service before forwarding any request here.

**Success:** An authenticated user can create, read, and update their daily, weekly, and
monthly planner pages. Data is stored server-side in MongoDB; the client holds no persistent
copy.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** MongoDB 7 via Motor (async MongoDB driver)
- **ODM:** Beanie (async ODM built on Motor + Pydantic)
- **Server:** Uvicorn
- **Testing:** pytest + pytest-asyncio + httpx + mongomock-motor (in-memory MongoDB for tests)
- **Containerization:** Docker

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start dev server
uvicorn app.main:app --reload --port 8003

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Build Docker image
docker build -t planner-data .

# Run via Docker
docker run -p 8003:8003 --env-file .env planner-data
```

## Project Structure

```
planner-data/
├── app/
│   ├── main.py                  ← FastAPI app factory, Beanie init, router registration
│   ├── config.py                ← Settings (pydantic-settings)
│   ├── database.py              ← Motor client + Beanie initialization
│   ├── models/
│   │   ├── daily_page.py        ← Beanie document model for daily pages
│   │   ├── weekly_page.py       ← Beanie document model for weekly pages
│   │   └── monthly_page.py      ← Beanie document model for monthly pages
│   ├── schemas/
│   │   ├── daily.py             ← Pydantic request/response schemas for daily endpoints
│   │   ├── weekly.py            ← Pydantic request/response schemas for weekly endpoints
│   │   └── monthly.py           ← Pydantic request/response schemas for monthly endpoints
│   ├── routers/
│   │   ├── daily.py             ← /daily/{date} endpoints
│   │   ├── weekly.py            ← /weekly/{year}/{week} endpoints
│   │   └── monthly.py           ← /monthly/{year}/{month} endpoints
│   └── services/
│       ├── daily_service.py     ← Get/upsert daily page
│       ├── weekly_service.py    ← Get/upsert weekly page
│       └── monthly_service.py   ← Get/upsert monthly page
├── tests/
│   ├── conftest.py              ← In-memory MongoDB fixture, async client fixture
│   ├── test_daily.py
│   ├── test_weekly.py
│   └── test_monthly.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Data Models

All documents include `user_id` (UUID string, sourced from the JWT validated by `auth`).
All writes are upserts keyed on `(user_id, <date fields>)` — no duplicate pages per user
per time period.

### Daily Page

```python
class TimeBlock(BaseModel):
    time: str        # "07:00", "07:30", ..., "21:00"
    text: str        # free text, default ""

class DailyPage(Document):
    user_id: str                    # UUID from auth
    date: str                       # ISO date "YYYY-MM-DD"
    time_blocks: list[TimeBlock]    # 30-min slots 07:00–21:00 (29 slots)
    notes: str                      # free text
    study_topic: str
    exercise_plan: str
    goals_for_today: str
    to_do_list: str

    class Settings:
        name = "daily_pages"
        indexes = [
            IndexModel([("user_id", 1), ("date", 1)], unique=True)
        ]
```

### Weekly Page

```python
class DayGlance(BaseModel):
    day: str         # "Monday", "Tuesday", etc.
    date: str        # ISO date "YYYY-MM-DD"
    text: str        # one-line summary

class WeeklyPage(Document):
    user_id: str
    year: int
    week: int                        # ISO week number 1–53
    week_of_date: str                # ISO date of Monday of that week
    study_topic: str
    educational_goal: str
    exercise_goal: str
    career_goal: str
    other_goals: str
    week_at_a_glance: list[DayGlance]  # 7 entries, Mon–Sun

    class Settings:
        name = "weekly_pages"
        indexes = [
            IndexModel([("user_id", 1), ("year", 1), ("week", 1)], unique=True)
        ]
```

### Monthly Page

```python
class MonthlyPage(Document):
    user_id: str
    year: int
    month: int                       # 1–12
    study_topic: str
    educational_goal: str
    exercise_goal: str
    career_goal: str
    other_goals: str

    class Settings:
        name = "monthly_pages"
        indexes = [
            IndexModel([("user_id", 1), ("year", 1), ("month", 1)], unique=True)
        ]
```

## API Endpoints

All endpoints receive `user_id` via the `X-User-ID` header, set by the proxy after
token validation. Endpoints do not accept or parse JWTs directly.

```
# Daily
GET  /daily/{date}
     date format: YYYY-MM-DD
     Returns: DailyPage document (empty-string fields if page not yet created)

PUT  /daily/{date}
     Body: partial DailyPage fields (any subset)
     Returns: updated DailyPage document

# Weekly
GET  /weekly/{year}/{week}
     Returns: WeeklyPage document

PUT  /weekly/{year}/{week}
     Body: partial WeeklyPage fields
     Returns: updated WeeklyPage document

# Monthly
GET  /monthly/{year}/{month}
     Returns: MonthlyPage document

PUT  /monthly/{year}/{month}
     Body: partial MonthlyPage fields
     Returns: updated MonthlyPage document
```

All GET endpoints return an empty-but-valid page document if none exists yet (not 404),
so the frontend can always render the form.

## Code Style

```python
# app/routers/daily.py
from fastapi import APIRouter, Header
from app.schemas.daily import DailyPageResponse, DailyPageUpdate
from app.services.daily_service import DailyService

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/{date}", response_model=DailyPageResponse)
async def get_daily_page(
    date: str,
    x_user_id: str = Header(...),
    service: DailyService = Depends(),
) -> DailyPageResponse:
    return await service.get_or_create(user_id=x_user_id, date=date)


@router.put("/{date}", response_model=DailyPageResponse)
async def update_daily_page(
    date: str,
    body: DailyPageUpdate,
    x_user_id: str = Header(...),
    service: DailyService = Depends(),
) -> DailyPageResponse:
    return await service.upsert(user_id=x_user_id, date=date, data=body)
```

- `user_id` always comes from `X-User-ID` header — never from the request body
- All writes are upserts (insert if not exists, update if exists)
- GET on a missing document returns a zeroed-out document, not 404
- All DB calls are async via Motor/Beanie

## Testing Strategy

- **Framework:** pytest + pytest-asyncio
- **MongoDB:** `mongomock-motor` for in-memory MongoDB (no live Mongo needed in CI)
- **HTTP client:** `httpx.AsyncClient` with `ASGITransport`
- **Coverage target:** 90% on `app/`
- **Test levels:**
  - Unit: service functions tested with mock collections
  - Integration: full endpoint tests with in-memory MongoDB
- Each test function sets up and tears down its own documents

## Environment Variables

```bash
# .env.example
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=planner_data
```

## Boundaries

- **Always:**
  - Trust `X-User-ID` header — do not validate the JWT here (proxy has already done it)
  - Use upsert semantics for all writes — never create duplicates
  - Return an empty page (all fields default to `""`) on GET when no document exists
  - Scope every query with `user_id` — never return another user's data

- **Ask first:**
  - Adding fields to any page document (affects frontend rendering)
  - Changing the time slot range or granularity on daily pages
  - Adding a new page type

- **Never:**
  - Accept or parse JWTs directly — auth is the proxy's responsibility
  - Return documents from a different `user_id` than the one in the header
  - Use synchronous MongoDB calls (always use `await`)
  - Commit `.env` files

## Success Criteria

- [ ] `GET /daily/{date}` returns an empty daily page document for a new user (not 404)
- [ ] `PUT /daily/{date}` saves partial updates and returns the full updated document
- [ ] `GET /weekly/{year}/{week}` returns an empty weekly page for a new user
- [ ] `PUT /weekly/{year}/{week}` saves goal sections and week-at-a-glance entries
- [ ] `GET /monthly/{year}/{month}` returns an empty monthly page for a new user
- [ ] `PUT /monthly/{year}/{month}` saves monthly goal sections
- [ ] Two different `user_id` values can each have a daily page for the same date without collision
- [ ] `pytest --cov=app` reports ≥ 90% coverage

## Open Questions

- None — requirements are fully resolved.
