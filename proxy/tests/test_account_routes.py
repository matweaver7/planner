"""
Tests for /api/accounts/* proxy routes.
"""
import uuid

import httpx
import respx
from httpx import AsyncClient

from app.config import settings
from tests.conftest import FAKE_USER_ID, VALID_TOKEN

AUTH_VALIDATE_URL = f"{settings.auth_service_url}/validate"
ACCOUNTS_URL = settings.accounts_service_url

_VALID_AUTH = httpx.Response(200, json={"valid": True, "user_id": FAKE_USER_ID})
_USER_RESPONSE = {
    "user_id": FAKE_USER_ID,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-01-01T00:00:00Z",
}


async def test_register_no_auth_required(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(f"{ACCOUNTS_URL}/register").mock(
            return_value=httpx.Response(201, json=_USER_RESPONSE)
        )
        resp = await client.post(
            "/api/accounts/register",
            json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
        )
    assert resp.status_code == 201


async def test_get_user_protected(client: AsyncClient) -> None:
    resp = await client.get(f"/api/accounts/users/{FAKE_USER_ID}")
    assert resp.status_code == 401


async def test_get_user_with_valid_token(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.get(f"{ACCOUNTS_URL}/users/{FAKE_USER_ID}").mock(
            return_value=httpx.Response(200, json=_USER_RESPONSE)
        )
        resp = await client.get(
            f"/api/accounts/users/{FAKE_USER_ID}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_put_user_protected(client: AsyncClient) -> None:
    resp = await client.put(f"/api/accounts/users/{FAKE_USER_ID}", json={"email": "b@example.com"})
    assert resp.status_code == 401


async def test_put_user_with_valid_token(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.put(f"{ACCOUNTS_URL}/users/{FAKE_USER_ID}").mock(
            return_value=httpx.Response(200, json=_USER_RESPONSE)
        )
        resp = await client.put(
            f"/api/accounts/users/{FAKE_USER_ID}",
            json={"email": "b@example.com"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_delete_user_protected(client: AsyncClient) -> None:
    resp = await client.delete(f"/api/accounts/users/{FAKE_USER_ID}")
    assert resp.status_code == 401


async def test_delete_user_with_valid_token(client: AsyncClient) -> None:
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(return_value=_VALID_AUTH)
        mock.delete(f"{ACCOUNTS_URL}/users/{FAKE_USER_ID}").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        resp = await client.delete(
            f"/api/accounts/users/{FAKE_USER_ID}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 200


async def test_auth_service_unavailable_returns_401(client: AsyncClient) -> None:
    """If auth service is down, middleware must return 401 not 500."""
    with respx.mock(assert_all_mocked=True) as mock:
        mock.post(AUTH_VALIDATE_URL).mock(side_effect=httpx.ConnectError("down"))
        resp = await client.get(
            f"/api/accounts/users/{FAKE_USER_ID}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )
    assert resp.status_code == 401
