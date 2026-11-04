import uuid

from fastapi import APIRouter, Depends, Request, Response

from app.config import settings
from app.middleware.auth_middleware import require_auth
from app.services.proxy_service import forward

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("/register")
async def register(request: Request) -> Response:
    return await forward(request, f"{settings.accounts_service_url}/register")


@router.get("/users/{user_id}")
async def get_user(
    request: Request,
    user_id: uuid.UUID,
    _auth: str = Depends(require_auth),
) -> Response:
    return await forward(request, f"{settings.accounts_service_url}/users/{user_id}")


@router.put("/users/{user_id}")
async def update_user(
    request: Request,
    user_id: uuid.UUID,
    _auth: str = Depends(require_auth),
) -> Response:
    return await forward(request, f"{settings.accounts_service_url}/users/{user_id}")


@router.delete("/users/{user_id}")
async def delete_user(
    request: Request,
    user_id: uuid.UUID,
    _auth: str = Depends(require_auth),
) -> Response:
    return await forward(request, f"{settings.accounts_service_url}/users/{user_id}")
