# check_tables.py
import sys
sys.path.append('.')

from app.database import engine
from sqlalchemy import inspect

print("=== ПРОВЕРКА ТАБЛИЦ В БАЗЕ ДАННЫХ ===")

inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"Таблицы в базе данных: {tables}")

if 'mood_entries' in tables:
    print("✅ Таблица 'mood_entries' существует")
else:
    print("❌ Таблица 'mood_entries' НЕ существует!")
    print("   Нужно создать таблицы через Alembic или SQLAlchemy")