from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ProgressCreate(BaseModel):
    lesson_id: int
    accuracy: float
    speed: float  # words per minute
    errors: Dict[str, Any]
    session_duration: int  # in seconds

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    accuracy: float
    speed: float
    errors: Dict[str, Any]
    session_duration: int
    created_at: datetime

    class Config:
        from_attributes = True
