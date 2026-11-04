"""
Proxy test fixtures.
Internal service calls are intercepted by respx — no live services needed.
"""
import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

FAKE_USER_ID = str(uuid.uuid4())
VALID_TOKEN = "valid.test.token"
INVALID_TOKEN = "invalid.test.token"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
