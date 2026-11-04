import datetime
import uuid
from typing import Any

import jwt

from app.config import settings


def create_token(user_id: uuid.UUID) -> tuple[str, datetime.datetime]:
    """
    Issue a signed JWT for user_id.
    Returns (encoded_token, expires_at).

    Claims:
      sub  — user UUID as string
      jti  — UUID4, unique per token (used for blocklist on logout)
      iat  — issued-at timestamp
      exp  — expiry timestamp (configurable via JWT_EXPIRY_HOURS)
    """
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    expires_at = now + datetime.timedelta(hours=settings.jwt_expiry_hours)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT.

    Raises:
      jwt.ExpiredSignatureError  — token has passed its exp claim
      jwt.InvalidTokenError      — bad signature, malformed token, etc.
    """
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
