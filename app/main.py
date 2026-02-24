from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints import workouts, diets, routines, auth
from app.models.user import User
from app.models.meal import Meal
from app.models.workout import Workout
from app.models.routine import Routine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB 테이블 생성
try:
    logger.info(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URL[:20]}...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")
    raise

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Health Assistant API",
    version="1.0.0"
)

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

# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    logger.info("Starting HealAssi API...")
    logger.info(f"Environment: DATABASE_URL configured")
    logger.info(f"CORS origins: {settings.BACKEND_CORS_ORIGINS}")

@app.get("/")
def root():
    return {
        "message": "Welcome to HealAssi API (Layered Architecture)",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 테스트
        from app.db.session import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
