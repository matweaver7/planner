# ADR-006: GET Planner Pages Never Return 404

## Status
Accepted

## Date
2026-11-03

## Context

A user navigating to `/daily/2026-11-03` for the first time has no existing document for that date. The planner-data service could respond with 404 (not found) and require the frontend to handle it, or it could return an empty-but-valid document.

## Decision

`GET /daily/{date}`, `GET /weekly/{year}/{week}`, and `GET /monthly/{year}/{month}` always return 200 with a fully-structured document, even if no data has been saved yet. For a new user or a new date, the response contains the default document structure (empty strings, default time blocks) rather than a 404.

```python
# planner-data/app/services/daily_service.py
async def get_or_create(user_id: str, date: str) -> DailyPage:
    page = await DailyPage.find_one({"user_id": user_id, "date": date})
    if page is None:
        return DailyPage(user_id=user_id, date=date)  # not saved yet
    return page
```

The empty document is **not** persisted — it exists only in the response. It is only persisted on the first PUT.

## Alternatives Considered

### Return 404 for missing pages
- Pros: Standard REST semantics — a resource that doesn't exist returns 404
- Cons: Every frontend component needs a special-case code path for "page doesn't exist yet vs. server error"; the user sees a blank page or error state instead of an empty planner page
- Rejected: The UX for a planner is "show me a blank page for today" not "today's page does not exist". 404 is technically correct but UX-wrong here.

### Auto-create on first GET (save empty document to DB)
- Pros: Subsequent GETs are consistent (always from DB)
- Cons: Creates a document for every date the user ever visits, even if they never write anything; storage grows unboundedly with browser history
- Rejected: Lazy creation (on first PUT) is cleaner

## Consequences

- **Positive:** Frontend components are simpler — they always receive a valid document and never need to distinguish "blank page" from "not found".
- **Positive:** No accidental documents created for dates the user navigates through without editing.
- **Negative:** Minor deviation from strict REST semantics. A GET for a date in 1900 returns 200 with an empty document rather than 404. This is acceptable given the domain — a planner is an open-ended document model, not a finite resource list.
- **Consistency note:** The `user_id` in the returned empty document comes from the `X-User-ID` header injected by the proxy. The planner-data service trusts this header completely and uses it as the document owner.
