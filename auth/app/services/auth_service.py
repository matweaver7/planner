import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncConnection

from db.token_blocklist import AsyncQuerier as BlocklistQuerier
from db.users import AsyncQuerier as UsersQuerier
from app.config import settings
from app.schemas.token import TokenResponse, ValidateResponse
from app.services.token_service import create_token, decode_token


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt. Used by the accounts service too."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def validate_token(conn: AsyncConnection, token: str) -> ValidateResponse:
    """
    Decode the JWT and check the blocklist.
    Always returns a ValidateResponse — never raises.
    """
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        return ValidateResponse(valid=False, user_id=None)

    jti = payload.get("jti", "")
    blocked = await BlocklistQuerier(conn).is_token_blocked(token_jti=jti)
    if blocked:
        return ValidateResponse(valid=False, user_id=None)

    return ValidateResponse(valid=True, user_id=payload["sub"])


async def logout(conn: AsyncConnection, token: str) -> None:
    """
    Block the token's jti.  Idempotent — works even for expired/invalid tokens
    (we still extract the jti if possible; if decoding fails, nothing to block).
    """
    try:
        payload = decode_token(token)
        jti = payload.get("jti", "")
    except jwt.ExpiredSignatureError:
        # Decode without verifying expiry to grab the jti
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
        jti = payload.get("jti", "")
    except jwt.InvalidTokenError:
        return  # Malformed token — nothing to block

    if jti:
        await BlocklistQuerier(conn).add_to_blocklist(token_jti=jti)


async def login(
    conn: AsyncConnection,
    username: str,
    password: str,
) -> TokenResponse | None:
    """
    Verify credentials and return a TokenResponse on success, None on failure.
    Callers must map None → 401; do not expose which field was wrong.
    """
    user = await UsersQuerier(conn).get_user_by_username(username=username)
    if user is None:
        return None
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None
    token, expires_at = create_token(user.id)
    return TokenResponse(token=token, expires_at=expires_at)
