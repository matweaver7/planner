from beanie import Document
from pymongo import IndexModel


class MonthlyPage(Document):
    user_id: str
    year: int
    month: int  # 1–12
    study_topic: str = ""
    educational_goal: str = ""
    exercise_goal: str = ""
    career_goal: str = ""
    other_goals: str = ""

    class Settings:
        name = "monthly_pages"
        indexes = [
            IndexModel([("user_id", 1), ("year", 1), ("month", 1)], unique=True)
        ]
