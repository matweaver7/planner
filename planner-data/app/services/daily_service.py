from app.models.daily_page import DailyPage
from app.schemas.daily import DailyPageResponse, DailyPageUpdate


def _to_response(page: DailyPage) -> DailyPageResponse:
    return DailyPageResponse(
        user_id=page.user_id,
        date=page.date,
        time_blocks=page.time_blocks,
        notes=page.notes,
        study_topic=page.study_topic,
        exercise_plan=page.exercise_plan,
        goals_for_today=page.goals_for_today,
        to_do_list=page.to_do_list,
    )


async def get_or_create(user_id: str, date: str) -> DailyPageResponse:
    page = await DailyPage.find_one({"user_id": user_id, "date": date})
    if page is None:
        page = DailyPage(user_id=user_id, date=date)
    return _to_response(page)


async def upsert(user_id: str, date: str, data: DailyPageUpdate) -> DailyPageResponse:
    page = await DailyPage.find_one({"user_id": user_id, "date": date})
    update_dict = data.model_dump(exclude_none=True)

    if page is None:
        page = DailyPage(user_id=user_id, date=date)
        for key, value in update_dict.items():
            setattr(page, key, value)
        await page.insert()
    else:
        for key, value in update_dict.items():
            setattr(page, key, value)
        await page.save()

    return _to_response(page)
