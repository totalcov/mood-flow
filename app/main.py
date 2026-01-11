# main.py - PostgreSQL версия
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.moods import router
from app.database import create_tables
import os

print("=" * 60)
print("🚀 Mood Flow API запускается...")
print("=" * 60)

# Инициализация PostgreSQL
print("📊 Инициализация базы данных...")
create_tables()

app = FastAPI(
    title="Mood Flow",
    description="Трекер настроений с календарем и статистикой",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Mood Flow Team",
        "url": "https://github.com/totalcov/mood-flow",
    }
)

# Раздача статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS настройки
origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://mood-flow.onrender.com",
    "http://mood-flow.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер
app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Mood Flow API работает на PostgreSQL! 🎉",
        "version": "1.0.0",
        "database": "PostgreSQL",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "moods": "/moods/",
            "statistics": "/moods/statistics/",
            "calendar": "/moods/calendar/",
            "health": "/health"
        },
        "note": "Данные сохраняются между деплоями"
    }

@app.get("/health")
def health_check():
    from app.database import engine
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_ok = True
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        db_ok = False
    
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "PostgreSQL",
        "connected": db_ok,
        "service": "Mood Flow API"
    }

@app.get("/db-info")
def db_info():
    """Информация о базе данных"""
    import os
    from app.database import engine
    
    database_url = os.getenv("DATABASE_URL", "")
    db_type = "PostgreSQL" if "postgres" in database_url else "SQLite"
    
    try:
        with engine.connect() as conn:
            # Проверяем таблицы
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Считаем записи
            from app.models.mood import MoodEntry
            from sqlalchemy.orm import Session
            from sqlalchemy import func
            
            with Session(engine) as session:
                count = session.query(func.count(MoodEntry.id)).scalar() or 0
            
            return {
                "status": "connected",
                "database_type": db_type,
                "tables": tables,
                "mood_entries_count": count,
                "has_data": count > 0
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database_type": db_type
        }

@app.on_event("startup")
def on_startup():
    print("\n" + "=" * 60)
    print("✅ Mood Flow API запущен!")
    print("🐘 Используется PostgreSQL")
    print("💾 Данные сохраняются между деплоями")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    print(f"🌐 Запуск сервера на порту {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)