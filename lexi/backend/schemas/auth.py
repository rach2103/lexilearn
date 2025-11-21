from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    preferred_font: str = "OpenDyslexic"
    font_size: int = 16
    line_spacing: float = 1.5
    color_scheme: str = "high_contrast"
    language_preference: str = "en"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    preferred_font: str
    font_size: int
    line_spacing: float
    color_scheme: str
    language_preference: str
    is_active: bool

    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
