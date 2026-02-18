from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# PostgreSQL와 SQLite 모두 지원
if settings.SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    # PostgreSQL 연결
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
else:
    # SQLite (개발환경)
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
