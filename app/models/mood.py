# app/models/mood.py
from sqlalchemy import Column, Integer, String, Date, DateTime, func
from sqlalchemy.sql import expression
from app.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)
    mood_score = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
    date = Column(Date, server_default=func.now())  # Автоматическая дата
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # ← ИСПРАВЛЕНО
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, type={self.mood_type})>"