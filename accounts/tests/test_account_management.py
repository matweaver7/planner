"""
Integration tests for GET/PUT/DELETE /users/{user_id}.
"""
import uuid

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Fixture — create a user and return its ID + original credentials
# ---------------------------------------------------------------------------


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    uid = uuid.uuid4().hex[:8]
    body = {
        "username": f"mgmt_{uid}",
        "email": f"mgmt_{uid}@example.com",
        "password": "password123",
    }
    resp = await client.post("/register", json=body)
    assert resp.status_code == 201
    data = resp.json()
    data["original_password"] = body["password"]
    return data


# ---------------------------------------------------------------------------
# GET /users/{user_id}
# ---------------------------------------------------------------------------


async def test_get_user_returns_200(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.get(f"/users/{registered_user['user_id']}")

    assert resp.status_code == 200


async def test_get_user_returns_correct_fields(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.get(f"/users/{registered_user['user_id']}")
    data = resp.json()

    assert data["user_id"] == registered_user["user_id"]
    assert data["username"] == registered_user["username"]
    assert data["email"] == registered_user["email"]
    assert "password_hash" not in data
    assert "password" not in data


async def test_get_unknown_user_returns_404(client: AsyncClient) -> None:
    resp = await client.get(f"/users/{uuid.uuid4()}")

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /users/{user_id}
# ---------------------------------------------------------------------------


async def test_update_email_returns_200(client: AsyncClient, registered_user: dict) -> None:
    new_email = f"new_{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.put(
        f"/users/{registered_user['user_id']}",
        json={"email": new_email},
    )

    assert resp.status_code == 200
    assert resp.json()["email"] == new_email


async def test_update_email_persists(client: AsyncClient, registered_user: dict) -> None:
    new_email = f"persist_{uuid.uuid4().hex[:8]}@example.com"
    await client.put(
        f"/users/{registered_user['user_id']}",
        json={"email": new_email},
    )

    resp = await client.get(f"/users/{registered_user['user_id']}")
    assert resp.json()["email"] == new_email


async def test_update_password_returns_200(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.put(
        f"/users/{registered_user['user_id']}",
        json={"password": "newpassword99"},
    )

    assert resp.status_code == 200


async def test_update_duplicate_email_returns_409(
    client: AsyncClient, registered_user: dict
) -> None:
    # Register a second user and try to take their email
    uid2 = uuid.uuid4().hex[:8]
    other_email = f"other_{uid2}@example.com"
    await client.post("/register", json={
        "username": f"other_{uid2}",
        "email": other_email,
        "password": "somepassword",
    })

    resp = await client.put(
        f"/users/{registered_user['user_id']}",
        json={"email": other_email},
    )

    assert resp.status_code == 409


async def test_update_unknown_user_returns_404(client: AsyncClient) -> None:
    resp = await client.put(
        f"/users/{uuid.uuid4()}",
        json={"email": "newemail@example.com"},
    )

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /users/{user_id}
# ---------------------------------------------------------------------------


async def test_delete_user_returns_200(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.delete(f"/users/{registered_user['user_id']}")

    assert resp.status_code == 200
    assert resp.json() == {"success": True}


async def test_delete_user_removes_from_db(client: AsyncClient, registered_user: dict) -> None:
    await client.delete(f"/users/{registered_user['user_id']}")

    get_resp = await client.get(f"/users/{registered_user['user_id']}")
    assert get_resp.status_code == 404


async def test_delete_unknown_user_returns_404(client: AsyncClient) -> None:
    resp = await client.delete(f"/users/{uuid.uuid4()}")

    assert resp.status_code == 404
