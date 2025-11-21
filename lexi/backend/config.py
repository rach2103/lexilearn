from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_TYPE: str = "sqlite"  # Options: "sqlite", "postgresql"
    DATABASE_URL: str = "sqlite:///lexi.db"
    # For PostgreSQL, use: DATABASE_URL="postgresql://user:password@localhost:5432/lexilearn"
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "lexilearn"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Speech Processing APIs
    SPEECH_API_TYPE: str = "local_whisper"  # Options: "openai", "huggingface", "local_whisper", "google", "azure"
    
    # OCR Provider
    OCR_PROVIDER: str = "tesseract"  # Options: "tesseract", "huggingface_api", "google_vision_api"
    
    # Text Analysis
    TEXT_ANALYSIS_PROVIDER: str = "bert"  # Options: "local_simple", "huggingface_api", "openai_api"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Hugging Face
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Google Vision API
    GOOGLE_VISION_API_KEY: Optional[str] = None
    
    # Google Cloud
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = None
    
    # Azure Cognitive Services
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # ML Models
    MODEL_CACHE_DIR: str = "ml_models/cache"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env

settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
