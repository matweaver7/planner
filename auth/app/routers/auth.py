from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import get_conn
from app.schemas.auth import LoginRequest, LogoutRequest, LogoutResponse, ValidateRequest
from app.schemas.token import TokenResponse, ValidateResponse
from app.services.auth_service import login, logout, validate_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    body: LoginRequest,
    conn: AsyncConnection = Depends(get_conn),
) -> TokenResponse:
    result = await login(conn, body.username, body.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return result


@router.post("/validate", response_model=ValidateResponse)
async def validate_endpoint(
    body: ValidateRequest,
    conn: AsyncConnection = Depends(get_conn),
) -> ValidateResponse:
    return await validate_token(conn, body.token)


@router.post("/logout", response_model=LogoutResponse)
async def logout_endpoint(
    body: LogoutRequest,
    conn: AsyncConnection = Depends(get_conn),
) -> LogoutResponse:
    await logout(conn, body.token)
    return LogoutResponse(success=True)
