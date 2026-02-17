from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    title = Column(String, index=True)
    count = Column(Integer)
    time = Column(String)
    exercises = Column(String)  # JSON string
