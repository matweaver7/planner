import datetime

from pydantic import BaseModel


class TokenResponse(BaseModel):
    token: str
    expires_at: datetime.datetime


class TokenPayload(BaseModel):
    sub: str   # user_id as string (UUID)
    jti: str   # unique token ID — used for blocklist lookups on logout
    exp: datetime.datetime
    iat: datetime.datetime


class ValidateResponse(BaseModel):
    valid: bool
    user_id: str | None
