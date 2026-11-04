from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

_client: AsyncIOMotorClient | None = None  # type: ignore[type-arg]


async def connect() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_url)
    from app.models.daily_page import DailyPage
    from app.models.monthly_page import MonthlyPage
    from app.models.weekly_page import WeeklyPage
    await init_beanie(
        database=_client[settings.mongodb_db_name],
        document_models=[DailyPage, WeeklyPage, MonthlyPage],
    )


async def disconnect() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
