from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class MoodBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    mood_type: str = Field(..., min_length=1, max_length=50)
    mood_score: int = Field(..., ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)

class MoodCreate(MoodBase):
    pass

class MoodUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    mood_type: Optional[str] = Field(None, min_length=1, max_length=50)
    mood_score: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)

class MoodResponse(MoodBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date: datetime
    created_at: Optional[datetime] = None