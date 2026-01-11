from sqlalchemy import Column, Integer, String, Date
from app.db.base import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date)
    sets = Column(Integer)
    weight = Column(Integer)
