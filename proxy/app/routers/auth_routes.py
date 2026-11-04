from fastapi import APIRouter, Depends, Request, Response

from app.config import settings
from app.middleware.auth_middleware import require_auth
from app.services.proxy_service import forward

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(request: Request) -> Response:
    return await forward(request, f"{settings.auth_service_url}/login")


@router.post("/validate")
async def validate(request: Request) -> Response:
    return await forward(request, f"{settings.auth_service_url}/validate")


@router.post("/logout")
async def logout(
    request: Request,
    user_id: str = Depends(require_auth),
) -> Response:
    return await forward(request, f"{settings.auth_service_url}/logout")
