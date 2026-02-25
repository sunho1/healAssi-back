from pydantic import BaseModel
from typing import List, Optional


class SetDetail(BaseModel):
    sets: str = ""
    reps: str = ""
    weight: str = ""


class Exercise(BaseModel):
    name: str
    body_part: str = ""
    set_details: List[SetDetail] = []
    # 이전 버전 호환 필드 (flat 구조)
    sets: Optional[str] = None
    reps: Optional[str] = None
    weight: Optional[str] = None


class RoutineBase(BaseModel):
    category: str
    title: str
    count: int
    time: str
    exercises: List[Exercise]
    active_days: List[str] = []  # 예: ["월", "수", "금"] 또는 ["매일"]


class RoutineCreate(RoutineBase):
    pass


class RoutineUpdate(RoutineBase):
    pass


class Routine(RoutineBase):
    id: int
    model_config = {"from_attributes": True}
