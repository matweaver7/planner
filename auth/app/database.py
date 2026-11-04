from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.config import settings

_engine: AsyncEngine | None = None


def _make_sa_url(url: str) -> str:
    """Convert asyncpg DSN to SQLAlchemy+asyncpg DSN."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url  # already has +asyncpg prefix


async def init_engine() -> None:
    global _engine
    if _engine is not None:
        return  # already initialised
    if not settings.database_url:
        return  # no URL configured — engine stays None; service errors on first DB use
    _engine = create_async_engine(
        _make_sa_url(settings.database_url),
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_conn() -> AsyncGenerator[AsyncConnection, None]:
    if _engine is None:
        raise RuntimeError(
            "Database engine is not initialised. Ensure DATABASE_URL is set."
        )
    async with _engine.connect() as conn:
        yield conn
