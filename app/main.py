# main.py - ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.moods import router
from app.database import create_tables, test_database_connection
import os

print("=" * 60)
print("🚀 Mood Flow API запускается...")
print("=" * 60)

# Всегда создаем таблицы для SQLite
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
        "message": "Mood Flow API работает! 🎉",
        "version": "1.0.0",
        "database": "SQLite",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "moods": "/moods/",
            "statistics": "/moods/statistics/",
            "calendar": "/moods/calendar/",
            "health": "/health",
            "data-check": "/data-check"
        },
        "note": "Используется SQLite с сохранением данных в /tmp на Render"
    }

@app.get("/health")
def health_check():
    db_ok = test_database_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "service": "Mood Flow API",
        "timestamp": "2024-01-09"
    }

@app.get("/data-check")
def data_check():
    """Проверка сохранения данных"""
    import sqlite3
    from pathlib import Path
    
    db_path = "/tmp/mood_flow.db" if os.getenv("RENDER") else "./mood_flow.db"
    
    try:
        if not Path(db_path).exists():
            return {
                "status": "no_database_file",
                "message": "Файл базы данных не найден",
                "path": db_path
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Считаем записи в mood_entries
        mood_count = 0
        if 'mood_entries' in tables:
            cursor.execute("SELECT COUNT(*) FROM mood_entries")
            mood_count = cursor.fetchone()[0]
        
        # Размер файла
        file_size = Path(db_path).stat().st_size
        
        conn.close()
        
        return {
            "status": "ok",
            "database_file": db_path,
            "file_size_bytes": file_size,
            "file_size_human": f"{file_size / 1024:.2f} KB",
            "tables": tables,
            "mood_entries_count": mood_count,
            "data_persists": True if mood_count > 0 else False
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database_file": db_path
        }

@app.on_event("startup")
def on_startup():
    print("\n" + "=" * 60)
    print("✅ Mood Flow API запущен и готов к работе!")
    print(f"🌐 Документация: https://mood-flow.onrender.com/docs")
    print(f"📊 Проверка данных: /data-check")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))  # Render использует 10000
    print(f"🌐 Запуск сервера на порту {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)