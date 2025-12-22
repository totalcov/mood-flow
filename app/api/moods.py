from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.crud import mood as crud_mood
from app.schemas.mood import MoodCreate, MoodUpdate, MoodResponse

router = APIRouter(prefix="/moods", tags=["moods"])

@router.post("/", response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
def create_mood(mood: MoodCreate, db: Session = Depends(get_db)):
    return crud_mood.create_mood_entry(db=db, mood=mood)

@router.get("/", response_model=List[MoodResponse])
def read_moods(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    date_filter: Optional[date] = Query(None),
    mood_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return crud_mood.get_mood_entries(db=db, skip=skip, limit=limit, date_filter=date_filter, mood_type_filter=mood_type)

@router.get("/{mood_id}", response_model=MoodResponse)
def read_mood(mood_id: int, db: Session = Depends(get_db)):
    db_mood = crud_mood.get_mood_entry_by_id(db=db, mood_id=mood_id)
    if not db_mood: raise HTTPException(404, detail="Not found")
    return db_mood

@router.put("/{mood_id}", response_model=MoodResponse)
def update_mood(mood_id: int, mood_update: MoodUpdate, db: Session = Depends(get_db)):
    db_mood = crud_mood.update_mood_entry(db=db, mood_id=mood_id, mood_update=mood_update)
    if not db_mood: raise HTTPException(404, detail="Not found")
    return db_mood

@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood(mood_id: int, db: Session = Depends(get_db)):
    if not crud_mood.delete_mood_entry(db=db, mood_id=mood_id):
        raise HTTPException(404, detail="Not found")
    
# В app/api/moods.py добавить:
@router.get("/statistics/", response_model=dict)
def get_statistics(
    start_date: date = Query(..., description="Начальная дата (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конечная дата (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Получить статистику настроений за период
    
    - **start_date**: Начало периода
    - **end_date**: Конец периода
    """
    return crud_mood.get_mood_statistics(db, start_date, end_date)



# Добавим новый эндпоинт после статистики

@router.get("/calendar/", response_model=dict)
def get_mood_calendar(
    year: int = Query(None, description="Год (например, 2023)"),
    month: int = Query(None, description="Месяц (1-12)"),
    db: Session = Depends(get_db)
):
    """
    Получить данные для календаря настроений (доски)
    
    Возвращает структуру для визуализации Heatmap.
    Каждый день содержит оценку, тип настроения и цвет.
    """
    return crud_mood.get_mood_calendar_data(db, year, month)