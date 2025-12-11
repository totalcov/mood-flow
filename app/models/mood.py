from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.now(), nullable=False)
    score = Column(Integer, nullable=False)  # 1-5
    note = Column(Text, nullable=True)  # Краткое описание дня
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, score={self.score}, date={self.date})>"