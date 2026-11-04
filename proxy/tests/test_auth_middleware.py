"""
Unit tests for the auth middleware (require_auth dependency).
"""
import httpx
import respx
from httpx import AsyncClient

from app.config import settings
from tests.conftest import FAKE_USER_ID, INVALID_TOKEN, VALID_TOKEN

AUTH_VALIDATE_URL = f"{settings.auth_service_url}/validate"
PLANNER_URL = settings.planner_data_service_url


async def test_no_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/api/planner/daily/2026-11-03")
    assert resp.status_code == 401


async def test_invalid_token_returns_401(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=False) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(
            return_value=httpx.Response(200, json={"valid": False, "user_id": None})
        )
        resp = await client.get(
            "/api/planner/daily/2026-11-03",
            headers={"Authorization": f"Bearer {INVALID_TOKEN}"},
        )
    assert resp.status_code == 401


async def test_valid_token_allows_request(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=False) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(
            return_value=httpx.Response(
                200, json={"valid": True, "user_id": FAKE_USER_ID}
            )
        )
        mock.get(f"{PLANNER_URL}/daily/2026-11-03").mock(
            return_value=httpx.Response(200, json={"user_id": FAKE_USER_ID, "date": "2026-11-03"})
        )
        resp = await client.get(
            "/api/planner/daily/2026-11-03",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200
