from pydantic import BaseModel


class MealBase(BaseModel):
    type: str
    menu: str
    kcal: int
    time: str


class MealCreate(MealBase):
    pass


class MealUpdate(MealBase):
    pass


class Meal(MealBase):
    id: int
    model_config = {"from_attributes": True}
