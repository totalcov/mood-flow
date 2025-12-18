# app/models/mood.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)        # Было: отсутствует
    mood_score = Column(Integer, nullable=False)      # Было: score
    notes = Column(String(500), nullable=True)        # Было: note
    date = Column(Date, default=datetime.now().date)
    created_at = Column(DateTime, default=datetime.now)