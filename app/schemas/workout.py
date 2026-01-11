from pydantic import BaseModel
from datetime import date

class WorkoutBase(BaseModel):
    name: str
    date: date
    sets: int
    weight: int

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: int

    class Config:
        orm_mode = True
