from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.schemas.workout_log import WorkoutLogOut, WorkoutLogUpsert
from app.crud import crud_workout_log
from app.api import deps
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[WorkoutLogOut])
def read_workout_logs(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """유저의 모든 날짜별 운동 로그 조회"""
    logs = crud_workout_log.get_workout_logs(db, user_id=current_user.id)
    return [crud_workout_log.serialize(log) for log in logs]


@router.get("/{log_date}", response_model=WorkoutLogOut)
def read_workout_log(
    log_date: date,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """특정 날짜의 운동 로그 조회"""
    log = crud_workout_log.get_workout_log_by_date(db, user_id=current_user.id, log_date=log_date)
    if log is None:
        raise HTTPException(status_code=404, detail="Workout log not found")
    return crud_workout_log.serialize(log)


@router.put("/{log_date}", response_model=WorkoutLogOut)
def upsert_workout_log(
    log_date: date,
    data: WorkoutLogUpsert,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """특정 날짜의 운동 로그 저장/수정 (upsert)
    - is_done: 완료 여부 변경
    - body_parts: 운동 내용 변경
    둘 중 하나만 보내도 동작
    """
    log = crud_workout_log.upsert_workout_log(
        db=db, user_id=current_user.id, log_date=log_date, data=data
    )
    return crud_workout_log.serialize(log)
