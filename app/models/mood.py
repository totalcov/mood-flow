# app/models/mood.py
from sqlalchemy import Column, Integer, String, Date, DateTime, func  # ← Date здесь!
from app.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)
    mood_score = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
    date = Column(Date, nullable=False, server_default=func.current_date())  # ← Теперь работает
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, type={self.mood_type})>"