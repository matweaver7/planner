"""
Integration tests for POST /register.
"""
import uuid

import pytest
from httpx import AsyncClient


def _reg_body(*, username: str | None = None, email: str | None = None, password: str = "securepass") -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "username": username or f"user_{uid}",
        "email": email or f"user_{uid}@example.com",
        "password": password,
    }


# ---------------------------------------------------------------------------
# Success
# ---------------------------------------------------------------------------


async def test_register_returns_201(client: AsyncClient) -> None:
    resp = await client.post("/register", json=_reg_body())

    assert resp.status_code == 201


async def test_register_response_fields(client: AsyncClient) -> None:
    body = _reg_body()
    resp = await client.post("/register", json=body)

    data = resp.json()
    assert "user_id" in data
    assert data["username"] == body["username"]
    assert data["email"] == body["email"]
    assert "created_at" in data
    # password_hash must never appear in the response
    assert "password_hash" not in data
    assert "password" not in data


async def test_register_user_id_is_uuid(client: AsyncClient) -> None:
    resp = await client.post("/register", json=_reg_body())
    user_id = resp.json()["user_id"]
    uuid.UUID(user_id)  # raises if invalid


# ---------------------------------------------------------------------------
# Conflict — 409
# ---------------------------------------------------------------------------


async def test_register_duplicate_username_returns_409(client: AsyncClient) -> None:
    body = _reg_body(username="dup_user")
    await client.post("/register", json=body)

    body2 = _reg_body(username="dup_user")  # same username, different email
    resp = await client.post("/register", json=body2)

    assert resp.status_code == 409


async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    await client.post("/register", json=_reg_body(email=email))

    body2 = _reg_body(email=email)  # same email, different username
    resp = await client.post("/register", json=body2)

    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Validation — 422
# ---------------------------------------------------------------------------


async def test_register_short_password_returns_422(client: AsyncClient) -> None:
    resp = await client.post("/register", json=_reg_body(password="short"))

    assert resp.status_code == 422


async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    resp = await client.post("/register", json={
        "username": "validuser",
        "email": "not-an-email",
        "password": "validpassword",
    })

    assert resp.status_code == 422
