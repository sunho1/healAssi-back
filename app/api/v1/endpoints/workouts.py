from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import workout as schemas
from app.crud import crud_workout
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Workout)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(deps.get_db)):
    return crud_workout.create_workout(db=db, workout=workout)

@router.get("/", response_model=List[schemas.Workout])
def read_workouts(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return crud_workout.get_workouts(db, skip=skip, limit=limit)

@router.get("/{workout_id}", response_model=schemas.Workout)
def read_workout(workout_id: int, db: Session = Depends(deps.get_db)):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@router.put("/{workout_id}", response_model=schemas.Workout)
def update_workout(workout_id: int, workout_in: schemas.WorkoutUpdate, db: Session = Depends(deps.get_db)):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return crud_workout.update_workout(db=db, db_obj=db_workout, workout_in=workout_in)

@router.delete("/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(deps.get_db)):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    crud_workout.delete_workout(db=db, workout_id=workout_id)
    return {"message": "Successfully deleted"}
