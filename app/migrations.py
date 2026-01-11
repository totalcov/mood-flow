# app/migrations.py
from sqlalchemy import text, inspect
from app.database import engine, Base, SessionLocal
from app.models.mood import MoodEntry
import os

def check_and_migrate():
    """Проверяет и применяет необходимые миграции"""
    print("🔍 Проверяем миграции...")
    
    with engine.connect() as conn:
        # Создаем таблицу для отслеживания миграций, если её нет
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
    
    # Список миграций в порядке применения
    migrations = [
        # Добавим индекс для быстрого поиска по дате
        ("001_add_date_index", 
         "CREATE INDEX IF NOT EXISTS idx_mood_entries_date ON mood_entries (date)"),
        
        # Добавим ограничение уникальности, если нужно (комментируем если не нужно)
        # ("002_unique_date_per_day",
        #  "ALTER TABLE mood_entries ADD CONSTRAINT unique_date_mood UNIQUE (date)"),
    ]
    
    applied_migrations = []
    with SessionLocal() as db:
        for migration_name, sql in migrations:
            # Проверяем, применялась ли уже миграция
            result = db.execute(
                text("SELECT name FROM migrations WHERE name = :name"),
                {"name": migration_name}
            ).fetchone()
            
            if not result:
                print(f"🔄 Применяем миграцию: {migration_name}")
                try:
                    db.execute(text(sql))
                    db.execute(
                        text("INSERT INTO migrations (name) VALUES (:name)"),
                        {"name": migration_name}
                    )
                    db.commit()
                    applied_migrations.append(migration_name)
                except Exception as e:
                    db.rollback()
                    print(f"❌ Ошибка миграции {migration_name}: {e}")
            else:
                print(f"✅ Миграция {migration_name} уже применена")
    
    if applied_migrations:
        print(f"🎉 Применены миграции: {', '.join(applied_migrations)}")
    else:
        print("✅ Все миграции уже применены")
    
    return applied_migrations