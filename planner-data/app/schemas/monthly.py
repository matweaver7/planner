from pydantic import BaseModel


class MonthlyPageUpdate(BaseModel):
    study_topic: str | None = None
    educational_goal: str | None = None
    exercise_goal: str | None = None
    career_goal: str | None = None
    other_goals: str | None = None


class MonthlyPageResponse(BaseModel):
    user_id: str
    year: int
    month: int
    study_topic: str
    educational_goal: str
    exercise_goal: str
    career_goal: str
    other_goals: str
