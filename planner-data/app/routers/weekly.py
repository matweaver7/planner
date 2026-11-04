from fastapi import APIRouter, Header

from app.schemas.weekly import WeeklyPageResponse, WeeklyPageUpdate
from app.services import weekly_service

router = APIRouter(prefix="/weekly", tags=["weekly"])


@router.get("/{year}/{week}", response_model=WeeklyPageResponse)
async def get_weekly_page(
    year: int,
    week: int,
    x_user_id: str = Header(...),
) -> WeeklyPageResponse:
    return await weekly_service.get_or_create(user_id=x_user_id, year=year, week=week)


@router.put("/{year}/{week}", response_model=WeeklyPageResponse)
async def update_weekly_page(
    year: int,
    week: int,
    body: WeeklyPageUpdate,
    x_user_id: str = Header(...),
) -> WeeklyPageResponse:
    return await weekly_service.upsert(user_id=x_user_id, year=year, week=week, data=body)
