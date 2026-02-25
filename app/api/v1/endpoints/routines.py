import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import routine as schemas
from app.crud import crud_routine
from app.api import deps
from app.models.user import User

router = APIRouter()


def _parse_routine(r):
    """운동 목록과 요일 데이터를 JSON 문자열에서 리스트로 변환"""
    try:
        r.exercises = json.loads(r.exercises) if r.exercises else []
    except Exception:
        r.exercises = []
    try:
        r.active_days = json.loads(r.active_days) if r.active_days else []
    except Exception:
        r.active_days = []
    return r


@router.post("/", response_model=schemas.Routine)
def create_routine(
    routine: schemas.RoutineCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_routine = crud_routine.create_routine(db=db, routine=routine, user_id=current_user.id)
    return _parse_routine(db_routine)


@router.get("/", response_model=List[schemas.Routine])
def read_routines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    routines = crud_routine.get_routines(db, user_id=current_user.id, skip=skip, limit=limit)
    return [_parse_routine(r) for r in routines]


@router.get("/{routine_id}", response_model=schemas.Routine)
def read_routine(
    routine_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_routine = crud_routine.get_routine(db, routine_id=routine_id)
    if db_routine is None or db_routine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Routine not found")
    return _parse_routine(db_routine)


@router.put("/{routine_id}", response_model=schemas.Routine)
def update_routine(
    routine_id: int,
    routine: schemas.RoutineUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_routine = crud_routine.get_routine(db, routine_id=routine_id)
    if db_routine is None or db_routine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Routine not found")
    updated = crud_routine.update_routine(db=db, db_obj=db_routine, routine_in=routine)
    return _parse_routine(updated)


@router.delete("/{routine_id}")
def delete_routine(
    routine_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_routine = crud_routine.get_routine(db, routine_id=routine_id)
    if not db_routine or db_routine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Routine not found")
    crud_routine.delete_routine(db=db, routine_id=routine_id)
    return {"message": "Successfully deleted"}
