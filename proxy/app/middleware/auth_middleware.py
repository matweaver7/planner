"""
Auth middleware: FastAPI Depends() that validates the Bearer token with the
auth service and returns the resolved user_id.
"""
import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """
    Extract Bearer token, validate with auth service, return user_id.
    Raises 401 on missing/invalid/expired token.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.auth_service_url}/validate",
                json={"token": token},
                timeout=5.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Auth service unavailable",
            )

    if not data.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return data["user_id"]
