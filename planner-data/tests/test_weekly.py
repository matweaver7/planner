"""
Integration tests for GET /weekly/{year}/{week} and PUT /weekly/{year}/{week}.
"""
import uuid

from httpx import AsyncClient


USER_A = str(uuid.uuid4())
USER_B = str(uuid.uuid4())
YEAR = 2026
WEEK = 45


async def test_get_weekly_new_user_returns_200(client: AsyncClient) -> None:
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    assert resp.status_code == 200


async def test_get_weekly_new_user_returns_empty_page(client: AsyncClient) -> None:
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    data = resp.json()

    assert data["user_id"] == USER_A
    assert data["year"] == YEAR
    assert data["week"] == WEEK
    assert data["study_topic"] == ""
    assert data["educational_goal"] == ""
    assert data["exercise_goal"] == ""
    assert data["career_goal"] == ""
    assert data["other_goals"] == ""


async def test_get_weekly_has_7_glance_entries(client: AsyncClient) -> None:
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    glance = resp.json()["week_at_a_glance"]
    assert len(glance) == 7


async def test_get_weekly_glance_starts_monday(client: AsyncClient) -> None:
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    glance = resp.json()["week_at_a_glance"]
    assert glance[0]["day"] == "Monday"
    assert glance[-1]["day"] == "Sunday"


async def test_get_weekly_glance_has_correct_dates(client: AsyncClient) -> None:
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    glance = resp.json()["week_at_a_glance"]
    # ISO week 45 of 2026 — Monday should be 2026-11-02
    assert glance[0]["date"] == "2026-11-02"
    assert glance[6]["date"] == "2026-11-08"


async def test_put_weekly_saves_goal_sections(client: AsyncClient) -> None:
    await client.put(
        f"/weekly/{YEAR}/{WEEK}",
        json={"study_topic": "history", "career_goal": "finish sprint"},
        headers={"x-user-id": USER_A},
    )
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    data = resp.json()
    assert data["study_topic"] == "history"
    assert data["career_goal"] == "finish sprint"


async def test_put_weekly_saves_week_at_a_glance(client: AsyncClient) -> None:
    glance = [
        {"day": d, "date": "", "text": f"{d} text"}
        for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ]
    await client.put(
        f"/weekly/{YEAR}/{WEEK}",
        json={"week_at_a_glance": glance},
        headers={"x-user-id": USER_A},
    )
    resp = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    returned = resp.json()["week_at_a_glance"]
    assert returned[0]["text"] == "Monday text"
    assert returned[6]["text"] == "Sunday text"


async def test_two_users_can_have_same_week(client: AsyncClient) -> None:
    await client.put(
        f"/weekly/{YEAR}/{WEEK}",
        json={"study_topic": "A's topic"},
        headers={"x-user-id": USER_A},
    )
    await client.put(
        f"/weekly/{YEAR}/{WEEK}",
        json={"study_topic": "B's topic"},
        headers={"x-user-id": USER_B},
    )

    resp_a = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_A})
    resp_b = await client.get(f"/weekly/{YEAR}/{WEEK}", headers={"x-user-id": USER_B})

    assert resp_a.json()["study_topic"] == "A's topic"
    assert resp_b.json()["study_topic"] == "B's topic"
