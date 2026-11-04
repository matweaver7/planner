import datetime

from app.models.weekly_page import DayGlance, WeeklyPage
from app.schemas.weekly import WeeklyPageResponse, WeeklyPageUpdate


_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _week_dates(year: int, week: int) -> list[DayGlance]:
    """Return DayGlance entries Mon-Sun with actual dates for the ISO week."""
    entries = []
    for day_num, day_name in enumerate(_DAYS, start=1):
        try:
            d = datetime.date.fromisocalendar(year, week, day_num)
            date_str = d.isoformat()
        except ValueError:
            date_str = ""
        entries.append(DayGlance(day=day_name, date=date_str, text=""))
    return entries


def _to_response(page: WeeklyPage) -> WeeklyPageResponse:
    return WeeklyPageResponse(
        user_id=page.user_id,
        year=page.year,
        week=page.week,
        week_of_date=page.week_of_date,
        study_topic=page.study_topic,
        educational_goal=page.educational_goal,
        exercise_goal=page.exercise_goal,
        career_goal=page.career_goal,
        other_goals=page.other_goals,
        week_at_a_glance=page.week_at_a_glance,
    )


async def get_or_create(user_id: str, year: int, week: int) -> WeeklyPageResponse:
    page = await WeeklyPage.find_one({"user_id": user_id, "year": year, "week": week})
    if page is None:
        week_at_a_glance = _week_dates(year, week)
        try:
            week_of_date = datetime.date.fromisocalendar(year, week, 1).isoformat()
        except ValueError:
            week_of_date = ""
        page = WeeklyPage(
            user_id=user_id,
            year=year,
            week=week,
            week_of_date=week_of_date,
            week_at_a_glance=week_at_a_glance,
        )
    return _to_response(page)


async def upsert(user_id: str, year: int, week: int, data: WeeklyPageUpdate) -> WeeklyPageResponse:
    page = await WeeklyPage.find_one({"user_id": user_id, "year": year, "week": week})
    update_dict = data.model_dump(exclude_none=True)

    if page is None:
        week_at_a_glance = update_dict.pop("week_at_a_glance", None) or _week_dates(year, week)
        try:
            week_of_date = update_dict.pop("week_of_date", None) or datetime.date.fromisocalendar(year, week, 1).isoformat()
        except ValueError:
            week_of_date = update_dict.pop("week_of_date", "")
        page = WeeklyPage(
            user_id=user_id,
            year=year,
            week=week,
            week_of_date=week_of_date,
            week_at_a_glance=week_at_a_glance,
        )
        for key, value in update_dict.items():
            setattr(page, key, value)
        await page.insert()
    else:
        for key, value in update_dict.items():
            setattr(page, key, value)
        await page.save()

    return _to_response(page)
