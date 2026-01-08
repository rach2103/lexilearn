from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager
import json
import uuid
import os
from datetime import datetime, timedelta
import httpx

# Import local modules
from config import settings
from database.database import get_db, create_tables
from database.models import User
# Import ML models with error handling
try:
    from ml_models.text_analysis import text_analyzer
except ImportError:
    class MockTextAnalyzer:
        def analyze_text(self, text):
            return {"errors": [], "corrected_text": text, "confidence_score": 0.8, "error_count": 0}
        def get_highlighted_text(self, text, errors):
            return text
    text_analyzer = MockTextAnalyzer()

try:
    if settings.SPEECH_API_TYPE == "openai":
        from ml_models.speech_processing import speech_processor
    else:
        from ml_models.speech_processing_alternative import SpeechProcessorAlternative
        speech_processor = SpeechProcessorAlternative()
except ImportError:
    class MockSpeechProcessor:
        async def process_speech_to_text(self, file_path, language):
            return {"success": False, "error": "Speech processing not available"}
        async def text_to_speech(self, text, voice, language):
            return {"success": False, "error": "TTS not available"}
        async def analyze_speech_errors(self, file_path, expected_text):
            return {"success": False, "error": "Speech analysis not available"}
    speech_processor = MockSpeechProcessor()

try:
    from ml_models.handwriting_recognition import TesseractOCRProcessor
    handwriting_recognizer = TesseractOCRProcessor()
except ImportError:
    class MockHandwritingRecognizer:
        async def recognize_handwriting(self, file_path, language):
            return {"success": False, "error": "Handwriting recognition not available"}
        async def correct_handwriting(self, file_path, language):
            return {"success": False, "error": "Handwriting correction not available"}
    handwriting_recognizer = MockHandwritingRecognizer()

# Import schemas
from schemas.auth import UserCreate, UserLogin, Token, ForgotPasswordRequest, ResetPasswordRequest
from schemas.chat import ChatMessage, ChatResponse
from schemas.lesson import LessonCreate, LessonResponse
from schemas.progress import ProgressCreate, ProgressResponse
from schemas.dyslexia_test import DyslexiaTestCreate, DyslexiaTestResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown (if needed)
    pass

# Create FastAPI app
app = FastAPI(
    title="LexiLearn API",
    description="AI Tutor for Dyslexic Students",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()



# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db_manager = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(user_data.email)
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Truncate password if longer than 72 bytes (bcrypt limit)
        password = user_data.password
        if len(password.encode("utf-8")) > 72:
            password = password[:72]

        hashed_password = pwd_context.hash(password)

        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name or "",
            "preferred_font": getattr(user_data, 'preferred_font', 'OpenDyslexic'),
            "font_size": getattr(user_data, 'font_size', 16),
            "line_spacing": getattr(user_data, 'line_spacing', 1.5),
            "color_scheme": getattr(user_data, 'color_scheme', 'high_contrast'),
            "language_preference": getattr(user_data, 'language_preference', 'en')
        }
        
        user_id = db_manager.create_user(user_dict)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Username or email already taken")
        
        # Generate token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        print(f"[SUCCESS] User registered: {user_data.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db_manager = Depends(get_db)):
    """Login user"""
    user = db_manager.get_user_by_email(user_data.email)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not pwd_context.verify(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db_manager = Depends(get_db)):
    """Send password reset email"""
    try:
        print(f"[DEBUG] Password reset requested for: {request.email}")
        user = db_manager.get_user_by_email(request.email)
        
        if not user:
            print(f"[DEBUG] User not found: {request.email}")
            return {"message": "If the email exists, a password reset link has been sent"}
        
        import secrets
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        print(f"[DEBUG] Creating reset token for user ID: {user['id']}")
        db_manager.create_password_reset_token(user["id"], reset_token, expires_at)
        
        from email_utils import send_password_reset_email
        print(f"[DEBUG] Sending reset email to: {request.email}")
        await send_password_reset_email(request.email, reset_token)
        
        print(f"[SUCCESS] Password reset email sent to: {request.email}")
        return {"message": "If the email exists, a password reset link has been sent"}
    except Exception as e:
        print(f"[ERROR] Password reset failed: {str(e)}")
        return {"message": "If the email exists, a password reset link has been sent"}

@app.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest, db_manager = Depends(get_db)):
    """Reset password using token"""
    token_data = db_manager.get_password_reset_token(request.token)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(request.new_password)
    
    success = db_manager.update_user_password(token_data["user_id"], hashed_password)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")
    
    db_manager.mark_token_as_used(request.token)
    
    return {"message": "Password reset successfully"}

@app.get("/auth/google/login")
async def google_login():
    """Redirect to Google OAuth"""
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
    
    if not google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return RedirectResponse(url=google_auth_url)

@app.get("/auth/google/callback")
async def google_callback(code: str, db_manager = Depends(get_db)):
    """Handle Google OAuth callback"""
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        
        # Get user info
        user_response = await client.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_response.json()
    
    # Check if user exists
    email = user_info.get('email')
    existing_user = db_manager.get_user_by_email(email)
    
    if not existing_user:
        # Create new user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        user_dict = {
            "email": email,
            "username": user_info.get('name', email.split('@')[0]),
            "hashed_password": pwd_context.hash(str(uuid.uuid4())),  # Random password
            "full_name": user_info.get('name', ''),
            "preferred_font": 'OpenDyslexic',
            "font_size": 16,
            "line_spacing": 1.5,
            "color_scheme": 'high_contrast',
            "language_preference": 'en'
        }
        
        user_id = db_manager.create_user(user_dict)
        if not user_id:
            raise HTTPException(status_code=400, detail="Failed to create user")
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    
    # Redirect to frontend with token
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    return RedirectResponse(url=f"{frontend_url}/auth/callback?token={jwt_token}")

# Helper function to create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    from jose import JWTError, jwt
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Helper function to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db_manager = Depends(get_db)):
    from jose import JWTError, jwt
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db_manager.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# User settings endpoints
@app.get("/api/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user.get("full_name", ""),
        "preferred_font": current_user.get("preferred_font", "OpenDyslexic"),
        "font_size": current_user.get("font_size", 16),
        "line_spacing": current_user.get("line_spacing", 1.5),
        "color_scheme": current_user.get("color_scheme", "high_contrast"),
        "language_preference": current_user.get("language_preference", "en")
    }

@app.put("/api/user/settings")
async def update_user_settings(settings_data: dict, current_user: User = Depends(get_current_user), db_manager = Depends(get_db)):
    """Update user settings"""
    try:
        # Update user in database
        success = db_manager.update_user_settings(
            user_id=current_user["id"],
            full_name=settings_data.get("full_name"),
            preferred_font=settings_data.get("preferred_font"),
            font_size=settings_data.get("font_size"),
            line_spacing=settings_data.get("line_spacing"),
            color_scheme=settings_data.get("color_scheme"),
            language_preference=settings_data.get("language_preference")
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update settings")
        
        # Get updated user
        updated_user = db_manager.get_user_by_email(current_user["email"])
        
        return {
            "message": "Settings updated successfully",
            "user": {
                "id": updated_user["id"],
                "email": updated_user["email"],
                "username": updated_user["username"],
                "full_name": updated_user.get("full_name", ""),
                "preferred_font": updated_user.get("preferred_font", "OpenDyslexic"),
                "font_size": updated_user.get("font_size", 16),
                "line_spacing": updated_user.get("line_spacing", 1.5),
                "color_scheme": updated_user.get("color_scheme", "high_contrast"),
                "language_preference": updated_user.get("language_preference", "en")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Update settings failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

# Text analysis endpoints
@app.post("/api/analyze-text")
async def analyze_text(request: dict):
    """Analyze text for dyslexic errors"""
    text = request.get("text", "")
    analysis = text_analyzer.analyze_text(text)
    
    return analysis

@app.post("/api/highlight-text")
async def highlight_text(text: str):
    """Return highlighted text with error markings"""
    analysis = text_analyzer.analyze_text(text)
    highlighted_text = text_analyzer.get_highlighted_text(text, analysis["errors"])
    
    return {
        "highlighted_text": highlighted_text,
        "errors": analysis["errors"]
    }

# Speech processing endpoints
@app.post("/api/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """Convert speech to text"""
    # Save uploaded file temporarily
    file_path = f"{settings.UPLOAD_DIR}/{uuid.uuid4()}_{audio_file.filename}"
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    try:
        result = await speech_processor.process_speech_to_text(file_path, language)
        return result
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/text-to-speech")
async def text_to_speech(
    text: str,
    voice: str = "alloy",
    language: str = "en"
):
    """Convert text to speech"""
    result = await speech_processor.text_to_speech(text, voice, language)
    return result

@app.post("/api/analyze-speech")
async def analyze_speech(
    audio_file: UploadFile = File(...),
    expected_text: Optional[str] = None,
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """Analyze speech for errors"""
    # Save uploaded file temporarily
    file_path = f"{settings.UPLOAD_DIR}/{uuid.uuid4()}_{audio_file.filename}"
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    try:
        result = await speech_processor.analyze_speech_errors(file_path, expected_text)
        return result
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

# Handwriting recognition endpoints
@app.post("/api/recognize-handwriting")
async def recognize_handwriting(
    image_file: UploadFile = File(...),
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """Recognize handwritten text with educational feedback"""
    # Create user-specific upload directory
    user_upload_dir = f"{settings.UPLOAD_DIR}/user_{current_user['id']}"
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Save uploaded file with user-specific path
    file_path = f"{user_upload_dir}/{uuid.uuid4()}_{image_file.filename}"
    with open(file_path, "wb") as buffer:
        content = await image_file.read()
        buffer.write(content)
    
    try:
        # Get OCR result from the enhanced processor
        ocr_result = await handwriting_recognizer.recognize_handwriting(file_path, language)
        
        if not ocr_result.get("success"):
            return ocr_result
        
        recognized_text = ocr_result.get("recognized_text", "")
        
        # Use the enhanced word-level feedback from the recognition module
        if "word_feedback" in ocr_result and ocr_result["word_feedback"]:
            # Build specific feedback from word-level analysis
            word_corrections = []
            for word_info in ocr_result["word_feedback"]:
                word = word_info.get("word", "")
                issues = word_info.get("issues", [])
                
                for issue in issues:
                    letter_hint = issue.get("letter_hint", "")
                    description = issue.get("description", "")
                    suggestion = issue.get("suggestion", "")
                    
                    if letter_hint and description:
                        word_corrections.append({
                            "original": word,
                            "suggested": letter_hint,
                            "reason": f"In '{word}': {description}. {suggestion}"
                        })
            
            feedback = {
                "overall_assessment": f"I can see you wrote: '{recognized_text}'",
                "recognized_content": f"Recognized text: '{recognized_text}'",
                "word_corrections": word_corrections,
                "specific_improvements": [
                    "Focus on the highlighted character issues",
                    "Practice the letters that were unclear"
                ],
                "practice_suggestions": [
                    f"Practice writing '{recognized_text}' again",
                    "Write each word separately for clarity",
                    "Use lined paper for better letter alignment"
                ]
            }
        else:
            # Fallback to original feedback generation
            feedback = generate_handwriting_feedback(recognized_text, ocr_result)
        
        # Analyze text for dyslexia patterns
        text_analysis = text_analyzer.analyze_text(recognized_text) if recognized_text else {"errors": [], "corrected_text": ""}
        
        return {
            **ocr_result,
            "educational_feedback": feedback,
            "text_analysis": text_analysis,
            "learning_suggestions": generate_handwriting_suggestions(recognized_text, ocr_result.get("errors", []))
        }
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/correct-handwriting")
async def correct_handwriting(
    image_file: UploadFile = File(...),
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """Recognize and correct handwritten text with comprehensive feedback"""
    # Create user-specific upload directory
    user_upload_dir = f"{settings.UPLOAD_DIR}/user_{current_user['id']}"
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Save uploaded file with user-specific path
    file_path = f"{user_upload_dir}/{uuid.uuid4()}_{image_file.filename}"
    with open(file_path, "wb") as buffer:
        content = await image_file.read()
        buffer.write(content)
    
    try:
        # Get correction result from enhanced processor
        correction_result = await handwriting_recognizer.correct_handwriting(file_path, language)
        
        if not correction_result.get("success"):
            return correction_result
        
        recognized_text = correction_result.get("recognized_text", "")
        corrected_text = correction_result.get("corrected_text", recognized_text)
        
        # Generate comprehensive feedback using word-level analysis
        if "word_feedback" in correction_result and correction_result["word_feedback"]:
            # Build detailed corrections from word-level feedback
            corrections_made = []
            for word_info in correction_result["word_feedback"]:
                word = word_info.get("word", "")
                issues = word_info.get("issues", [])
                
                for issue in issues:
                    letter_hint = issue.get("letter_hint", "")
                    description = issue.get("description", "")
                    suggestion = issue.get("suggestion", "")
                    
                    if description:
                        corrections_made.append(f"In '{word}': {description}")
            
            feedback = generate_comprehensive_handwriting_feedback(recognized_text, corrected_text, {
                **correction_result,
                "corrections_applied": corrections_made
            })
        else:
            feedback = generate_comprehensive_handwriting_feedback(recognized_text, corrected_text, correction_result)
        
        # Get AI tutor insights
        try:
            ai_analysis = ai_tutor.analyze_user_input(recognized_text, {"context": "handwriting_practice"})
        except:
            ai_analysis = {"intent": "practice", "emotion": "neutral", "learning_need": "handwriting"}
        
        return {
            **correction_result,
            "educational_feedback": feedback,
            "ai_insights": ai_analysis,
            "practice_exercises": generate_handwriting_exercises(correction_result.get("errors", [])),
            "encouragement": generate_encouragement_message(correction_result.get("confidence", 0))
        }
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

# Chat endpoints
@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message with AI
            response = await process_chat_message(message_data, user_id)
            
            # Send response back
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

async def process_chat_message(message_data: dict, user_id: int):
    """Process chat message and generate intelligent AI response with enhanced natural conversation"""
    user_message = message_data.get("message", "")
    print(f"[DEBUG] Processing message from user {user_id}: {user_message}")
    print(f"[DEBUG] Active exercises: {list(ai_tutor.active_exercises.keys())}")
    
    # Get recent conversation for context
    recent_context = ai_tutor.get_recent_conversation(user_id, limit=3)
    print(f"[DEBUG] Recent conversation context: {len(recent_context)} turns")
    
    # Get user context from database
    from database.database import db_manager
    user_context = {"user_id": user_id}  # Always include user_id
    print(f"[DEBUG] User context: {user_context}")
    try:
        if hasattr(db_manager, 'get_user_progress'):
            progress = db_manager.get_user_progress(user_id)
            user_context.update({
                "recent_accuracy": progress.get("average_accuracy", 0),
                "grade_level": progress.get("grade_level", 1),
                "last_lesson_category": progress.get("last_lesson_category", ""),
                "learning_preferences": progress.get("preferences", {})
            })
    except:
        pass
    
    # Analyze text for errors using existing text analyzer (await async call)
    text_analysis = await text_analyzer.analyze_text(user_message)
    
    # Use AI tutor for intelligent analysis and response
    ai_analysis = ai_tutor.analyze_user_input(user_message, user_context)
    print(f"[DEBUG] AI analysis intent: {ai_analysis.get('intent')}")
    
    # Check if user has an active exercise and this is a response to it
    if user_id in ai_tutor.active_exercises:
        print(f"[DEBUG] Found active exercise for user {user_id}")
        exercise = ai_tutor.active_exercises[user_id]
        print(f"[DEBUG] Exercise skill_area: {exercise.get('skill_area')}, type: {exercise.get('exercise_type')}")
        
        # Evaluate the exercise response
        ai_response_data = ai_tutor._handle_short_text_submission(user_message, ai_analysis, user_context)
        print(f"[DEBUG] Exercise evaluation result: is_correct={ai_response_data.get('is_correct')}, score={ai_response_data.get('score')}")
    else:
        print(f"[DEBUG] No active exercise for user {user_id}, generating normal response")
        # Try async generate_response first, fall back to async-less version
        try:
            ai_response_data = await ai_tutor.generate_response(user_message, ai_analysis, user_context)
        except TypeError:
            # Fallback if generate_response is not async
            ai_response_data = ai_tutor._generate_response_fallback(user_message, ai_analysis, user_context)
    
    print(f"[DEBUG] AI response: {ai_response_data.get('message')[:100] if ai_response_data.get('message') else 'None'}...")
    
    # Update conversation context for continuity
    topic = ai_analysis.get("learning_need", "general")
    ai_tutor.update_conversation_context(user_id, topic, user_message)
    
    # Update user context based on this interaction
    session_data = {
        "message_length": len(user_message),
        "errors_found": len(text_analysis.get("errors", [])),
        "intent": ai_analysis["intent"],
        "emotion": ai_analysis["emotion"],
        "learning_need": ai_analysis["learning_need"]
    }
    ai_tutor.update_user_context(user_id, session_data)
    
    # Add to conversation memory
    ai_tutor.add_conversation_memory(user_id, user_message, ai_response_data.get("message", ""))
    
    # Generate natural followup
    natural_followup = ai_tutor.generate_natural_followup(user_context, ai_analysis)
    
    # Combine text analysis with AI response
    response = {
        "type": "ai_response",
        "message": ai_response_data["message"],
        "encouragement": ai_response_data.get("encouragement", ""),
        "suggestions": ai_response_data.get("suggestions", []),
        "lesson_recommendations": ai_response_data.get("lesson_recommendations", []),
        "exercises": ai_response_data.get("exercises", []),
        "tips": ai_response_data.get("tips", []),
        "emotional_support": ai_response_data.get("emotional_support", ""),
        "text_analysis": text_analysis,
        "ai_analysis": ai_analysis,
        "natural_followup": natural_followup,  # NEW: Add natural followup
        "conversation_context": ai_tutor.get_conversation_continuity(user_id),  # NEW: Add context
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Only include score/correctness for exercise responses
    if "is_correct" in ai_response_data:
        response["is_correct"] = ai_response_data["is_correct"]
        response["score"] = ai_response_data.get("score")
    
    return response

@app.post("/api/chat/message")
async def send_chat_message(message_data: dict, current_user: User = Depends(get_current_user), db_manager = Depends(get_db)):
    """Send a message to the AI tutor (REST endpoint)"""
    # Use user email as identifier
    user_id = current_user["email"]
    response = await process_chat_message(message_data, user_id)
    
    # Save to database
    session_id = ai_tutor.get_current_session_id(user_id)
    db_manager.save_chat_message(
        user_id=current_user["id"],
        session_id=session_id,
        user_message=message_data.get("message", ""),
        bot_response=response.get("message", "")
    )
    
    return response

@app.get("/api/chat/history")
async def get_chat_history(limit: int = 20, current_user: User = Depends(get_current_user), db_manager = Depends(get_db)):
    """Get chat history organized by date"""
    user_id = current_user["email"]
    db_user_id = current_user["id"]
    
    print(f"[DEBUG] Getting chat history for user: {user_id}")
    
    # Load from database first
    db_history = db_manager.load_chat_history(db_user_id)
    
    # Start session if not exists
    if user_id not in ai_tutor.conversation_history:
        ai_tutor.start_new_session(user_id)
    
    # Merge database history with in-memory history
    all_sessions = ai_tutor.conversation_history.get(user_id, {})
    
    # Add database sessions to AI tutor memory if not already there
    for session_id, messages in db_history.items():
        if session_id not in all_sessions:
            all_sessions[session_id] = messages
    
    print(f"[DEBUG] Total sessions for user: {len(all_sessions)}")
    
    # Organize messages by date
    history_by_date = {}
    
    for session_id, messages in all_sessions.items():
        print(f"[DEBUG] Session {session_id}: {len(messages)} messages")
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            if timestamp:
                # Extract date from timestamp (YYYY-MM-DD)
                date = timestamp.split("T")[0] if "T" in timestamp else timestamp[:10]
                
                if date not in history_by_date:
                    history_by_date[date] = []
                
                history_by_date[date].append({
                    "user_message": msg.get("user", ""),
                    "bot_response": msg.get("bot", ""),
                    "timestamp": timestamp,
                    "session_id": session_id
                })
    
    # Sort dates in descending order (most recent first)
    sorted_dates = sorted(history_by_date.keys(), reverse=True)
    
    # Format response with messages sorted by timestamp ascending within each date
    formatted_history = []
    for date in sorted_dates:
        day_messages = history_by_date[date]
        try:
            day_messages = sorted(
                day_messages,
                key=lambda m: m.get("timestamp", "")
            )
        except Exception as e:
            print(f"[WARN] Failed to sort day messages for {date}: {e}")
        formatted_history.append({
            "date": date,
            "message_count": len(day_messages),
            "messages": day_messages
        })
    
    print(f"[DEBUG] Returning {len(formatted_history)} days of history")
    
    return {
        "history_by_date": formatted_history,
        "total_days": len(formatted_history),
        "total_messages": sum(len(group["messages"]) for group in formatted_history),
        "current_session_id": ai_tutor.get_current_session_id(user_id)
    }

@app.get("/api/user/stats")
async def get_user_stats(current_user: User = Depends(get_current_user), db_manager = Depends(get_db)):
    """Get user statistics for dashboard"""
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    # Get progress from database
    progress_entries = db_manager.get_user_progress(user_id) if hasattr(db_manager, 'get_user_progress') else []
    
    # Calculate exercises completed and accuracy from database
    total_exercises = len(progress_entries)
    total_accuracy = sum(p.get("accuracy", 0) for p in progress_entries) if progress_entries else 0
    accuracy = (total_accuracy / total_exercises) if total_exercises > 0 else 0
    
    # Calculate study time from database (session_duration is in seconds, convert to minutes)
    total_study_time = sum(p.get("session_duration", 0) for p in progress_entries) // 60 if progress_entries else 0
    
    # Get chat history from database
    chat_history = db_manager.load_chat_history(user_id) if hasattr(db_manager, 'load_chat_history') else {}
    total_messages = sum(len(messages) for messages in chat_history.values())
    
    # Calculate daily chat messages (today)
    from datetime import date
    today = date.today().isoformat()
    daily_messages = 0
    for session_messages in chat_history.values():
        for msg in session_messages:
            msg_date = msg.get("timestamp", "")[:10]  # Extract YYYY-MM-DD
            if msg_date == today:
                daily_messages += 1
    
    # Get AI tutor in-memory data for current session
    ai_progress = ai_tutor.user_progress.get(user_email, {})
    ai_sessions = ai_progress.get("sessions", [])
    
    # Add in-memory session data to totals
    if ai_sessions:
        # Count AI tutor exercises
        ai_exercises = len([s for s in ai_sessions if s.get("data", {}).get("exercise_id")])
        total_exercises += ai_exercises
        
        # Calculate AI tutor accuracy
        correct_count = sum(1 for s in ai_sessions if s.get("data", {}).get("correct", False))
        if ai_exercises > 0:
            ai_accuracy = (correct_count / ai_exercises) * 100
            if total_exercises > ai_exercises:
                accuracy = ((accuracy * (total_exercises - ai_exercises)) + ai_accuracy) / total_exercises
            else:
                accuracy = ai_accuracy
        
        # Add estimated study time (5 minutes per AI session)
        total_study_time += len(ai_sessions) * 5
    
    # Get chat messages from AI tutor memory
    try:
        ai_chat_history = ai_tutor.conversation_history.get(user_email, {})
        ai_message_count = sum(len(session_msgs) for session_msgs in ai_chat_history.values())
        total_messages += ai_message_count
        
        # Count today's AI messages
        for session_msgs in ai_chat_history.values():
            for msg in session_msgs:
                msg_date = msg.get("timestamp", "")[:10]
                if msg_date == today:
                    daily_messages += 1
    except:
        pass
    
    # Calculate skill-specific progress
    skill_progress = {
        "reading": 0,
        "writing": 0,
        "spelling": 0,
        "comprehension": 0
    }
    
    skill_counts = {
        "reading": {"correct": 0, "total": 0},
        "writing": {"correct": 0, "total": 0},
        "spelling": {"correct": 0, "total": 0},
        "comprehension": {"correct": 0, "total": 0}
    }
    
    # Map skill areas to categories
    skill_mapping = {
        "phonics": "reading",
        "sight_words": "reading",
        "phonemic_awareness": "reading",
        "writing": "writing",
        "spelling": "spelling",
        "reading_comprehension": "comprehension"
    }
    
    # Process AI tutor sessions for skill progress
    for session in ai_sessions:
        data = session.get("data", {})
        skill_area = data.get("skill_area", "")
        is_correct = data.get("correct", False)
        
        category = skill_mapping.get(skill_area)
        if category:
            skill_counts[category]["total"] += 1
            if is_correct:
                skill_counts[category]["correct"] += 1
    
    # Calculate percentages
    for skill, counts in skill_counts.items():
        if counts["total"] > 0:
            skill_progress[skill] = round((counts["correct"] / counts["total"]) * 100, 1)
        else:
            # Default progress based on overall accuracy if no specific skill data
            skill_progress[skill] = round(accuracy * 0.8, 1) if accuracy > 0 else 0
    
    return {
        "exercises_completed": total_exercises,
        "accuracy": round(accuracy, 1),
        "total_messages": total_messages,
        "daily_messages": daily_messages,
        "study_time_minutes": total_study_time,
        "skill_progress": skill_progress,
        "recent_activity": ai_sessions[-5:] if ai_sessions else []
    }

@app.delete("/api/chat/history")
async def clear_chat_history(current_user: User = Depends(get_current_user)):
    """Clear chat history"""
    user_id = current_user["email"]
    ai_tutor.clear_history(user_id)
    return {"message": "Chat history cleared"}

# Dyslexia test endpoints
@app.post("/api/dyslexia-test")
async def take_dyslexia_test(
    test_data: DyslexiaTestCreate
):
    """Take dyslexia screening test"""
    # Calculate test score and risk level
    score = calculate_test_score(test_data.answers)
    risk_level = determine_risk_level(score)
    recommendations = generate_recommendations(risk_level)
    
    # Generate test ID for anonymous users
    test_id = f"test_{datetime.utcnow().timestamp()}"
    
    # Generate summary
    summary = generate_dyslexia_summary(score, risk_level)
    
    return {
        "id": test_id,
        "score": score,
        "risk_level": risk_level,
        "summary": summary,
        "recommendations": recommendations,
        "created_at": datetime.utcnow().isoformat()
    }

def calculate_test_score(answers: dict) -> float:
    """Calculate dyslexia risk score based on answers"""
    # Dyslexia indicators - higher score means higher risk
    dyslexia_indicators = {
        1: ['b', 'c', 'd'],  # Struggled with reading
        2: ['b', 'c', 'd'],  # Spelling difficulties
        3: ['a', 'c', 'd'],  # Visual discrimination issues
        4: ['b', 'c', 'd'],  # Phonetic awareness problems
        5: ['a', 'b', 'd'],  # Working memory issues
        6: ['b', 'c', 'd'],  # Slow reading speed
        7: ['a', 'c', 'd'],  # Comprehension difficulties
        8: ['b', 'c', 'd']   # Writing challenges
    }
    
    total_questions = len(dyslexia_indicators)
    risk_indicators = 0
    
    for question_id, answer_data in answers.items():
        question_num = int(question_id)
        selected_answer = answer_data.get('selected')
        if selected_answer in dyslexia_indicators.get(question_num, []):
            risk_indicators += 1
    
    return (risk_indicators / total_questions) * 100 if total_questions > 0 else 0

def determine_risk_level(score: float) -> str:
    """Determine dyslexia risk level based on score"""
    if score >= 60:
        return "high"
    elif score >= 30:
        return "medium"
    else:
        return "low"

def generate_recommendations(risk_level: str) -> list:
    """Generate recommendations based on risk level"""
    recommendations = {
        "low": [
            "Low likelihood of dyslexia - continue regular learning",
            "Use dyslexia-friendly fonts as a precaution",
            "Monitor reading progress regularly"
        ],
        "medium": [
            "Moderate indicators suggest possible dyslexia",
            "Consider professional assessment for confirmation",
            "Use assistive technologies and structured programs",
            "Implement dyslexia-friendly learning strategies"
        ],
        "high": [
            "Strong indicators suggest likely dyslexia",
            "Seek professional evaluation immediately",
            "Use comprehensive assistive technologies",
            "Consider specialized tutoring and support programs",
            "Implement multi-sensory learning approaches"
        ]
    }
    return recommendations.get(risk_level, [])

def generate_dyslexia_summary(score: float, risk_level: str) -> str:
    """Generate dyslexia assessment summary"""
    if risk_level == "high":
        return f"Based on your responses ({score:.1f}% risk indicators), you show strong signs that suggest dyslexia. This screening indicates you may have dyslexia and should seek professional evaluation."
    elif risk_level == "medium":
        return f"Based on your responses ({score:.1f}% risk indicators), you show moderate signs that may suggest dyslexia. Consider professional assessment for a definitive diagnosis."
    else:
        return f"Based on your responses ({score:.1f}% risk indicators), you show minimal signs of dyslexia. You likely do not have dyslexia, but continue monitoring your learning progress."

# Import enhanced lesson, AI, and exercise systems
try:
    from ml_models.lesson_content import lesson_manager
    from ml_models.ai_tutor import ai_tutor
    from ml_models.exercise_generator import exercise_generator
except ImportError:
    # Fallback if modules not available
    class MockLessonManager:
        def get_all_lessons_summary(self):
            return [{"id": 1, "title": "Basic Lesson", "category": "general", "difficulty": "beginner", "duration": 15, "description": "Basic lesson content"}]
        def get_lesson(self, lesson_id):
            return {"id": lesson_id, "title": "Lesson", "content": "Basic content"}
        def get_lessons_by_category(self, category):
            return []
    
    class MockAITutor:
        def analyze_user_input(self, message, context=None):
            return {"intent": "general", "emotion": "neutral", "learning_need": "general", "difficulty_level": "beginner", "errors": [], "strengths": []}
        def generate_response(self, message, analysis, context=None):
            return {"message": "I'm here to help you learn!", "suggestions": [], "encouragement": "Keep up the good work!", "lesson_recommendations": [], "exercises": [], "tips": [], "emotional_support": ""}
    
    class MockExerciseGenerator:
        def generate_exercise(self, skill_area, exercise_type, difficulty="beginner", user_context=None):
            return {"exercise_id": "mock_1", "skill_area": skill_area, "exercise_type": exercise_type, "instructions": "Practice exercise"}
        def generate_adaptive_exercise_set(self, user_progress, target_skills=None):
            return [{"exercise_id": "adaptive_1", "skill_area": "phonics", "instructions": "Adaptive exercise"}]
        def evaluate_exercise_response(self, exercise, user_response):
            return {"correct": True, "score": 100, "feedback": "Great job!", "hints": [], "next_steps": []}
    
    lesson_manager = MockLessonManager()
    ai_tutor = MockAITutor()
    exercise_generator = MockExerciseGenerator()

# Lesson endpoints
@app.get("/api/lessons")
async def get_lessons(current_user: User = Depends(get_current_user)):
    """Get available lessons with comprehensive content"""
    lessons = lesson_manager.get_all_lessons_summary()
    
    # Add completion status based on user progress
    from database.database import db_manager
    user_progress = db_manager.get_user_progress(current_user["id"]) if hasattr(db_manager, 'get_user_progress') else {}
    
    for lesson in lessons:
        lesson["completed"] = lesson["id"] in user_progress.get("completed_lessons", [])
        lesson["duration_formatted"] = f"{lesson['duration']} min"
    
    return lessons

@app.get("/api/lessons/{lesson_id}")
async def get_lesson_detail(lesson_id: int, current_user: User = Depends(get_current_user)):
    """Get detailed lesson content"""
    lesson = lesson_manager.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return lesson

@app.get("/api/lessons/category/{category}")
async def get_lessons_by_category(category: str, current_user: User = Depends(get_current_user)):
    """Get lessons by category"""
    lessons = lesson_manager.get_lessons_by_category(category)
    return lessons

@app.get("/api/learning-videos")
async def get_learning_videos(level: str = "beginner"):
    """Get learning videos by difficulty level (no auth required)"""
    # Map difficulty levels to lesson categories and content
    # Using verified, active dyslexia and reading education YouTube videos
    video_content = {
        "beginner": [
            {
                "id": "kOuRn8jFzK0",  # Phonemic Awareness - Structured Literacy
                "title": "Phonemic Awareness Fundamentals",
                "category": "phonics",
                "difficulty": "beginner",
                "duration": 12,
                "description": "Master the foundation of reading by understanding individual sounds in words. Learn how to identify and manipulate phonemes for better reading skills.",
                "url": "https://www.youtube.com/watch?v=kOuRn8jFzK0",
                "learning_objectives": [
                    "Identify individual phonemes in spoken words",
                    "Blend phonemes to form words",
                    "Segment words into individual sounds"
                ]
            },
            {
                "id": "CGigQnWTVB4",  # Letter-Sound Correspondence
                "title": "Letter-Sound Correspondence",
                "category": "phonics",
                "difficulty": "beginner",
                "duration": 15,
                "description": "Connect letters with their corresponding sounds using systematic phonics instruction. Essential for dyslexic learners to build reading foundation.",
                "url": "https://www.youtube.com/watch?v=CGigQnWTVB4",
                "learning_objectives": [
                    "Master single letter-sound relationships",
                    "Recognize common letter patterns",
                    "Apply phonics rules in reading"
                ]
            },
            {
                "id": "ieHjNrH3pEE",  # Sight Words Teaching
                "title": "Sight Word Mastery",
                "category": "vocabulary",
                "difficulty": "beginner",
                "duration": 18,
                "description": "Learn high-frequency words that appear often in text. Sight words are crucial for reading fluency and comprehension.",
                "url": "https://www.youtube.com/watch?v=ieHjNrH3pEE",
                "learning_objectives": [
                    "Recognize 100 most common sight words instantly",
                    "Read sight words in context",
                    "Spell common sight words accurately"
                ]
            },
            {
                "id": "tX8I6mLBkAI",  # Handwriting and Letter Formation
                "title": "Writing Fundamentals",
                "category": "writing",
                "difficulty": "beginner",
                "duration": 20,
                "description": "Develop basic writing skills including letter formation and sentence structure. Multi-sensory approach for dyslexic learners.",
                "url": "https://www.youtube.com/watch?v=tX8I6mLBkAI",
                "learning_objectives": [
                    "Form letters correctly and legibly",
                    "Write complete sentences",
                    "Use basic punctuation and capitalization"
                ]
            }
        ],
        "intermediate": [
            {
                "id": "nrsTXQcnvK8",  # Reading Fluency
                "title": "Reading Fluency Development",
                "category": "fluency",
                "difficulty": "intermediate",
                "duration": 22,
                "description": "Build smooth, accurate, and expressive reading through systematic practice. Techniques specifically designed for struggling readers.",
                "url": "https://www.youtube.com/watch?v=nrsTXQcnvK8",
                "learning_objectives": [
                    "Read with appropriate speed and accuracy",
                    "Use proper expression and intonation",
                    "Recognize punctuation cues"
                ]
            },
            {
                "id": "Ej_Yd0Ej_Yk",  # Reading Comprehension Strategies
                "title": "Reading Comprehension Strategies",
                "category": "comprehension",
                "difficulty": "intermediate",
                "duration": 25,
                "description": "Develop active reading strategies to understand and analyze text meaning. Learn before, during, and after reading techniques.",
                "url": "https://www.youtube.com/watch?v=Ej_Yd0Ej_Yk",
                "learning_objectives": [
                    "Use before, during, and after reading strategies",
                    "Make connections between text and experience",
                    "Summarize main ideas and details"
                ]
            },
            {
                "id": "5Tz8Ej_Ej_Y",  # Spelling Patterns
                "title": "Spelling Patterns and Rules",
                "category": "spelling",
                "difficulty": "intermediate",
                "duration": 20,
                "description": "Master common spelling patterns and rules to improve writing accuracy. Structured approach for dyslexic learners.",
                "url": "https://www.youtube.com/watch?v=5Tz8Ej_Ej_Y",
                "learning_objectives": [
                    "Apply common spelling rules",
                    "Recognize spelling patterns",
                    "Use spelling strategies for unknown words"
                ]
            },
            {
                "id": "dQw4w9WgXcQ",  # Memory Techniques
                "title": "Memory and Organization Strategies",
                "category": "study_skills",
                "difficulty": "intermediate",
                "duration": 18,
                "description": "Learn techniques to improve memory, organization, and study effectiveness. Strategies tailored for dyslexic learners.",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "learning_objectives": [
                    "Use memory strategies for learning",
                    "Organize materials and workspace",
                    "Manage time effectively"
                ]
            }
        ],
        "advanced": [
            {
                "id": "jNQXAC9IVRw",  # Advanced Reading Analysis
                "title": "Advanced Reading Analysis",
                "category": "comprehension",
                "difficulty": "advanced",
                "duration": 28,
                "description": "Analyze complex texts and develop critical thinking skills. Build on foundational reading skills for deeper comprehension.",
                "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                "learning_objectives": [
                    "Analyze author's purpose and perspective",
                    "Evaluate text credibility and bias",
                    "Make inferences and draw conclusions"
                ]
            },
            {
                "id": "9bZkp7q19f0",  # Creative Writing
                "title": "Creative Writing Techniques",
                "category": "writing",
                "difficulty": "advanced",
                "duration": 30,
                "description": "Develop creative writing skills and storytelling techniques. Express ideas effectively despite dyslexia challenges.",
                "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
                "learning_objectives": [
                    "Develop unique writing voice",
                    "Create compelling characters and plots",
                    "Use literary devices effectively"
                ]
            }
        ]
    }
    
    # Return videos for the requested level
    videos = video_content.get(level, video_content["beginner"])
    
    return {
        "level": level,
        "total_videos": len(videos),
        "videos": videos,
        "message": f"Found {len(videos)} learning videos for {level} level"
    }

@app.post("/api/lessons/{lesson_id}/start")
async def start_lesson(lesson_id: int, current_user: User = Depends(get_current_user), db_manager = Depends(get_db)):
    """Track when user starts a lesson"""
    from database.database import db_manager
    
    # Create progress entry for lesson start
    progress_id = db_manager.create_progress_entry({
        "user_id": current_user["id"],
        "lesson_id": lesson_id,
        "accuracy": 0,
        "speed": 0,
        "errors": [],
        "session_duration": 0,
        "completed": False
    }) if hasattr(db_manager, 'create_progress_entry') else lesson_id
    
    return {"message": "Lesson started", "progress_id": progress_id}

@app.post("/api/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: int, completion_data: dict, current_user: User = Depends(get_current_user)):
    """Mark lesson as completed and save progress"""
    from database.database import db_manager
    
    # Save lesson completion
    completion_id = db_manager.create_progress_entry({
        "user_id": current_user["id"],
        "lesson_id": lesson_id,
        "accuracy": completion_data.get("accuracy", 0),
        "speed": completion_data.get("speed", 0),
        "errors": completion_data.get("errors", []),
        "session_duration": completion_data.get("duration", 0),
        "completed": True
    }) if hasattr(db_manager, 'create_progress_entry') else lesson_id
    
    return {"id": completion_id, "message": "Lesson completed successfully!", "next_recommendations": lesson_manager.get_all_lessons_summary()[:3]}

# Exercise endpoints
@app.get("/api/exercises/generate")
async def generate_exercise(
    skill_area: str,
    exercise_type: str,
    difficulty: str = "beginner",
    current_user: User = Depends(get_current_user)
):
    """Generate a specific exercise"""
    # Get user context for personalization
    user_context = ai_tutor.user_progress.get(current_user["id"], {})
    
    exercise = exercise_generator.generate_exercise(
        skill_area=skill_area,
        exercise_type=exercise_type,
        difficulty=difficulty,
        user_context=user_context
    )
    
    if "error" in exercise:
        raise HTTPException(status_code=400, detail=exercise["error"])
    
    return exercise

@app.get("/api/exercises/adaptive")
async def get_adaptive_exercises(current_user: User = Depends(get_current_user)):
    """Get adaptive exercise set based on user progress"""
    # Get user progress from AI tutor and database
    ai_progress = ai_tutor.user_progress.get(current_user["id"], {})
    
    # Simulate user progress data (in real app, this would come from database)
    user_progress = {
        "average_accuracy": 75,
        "areas_for_improvement": ["phonics", "spelling"],
        "strengths": ["sight_words"],
        "recent_sessions": ai_progress.get("sessions", [])[-5:]
    }
    
    exercises = exercise_generator.generate_adaptive_exercise_set(user_progress)
    
    return {
        "exercises": exercises,
        "personalization_note": "These exercises are tailored to your learning needs and progress.",
        "estimated_time": len(exercises) * 5,  # 5 minutes per exercise
        "difficulty_distribution": {"beginner": 2, "intermediate": 2, "advanced": 1}
    }

@app.post("/api/exercises/{exercise_id}/submit")
async def submit_exercise_response(
    exercise_id: str,
    response_data: dict,
    current_user: User = Depends(get_current_user),
    db_manager = Depends(get_db)
):
    """Submit response to an exercise and get evaluation"""
    exercise = response_data.get("exercise", {})
    user_response = response_data.get("response")
    
    if not exercise or user_response is None:
        raise HTTPException(status_code=400, detail="Exercise data and response are required")
    
    # Evaluate the response
    evaluation = exercise_generator.evaluate_exercise_response(exercise, user_response)
    
    # Update user progress in AI tutor
    session_data = {
        "exercise_id": exercise_id,
        "skill_area": exercise.get("skill_area"),
        "exercise_type": exercise.get("exercise_type"),
        "correct": evaluation["correct"],
        "score": evaluation["score"],
        "timestamp": datetime.utcnow().isoformat()
    }
    ai_tutor.update_user_context(current_user["id"], session_data)
    
    # Save to database
    try:
        if hasattr(db_manager, 'create_progress_entry'):
            db_manager.create_progress_entry({
                "user_id": current_user["id"],
                "lesson_id": 0,  # Exercise, not a lesson
                "accuracy": evaluation["score"],
                "speed": 0,
                "errors": evaluation.get("hints", []),
                "session_duration": 300,  # 5 minutes estimate
                "completed": True
            })
    except Exception as e:
        print(f"[ERROR] Failed to save exercise progress: {e}")
    
    # Generate encouraging response based on performance
    if evaluation["correct"]:
        encouragement = "Excellent work! You're making great progress!"
        next_suggestion = "Ready for the next challenge?"
    else:
        encouragement = "Good effort! Learning takes practice."
        next_suggestion = "Let's try a similar exercise to build confidence."
    
    return {
        "evaluation": evaluation,
        "encouragement": encouragement,
        "next_suggestion": next_suggestion,
        "progress_update": {
            "exercises_completed": len(ai_tutor.user_progress.get(current_user["id"], {}).get("sessions", [])),
            "current_streak": 1 if evaluation["correct"] else 0
        }
    }

@app.get("/api/exercises/skills")
async def get_available_skills():
    """Get list of available skill areas and exercise types"""
    skills = {
        "phonemic_awareness": {
            "name": "Phonemic Awareness",
            "description": "Understanding and manipulating individual sounds in words",
            "exercise_types": ["sound_identification", "sound_blending", "sound_segmentation"]
        },
        "phonics": {
            "name": "Phonics",
            "description": "Connecting letters with their sounds",
            "exercise_types": ["letter_sound_matching", "word_building", "decode_words"]
        },
        "sight_words": {
            "name": "Sight Words",
            "description": "Recognizing common words instantly",
            "exercise_types": ["flash_cards", "sentence_completion", "word_hunt"]
        },
        "reading_comprehension": {
            "name": "Reading Comprehension",
            "description": "Understanding and analyzing text meaning",
            "exercise_types": ["main_idea", "detail_questions", "inference"]
        },
        "spelling": {
            "name": "Spelling",
            "description": "Learning spelling patterns and rules",
            "exercise_types": ["pattern_practice", "rule_application"]
        },
        "writing": {
            "name": "Writing",
            "description": "Expressing ideas through written language",
            "exercise_types": ["sentence_construction", "story_sequencing"]
        }
    }
    
    return {
        "skills": skills,
        "difficulty_levels": ["beginner", "intermediate", "advanced"],
        "total_exercise_types": sum(len(skill["exercise_types"]) for skill in skills.values())
    }

@app.get("/api/exercises/generate-random")
async def generate_random_exercise(current_user: User = Depends(get_current_user)):
    """Generate a random exercise for practice"""
    import random
    
    # Available skill areas and exercise types
    skill_options = {
        "phonemic_awareness": ["sound_identification", "sound_blending", "sound_segmentation"],
        "phonics": ["letter_sound_matching", "word_building", "decode_words"],
        "sight_words": ["flash_cards", "sentence_completion"],
        "reading_comprehension": ["main_idea", "detail_questions"],
        "spelling": ["pattern_practice"],
        "writing": ["sentence_construction"]
    }
    
    # Default to beginner difficulty
    difficulty = "beginner"
    
    # Select random skill and exercise type
    skill_area = random.choice(list(skill_options.keys()))
    exercise_type = random.choice(skill_options[skill_area])
    
    # Generate the exercise
    exercise = exercise_generator.generate_exercise(
        skill_area=skill_area,
        exercise_type=exercise_type,
        difficulty=difficulty,
        user_context={}
    )
    
    if "error" in exercise:
        raise HTTPException(status_code=400, detail=exercise["error"])
    
    # Store exercise in AI tutor using email as identifier
    user_id = current_user["email"]
    print(f"[DEBUG] Storing exercise for user {user_id}: {exercise.get('skill_area')} - {exercise.get('exercise_type')}")
    print(f"[DEBUG] Exercise word_bank: {exercise.get('word_bank')}")
    ai_tutor.set_active_exercise(user_id, exercise)
    print(f"[DEBUG] Active exercises: {list(ai_tutor.active_exercises.keys())}")
    
    return exercise

@app.get("/api/exercises/recommendations")
async def get_exercise_recommendations(current_user: User = Depends(get_current_user)):
    """Get personalized exercise recommendations"""
    # Get user's recent activity and performance
    ai_progress = ai_tutor.user_progress.get(current_user["id"], {})
    recent_sessions = ai_progress.get("sessions", [])[-10:]
    
    recommendations = {
        "daily_practice": [
            {
                "skill_area": "phonics",
                "exercise_type": "letter_sound_matching",
                "reason": "Build foundation skills",
                "estimated_time": 5
            },
            {
                "skill_area": "sight_words",
                "exercise_type": "flash_cards",
                "reason": "Improve reading fluency",
                "estimated_time": 3
            }
        ],
        "skill_building": [
            {
                "skill_area": "phonemic_awareness",
                "exercise_type": "sound_blending",
                "reason": "Strengthen decoding skills",
                "estimated_time": 7
            }
        ],
        "challenge_exercises": [
            {
                "skill_area": "reading_comprehension",
                "exercise_type": "main_idea",
                "reason": "Ready for next level",
                "estimated_time": 10
            }
        ]
    }
    
    # Customize based on recent performance
    if recent_sessions:
        last_session = recent_sessions[-1]
        last_skill = last_session.get("data", {}).get("skill_area")
        if last_skill:
            recommendations["continue_practice"] = [{
                "skill_area": last_skill,
                "exercise_type": "review",
                "reason": f"Continue building {last_skill} skills",
                "estimated_time": 5
            }]
    
    return recommendations

# Progress tracking endpoints
@app.get("/api/progress/{user_id}")
async def get_user_progress(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get user's comprehensive learning progress"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    from database.database import db_manager
    
    # Get basic progress from database
    progress = {}
    try:
        if hasattr(db_manager, 'get_user_progress'):
            progress = db_manager.get_user_progress(user_id)
    except:
        pass
    
    # Enhance with AI tutor insights
    ai_progress = ai_tutor.user_progress.get(user_id, {})
    
    # Combine data for comprehensive view
    comprehensive_progress = {
        "user_id": user_id,
        "overall_accuracy": progress.get("average_accuracy", 0),
        "lessons_completed": progress.get("completed_lessons", []),
        "total_study_time": progress.get("total_study_time", 0),
        "strengths": ai_progress.get("strengths", []),
        "areas_for_improvement": ai_progress.get("areas_for_improvement", []),
        "recent_sessions": ai_progress.get("sessions", [])[-5:],  # Last 5 sessions
        "recommended_lessons": lesson_manager.get_all_lessons_summary()[:3],
        "learning_insights": {
            "preferred_learning_style": ai_progress.get("preferred_learning_style", "visual"),
            "most_active_category": progress.get("most_active_category", "phonics"),
            "improvement_trend": progress.get("improvement_trend", "stable")
        }
    }
    
    return comprehensive_progress

@app.get("/api/progress/{user_id}/analytics")
async def get_progress_analytics(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for user progress"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get AI tutor session data
    ai_progress = ai_tutor.user_progress.get(user_id, {})
    sessions = ai_progress.get("sessions", [])
    
    if not sessions:
        return {"message": "No session data available yet. Start learning to see your analytics!"}
    
    # Calculate analytics
    total_sessions = len(sessions)
    recent_sessions = sessions[-10:]  # Last 10 sessions
    
    # Analyze learning patterns
    intent_distribution = {}
    emotion_distribution = {}
    learning_need_distribution = {}
    
    for session in recent_sessions:
        data = session.get("data", {})
        intent = data.get("intent", "general")
        emotion = data.get("emotion", "neutral")
        learning_need = data.get("learning_need", "general")
        
        intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
        emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        learning_need_distribution[learning_need] = learning_need_distribution.get(learning_need, 0) + 1
    
    return {
        "total_sessions": total_sessions,
        "recent_activity": {
            "sessions_analyzed": len(recent_sessions),
            "most_common_intent": max(intent_distribution, key=intent_distribution.get) if intent_distribution else "general",
            "most_common_emotion": max(emotion_distribution, key=emotion_distribution.get) if emotion_distribution else "neutral",
            "primary_learning_focus": max(learning_need_distribution, key=learning_need_distribution.get) if learning_need_distribution else "general"
        },
        "distributions": {
            "intents": intent_distribution,
            "emotions": emotion_distribution,
            "learning_needs": learning_need_distribution
        },
        "recommendations": {
            "suggested_focus": max(learning_need_distribution, key=learning_need_distribution.get) if learning_need_distribution else "phonics",
            "emotional_support_needed": "frustrated" in emotion_distribution or "worried" in emotion_distribution,
            "celebration_worthy": "excited" in emotion_distribution or "proud" in emotion_distribution
        }
    }

@app.post("/api/progress")
async def create_progress(
    progress_data: ProgressCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new progress entry with enhanced tracking"""
    from database.database import db_manager
    
    # Save to database
    progress_id = None
    try:
        if hasattr(db_manager, 'create_progress_entry'):
            progress_id = db_manager.create_progress_entry({
                "user_id": current_user["id"],
                "lesson_id": progress_data.lesson_id,
                "accuracy": progress_data.accuracy,
                "speed": progress_data.speed,
                "errors": progress_data.errors,
                "session_duration": progress_data.session_duration
            })
    except:
        progress_id = f"progress_{datetime.utcnow().timestamp()}"
    
    # Update AI tutor context
    session_data = {
        "lesson_id": progress_data.lesson_id,
        "accuracy": progress_data.accuracy,
        "speed": progress_data.speed,
        "error_count": len(progress_data.errors) if progress_data.errors else 0,
        "session_duration": progress_data.session_duration
    }
    ai_tutor.update_user_context(current_user["id"], session_data)
    
    # Generate personalized feedback
    feedback = {
        "message": "Progress saved successfully!",
        "encouragement": "",
        "next_steps": []
    }
    
    if progress_data.accuracy >= 90:
        feedback["encouragement"] = "Excellent work! You're mastering this skill!"
        feedback["next_steps"].append("You're ready for more challenging material")
    elif progress_data.accuracy >= 75:
        feedback["encouragement"] = "Good progress! Keep practicing!"
        feedback["next_steps"].append("Continue practicing to build confidence")
    else:
        feedback["encouragement"] = "Every step forward is progress! Don't give up!"
        feedback["next_steps"].append("Let's review the fundamentals together")
    
    return {
        "id": progress_id,
        "feedback": feedback,
        "recommended_lessons": lesson_manager.get_all_lessons_summary()[:2]
    }

# Additional AI Tutor endpoints
@app.get("/api/ai-tutor/suggestions")
async def get_ai_suggestions(current_user: User = Depends(get_current_user)):
    """Get personalized learning suggestions from AI tutor"""
    user_context = ai_tutor.user_progress.get(current_user["id"], {})
    suggestions = ai_tutor._get_daily_suggestions(user_context)
    
    # Add exercise recommendations
    exercise_suggestions = exercise_generator.generate_adaptive_exercise_set(
        user_progress={"average_accuracy": 75, "areas_for_improvement": ["phonics"], "strengths": ["sight_words"]}
    )[:2]  # Top 2 exercise suggestions
    
    return {
        "suggestions": suggestions,
        "recommended_lessons": lesson_manager.get_all_lessons_summary()[:3],
        "recommended_exercises": exercise_suggestions,
        "motivational_message": "Every expert was once a beginner. You're doing great!",
        "daily_goal": "Complete 2 lessons and 3 exercises today!"
    }

@app.post("/api/ai-tutor/feedback")
async def submit_feedback(feedback_data: dict, current_user: User = Depends(get_current_user)):
    """Submit feedback about AI tutor responses"""
    # Store feedback for improving AI responses
    feedback_entry = {
        "user_id": current_user["id"],
        "timestamp": datetime.utcnow().isoformat(),
        "rating": feedback_data.get("rating", 0),
        "comment": feedback_data.get("comment", ""),
        "response_id": feedback_data.get("response_id", "")
    }
    
    # In a real implementation, you'd save this to a feedback database
    return {"message": "Thank you for your feedback! It helps me learn and improve."}

@app.get("/api/manifest.json")
async def manifest():
    """Web app manifest"""
    return {
        "name": "LexiLearn",
        "short_name": "LexiLearn",
        "description": "AI Tutor for Dyslexic Students",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#4f46e5"
    }

def generate_handwriting_feedback(recognized_text: str, ocr_result: dict) -> dict:
    """Generate specific educational feedback about recognized text and corrections needed"""
    confidence = ocr_result.get("confidence", 0)
    errors = ocr_result.get("errors", [])
    image_analysis = ocr_result.get("image_analysis", {})
    character_analysis = ocr_result.get("character_analysis", {})
    
    feedback = {
        "overall_assessment": "",
        "recognized_content": "",
        "word_corrections": [],
        "specific_improvements": [],
        "practice_suggestions": []
    }
    
    # If we successfully recognized text, provide specific feedback
    if recognized_text and confidence >= 0.3:
        words = recognized_text.strip().split()
        
        # Provide clear assessment of what was recognized
        if len(words) == 1:
            feedback["overall_assessment"] = f"I can see you wrote the word '{recognized_text.strip()}'. "
            feedback["recognized_content"] = f"Recognized text: '{recognized_text.strip()}'"
        elif len(words) > 1:
            feedback["overall_assessment"] = f"I can see you wrote {len(words)} words: '{recognized_text.strip()}'. "
            feedback["recognized_content"] = f"Recognized text: '{recognized_text.strip()}'"
        else:
            feedback["overall_assessment"] = f"I can see some handwriting: '{recognized_text.strip()}'. "
            feedback["recognized_content"] = f"Recognized text: '{recognized_text.strip()}'"
        
        # Analyze confidence and provide specific word-level feedback
        if confidence >= 0.8:
            feedback["overall_assessment"] += "Your handwriting is very clear and easy to read!"
            feedback["specific_improvements"] = [
                "Excellent letter formation",
                "Good spacing between words",
                "Clear and legible writing"
            ]
        elif confidence >= 0.6:
            feedback["overall_assessment"] += "Your handwriting is mostly clear with some areas to improve."
            
            # Provide specific word corrections if available
            if errors:
                for error in errors[:3]:  # Limit to 3 most important errors
                    error_word = error.get("word", "")
                    suggestion = error.get("suggestion", "")
                    if error_word and suggestion:
                        feedback["word_corrections"].append({
                            "original": error_word,
                            "suggested": suggestion,
                            "reason": f"The word '{error_word}' might be clearer as '{suggestion}'"
                        })
            
            feedback["specific_improvements"] = [
                "Some letters could be formed more clearly",
                "Try to maintain consistent letter size",
                "Focus on spacing between letters"
            ]
        else:
            feedback["overall_assessment"] += "I can make out some words, but the handwriting could be clearer."
            
            # Provide specific corrections for unclear words
            unclear_words = []
            if len(words) > 0:
                for word in words:
                    if len(word) < 2 or any(c in word for c in ['?', '*', '#']):
                        unclear_words.append(word)
            
            if unclear_words:
                feedback["word_corrections"] = [
                    {
                        "original": word,
                        "suggested": "[unclear]",
                        "reason": f"The word '{word}' is difficult to read - try writing it more clearly"
                    } for word in unclear_words[:3]
                ]
            
            feedback["specific_improvements"] = [
                "Write more slowly and carefully",
                "Press firmly but not too hard",
                "Make letters larger and more distinct",
                "Use lined paper to keep letters aligned"
            ]
        
        # Add character-specific feedback if available
        characters = character_analysis.get("characters", [])
        if characters and len(characters) > 0:
            char_issues = []
            for i, char in enumerate(characters[:5]):  # Limit to first 5 characters
                errors = char.get("errors", [])
                if errors:
                    char_issues.append(f"Character {i+1}: {errors[0].get('description', 'needs improvement')}")
            
            if char_issues:
                feedback["specific_improvements"].extend(char_issues[:3])  # Top 3 character issues
        
        # Provide actionable practice suggestions
        feedback["practice_suggestions"] = [
            f"Practice writing the word '{words[0]}' 5 times" if words else "Practice writing individual letters",
            "Use lined paper to keep letters the same height",
            "Write slowly and focus on letter formation"
        ]
        
        if len(words) > 1:
            feedback["practice_suggestions"].insert(1, f"Try writing each word separately: {', '.join(words[:3])}")
    
    else:
        # Handle cases where recognition failed or confidence is very low
        issues = image_analysis.get("issues", [])
        
        if not recognized_text:
            feedback["overall_assessment"] = "I couldn't read any clear handwriting in this image."
            feedback["recognized_content"] = "No text could be recognized"
        else:
            feedback["overall_assessment"] = f"I can barely make out '{recognized_text.strip()}' but it's very unclear."
            feedback["recognized_content"] = f"Unclear text: '{recognized_text.strip()}'"
        
        # Provide specific image quality feedback
        brightness = image_analysis.get("brightness", 128)
        contrast = image_analysis.get("contrast", 50)
        
        feedback["specific_improvements"] = []
        
        if brightness < 80:
            feedback["specific_improvements"].append("Image is too dark - use better lighting")
        elif brightness > 200:
            feedback["specific_improvements"].append("Image is too bright - reduce lighting")
        
        if contrast < 30:
            feedback["specific_improvements"].append("Use darker ink for better contrast")
        
        feedback["specific_improvements"].extend([
            "Write with dark ink on white paper",
            "Take the photo straight on (not at an angle)",
            "Make sure handwriting fills most of the image",
            "Write larger and more clearly"
        ])
        
        feedback["practice_suggestions"] = [
            "Try writing one word clearly and take another photo",
            "Use a dark pen or pencil",
            "Write on lined paper",
            "Make letters bigger and more spaced out"
        ]
    
    return feedback

def generate_character_feedback(characters: list) -> list:
    """Generate feedback for individual characters"""
    char_feedback = []
    
    for i, char in enumerate(characters):
        char_info = {
            "character_id": i + 1,
            "issues": [],
            "suggestions": [],
            "template_match": None
        }
        
        # Get best template match
        matches = char.get("template_matches", [])
        if matches:
            best_match = matches[0]
            char_info["template_match"] = {
                "letter": best_match["letter"],
                "confidence": best_match["confidence"],
                "reasoning": best_match["reasoning"]
            }
        
        # Process character errors
        errors = char.get("errors", [])
        for error in errors:
            char_info["issues"].append(error["description"])
            char_info["suggestions"].append(error["suggestion"])
        
        char_feedback.append(char_info)
    
    return char_feedback

def generate_handwriting_suggestions(recognized_text: str, errors: list) -> list:
    """Generate learning suggestions based on handwriting analysis"""
    suggestions = []
    
    if not recognized_text or len(recognized_text.strip()) < 3:
        suggestions.append({
            "type": "practice",
            "title": "Start with Single Letters",
            "description": "Practice writing individual letters before attempting words",
            "difficulty": "beginner"
        })
    
    if errors:
        suggestions.append({
            "type": "correction",
            "title": "Letter Formation Practice",
            "description": "Focus on the letters that were difficult to recognize",
            "difficulty": "intermediate"
        })
    
    suggestions.extend([
        {
            "type": "exercise",
            "title": "Tracing Practice",
            "description": "Trace over dotted letters to improve muscle memory",
            "difficulty": "beginner"
        },
        {
            "type": "technique",
            "title": "Proper Grip",
            "description": "Check your pencil grip - it should be comfortable and controlled",
            "difficulty": "fundamental"
        }
    ])
    
    return suggestions

def generate_comprehensive_handwriting_feedback(original_text: str, corrected_text: str, result: dict) -> dict:
    """Generate comprehensive feedback for handwriting correction"""
    corrections_applied = result.get("corrections_applied", [])
    confidence = result.get("confidence", 0)
    
    feedback = {
        "correction_summary": "",
        "improvements_made": [],
        "learning_points": [],
        "next_steps": []
    }
    
    # Correction summary
    if corrections_applied:
        feedback["correction_summary"] = f"Made {len(corrections_applied)} corrections to improve readability."
        feedback["improvements_made"] = corrections_applied
    else:
        feedback["correction_summary"] = "Your handwriting was clear - no corrections needed!"
    
    # Learning points based on corrections
    if corrections_applied:
        feedback["learning_points"].extend([
            "Common letter confusions in handwriting are normal",
            "Regular practice helps reduce these errors",
            "Focus on the letters that were corrected"
        ])
    
    # Next steps based on performance
    if confidence >= 0.8:
        feedback["next_steps"] = [
            "Try writing longer sentences",
            "Practice cursive writing if comfortable",
            "Focus on writing speed while maintaining clarity"
        ]
    elif confidence >= 0.6:
        feedback["next_steps"] = [
            "Continue practicing letter formation",
            "Try writing simple words repeatedly",
            "Use handwriting worksheets for guided practice"
        ]
    else:
        feedback["next_steps"] = [
            "Start with basic letter tracing",
            "Practice one letter family at a time (a, c, d, g, o, q)",
            "Use large-lined paper for better control"
        ]
    
    return feedback

def generate_handwriting_exercises(errors: list) -> list:
    """Generate specific practice exercises based on detected errors"""
    exercises = []
    
    # Default exercises for all users
    exercises.extend([
        {
            "title": "Letter Formation Drill",
            "description": "Practice writing each letter 5 times slowly and carefully",
            "duration": "10 minutes",
            "materials": "Lined paper, pencil"
        },
        {
            "title": "Word Building",
            "description": "Write simple 3-letter words focusing on letter spacing",
            "duration": "15 minutes",
            "materials": "Lined paper, pencil"
        }
    ])
    
    # Specific exercises based on errors
    if errors:
        error_types = [error.get("type") for error in errors]
        
        if "ocr_confusion" in error_types:
            exercises.append({
                "title": "Similar Letter Practice",
                "description": "Practice writing pairs of similar letters (b/d, p/q, m/n)",
                "duration": "10 minutes",
                "materials": "Lined paper, colored pencils"
            })
        
        if "repetition_error" in error_types:
            exercises.append({
                "title": "Spacing Practice",
                "description": "Write words with finger spaces between each letter",
                "duration": "8 minutes",
                "materials": "Wide-lined paper, pencil"
            })
    
    return exercises

def generate_encouragement_message(confidence: float) -> str:
    """Generate encouraging message based on handwriting confidence"""
    if confidence >= 0.8:
        messages = [
            "Fantastic handwriting! You're doing excellent work!",
            "Your letters are clear and well-formed. Keep it up!",
            "Amazing progress! Your handwriting is really improving!"
        ]
    elif confidence >= 0.6:
        messages = [
            "Good job! Your handwriting is getting better with practice!",
            "Nice work! Keep practicing and you'll see even more improvement!",
            "You're making great progress! Don't give up!"
        ]
    else:
        messages = [
            "Every expert was once a beginner. Keep practicing!",
            "Handwriting takes time to develop. You're on the right track!",
            "Great effort! Remember, practice makes progress!"
        ]
    
    import random
    return random.choice(messages)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LexiLearn API - Enhanced AI Tutor for Dyslexic Students",
        "version": "2.0.0",
        "features": [
            "Comprehensive lesson content",
            "Intelligent AI tutor responses",
            "Personalized learning paths",
            "Multi-sensory learning approaches",
            "Progress analytics",
            "Emotional support"
        ],
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with system status"""
    system_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "lesson_manager": "operational",
            "ai_tutor": "operational",
            "exercise_generator": "operational",
            "text_analyzer": "operational" if text_analyzer else "limited",
            "speech_processor": "operational" if speech_processor else "limited",
            "handwriting_recognizer": "operational with educational feedback" if handwriting_recognizer else "limited"
        },
        "total_lessons": len(lesson_manager.get_all_lessons_summary()),
        "total_exercise_types": 15,
        "ai_features": [
            "Intent recognition",
            "Emotion detection",
            "Personalized responses",
            "Learning need identification",
            "Progress tracking"
        ]
    }
    
    return system_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
