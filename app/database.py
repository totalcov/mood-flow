import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mood_flow.db")

# Создаем движок SQLAlchemy
# connect_args нужен только для SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Функция для получения сессии БД (будет использоваться в зависимостях FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()