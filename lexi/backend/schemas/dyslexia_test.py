from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

class DyslexiaTestCreate(BaseModel):
    test_type: str  # screening, comprehensive
    answers: Dict[str, Any]

class DyslexiaTestResponse(BaseModel):
    id: int
    score: float
    risk_level: str  # low, medium, high
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
