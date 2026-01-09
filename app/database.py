# app/database.py - ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print("=" * 60)
print("🔄 Инициализация базы данных Mood Flow...")

# Определяем путь к базе данных
if os.getenv("RENDER"):
    # На Render используем /tmp (сохраняется между деплоями)
    DB_PATH = "/tmp/mood_flow.db"
    print(f"🌐 Production (Render): SQLite в {DB_PATH}")
    print(f"⚠️  ВАЖНО: Данные сохраняются в /tmp между перезапусками")
else:
    # Локальная разработка
    DB_PATH = "./mood_flow.db"
    print(f"💻 Development: SQLite в {DB_PATH}")

DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"📊 Database URL: {DATABASE_URL}")

# Создаем движок SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    echo=False  # Поставьте True для отладки SQL запросов
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Зависимость для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """Проверка подключения к БД"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Подключение к БД успешно")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def create_tables():
    """Создание таблиц при запуске"""
    try:
        print("📦 Создаем таблицы...")
        Base.metadata.create_all(bind=engine)
        
        # Создаем таблицу для отслеживания миграций
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS _app_info (
                    id INTEGER PRIMARY KEY,
                    version TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Записываем информацию о приложении
            conn.execute(text("""
                INSERT OR REPLACE INTO _app_info (id, version) 
                VALUES (1, '1.0.0')
            """))
            conn.commit()
        
        print("✅ Таблицы созданы успешно")
        return True
    except Exception as e:
        print(f"⚠️  Ошибка создания таблиц: {e}")
        return False

# Автоматическая проверка при импорте
if __name__ == "__main__":
    test_database_connection()

print("=" * 60)