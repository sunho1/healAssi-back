from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints import workouts, diets, routines, auth
from app.models.user import User
from app.models.meal import Meal
from app.models.workout import Workout
from app.models.routine import Routine

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://healassi-web.vercel.app",
        "https://heal-assistant.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(workouts.router, prefix=f"{settings.API_V1_STR}/workouts", tags=["workouts"])
app.include_router(diets.router, prefix=f"{settings.API_V1_STR}/meals", tags=["meals"])
app.include_router(routines.router, prefix=f"{settings.API_V1_STR}/routines", tags=["routines"])

@app.get("/")
def root():
    return {"message": "Welcome to HealAssi API (Layered Architecture)"}

@app.get("/api/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
