import json
from sqlalchemy.orm import Session
from datetime import date

from app.models.workout_log import WorkoutLog
from app.schemas.workout_log import WorkoutLogUpsert


def serialize(db_log: WorkoutLog) -> dict:
    """ORM 객체 → API 응답 딕셔너리 변환 (body_parts JSON 파싱)"""
    return {
        "id": db_log.id,
        "date": db_log.date,
        "is_done": db_log.is_done,
        "body_parts": json.loads(db_log.body_parts or "[]"),
    }


def get_workout_logs(db: Session, user_id: int, skip: int = 0, limit: int = 1000):
    return (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_workout_log_by_date(db: Session, user_id: int, log_date: date):
    return (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user_id, WorkoutLog.date == log_date)
        .first()
    )


def upsert_workout_log(db: Session, user_id: int, log_date: date, data: WorkoutLogUpsert):
    """해당 날짜 로그가 없으면 생성, 있으면 업데이트 (upsert)"""
    db_log = get_workout_log_by_date(db, user_id, log_date)

    if db_log is None:
        db_log = WorkoutLog(
            user_id=user_id,
            date=log_date,
            is_done=data.is_done if data.is_done is not None else False,
            body_parts=json.dumps(
                [bp.model_dump() for bp in data.body_parts],
                ensure_ascii=False,
            ) if data.body_parts is not None else "[]",
        )
        db.add(db_log)
    else:
        if data.is_done is not None:
            db_log.is_done = data.is_done
        if data.body_parts is not None:
            db_log.body_parts = json.dumps(
                [bp.model_dump() for bp in data.body_parts],
                ensure_ascii=False,
            )

    db.commit()
    db.refresh(db_log)
    return db_log
