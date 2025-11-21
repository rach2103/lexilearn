from config import settings
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Pydantic Models for API
class User(BaseModel):
    id: Optional[int] = None
    email: str
    username: str
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class Lesson(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    content: Optional[str] = None
    lesson_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    completed: bool = False
    score: Optional[float] = None
    created_at: Optional[datetime] = None

class Progress(BaseModel):
    id: Optional[int] = None
    user_id: int
    lesson_id: int
    accuracy: float
    speed: float
    errors: Optional[Dict[str, Any]] = None
    session_duration: int
    created_at: Optional[datetime] = None

class ChatSession(BaseModel):
    id: Optional[int] = None
    user_id: int
    session_id: str
    messages: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DyslexiaTest(BaseModel):
    id: Optional[int] = None
    user_id: int
    test_type: str
    results: Dict[str, Any]
    score: float
    recommendations: Optional[List[str]] = None
    created_at: Optional[datetime] = None

class ErrorCorrection(BaseModel):
    id: Optional[int] = None
    user_id: int
    original_text: str
    corrected_text: str
    error_types: Optional[List[str]] = None
    confidence_score: float
    created_at: Optional[datetime] = None