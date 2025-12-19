# app/models/mood.py - АБСОЛЮТНО ПРАВИЛЬНАЯ ВЕРСИЯ
from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime

# КРИТИЧЕСКИ ВАЖНО: импортируем Base из database.py
from app.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)
    mood_score = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
    date = Column(Date, default=datetime.now().date)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, type={self.mood_type}, score={self.mood_score})>"