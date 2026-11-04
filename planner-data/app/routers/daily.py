from fastapi import APIRouter, Header

from app.schemas.daily import DailyPageResponse, DailyPageUpdate
from app.services import daily_service

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/{date}", response_model=DailyPageResponse)
async def get_daily_page(
    date: str,
    x_user_id: str = Header(...),
) -> DailyPageResponse:
    return await daily_service.get_or_create(user_id=x_user_id, date=date)


@router.put("/{date}", response_model=DailyPageResponse)
async def update_daily_page(
    date: str,
    body: DailyPageUpdate,
    x_user_id: str = Header(...),
) -> DailyPageResponse:
    return await daily_service.upsert(user_id=x_user_id, date=date, data=body)
