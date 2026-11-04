from pydantic import BaseModel

from app.models.weekly_page import DayGlance


class WeeklyPageUpdate(BaseModel):
    week_of_date: str | None = None
    study_topic: str | None = None
    educational_goal: str | None = None
    exercise_goal: str | None = None
    career_goal: str | None = None
    other_goals: str | None = None
    week_at_a_glance: list[DayGlance] | None = None


class WeeklyPageResponse(BaseModel):
    user_id: str
    year: int
    week: int
    week_of_date: str
    study_topic: str
    educational_goal: str
    exercise_goal: str
    career_goal: str
    other_goals: str
    week_at_a_glance: list[DayGlance]
