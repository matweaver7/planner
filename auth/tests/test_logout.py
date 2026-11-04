"""
Integration tests for POST /logout.
Endpoint must always return { "success": true } (idempotent).
Subsequent /validate calls on a logged-out token must return valid=false.
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
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def user_token(db_conn) -> tuple[str, str]:
    """Insert a user and return (user_id_str, valid_jwt)."""
    user_id = uuid.uuid4()
    username = f"logout_user_{user_id.hex[:8]}"
    pw_hash = hash_password("password!")

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
    return str(user_id), token


# ---------------------------------------------------------------------------
# Success / idempotency
# ---------------------------------------------------------------------------


async def test_logout_returns_success(client: AsyncClient, user_token) -> None:
    _, token = user_token

    resp = await client.post("/logout", json={"token": token})

    assert resp.status_code == 200
    assert resp.json() == {"success": True}


async def test_logout_blocks_subsequent_validate(
    client: AsyncClient, user_token
) -> None:
    _, token = user_token

    await client.post("/logout", json={"token": token})

    validate_resp = await client.post("/validate", json={"token": token})
    assert validate_resp.status_code == 200
    body = validate_resp.json()
    assert body["valid"] is False
    assert body["user_id"] is None


async def test_logout_twice_is_idempotent(client: AsyncClient, user_token) -> None:
    _, token = user_token

    resp1 = await client.post("/logout", json={"token": token})
    resp2 = await client.post("/logout", json={"token": token})

    assert resp1.status_code == resp2.status_code == 200
    assert resp1.json() == resp2.json() == {"success": True}


async def test_logout_expired_token_returns_success(client: AsyncClient) -> None:
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

    resp = await client.post("/logout", json={"token": expired_token})

    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_logout_malformed_token_returns_success(client: AsyncClient) -> None:
    resp = await client.post("/logout", json={"token": "totally.not.valid"})

    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_logout_does_not_affect_other_tokens(
    client: AsyncClient, db_conn
) -> None:
    """Logging out one token must not block a different token for the same user."""
    user_id = uuid.uuid4()
    token_a, _ = create_token(user_id)
    token_b, _ = create_token(user_id)

    await client.post("/logout", json={"token": token_a})

    validate_resp = await client.post("/validate", json={"token": token_b})
    assert validate_resp.status_code == 200
    assert validate_resp.json()["valid"] is True
