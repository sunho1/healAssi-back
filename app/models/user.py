from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    username = Column(String, index=True)

    # 1:N 관계
    meals = relationship("Meal", back_populates="user")
    workouts = relationship("Workout", back_populates="user")
    routines = relationship("Routine", back_populates="user")
