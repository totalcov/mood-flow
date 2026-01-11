# app/models/mood.py - ВЕРНИ СТАРУЮ ВЕРСИЮ
from sqlalchemy import Column, Integer, String, Date, DateTime
from app.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)
    mood_score = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
    date = Column(Date)  # Только дата
    created_at = Column(DateTime)  # Дата и время
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, type={self.mood_type})>"