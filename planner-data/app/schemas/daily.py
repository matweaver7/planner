from pydantic import BaseModel

from app.models.daily_page import TimeBlock


class DailyPageUpdate(BaseModel):
    time_blocks: list[TimeBlock] | None = None
    notes: str | None = None
    study_topic: str | None = None
    exercise_plan: str | None = None
    goals_for_today: str | None = None
    to_do_list: str | None = None


class DailyPageResponse(BaseModel):
    user_id: str
    date: str
    time_blocks: list[TimeBlock]
    notes: str
    study_topic: str
    exercise_plan: str
    goals_for_today: str
    to_do_list: str
