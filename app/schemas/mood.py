from pydantic import BaseModel, Field
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
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True