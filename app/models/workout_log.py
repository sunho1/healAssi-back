from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class WorkoutLog(Base):
    """날짜별 운동 로그 - 운동 완료 여부 + 실제 운동 내용 저장"""
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(Date, index=True)
    is_done = Column(Boolean, default=False)
    # JSON string: [{body_part, exercises:[{name, set_details:[{weight,reps}]}]}]
    body_parts = Column(String, default="[]")

    # N:1 관계
    user = relationship("User", back_populates="workout_logs")
