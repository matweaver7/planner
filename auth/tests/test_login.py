"""
Integration tests for POST /login.
Each test runs inside a rolled-back transaction — no data persists between tests.
"""
import uuid

import pytest
from httpx import AsyncClient

from app.services.auth_service import hash_password


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_user(
    client: AsyncClient,
    *,
    username: str,
    password: str,
    email: str | None = None,
) -> None:
    """Insert a user row directly via the test DB connection."""
    # We access db_conn through the client fixture's closure; instead, insert
    # via the conftest db_conn fixture passed in below.
    raise NotImplementedError("use _insert_user with db_conn directly")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def user_credentials(db_conn):
    """Insert a test user and return (username, plaintext_password)."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "s3cur3P@ss!"
    pw_hash = hash_password(password)
    email = f"{username}@example.com"

    from sqlalchemy import text
    await db_conn.execute(
        text(
            "INSERT INTO users (username, email, password_hash) "
            "VALUES (:username, :email, :pw_hash)"
        ),
        {"username": username, "email": email, "pw_hash": pw_hash},
    )

    return username, password


# ---------------------------------------------------------------------------
# Success cases
# ---------------------------------------------------------------------------


async def test_login_valid_credentials_returns_token(client: AsyncClient, user_credentials) -> None:
    username, password = user_credentials

    resp = await client.post("/login", json={"username": username, "password": password})

    assert resp.status_code == 200
    body = resp.json()
    assert "token" in body
    assert isinstance(body["token"], str)
    assert len(body["token"]) > 0
    assert "expires_at" in body


async def test_login_valid_credentials_token_is_jwt(client: AsyncClient, user_credentials) -> None:
    username, password = user_credentials

    resp = await client.post("/login", json={"username": username, "password": password})

    assert resp.status_code == 200
    token = resp.json()["token"]
    # A JWT has exactly 3 dot-separated base64url segments
    assert token.count(".") == 2


# ---------------------------------------------------------------------------
# Failure cases — both must return 401 with the same shape (no info leak)
# ---------------------------------------------------------------------------


async def test_login_wrong_password_returns_401(client: AsyncClient, user_credentials) -> None:
    username, _ = user_credentials

    resp = await client.post("/login", json={"username": username, "password": "wr0ngP@ss!"})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


async def test_login_unknown_username_returns_401(client: AsyncClient) -> None:
    resp = await client.post(
        "/login",
        json={"username": "nonexistent_user_xyz", "password": "doesntmatter"},
    )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


async def test_login_wrong_password_and_unknown_user_same_response(
    client: AsyncClient, user_credentials
) -> None:
    """Both failure modes return the identical body — no username enumeration."""
    username, _ = user_credentials

    wrong_pw = await client.post("/login", json={"username": username, "password": "bad"})
    unknown = await client.post("/login", json={"username": "nobody", "password": "bad"})

    assert wrong_pw.status_code == unknown.status_code == 401
    assert wrong_pw.json() == unknown.json()
