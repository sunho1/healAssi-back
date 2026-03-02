from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class SetDetailLog(BaseModel):
    weight: str = ""
    reps: str = ""


class ExerciseItemLog(BaseModel):
    name: str = ""
    set_details: List[SetDetailLog] = []


class BodyPartLog(BaseModel):
    body_part: str = ""
    exercises: List[ExerciseItemLog] = []


class WorkoutLogUpsert(BaseModel):
    """PUT /workout-logs/{date} 요청 바디"""
    is_done: Optional[bool] = None
    body_parts: Optional[List[BodyPartLog]] = None


class WorkoutLogOut(BaseModel):
    """응답 스키마"""
    id: int
    date: date
    is_done: bool
    body_parts: List[BodyPartLog]

    model_config = {"from_attributes": True}
