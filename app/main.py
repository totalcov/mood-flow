from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.moods import router
from app.database import create_tables
import os

# Автоматически создаем таблицы при запуске в production
# На Render SQLite будет использовать /tmp для хранения БД
if os.getenv("RENDER") or not os.getenv("DATABASE_URL", "").startswith("postgres"):
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
    "https://mood-flow.onrender.com",  # замените на ваш URL
    "http://mood-flow.onrender.com",   # замените на ваш URL
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
        "message": "Mood Flow API работает!",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "/static/index.html",
        "endpoints": {
            "moods": "/moods/",
            "statistics": "/moods/statistics/",
            "calendar": "/moods/calendar/"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Mood Flow API"}


