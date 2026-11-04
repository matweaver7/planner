import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.config import settings

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None


def _make_sa_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def init_engine() -> None:
    global _engine
    if _engine is not None:
        return
    if not settings.database_url:
        logger.warning("DATABASE_URL is not set — engine will not be initialised")
        return
    logger.info("Initialising database engine (pool_size=5, max_overflow=10)")
    _engine = create_async_engine(
        _make_sa_url(settings.database_url),
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    logger.info("Database engine initialised")


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        logger.info("Disposing database engine")
        await _engine.dispose()
        _engine = None


async def get_conn() -> AsyncGenerator[AsyncConnection, None]:
    if _engine is None:
        raise RuntimeError(
            "Database engine is not initialised. Ensure DATABASE_URL is set."
        )
    logger.debug("Acquiring database connection from pool")
    async with _engine.connect() as conn:
        logger.debug("Connection acquired — in_transaction=%s", conn.in_transaction())
        try:
            yield conn
            # NOTE: SQLAlchemy connect() starts an implicit transaction that must
            # be committed explicitly; without this the transaction is rolled back
            # on close even when the query succeeds.
            logger.debug(
                "Handler finished — in_transaction=%s, committing",
                conn.in_transaction(),
            )
            await conn.commit()
            logger.debug("Transaction committed successfully")
        except Exception:
            logger.debug("Exception in handler — rolling back transaction")
            await conn.rollback()
            raise
        finally:
            logger.debug("Releasing connection back to pool")
