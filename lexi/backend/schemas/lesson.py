from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LessonCreate(BaseModel):
    title: str
    content: str
    lesson_type: str  # reading, writing, speaking, listening
    difficulty_level: str  # beginner, intermediate, advanced

class LessonResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    lesson_type: str
    difficulty_level: str
    completed: bool
    score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
