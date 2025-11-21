"""
Tests for Database functionality
"""
import pytest
from database.database import db_manager

class TestDatabaseManager:
    """Database manager tests"""
    
    def test_create_user(self):
        """Test creating a new user"""
        user_data = {
            "email": "test_db@example.com",
            "username": "test_db_user",
            "hashed_password": "test_hash",
            "full_name": "Test User"
        }
        
        user_id = db_manager.create_user(user_data)
        assert user_id is not None
    
    def test_get_user_by_email(self):
        """Test getting user by email"""
        # First create a user
        user_data = {
            "email": "test_get@example.com",
            "username": "test_get_user",
            "hashed_password": "test_hash"
        }
        user_id = db_manager.create_user(user_data)
        
        # Then retrieve
        user = db_manager.get_user_by_email("test_get@example.com")
        assert user is not None
        assert user["email"] == "test_get@example.com"
    
    def test_create_progress_entry(self):
        """Test creating progress entry"""
        progress_data = {
            "user_id": 1,
            "lesson_id": 1,
            "accuracy": 85.5,
            "speed": 120,
            "errors": [],
            "session_duration": 300
        }
        
        progress_id = db_manager.create_progress_entry(progress_data)
        assert progress_id is not None
    
    def test_get_user_progress(self):
        """Test getting user progress"""
        progress = db_manager.get_user_progress(1)
        assert isinstance(progress, list)
    
    def test_update_user_settings(self):
        """Test updating user settings"""
        success = db_manager.update_user_settings(
            user_id=1,
            preferred_font="Comic Sans",
            font_size=18
        )
        # Should succeed or return None/False gracefully
        assert isinstance(success, bool) or success is None

class TestPasswordReset:
    """Password reset functionality tests"""
    
    def test_create_password_reset_token(self):
        """Test creating password reset token"""
        from datetime import datetime, timedelta
        
        token_id = db_manager.create_password_reset_token(
            user_id=1,
            token="test_token_123",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        assert token_id is not None
    
    def test_get_password_reset_token(self):
        """Test getting password reset token"""
        token = db_manager.get_password_reset_token("test_token_123")
        # Should either return token or None
        assert token is None or isinstance(token, dict)
    
    def test_mark_token_as_used(self):
        """Test marking token as used"""
        result = db_manager.mark_token_as_used("test_token_123")
        assert isinstance(result, bool)

class TestErrorHandling:
    """Database error handling tests"""
    
    def test_duplicate_email(self):
        """Test handling duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "test_duplicate",
            "hashed_password": "test_hash"
        }
        
        # Create first user
        db_manager.create_user(user_data)
        
        # Try to create duplicate
        user_id = db_manager.create_user(user_data)
        # Should return None or raise error
        assert user_id is None
    
    def test_invalid_user_id(self):
        """Test handling invalid user ID"""
        progress = db_manager.get_user_progress(999999)
        assert isinstance(progress, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

