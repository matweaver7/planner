import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import get_conn
from app.schemas.account import DeleteResponse, RegisterRequest, UpdateRequest, UserResponse
from app.services.account_service import delete_user, get_user, register_user, update_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["accounts"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    conn: AsyncConnection = Depends(get_conn),
) -> UserResponse:
    logger.info("POST /register — username=%r email=%r", body.username, body.email)
    user = await register_user(conn, body.username, body.email, body.password)
    if user is None:
        logger.info(
            "POST /register — 409 Conflict for username=%r email=%r",
            body.username,
            body.email,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    logger.info("POST /register — 201 Created user_id=%s", user.id)
    return UserResponse.from_db(user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: uuid.UUID,
    conn: AsyncConnection = Depends(get_conn),
) -> UserResponse:
    user = await get_user(conn, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_db(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: uuid.UUID,
    body: UpdateRequest,
    conn: AsyncConnection = Depends(get_conn),
) -> UserResponse:
    try:
        user = await update_user(
            conn,
            user_id,
            email=body.email,
            password=body.password,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already in use",
        )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_db(user)


@router.delete("/users/{user_id}", response_model=DeleteResponse)
async def delete_user_endpoint(
    user_id: uuid.UUID,
    conn: AsyncConnection = Depends(get_conn),
) -> DeleteResponse:
    found = await delete_user(conn, user_id)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return DeleteResponse(success=True)
