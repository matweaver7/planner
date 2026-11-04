from pydantic import BaseModel, Field
from beanie import Document
from pymongo import IndexModel


def _default_time_blocks() -> list["TimeBlock"]:
    """Generate 29 half-hour slots from 07:00 to 21:00 inclusive."""
    slots = []
    for half_hours in range(7 * 2, 21 * 2 + 1):  # 14..42 = 29 values
        total_minutes = half_hours * 30
        h, m = divmod(total_minutes, 60)
        slots.append(TimeBlock(time=f"{h:02d}:{m:02d}", text=""))
    return slots


class TimeBlock(BaseModel):
    time: str  # "HH:MM"
    text: str = ""


class DailyPage(Document):
    user_id: str
    date: str  # "YYYY-MM-DD"
    time_blocks: list[TimeBlock] = Field(default_factory=_default_time_blocks)
    notes: str = ""
    study_topic: str = ""
    exercise_plan: str = ""
    goals_for_today: str = ""
    to_do_list: str = ""

    class Settings:
        name = "daily_pages"
        indexes = [
            IndexModel([("user_id", 1), ("date", 1)], unique=True)
        ]
