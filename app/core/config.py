from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra='ignore')

    # 데이터베이스 설정 - Railway의 DATABASE_URL을 사용하거나 로컬 SQLite 사용
    DATABASE_URL: str = "sqlite:///./health.db"
    PROJECT_NAME: str = "HealAssi API"
    API_V1_STR: str = "/api/v1"

    # Railway는 postgres:// 를 제공하지만 SQLAlchemy는 postgresql:// 필요
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        db_url = self.DATABASE_URL
        # Railway의 postgres:// 프로토콜을 postgresql://로 변경
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://healassi-web.vercel.app",
        "https://heal-assistant.vercel.app",  # Vercel 배포 프론트엔드
    ]

    # JWT 설정
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

settings = Settings()
