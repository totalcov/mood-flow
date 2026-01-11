from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.sql import expression
from app.database import Base
from datetime import datetime, timezone

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String, nullable=False)
    mood_score = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
    
    # Сохраняем время в UTC
    date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Для обратной совместимости - также сохраняем дату отдельно
    date_only = Column(String, nullable=False, default=lambda: datetime.now(timezone.utc).date().isoformat())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, type={self.mood_type})>"