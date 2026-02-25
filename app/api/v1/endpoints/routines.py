import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import routine as schemas
from app.crud import crud_routine
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Routine)
def create_routine(routine: schemas.RoutineCreate, db: Session = Depends(deps.get_db)):
    return crud_routine.create_routine(db=db, routine=routine)


@router.get("/", response_model=List[schemas.Routine])
def read_routines(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    routines = crud_routine.get_routines(db, skip=skip, limit=limit)
    # convert exercises JSON string to list
    for r in routines:
        try:
            r.exercises = json.loads(r.exercises) if r.exercises else []
        except Exception:
            r.exercises = []
    return routines


@router.get("/{routine_id}", response_model=schemas.Routine)
def read_routine(routine_id: int, db: Session = Depends(deps.get_db)):
    db_routine = crud_routine.get_routine(db, routine_id=routine_id)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Routine not found")
    try:
        db_routine.exercises = json.loads(db_routine.exercises) if db_routine.exercises else []
    except Exception:
        db_routine.exercises = []
    return db_routine


@router.put("/{routine_id}", response_model=schemas.Routine)
def update_routine(routine_id: int, routine: schemas.RoutineUpdate, db: Session = Depends(deps.get_db)):
    db_routine = crud_routine.get_routine(db, routine_id=routine_id)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Routine not found")
    updated = crud_routine.update_routine(db=db, db_obj=db_routine, routine_in=routine)
    try:
        updated.exercises = json.loads(updated.exercises) if updated.exercises else []
    except Exception:
        updated.exercises = []
    return updated


@router.delete("/{routine_id}")
def delete_routine(routine_id: int, db: Session = Depends(deps.get_db)):
    db_routine = crud_routine.get_routine(db, routine_id=routine_id)
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    crud_routine.delete_routine(db=db, routine_id=routine_id)
    return {"message": "Successfully deleted"}
