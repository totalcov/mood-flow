import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print("=" * 60)
print("🔄 Настройка PostgreSQL...")

# Получаем URL от Render
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Исправляем для SQLAlchemy
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("✅ PostgreSQL подключен!")
    print("💾 Данные будут сохраняться навсегда!")
elif DATABASE_URL:
    print(f"📊 Используется: {DATABASE_URL[:50]}...")
else:
    print("❌ DATABASE_URL не найден. Используем SQLite")
    DATABASE_URL = "sqlite:///./mood_flow.db"

print(f"🔧 Database URL: {DATABASE_URL[:60]}...")

# Создаем движок
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы в PostgreSQL!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    

