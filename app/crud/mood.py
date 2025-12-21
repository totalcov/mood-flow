from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, date
from app.models.mood import MoodEntry
from app.schemas.mood import MoodCreate, MoodUpdate

def create_mood_entry(db: Session, mood: MoodCreate) -> MoodEntry:
    db_mood = MoodEntry(
        mood_type=mood.mood_type,
        mood_score=mood.mood_score,
        notes=mood.notes,
        date=datetime.now().date()
    )
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

def get_mood_entries(db: Session, skip: int = 0, limit: int = 100, date_filter: Optional[date] = None, mood_type_filter: Optional[str] = None) -> List[MoodEntry]:
    query = db.query(MoodEntry)
    if date_filter: query = query.filter(MoodEntry.date == date_filter)
    if mood_type_filter: query = query.filter(MoodEntry.mood_type == mood_type_filter)
    query = query.order_by(desc(MoodEntry.created_at))
    return query.offset(skip).limit(limit).all()

def get_mood_entry_by_id(db: Session, mood_id: int) -> Optional[MoodEntry]:
    return db.query(MoodEntry).filter(MoodEntry.id == mood_id).first()

def update_mood_entry(db: Session, mood_id: int, mood_update: MoodUpdate) -> Optional[MoodEntry]:
    db_mood = get_mood_entry_by_id(db, mood_id)
    if not db_mood: return None
    update_data = mood_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None: setattr(db_mood, field, value)
    db.commit()
    db.refresh(db_mood)
    return db_mood

def delete_mood_entry(db: Session, mood_id: int) -> bool:
    db_mood = get_mood_entry_by_id(db, mood_id)
    if not db_mood: return False
    db.delete(db_mood)
    db.commit()
    return True

def get_mood_statistics(db: Session, start_date: date, end_date: date) -> dict:
    """
    Получить статистику настроений за период
    """
    entries = db.query(MoodEntry).filter(
        MoodEntry.date.between(start_date, end_date)
    ).all()
    
    if not entries:
        return {
            "average_score": 0, 
            "total_entries": 0, 
            "mood_types": {},
            "entries_data": []  # Добавляем для фронтенда
        }
    
    total_score = sum(entry.mood_score for entry in entries)
    average_score = total_score / len(entries)
    
    mood_types = {}
    for entry in entries:
        mood_types[entry.mood_type] = mood_types.get(entry.mood_type, 0) + 1
    
    # Подготовка данных для фронтенда
    entries_data = [
        {
            "id": entry.id,
            "mood_type": entry.mood_type,
            "mood_score": entry.mood_score,
            "date": entry.date.isoformat() if entry.date else None
        }
        for entry in entries
    ]
    
    return {
        "average_score": round(average_score, 2),
        "total_entries": len(entries),
        "mood_types": mood_types,
        "entries_data": entries_data  # Отправляем на фронтенд
    }