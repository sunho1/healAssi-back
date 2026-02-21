from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    category = Column(String, index=True)
    title = Column(String, index=True)
    count = Column(Integer)
    time = Column(String)
    exercises = Column(String)  # JSON string

    # N:1 관계
    user = relationship("User", back_populates="routines")
