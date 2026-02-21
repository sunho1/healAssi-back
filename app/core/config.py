from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra='ignore')
    
    PROJECT_NAME: str = "HealAssi API"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./health.db"
    )
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://healassi-web.vercel.app",  # 웹 배포 URL 추가
    ]

settings = Settings()
