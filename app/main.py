from fastapi import FastAPI
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
