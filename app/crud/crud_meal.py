from sqlalchemy.orm import Session
from app.models.meal import Meal
from app.schemas.meal import MealCreate, MealUpdate


def get_meal(db: Session, meal_id: int):
    return db.query(Meal).filter(Meal.id == meal_id).first()


def get_meals(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Meal)
        .filter(Meal.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_meal(db: Session, meal: MealCreate, user_id: int):
    db_meal = Meal(
        user_id=user_id,
        type=meal.type,
        menu=meal.menu,
        kcal=meal.kcal,
        time=meal.time,
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def update_meal(db: Session, db_obj: Meal, meal_in: MealUpdate):
    update_data = meal_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_meal(db: Session, meal_id: int):
    obj = db.query(Meal).get(meal_id)
    db.delete(obj)
    db.commit()
    return obj
