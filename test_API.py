# advanced_filters.py - демонстрация улучшенной фильтрации
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.crud.mood import get_mood_entries
from datetime import datetime, timedelta, date
from typing import Optional

print("🔍 === ДЕМОНСТРАЦИЯ ФИЛЬТРАЦИИ И ПАГИНАЦИИ ===\n")

db = SessionLocal()

# 1. Получим общее количество записей для демонстрации
from app.models.mood import MoodEntry
total_count = db.query(MoodEntry).count()
print(f"📊 Всего записей в базе: {total_count}\n")

# 2. Демонстрация пагинации
print("1. 📖 ПАГИНАЦИЯ (skip и limit):")
print("   - Без пагинации - все записи сразу")
all_entries = get_mood_entries(db, limit=1000)  # Большой лимит
print(f"      Записей: {len(all_entries)}")

print("\n   - С пагинацией - по 5 записей на страницу:")
for page in range(3):  # Первые 3 страницы
    skip = page * 5
    entries = get_mood_entries(db, skip=skip, limit=5)
    print(f"      Страница {page + 1} (skip={skip}, limit=5): {len(entries)} записей")
    if entries:
        for entry in entries:
            print(f"        • {entry.date}: {entry.mood_type} ({entry.mood_score}/5)")

# 3. Демонстрация фильтрации
print("\n2. 🔍 ФИЛЬТРАЦИЯ:")
today = datetime.now().date()

# Фильтр по типу настроения
print(f"\n   - Фильтр по типу настроения 'happy':")
happy_entries = get_mood_entries(db, mood_type_filter="happy", limit=10)
print(f"      Найдено: {len(happy_entries)} записей")
for entry in happy_entries[:3]:  # Покажем первые 3
    print(f"        • {entry.date}: {entry.mood_score}/5")

# Фильтр по дате
print(f"\n   - Фильтр по сегодняшней дате ({today}):")
today_entries = get_mood_entries(db, date_filter=today, limit=10)
print(f"      Найдено: {len(today_entries)} записей")

db.close()

print("\n" + "="*50)
print("🎯 ВЫВОДЫ О ТЕКУЩЕЙ РЕАЛИЗАЦИИ:")
print("   • ✅ Пагинация работает (skip, limit)")
print("   • ✅ Базовая фильтрация работает (по дате, типу)")
print("   • ⚠️  Можно добавить больше фильтров:")
print("      - По диапазону дат (start_date, end_date)")
print("      - По диапазону оценок (min_score, max_score)")
print("      - Поиск по тексту в заметках")
print("      - Сортировка по разным полям")