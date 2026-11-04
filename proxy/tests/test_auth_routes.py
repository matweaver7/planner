"""
Tests for /api/auth/* proxy routes.
"""
import httpx
import respx
from httpx import AsyncClient

from app.config import settings
from tests.conftest import FAKE_USER_ID, VALID_TOKEN

AUTH_SERVICE = settings.auth_service_url
AUTH_VALIDATE_URL = f"{AUTH_SERVICE}/validate"


async def test_login_forwarded_to_auth_service(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=False) as mock:
        mock.post(f"{AUTH_SERVICE}/login").mock(
            return_value=httpx.Response(
                200, json={"token": "t", "expires_at": "2026-01-01T00:00:00Z"}
            )
        )
        resp = await client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "secret"},
        )
    assert resp.status_code == 200
    assert resp.json()["token"] == "t"


async def test_login_no_auth_required(client: AsyncClient) -> None:
    """Login must not require a Bearer token."""
    with respx.mock(assert_all_mocked=False) as mock:
        mock.post(f"{AUTH_SERVICE}/login").mock(
            return_value=httpx.Response(
                200, json={"token": "t", "expires_at": "2026-01-01T00:00:00Z"}
            )
        )
        resp = await client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "secret"},
        )
    assert resp.status_code != 401


async def test_validate_forwarded_to_auth_service(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=False) as mock:
        mock.post(f"{AUTH_SERVICE}/validate").mock(
            return_value=httpx.Response(
                200, json={"valid": True, "user_id": FAKE_USER_ID}
            )
        )
        resp = await client.post("/api/auth/validate", json={"token": VALID_TOKEN})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


async def test_logout_requires_auth(client: AsyncClient) -> None:
    """Logout without a token should return 401."""
    resp = await client.post("/api/auth/logout", json={"token": VALID_TOKEN})
    assert resp.status_code == 401


async def test_logout_with_valid_token_forwarded(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=False) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(
            return_value=httpx.Response(
                200, json={"valid": True, "user_id": FAKE_USER_ID}
            )
        )
        mock.post(f"{AUTH_SERVICE}/logout").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        resp = await client.post(
            "/api/auth/logout",
            json={"token": VALID_TOKEN},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
