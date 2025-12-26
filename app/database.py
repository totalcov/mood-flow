import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # для SQLite в production

# Получаем URL БД из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mood_flow.db")

# Настройка движка в зависимости от типа БД
if DATABASE_URL.startswith("sqlite"):
    # Для SQLite (локальная разработка)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # важно для SQLite в production
    )
elif DATABASE_URL.startswith("postgres"):
    # Для PostgreSQL (production на Render)
    engine = create_engine(DATABASE_URL)
else:
    # Для других БД
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания таблиц при запуске (если их нет)
def create_tables():
    Base.metadata.create_all(bind=engine)

    