from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import meal as schemas
from app.crud import crud_meal
from app.api import deps
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=schemas.Meal)
def create_meal(
    meal: schemas.MealCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_meal.create_meal(db=db, meal=meal, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Meal])
def read_meals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_meal.get_meals(db, user_id=current_user.id, skip=skip, limit=limit)


@router.delete("/{meal_id}")
def delete_meal(
    meal_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_meal = crud_meal.get_meal(db, meal_id=meal_id)
    if not db_meal or db_meal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meal not found")
    crud_meal.delete_meal(db=db, meal_id=meal_id)
    return {"message": "Successfully deleted"}
