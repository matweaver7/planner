from fastapi import APIRouter, Header

from app.schemas.monthly import MonthlyPageResponse, MonthlyPageUpdate
from app.services import monthly_service

router = APIRouter(prefix="/monthly", tags=["monthly"])


@router.get("/{year}/{month}", response_model=MonthlyPageResponse)
async def get_monthly_page(
    year: int,
    month: int,
    x_user_id: str = Header(...),
) -> MonthlyPageResponse:
    return await monthly_service.get_or_create(user_id=x_user_id, year=year, month=month)


@router.put("/{year}/{month}", response_model=MonthlyPageResponse)
async def update_monthly_page(
    year: int,
    month: int,
    body: MonthlyPageUpdate,
    x_user_id: str = Header(...),
) -> MonthlyPageResponse:
    return await monthly_service.upsert(user_id=x_user_id, year=year, month=month, data=body)
