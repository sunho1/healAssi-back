from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Exercise(BaseModel):
    name: str
    sets: str
    reps: str
    weight: str


class RoutineBase(BaseModel):
    category: str
    title: str
    count: int
    time: str
    exercises: List[Exercise]


class RoutineCreate(RoutineBase):
    pass


class RoutineUpdate(RoutineBase):
    pass


class Routine(RoutineBase):
    id: int

    class Config:
        orm_mode = True
