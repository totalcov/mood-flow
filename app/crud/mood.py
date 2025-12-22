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


# Добавим в конец файла (после get_mood_statistics)
def get_mood_calendar_data(db: Session, year: int = None, month: int = None) -> dict:
    """
    Получить данные для календарной визуализации
    
    Возвращает:
    {
        "calendar": {
            "2023-12-01": {
                "average_score": 4.2,  # СРЕДНЯЯ оценка за день
                "mood_types": ["happy", "calm"],  # Все типы настроений за день
                "entries_count": 3,  # Количество записей за день
                "entries": [  # Все записи за день
                    {"score": 5, "type": "happy", "notes": "..."},
                    {"score": 4, "type": "calm", "notes": "..."},
                    {"score": 3, "type": "neutral", "notes": "..."}
                ],
                "color": "#4fd1c5",
                "has_data": True
            },
            ...
        },
        "month": 12,
        "year": 2023,
        "month_name": "Декабрь"
    }
    """
    from datetime import datetime, date
    from collections import defaultdict
    
    # Если год и месяц не указаны, используем текущие
    now = datetime.now()
    target_year = year or now.year
    target_month = month or now.month
    
    # Определяем начало и конец месяца
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
    
    # Группируем записи по дням
    daily_entries = defaultdict(list)
    for entry in entries:
        day_str = entry.date.isoformat()
        daily_entries[day_str].append({
            "score": entry.mood_score,
            "type": entry.mood_type,
            "notes": entry.notes,
            "created_at": entry.created_at
        })
    
    # Создаем полный календарь на месяц
    calendar_data = {}
    current_date = start_date
    
    while current_date < end_date:
        day_str = current_date.isoformat()
        
        if day_str in daily_entries:
            entries_list = daily_entries[day_str]
            entries_count = len(entries_list)
            
            # Рассчитываем среднюю оценку
            total_score = sum(entry["score"] for entry in entries_list)
            average_score = round(total_score / entries_count, 1)
            
            # Получаем все уникальные типы настроений
            mood_types = list(set(entry["type"] for entry in entries_list))
            
            # Получаем цвет по средней оценке (округляем до целого)
            rounded_score = round(average_score)
            color = get_mood_color(rounded_score)
            
            calendar_data[day_str] = {
                "average_score": average_score,
                "mood_types": mood_types,
                "entries_count": entries_count,
                "entries": entries_list,
                "color": color,
                "has_data": True
            }
        else:
            # День без данных
            calendar_data[day_str] = {
                "average_score": 0,
                "mood_types": [],
                "entries_count": 0,
                "entries": [],
                "color": "#e2e8f0",
                "has_data": False
            }
        
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
    """Получить цвет в зависимости от оценки настроения"""
    colors = {
        1: "#ef4444",  # ярко-красный - очень плохо
        2: "#f97316",  # оранжевый - плохо
        3: "#eab308",  # желтый/рыжий - нормально
        4: "#62f28b",  # СИНИЙ - хорошо (был светло-зеленый)
        5: "#048509",  # ИЗУМРУДНЫЙ - отлично (был темно-зеленый)
    }
    return colors.get(score, "#e2e8f0")



def get_month_name_ru(month: int) -> str:
    """Название месяца на русском"""
    months = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    return months[month - 1] if 1 <= month <= 12 else "Неизвестный месяц"


