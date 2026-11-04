from fastapi import APIRouter, Depends, Request, Response

from app.config import settings
from app.middleware.auth_middleware import require_auth
from app.services.proxy_service import forward

router = APIRouter(prefix="/api/planner", tags=["planner"])


@router.get("/daily/{date}")
async def get_daily(
    date: str,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        f"{settings.planner_data_service_url}/daily/{date}",
        extra_headers={"X-User-ID": user_id},
    )


@router.put("/daily/{date}")
async def put_daily(
    date: str,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        f"{settings.planner_data_service_url}/daily/{date}",
        extra_headers={"X-User-ID": user_id},
    )


@router.get("/weekly/{year}/{week}")
async def get_weekly(
    year: int,
    week: int,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        f"{settings.planner_data_service_url}/weekly/{year}/{week}",
        extra_headers={"X-User-ID": user_id},
    )


@router.put("/weekly/{year}/{week}")
async def put_weekly(
    year: int,
    week: int,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        f"{settings.planner_data_service_url}/weekly/{year}/{week}",
        extra_headers={"X-User-ID": user_id},
    )


@router.get("/monthly/{year}/{month}")
async def get_monthly(
    year: int,
    month: int,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        f"{settings.planner_data_service_url}/monthly/{year}/{month}",
        extra_headers={"X-User-ID": user_id},
    )


@router.put("/monthly/{year}/{month}")
async def put_monthly(
    year: int,
    month: int,
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(
        request,
        f"{settings.planner_data_service_url}/monthly/{year}/{month}",
        extra_headers={"X-User-ID": user_id},
    )
