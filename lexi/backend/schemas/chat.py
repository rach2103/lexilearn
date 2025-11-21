from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    message_type: str = "text"  # text, image, voice
    timestamp: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None  # BERT context embeddings

class ChatResponse(BaseModel):
    message: str
    analysis: Optional[Dict[str, Any]] = None
    timestamp: datetime
    message_type: str = "ai_response"
    confidence: Optional[float] = None  # BERT confidence score
    embeddings: Optional[List[float]] = None  # BERT embeddings

class ChatSession(BaseModel):
    session_id: str
    user_id: int
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    context_embeddings: Optional[List[List[float]]] = None  # Session context

    class Config:
        from_attributes = True
