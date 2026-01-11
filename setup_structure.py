import os

# 프로젝트 구조 및 파일 내용 정의
structure = {
    "requirements.txt": """fastapi
uvicorn
sqlalchemy
pydantic
""",
    "app/__init__.py": "",
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints import workouts

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(workouts.router, prefix=f"{settings.API_V1_STR}/workouts", tags=["workouts"])

@app.get("/")
def root():
    return {"message": "Welcome to HealAssi API (Layered Architecture)"}
""",
    "app/core/__init__.py": "",
    "app/core/config.py": """class Settings:
    PROJECT_NAME: str = "HealAssi API"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./health.db"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

settings = Settings()
""",
    "app/db/__init__.py": "",
    "app/db/base.py": """from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
""",
    "app/db/session.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
""",
    "app/models/__init__.py": "",
    "app/models/workout.py": """from sqlalchemy import Column, Integer, String, Date
from app.db.base import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date)
    sets = Column(Integer)
    weight = Column(Integer)
""",
    "app/schemas/__init__.py": "",
    "app/schemas/workout.py": """from pydantic import BaseModel
from datetime import date

class WorkoutBase(BaseModel):
    name: str
    date: date
    sets: int
    weight: int

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: int

    class Config:
        orm_mode = True
""",
    "app/crud/__init__.py": "",
    "app/crud/crud_workout.py": """from sqlalchemy.orm import Session
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate

def get_workout(db: Session, workout_id: int):
    return db.query(Workout).filter(Workout.id == workout_id).first()

def get_workouts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Workout).offset(skip).limit(limit).all()

def create_workout(db: Session, workout: WorkoutCreate):
    db_workout = Workout(
        name=workout.name,
        date=workout.date,
        sets=workout.sets,
        weight=workout.weight
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

def update_workout(db: Session, db_obj: Workout, workout_in: WorkoutUpdate):
    update_data = workout_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_workout(db: Session, workout_id: int):
    obj = db.query(Workout).get(workout_id)
    db.delete(obj)
    db.commit()
    return obj
""",
    "app/api/__init__.py": "",
    "app/api/deps.py": """from typing import Generator
from app.db.session import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "app/api/v1/__init__.py": "",
    "app/api/v1/endpoints/__init__.py": "",
    "app/api/v1/endpoints/workouts.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import workout as schemas
from app.crud import crud_workout
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Workout)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(deps.get_db)):
    return crud_workout.create_workout(db=db, workout=workout)

@router.get("/", response_model=List[schemas.Workout])
def read_workouts(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return crud_workout.get_workouts(db, skip=skip, limit=limit)

@router.get("/{workout_id}", response_model=schemas.Workout)
def read_workout(workout_id: int, db: Session = Depends(deps.get_db)):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@router.put("/{workout_id}", response_model=schemas.Workout)
def update_workout(workout_id: int, workout_in: schemas.WorkoutUpdate, db: Session = Depends(deps.get_db)):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return crud_workout.update_workout(db=db, db_obj=db_workout, workout_in=workout_in)

@router.delete("/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(deps.get_db)):
    db_workout = crud_workout.get_workout(db, workout_id=workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    crud_workout.delete_workout(db=db, workout_id=workout_id)
    return {"message": "Successfully deleted"}
"""
}

def create_project_structure():
    print("🚀 프로젝트 구조 생성 시작...")
    for filepath, content in structure.items():
        # 디렉토리 생성
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # 파일 쓰기
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 생성됨: {filepath}")
    
    print("\n🎉 모든 파일이 성공적으로 생성되었습니다!")
    print("이제 아래 명령어로 서버를 실행하세요:")
    print("uvicorn app.main:app --reload")

if __name__ == "__main__":
    create_project_structure()