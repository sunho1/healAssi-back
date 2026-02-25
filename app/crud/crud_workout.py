from sqlalchemy.orm import Session
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate


def get_workout(db: Session, workout_id: int):
    return db.query(Workout).filter(Workout.id == workout_id).first()


def get_workouts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_workout(db: Session, workout: WorkoutCreate, user_id: int):
    db_workout = Workout(
        user_id=user_id,
        name=workout.name,
        date=workout.date,
        sets=workout.sets,
        weight=workout.weight,
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
