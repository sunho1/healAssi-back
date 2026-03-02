from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class User(Base):
    """유저 모델 - 회원 정보 저장"""
    __tablename__ = "users"

    # 기본 정보
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # 이메일 (로그인 아이디)
    username = Column(String, index=True, nullable=False)  # 사용자 이름
    password_hash = Column(String, nullable=False)  # 해시된 비밀번호
    
    # 계정 상태
    is_active = Column(Boolean, default=True)  # 활성화 여부
    is_verified = Column(Boolean, default=False)  # 이메일 인증 여부
    
    # 타임스탐프
    created_at = Column(DateTime, default=datetime.utcnow)  # 가입일
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 수정일
    last_login = Column(DateTime, nullable=True)  # 마지막 로그인 시간

    # 1:N 관계
    meals = relationship("Meal", back_populates="user")
    workouts = relationship("Workout", back_populates="user")
    routines = relationship("Routine", back_populates="user")
    workout_logs = relationship("WorkoutLog", back_populates="user")

