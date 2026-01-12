# app/crud/mood.py - БЕЗ date_only
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, date
from app.models.mood import MoodEntry
from app.schemas.mood import MoodCreate, MoodUpdate

def create_mood_entry(db: Session, mood: MoodCreate) -> MoodEntry:
    from datetime import datetime, timezone, timedelta
    
    # UTC время
    now_utc = datetime.now(timezone.utc)
    # Добавляем 3 часа
    now_local = now_utc + timedelta(hours=3)
    
    db_mood = MoodEntry(
        mood_type=mood.mood_type,
        mood_score=mood.mood_score,
        notes=mood.notes,
        date=now_local,  # ← Уже с поправкой
        created_at=now_local
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
    entries = db.query(MoodEntry).filter(
        MoodEntry.date.between(start_date, end_date)
    ).all()
    
    if not entries:
        return {
            "average_score": 0, 
            "total_entries": 0, 
            "mood_types": {},
            "entries_data": []
        }
    
    total_score = sum(entry.mood_score for entry in entries)
    average_score = total_score / len(entries)
    
    mood_types = {}
    for entry in entries:
        mood_types[entry.mood_type] = mood_types.get(entry.mood_type, 0) + 1
    
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
        "entries_data": entries_data
    }
from datetime import timedelta


def get_mood_calendar_data(db: Session, year: int = None, month: int = None) -> dict:
    from datetime import datetime, date
    from collections import defaultdict
    
    now = datetime.now()
    target_year = year or now.year
    target_month = month or now.month
    
    start_date = date(target_year, target_month, 1)
    
    if target_month == 12:
        end_date = date(target_year + 1, 1, 1)
    else:
        end_date = date(target_year, target_month + 1, 1)
    
    # Получаем все записи за месяц
    entries = db.query(MoodEntry).filter(
        MoodEntry.date >= start_date,
        MoodEntry.date < end_date
    ).order_by(MoodEntry.created_at).all()
    
    # Группируем по дням
    daily_entries = defaultdict(list)
    for entry in entries:
        # Получаем дату как строку (обрабатываем и Date и DateTime)
        day_str = entry.date.isoformat()
        
        daily_entries[day_str].append({
            "score": entry.mood_score,
            "type": entry.mood_type,
            "notes": entry.notes,
            "created_at": entry.created_at
        })
    
    # Создаем календарь на весь месяц
    calendar_data = {}
    current_date = start_date
    
    while current_date < end_date:
        day_str = current_date.isoformat()
        
        if day_str in daily_entries:
            entries_list = daily_entries[day_str]
            entries_count = len(entries_list)
            
            # Средняя оценка
            total_score = sum(entry["score"] for entry in entries_list)
            average_score = round(total_score / entries_count, 1) if entries_count > 0 else 0
            
            # Типы настроений
            mood_types = list(set(entry["type"] for entry in entries_list))
            
            # Цвет по оценке
            rounded_score = round(average_score) if average_score > 0 else 0
            color = get_mood_color(rounded_score)
            
            # Фиксируем время (добавляем 3 часа если нужно)
            fixed_entries = []
            for entry_data in entries_list:
                fixed_entry = entry_data.copy()
                if fixed_entry["created_at"]:
                    # Если время в UTC, можно добавить 3 часа
                    # fixed_entry["created_at"] = entry_data["created_at"] + timedelta(hours=3)
                    pass
                fixed_entries.append(fixed_entry)
            
            calendar_data[day_str] = {
                "average_score": average_score,
                "mood_types": mood_types,
                "entries_count": entries_count,
                "entries": fixed_entries,
                "color": color,
                "has_data": True
            }
        else:
            # День без записей
            calendar_data[day_str] = {
                "average_score": 0,
                "mood_types": [],
                "entries_count": 0,
                "entries": [],
                "color": "#e2e8f0",
                "has_data": False
            }
        
        # Следующий день
        current_date = date.fromordinal(current_date.toordinal() + 1)
    
    return {
        "calendar": calendar_data,
        "month": target_month,
        "year": target_year,
        "month_name": get_month_name_ru(target_month),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_days": len(calendar_data)
    }

def get_mood_color(score: int) -> str:
    colors = {
        1: "#ef4444",
        2: "#f97316",
        3: "#eab308",
        4: "#62f28b",
        5: "#048509",
    }
    return colors.get(score, "#e2e8f0")

def get_month_name_ru(month: int) -> str:
    months = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    return months[month - 1] if 1 <= month <= 12 else "Неизвестный месяц"