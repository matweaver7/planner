"""
Test configuration for the accounts service.

Requires a running PostgreSQL instance with the auth schema applied.
Configure via env vars:
  TEST_DATABASE_URL  (default: postgresql://planner:planner@localhost:5432/planner_auth)

The accounts service shares the database with auth (same schema, no own migrations).
Run auth migrations first:
  cd ../auth && alembic upgrade head
"""
import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.database import get_conn
from app.main import app

_RAW_URL: str = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://planner:planner@localhost:5432/planner_auth",
)
_TEST_SA_URL: str = (
    _RAW_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    if _RAW_URL.startswith("postgresql://")
    else _RAW_URL
)


@pytest.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(_TEST_SA_URL)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_conn(test_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with test_engine.connect() as conn:
        yield conn
        await conn.rollback()


@pytest.fixture
async def client(db_conn: AsyncConnection) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_conn() -> AsyncGenerator[AsyncConnection, None]:
        yield db_conn

    app.dependency_overrides[get_conn] = _override_get_conn
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
