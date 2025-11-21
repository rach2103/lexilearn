import sqlite3
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from config import settings

class DatabaseManager:
    """Lightweight database manager with pluggable backends"""
    
    def __init__(self):
        self.db_type = settings.DATABASE_TYPE
        self.connection_string = settings.DATABASE_URL
        self.setup_database()
    
    def setup_database(self):
        """Initialize database based on type"""
        if self.db_type == "sqlite":
            self.setup_sqlite()
        elif self.db_type == "postgresql":
            self.setup_postgresql()
        elif self.db_type == "mongodb":
            self.setup_mongodb()
    
    def setup_sqlite(self):
        """Setup SQLite database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    preferences TEXT,  -- JSON string
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    lesson_type TEXT,
                    difficulty_level TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    lesson_id INTEGER,
                    accuracy REAL,
                    speed REAL,
                    errors TEXT,  -- JSON string
                    session_duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT UNIQUE,
                    messages TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    original_text TEXT,
                    corrected_text TEXT,
                    error_types TEXT,  -- JSON string
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dyslexia_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    test_type TEXT,
                    answers TEXT,  -- JSON string
                    score REAL,
                    risk_level TEXT,
                    recommendations TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def setup_postgresql(self):
        """Setup PostgreSQL (simplified version)"""
        try:
            import psycopg2
            # Similar table creation but with PostgreSQL syntax
            pass
        except ImportError:
            raise ImportError("psycopg2-binary required for PostgreSQL support")
    
    def setup_mongodb(self):
        """Setup MongoDB (simplified version)"""
        try:
            import pymongo
            # MongoDB collection setup
            pass
        except ImportError:
            raise ImportError("pymongo required for MongoDB support")
    
    @contextmanager
    def get_connection(self):
        """Get database connection based on type"""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.connection_string.replace("sqlite:///", ""))
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()
        else:
            # Add other database connection logic here
            pass
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """Create new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            preferences = json.dumps({
                "preferred_font": user_data.get("preferred_font", "OpenDyslexic"),
                "font_size": user_data.get("font_size", 16),
                "line_spacing": user_data.get("line_spacing", 1.5),
                "color_scheme": user_data.get("color_scheme", "high_contrast"),
                "language_preference": user_data.get("language_preference", "en")
            })
            
            try:
                cursor.execute('''
                    INSERT INTO users (email, username, hashed_password, full_name, preferences)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_data["email"],
                    user_data["username"],
                    user_data["hashed_password"],
                    user_data.get("full_name", ""),
                    preferences
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            
            if row:
                user = dict(row)
                preferences = json.loads(user["preferences"]) if user["preferences"] else {}
                # Merge preferences into user object for easy access
                user["preferred_font"] = preferences.get("preferred_font", "OpenDyslexic")
                user["font_size"] = preferences.get("font_size", 16)
                user["line_spacing"] = preferences.get("line_spacing", 1.5)
                user["color_scheme"] = preferences.get("color_scheme", "high_contrast")
                user["language_preference"] = preferences.get("language_preference", "en")
                user["preferences"] = preferences
                return user
            return None
    
    def create_progress_entry(self, progress_data: Dict[str, Any]) -> int:
        """Create progress entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO progress (user_id, lesson_id, accuracy, speed, errors, session_duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                progress_data["user_id"],
                progress_data["lesson_id"],
                progress_data["accuracy"],
                progress_data["speed"],
                json.dumps(progress_data["errors"]),
                progress_data["session_duration"]
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's progress data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, l.title as lesson_title 
                FROM progress p 
                JOIN lessons l ON p.lesson_id = l.id 
                WHERE p.user_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            progress_list = []
            
            for row in rows:
                progress = dict(row)
                progress["errors"] = json.loads(progress["errors"]) if progress["errors"] else {}
                progress_list.append(progress)
            
            return progress_list
    
    def save_error_correction(self, correction_data: Dict[str, Any]) -> int:
        """Save error correction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO error_corrections (user_id, original_text, corrected_text, error_types, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                correction_data["user_id"],
                correction_data["original_text"],
                correction_data["corrected_text"],
                json.dumps(correction_data["error_types"]),
                correction_data["confidence_score"]
            ))
            conn.commit()
            return cursor.lastrowid
    
    def create_dyslexia_test(self, user_id: int, test_type: str, answers: dict, score: float, risk_level: str, recommendations: list) -> int:
        """Create dyslexia test result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO dyslexia_tests (user_id, test_type, answers, score, risk_level, recommendations)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                test_type,
                json.dumps(answers),
                score,
                risk_level,
                json.dumps(recommendations)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def create_password_reset_token(self, user_id: int, token: str, expires_at: datetime) -> int:
        """Create password reset token"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, token, expires_at))
            conn.commit()
            return cursor.lastrowid
    
    def get_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get password reset token"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM password_reset_tokens 
                WHERE token = ? AND used = FALSE AND expires_at > datetime('now')
            ''', (token,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def mark_token_as_used(self, token: str) -> bool:
        """Mark password reset token as used"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE password_reset_tokens SET used = TRUE WHERE token = ?
            ''', (token,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET hashed_password = ? WHERE id = ?
            ''', (hashed_password, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_user_settings(self, user_id: int, full_name: str = None, preferred_font: str = None, 
                            font_size: int = None, line_spacing: float = None, 
                            color_scheme: str = None, language_preference: str = None) -> bool:
        """Update user settings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current preferences
            cursor.execute('SELECT preferences FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            preferences = json.loads(row[0]) if row[0] else {}
            
            # Update preferences
            if preferred_font is not None:
                preferences["preferred_font"] = preferred_font
            if font_size is not None:
                preferences["font_size"] = font_size
            if line_spacing is not None:
                preferences["line_spacing"] = line_spacing
            if color_scheme is not None:
                preferences["color_scheme"] = color_scheme
            if language_preference is not None:
                preferences["language_preference"] = language_preference
            
            # Update user
            if full_name is not None:
                cursor.execute('''
                    UPDATE users SET full_name = ?, preferences = ? WHERE id = ?
                ''', (full_name, json.dumps(preferences), user_id))
            else:
                cursor.execute('''
                    UPDATE users SET preferences = ? WHERE id = ?
                ''', (json.dumps(preferences), user_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def save_chat_message(self, user_id: int, session_id: str, user_message: str, bot_response: str) -> bool:
        """Save a single chat message to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if session exists
            cursor.execute('SELECT id, messages FROM chat_sessions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            
            message_data = {
                "user": user_message,
                "bot": bot_response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if row:
                # Update existing session
                messages = json.loads(row[1]) if row[1] else []
                messages.append(message_data)
                
                cursor.execute('''
                    UPDATE chat_sessions SET messages = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE session_id = ?
                ''', (json.dumps(messages), session_id))
            else:
                # Create new session
                cursor.execute('''
                    INSERT INTO chat_sessions (user_id, session_id, messages)
                    VALUES (?, ?, ?)
                ''', (user_id, session_id, json.dumps([message_data])))
            
            conn.commit()
            return True
    
    def load_chat_history(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Load all chat history for a user organized by session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, messages FROM chat_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            history = {}
            
            for row in rows:
                session_id = row[0]
                messages = json.loads(row[1]) if row[1] else []
                history[session_id] = messages
            
            return history

# Initialize database manager
db_manager = DatabaseManager()

# FastAPI dependency functions
def get_db():
    """FastAPI dependency to get database manager"""
    return db_manager

def create_tables():
    """Create database tables"""
    db_manager.setup_database()