"""
Integration tests for GET /monthly/{year}/{month} and PUT /monthly/{year}/{month}.
"""
import uuid

from httpx import AsyncClient


USER_A = str(uuid.uuid4())
USER_B = str(uuid.uuid4())
YEAR = 2026
MONTH = 11


async def test_get_monthly_new_user_returns_200(client: AsyncClient) -> None:
    resp = await client.get(f"/monthly/{YEAR}/{MONTH}", headers={"x-user-id": USER_A})
    assert resp.status_code == 200


async def test_get_monthly_new_user_returns_empty_page(client: AsyncClient) -> None:
    resp = await client.get(f"/monthly/{YEAR}/{MONTH}", headers={"x-user-id": USER_A})
    data = resp.json()

    assert data["user_id"] == USER_A
    assert data["year"] == YEAR
    assert data["month"] == MONTH
    assert data["study_topic"] == ""
    assert data["educational_goal"] == ""
    assert data["exercise_goal"] == ""
    assert data["career_goal"] == ""
    assert data["other_goals"] == ""


async def test_put_monthly_saves_all_goal_sections(client: AsyncClient) -> None:
    payload = {
        "study_topic": "guitar",
        "educational_goal": "finish course",
        "exercise_goal": "5 days/week",
        "career_goal": "ship v1",
        "other_goals": "read 2 books",
    }
    await client.put(f"/monthly/{YEAR}/{MONTH}", json=payload, headers={"x-user-id": USER_A})
    resp = await client.get(f"/monthly/{YEAR}/{MONTH}", headers={"x-user-id": USER_A})
    data = resp.json()

    assert data["study_topic"] == "guitar"
    assert data["educational_goal"] == "finish course"
    assert data["exercise_goal"] == "5 days/week"
    assert data["career_goal"] == "ship v1"
    assert data["other_goals"] == "read 2 books"


async def test_put_monthly_partial_update(client: AsyncClient) -> None:
    await client.put(
        f"/monthly/{YEAR}/{MONTH}",
        json={"study_topic": "piano", "career_goal": "hire 2 engineers"},
        headers={"x-user-id": USER_A},
    )
    await client.put(
        f"/monthly/{YEAR}/{MONTH}",
        json={"career_goal": "updated goal"},
        headers={"x-user-id": USER_A},
    )
    resp = await client.get(f"/monthly/{YEAR}/{MONTH}", headers={"x-user-id": USER_A})
    data = resp.json()
    assert data["study_topic"] == "piano"
    assert data["career_goal"] == "updated goal"


async def test_two_users_can_have_same_month(client: AsyncClient) -> None:
    await client.put(
        f"/monthly/{YEAR}/{MONTH}",
        json={"study_topic": "A's topic"},
        headers={"x-user-id": USER_A},
    )
    await client.put(
        f"/monthly/{YEAR}/{MONTH}",
        json={"study_topic": "B's topic"},
        headers={"x-user-id": USER_B},
    )

    resp_a = await client.get(f"/monthly/{YEAR}/{MONTH}", headers={"x-user-id": USER_A})
    resp_b = await client.get(f"/monthly/{YEAR}/{MONTH}", headers={"x-user-id": USER_B})

    assert resp_a.json()["study_topic"] == "A's topic"
    assert resp_b.json()["study_topic"] == "B's topic"
