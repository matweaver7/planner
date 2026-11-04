import datetime
import uuid

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class UpdateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class UserResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: str
    created_at: datetime.datetime

    @classmethod
    def from_db(cls, user) -> "UserResponse":  # type: ignore[no-untyped-def]
        return cls(
            user_id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
        )


class DeleteResponse(BaseModel):
    success: bool
