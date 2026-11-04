"""
Test fixtures for planner-data service.
Uses mongomock-motor for in-memory MongoDB — no live Mongo required.
"""
from collections.abc import AsyncGenerator

import mongomock_motor
import pytest
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.daily_page import DailyPage
from app.models.monthly_page import MonthlyPage
from app.models.weekly_page import WeeklyPage


@pytest.fixture
async def mongo_client():
    """Fresh in-memory MongoDB client per test."""
    client = mongomock_motor.AsyncMongoMockClient()
    await init_beanie(
        database=client.get_database("test"),
        document_models=[DailyPage, WeeklyPage, MonthlyPage],
    )
    yield client
    client.close()


@pytest.fixture
async def client(mongo_client) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client with in-memory MongoDB initialized."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
