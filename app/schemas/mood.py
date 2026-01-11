from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class MoodBase(BaseModel):
    mood_type: str = Field(..., min_length=1, max_length=50, description="Тип настроения")
    mood_score: int = Field(..., ge=1, le=5, description="Оценка настроения от 1 до 5")
    notes: Optional[str] = Field(None, max_length=500, description="Краткое описание причины")

class MoodCreate(MoodBase):
    pass

class MoodUpdate(BaseModel):
    mood_type: Optional[str] = Field(None, min_length=1, max_length=50)
    mood_score: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)

class MoodResponse(MoodBase):
    id: int
    date: str  # Изменили на str
    created_at: Optional[str] = None  # Optional[str] вместо datetime
    
    @validator('date', 'created_at', pre=True)
    def convert_to_string(cls, value):
        if value is None:
            return None
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True