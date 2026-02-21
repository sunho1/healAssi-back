from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    type = Column(String, index=True)
    menu = Column(String)
    kcal = Column(Integer)
    time = Column(String)

    # N:1 관계
    user = relationship("User", back_populates="meals")
