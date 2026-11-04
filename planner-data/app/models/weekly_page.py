import datetime

from pydantic import BaseModel, Field
from beanie import Document
from pymongo import IndexModel


_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _default_week_at_a_glance() -> list["DayGlance"]:
    return [DayGlance(day=d, date="", text="") for d in _DAYS]


class DayGlance(BaseModel):
    day: str   # "Monday" .. "Sunday"
    date: str  # "YYYY-MM-DD"
    text: str = ""


class WeeklyPage(Document):
    user_id: str
    year: int
    week: int              # ISO week number 1–53
    week_of_date: str = "" # ISO date of Monday of that week
    study_topic: str = ""
    educational_goal: str = ""
    exercise_goal: str = ""
    career_goal: str = ""
    other_goals: str = ""
    week_at_a_glance: list[DayGlance] = Field(default_factory=_default_week_at_a_glance)

    class Settings:
        name = "weekly_pages"
        indexes = [
            IndexModel([("user_id", 1), ("year", 1), ("week", 1)], unique=True)
        ]
