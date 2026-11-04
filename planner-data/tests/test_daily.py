"""
Integration tests for GET /daily/{date} and PUT /daily/{date}.
"""
import uuid

import pytest
from httpx import AsyncClient


USER_A = str(uuid.uuid4())
USER_B = str(uuid.uuid4())
DATE = "2026-11-03"


# ---------------------------------------------------------------------------
# GET — empty page for new user
# ---------------------------------------------------------------------------


async def test_get_daily_new_user_returns_200(client: AsyncClient) -> None:
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    assert resp.status_code == 200


async def test_get_daily_new_user_returns_empty_page(client: AsyncClient) -> None:
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    data = resp.json()

    assert data["user_id"] == USER_A
    assert data["date"] == DATE
    assert data["notes"] == ""
    assert data["study_topic"] == ""
    assert data["exercise_plan"] == ""
    assert data["goals_for_today"] == ""
    assert data["to_do_list"] == ""


async def test_get_daily_has_29_time_blocks(client: AsyncClient) -> None:
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    blocks = resp.json()["time_blocks"]

    assert len(blocks) == 29


async def test_get_daily_time_blocks_start_at_0700(client: AsyncClient) -> None:
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    blocks = resp.json()["time_blocks"]

    assert blocks[0]["time"] == "07:00"
    assert blocks[-1]["time"] == "21:00"


async def test_get_daily_time_blocks_have_empty_text(client: AsyncClient) -> None:
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    blocks = resp.json()["time_blocks"]

    assert all(block["text"] == "" for block in blocks)


# ---------------------------------------------------------------------------
# PUT — upsert
# ---------------------------------------------------------------------------


async def test_put_daily_returns_200(client: AsyncClient) -> None:
    resp = await client.put(
        f"/daily/{DATE}",
        json={"notes": "hello"},
        headers={"x-user-id": USER_A},
    )
    assert resp.status_code == 200


async def test_put_daily_saves_notes(client: AsyncClient) -> None:
    await client.put(
        f"/daily/{DATE}",
        json={"notes": "important note"},
        headers={"x-user-id": USER_A},
    )
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    assert resp.json()["notes"] == "important note"


async def test_put_daily_partial_update_preserves_other_fields(client: AsyncClient) -> None:
    await client.put(
        f"/daily/{DATE}",
        json={"notes": "first note", "study_topic": "Python"},
        headers={"x-user-id": USER_A},
    )
    await client.put(
        f"/daily/{DATE}",
        json={"notes": "updated note"},
        headers={"x-user-id": USER_A},
    )
    resp = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    data = resp.json()
    assert data["notes"] == "updated note"
    assert data["study_topic"] == "Python"


async def test_put_daily_updates_time_blocks(client: AsyncClient) -> None:
    blocks = [{"time": "07:00", "text": "wake up"}, {"time": "07:30", "text": "exercise"}]
    resp = await client.put(
        f"/daily/{DATE}",
        json={"time_blocks": blocks},
        headers={"x-user-id": USER_A},
    )
    returned_blocks = resp.json()["time_blocks"]
    assert returned_blocks[0]["text"] == "wake up"
    assert returned_blocks[1]["text"] == "exercise"


# ---------------------------------------------------------------------------
# User isolation
# ---------------------------------------------------------------------------


async def test_two_users_can_have_same_date(client: AsyncClient) -> None:
    await client.put(
        f"/daily/{DATE}",
        json={"notes": "user A note"},
        headers={"x-user-id": USER_A},
    )
    await client.put(
        f"/daily/{DATE}",
        json={"notes": "user B note"},
        headers={"x-user-id": USER_B},
    )

    resp_a = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_A})
    resp_b = await client.get(f"/daily/{DATE}", headers={"x-user-id": USER_B})

    assert resp_a.json()["notes"] == "user A note"
    assert resp_b.json()["notes"] == "user B note"


# ---------------------------------------------------------------------------
# Missing header
# ---------------------------------------------------------------------------


async def test_get_daily_missing_user_id_header_returns_422(client: AsyncClient) -> None:
    resp = await client.get(f"/daily/{DATE}")
    assert resp.status_code == 422
