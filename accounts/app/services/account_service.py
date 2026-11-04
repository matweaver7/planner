import logging

import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

from db.users import AsyncQuerier

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def register_user(
    conn: AsyncConnection,
    username: str,
    email: str,
    password: str,
):
    """
    Create a new user. Returns the created User dataclass on success,
    None on unique constraint violation (caller raises 409).
    """
    logger.info("register_user called: username=%r email=%r", username, email)
    pw_hash = hash_password(password)
    logger.debug("Password hashed, executing INSERT")
    try:
        user = await AsyncQuerier(conn).create_user(
            username=username,
            email=email,
            password_hash=pw_hash,
        )
        if user is None:
            logger.warning(
                "create_user returned None for username=%r — INSERT returned no row",
                username,
            )
        else:
            logger.info(
                "create_user succeeded: user_id=%s username=%r — "
                "row is in the current transaction but NOT yet committed",
                user.id,
                user.username,
            )
        return user
    except IntegrityError as exc:
        logger.info(
            "IntegrityError for username=%r email=%r — duplicate constraint: %s",
            username,
            email,
            exc.orig,
        )
        return None
    except Exception:
        logger.exception("Unexpected error in register_user for username=%r", username)
        raise


async def get_user(conn: AsyncConnection, user_id):
    """Return User dataclass or None if not found."""
    import uuid
    uid = uuid.UUID(str(user_id))
    return await AsyncQuerier(conn).get_user_by_id(id=uid)


async def update_user(
    conn: AsyncConnection,
    user_id,
    *,
    email: str | None = None,
    password: str | None = None,
):
    """
    Update email and/or password. Returns updated User on success,
    None if user not found, raises IntegrityError on duplicate email.
    """
    import uuid
    uid = uuid.UUID(str(user_id))
    querier = AsyncQuerier(conn)

    # Check existence first so we can return None (not found) vs raise (conflict)
    user = await querier.get_user_by_id(id=uid)
    if user is None:
        return None

    if password is not None:
        await querier.update_user_password(id=uid, password_hash=hash_password(password))

    if email is not None:
        try:
            user = await querier.update_user_email(id=uid, email=email)
        except IntegrityError:
            raise  # caller maps to 409

    if email is None:
        # Re-fetch to get fresh updated_at if only password changed
        user = await querier.get_user_by_id(id=uid)

    return user


async def delete_user(conn: AsyncConnection, user_id) -> bool:
    """Delete user. Returns True if deleted, False if not found."""
    import uuid
    uid = uuid.UUID(str(user_id))
    querier = AsyncQuerier(conn)
    user = await querier.get_user_by_id(id=uid)
    if user is None:
        return False
    await querier.delete_user(id=uid)
    return True
