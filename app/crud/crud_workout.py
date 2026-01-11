from sqlalchemy.orm import Session
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate

def get_workout(db: Session, workout_id: int):
    return db.query(Workout).filter(Workout.id == workout_id).first()

def get_workouts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Workout).offset(skip).limit(limit).all()

def create_workout(db: Session, workout: WorkoutCreate):
    db_workout = Workout(
        name=workout.name,
        date=workout.date,
        sets=workout.sets,
        weight=workout.weight
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

def update_workout(db: Session, db_obj: Workout, workout_in: WorkoutUpdate):
    update_data = workout_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_workout(db: Session, workout_id: int):
    obj = db.query(Workout).get(workout_id)
    db.delete(obj)
    db.commit()
    return obj
