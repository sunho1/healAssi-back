import json
from sqlalchemy.orm import Session
from app.models.routine import Routine
from app.schemas.routine import RoutineCreate, RoutineUpdate


def get_routine(db: Session, routine_id: int):
    return db.query(Routine).filter(Routine.id == routine_id).first()


def get_routines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Routine).offset(skip).limit(limit).all()


def create_routine(db: Session, routine: RoutineCreate):
    db_routine = Routine(
        category=routine.category,
        title=routine.title,
        count=routine.count,
        time=routine.time,
        exercises=json.dumps([e.dict() for e in routine.exercises]),
    )
    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)
    return db_routine


def update_routine(db: Session, db_obj: Routine, routine_in: RoutineUpdate):
    update_data = routine_in.dict(exclude_unset=True)
    if "exercises" in update_data:
        update_data["exercises"] = json.dumps([e for e in update_data["exercises"]])
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_routine(db: Session, routine_id: int):
    obj = db.query(Routine).get(routine_id)
    db.delete(obj)
    db.commit()
    return obj
