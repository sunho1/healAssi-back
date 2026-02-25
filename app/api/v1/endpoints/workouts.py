from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import workout as schemas
from app.crud import crud_workout
from app.api import deps
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=schemas.Workout)
def create_workout(
    workout: schemas.WorkoutCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_workout.create_workout(db=db, workout=workout, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Workout])
def read_workouts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_workout.get_workouts(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{workout_id}", response_model=schemas.Workout)
def read_workout(
    workout_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if db_workout is None or db_workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout


@router.put("/{workout_id}", response_model=schemas.Workout)
def update_workout(
    workout_id: int,
    workout_in: schemas.WorkoutUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if not db_workout or db_workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    return crud_workout.update_workout(db=db, db_obj=db_workout, workout_in=workout_in)


@router.delete("/{workout_id}")
def delete_workout(
    workout_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if not db_workout or db_workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    crud_workout.delete_workout(db=db, workout_id=workout_id)
    return {"message": "Successfully deleted"}
