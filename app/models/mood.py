# app/models/mood.py
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)
    mood_score = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
    
    # ИЗМЕНИЛ: DateTime вместо Date, храним полную дату-время
    date = Column(DateTime, nullable=False, server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, type={self.mood_type})>"