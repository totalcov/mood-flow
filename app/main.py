# main.py - С БЭКАПАМИ
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.moods import router
from app.database import create_tables, test_database_connection
from app.backup import export_to_json, import_from_json
import os

print("=" * 60)
print("🚀 Mood Flow API запускается...")
print("=" * 60)

print("🔍 Восстанавливаем БД из бэкапа...")
from app.backup import import_from_backup, check_backup_status

backup_status = check_backup_status()
print(f"📊 Статус бэкапов: {backup_status}")

if backup_status["db_backup_exists"]:
    restored = import_from_backup()
    if restored:
        print("✅ БД восстановлена из постоянного бэкапа")
else:
    print("ℹ️  Постоянный бэкап не найден, создаем новую БД")

# Создаем таблицы
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

# Middleware для авто-бэкапа
@app.middleware("http")
async def backup_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Делаем бэкап после успешных POST запросов
    if request.method == "POST" and "/moods/" in str(request.url.path):
        if response.status_code in [200, 201]:  # Только при успехе
            try:
                print("💾 Авто-бэкап после создания записи...")
                backup_file = export_to_json()
                if backup_file:
                    print(f"✅ Бэкап сохранен: {backup_file.name}")
            except Exception as e:
                print(f"⚠️  Ошибка авто-бэкапа: {e}")
    
    return response

# Подключаем роутер
app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Mood Flow API работает! 🎉",
        "version": "1.0.0",
        "database": "SQLite с бэкапами",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "moods": "/moods/",
            "statistics": "/moods/statistics/",
            "calendar": "/moods/calendar/",
            "health": "/health",
            "data-check": "/data-check",
            "backup-create": "/moods/backup/create",
            "backup-restore": "/moods/backup/restore"
        },
        "note": "Авто-бэкап после каждой новой записи"
    }

@app.get("/health")
def health_check():
    db_ok = test_database_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "service": "Mood Flow API",
        "backup_system": "active"
    }

@app.get("/data-check")
def data_check():
    """Проверка сохранения данных"""
    import sqlite3
    from pathlib import Path
    import json
    
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
        
        # Проверяем бэкапы
        backup_dir = Path("./backups") if not os.getenv("RENDER") else Path("/opt/render/project/src/backups")
        backups = list(backup_dir.glob("*.json")) if backup_dir.exists() else []
        
        conn.close()
        
        return {
            "status": "ok",
            "database_file": db_path,
            "file_size_bytes": file_size,
            "file_size_human": f"{file_size / 1024:.2f} KB",
            "tables": tables,
            "mood_entries_count": mood_count,
            "data_persists": True if mood_count > 0 else False,
            "backups": {
                "count": len(backups),
                "latest": backups[-1].name if backups else None,
                "directory": str(backup_dir)
            }
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
    print("💾 Система бэкапов активна")
    print("📊 Проверка данных: /data-check")
    print("=" * 60)
    
    # Создаем начальный бэкап
    try:
        backup_file = export_to_json()
        if backup_file:
            print(f"📁 Начальный бэкап создан: {backup_file.name}")
    except Exception as e:
        print(f"⚠️  Не удалось создать начальный бэкап: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    print(f"🌐 Запуск сервера на порту {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)