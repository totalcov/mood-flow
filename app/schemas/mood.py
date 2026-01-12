from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class MoodBase(BaseModel):
    mood_type: str = Field(..., min_length=1, max_length=50)
    mood_score: int = Field(..., ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)

class MoodCreate(MoodBase):
    pass

class MoodUpdate(BaseModel):
    mood_type: Optional[str] = Field(None, min_length=1, max_length=50)
    mood_score: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)

class MoodResponse(MoodBase):
    id: int
    date: datetime  # ← ИЗМЕНИ на datetime
    created_at: datetime  # ← ИЗМЕНИ на datetime
    
    # Добавь валидатор для конвертации в строку при необходимости
    @validator('date', 'created_at', pre=True)
    def ensure_datetime(cls, value):
        """Обеспечиваем что значение datetime"""
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        return value
    
    class Config:
        from_attributes = True