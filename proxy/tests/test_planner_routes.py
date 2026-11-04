"""
Tests for /api/planner/* proxy routes (protected).
"""
import uuid

import httpx
import respx
from httpx import AsyncClient

from app.config import settings
from tests.conftest import FAKE_USER_ID, VALID_TOKEN

AUTH_VALIDATE_URL = f"{settings.auth_service_url}/validate"
PLANNER_URL = settings.planner_data_service_url

_VALID_AUTH = httpx.Response(200, json={"valid": True, "user_id": FAKE_USER_ID})
_DAILY_RESPONSE = {"user_id": FAKE_USER_ID, "date": "2026-11-03", "time_blocks": [], "notes": "", "study_topic": "", "exercise_plan": "", "goals_for_today": "", "to_do_list": ""}
_WEEKLY_RESPONSE = {"user_id": FAKE_USER_ID, "year": 2026, "week": 45, "week_of_date": "2026-11-02", "study_topic": "", "educational_goal": "", "exercise_goal": "", "career_goal": "", "other_goals": "", "week_at_a_glance": []}
_MONTHLY_RESPONSE = {"user_id": FAKE_USER_ID, "year": 2026, "month": 11, "study_topic": "", "educational_goal": "", "exercise_goal": "", "career_goal": "", "other_goals": ""}


async def test_get_daily_no_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/api/planner/daily/2026-11-03")
    assert resp.status_code == 401


async def test_get_daily_with_valid_token_forwards(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.get(f"{PLANNER_URL}/daily/2026-11-03").mock(
            return_value=httpx.Response(200, json=_DAILY_RESPONSE)
        )
        resp = await client.get(
            "/api/planner/daily/2026-11-03",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_get_daily_injects_x_user_id(client: AsyncClient) -> None:
    """Verify X-User-ID header reaches the upstream service."""
    received_headers = {}

    def capture_headers(request, *args, **kwargs):
        received_headers.update(dict(request.headers))
        return httpx.Response(200, json=_DAILY_RESPONSE)

    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.get(f"{PLANNER_URL}/daily/2026-11-03").mock(side_effect=capture_headers)
        await client.get(
            "/api/planner/daily/2026-11-03",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

    assert received_headers.get("x-user-id") == FAKE_USER_ID


async def test_put_daily_no_token_returns_401(client: AsyncClient) -> None:
    resp = await client.put("/api/planner/daily/2026-11-03", json={"notes": "x"})
    assert resp.status_code == 401


async def test_put_daily_with_valid_token_forwards(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.put(f"{PLANNER_URL}/daily/2026-11-03").mock(
            return_value=httpx.Response(200, json=_DAILY_RESPONSE)
        )
        resp = await client.put(
            "/api/planner/daily/2026-11-03",
            json={"notes": "test"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_get_weekly_protected(client: AsyncClient) -> None:
    resp = await client.get("/api/planner/weekly/2026/45")
    assert resp.status_code == 401


async def test_get_weekly_with_valid_token(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.get(f"{PLANNER_URL}/weekly/2026/45").mock(
            return_value=httpx.Response(200, json=_WEEKLY_RESPONSE)
        )
        resp = await client.get(
            "/api/planner/weekly/2026/45",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_get_monthly_protected(client: AsyncClient) -> None:
    resp = await client.get("/api/planner/monthly/2026/11")
    assert resp.status_code == 401


async def test_get_monthly_with_valid_token(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.get(f"{PLANNER_URL}/monthly/2026/11").mock(
            return_value=httpx.Response(200, json=_MONTHLY_RESPONSE)
        )
        resp = await client.get(
            "/api/planner/monthly/2026/11",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_put_weekly_injects_x_user_id(client: AsyncClient) -> None:
    received_headers = {}

    def capture(request, *args, **kwargs):
        received_headers.update(dict(request.headers))
        return httpx.Response(200, json=_WEEKLY_RESPONSE)

    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.put(f"{PLANNER_URL}/weekly/2026/45").mock(side_effect=capture)
        await client.put(
            "/api/planner/weekly/2026/45",
            json={"study_topic": "x"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

    assert received_headers.get("x-user-id") == FAKE_USER_ID
