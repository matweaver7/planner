"""
Integration tests for POST /validate.
Endpoint must never return 4xx/5xx — always 200 with {valid, user_id}.
"""
import datetime
import uuid

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.config import settings
from app.services.auth_service import hash_password
from app.services.token_service import create_token


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def valid_token(db_conn) -> str:
    """Insert a user and return a fresh, valid JWT for that user."""
    user_id = uuid.uuid4()
    username = f"val_user_{user_id.hex[:8]}"
    pw_hash = hash_password("password123")

    await db_conn.execute(
        text(
            "INSERT INTO users (id, username, email, password_hash) "
            "VALUES (:id, :username, :email, :pw_hash)"
        ),
        {
            "id": str(user_id),
            "username": username,
            "email": f"{username}@example.com",
            "pw_hash": pw_hash,
        },
    )

    token, _ = create_token(user_id)
    return token


@pytest.fixture
async def blocked_token(db_conn, valid_token: str) -> str:
    """Return a valid token whose jti has been inserted into the blocklist."""
    payload = jwt.decode(
        valid_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    jti = payload["jti"]
    await db_conn.execute(
        text("INSERT INTO token_blocklist (token_jti) VALUES (:jti)"),
        {"jti": jti},
    )
    return valid_token


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


async def test_validate_valid_token_returns_true(
    client: AsyncClient, valid_token: str
) -> None:
    resp = await client.post("/validate", json={"token": valid_token})

    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["user_id"] is not None
    # user_id is a valid UUID string
    uuid.UUID(body["user_id"])


async def test_validate_returns_correct_user_id(
    client: AsyncClient, db_conn, valid_token: str
) -> None:
    payload = jwt.decode(
        valid_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    expected_user_id = payload["sub"]

    resp = await client.post("/validate", json={"token": valid_token})

    assert resp.status_code == 200
    assert resp.json()["user_id"] == expected_user_id


# ---------------------------------------------------------------------------
# Failure paths — all must be 200 with valid=false
# ---------------------------------------------------------------------------


async def test_validate_expired_token_returns_false(client: AsyncClient) -> None:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "jti": str(uuid.uuid4()),
        "iat": now - datetime.timedelta(hours=2),
        "exp": now - datetime.timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )

    resp = await client.post("/validate", json={"token": expired_token})

    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["user_id"] is None


async def test_validate_malformed_token_returns_false(client: AsyncClient) -> None:
    resp = await client.post("/validate", json={"token": "not.a.jwt"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["user_id"] is None


async def test_validate_wrong_secret_returns_false(client: AsyncClient) -> None:
    payload = {
        "sub": str(uuid.uuid4()),
        "jti": str(uuid.uuid4()),
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
        "exp": datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    resp = await client.post("/validate", json={"token": token})

    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["user_id"] is None


async def test_validate_blocked_token_returns_false(
    client: AsyncClient, blocked_token: str
) -> None:
    resp = await client.post("/validate", json={"token": blocked_token})

    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["user_id"] is None


async def test_validate_never_returns_4xx(client: AsyncClient) -> None:
    """Canary: even total garbage must yield 200."""
    for bad_token in ["", "garbage", "a.b.c", "x" * 500]:
        resp = await client.post("/validate", json={"token": bad_token})
        assert resp.status_code == 200, f"Got {resp.status_code} for token={bad_token!r}"
