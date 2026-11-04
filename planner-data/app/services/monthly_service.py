from app.models.monthly_page import MonthlyPage
from app.schemas.monthly import MonthlyPageResponse, MonthlyPageUpdate


def _to_response(page: MonthlyPage) -> MonthlyPageResponse:
    return MonthlyPageResponse(
        user_id=page.user_id,
        year=page.year,
        month=page.month,
        study_topic=page.study_topic,
        educational_goal=page.educational_goal,
        exercise_goal=page.exercise_goal,
        career_goal=page.career_goal,
        other_goals=page.other_goals,
    )


async def get_or_create(user_id: str, year: int, month: int) -> MonthlyPageResponse:
    page = await MonthlyPage.find_one({"user_id": user_id, "year": year, "month": month})
    if page is None:
        page = MonthlyPage(user_id=user_id, year=year, month=month)
    return _to_response(page)


async def upsert(user_id: str, year: int, month: int, data: MonthlyPageUpdate) -> MonthlyPageResponse:
    page = await MonthlyPage.find_one({"user_id": user_id, "year": year, "month": month})
    update_dict = data.model_dump(exclude_none=True)

    if page is None:
        page = MonthlyPage(user_id=user_id, year=year, month=month)
        for key, value in update_dict.items():
            setattr(page, key, value)
        await page.insert()
    else:
        for key, value in update_dict.items():
            setattr(page, key, value)
        await page.save()

    return _to_response(page)
