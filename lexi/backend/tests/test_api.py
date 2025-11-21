"""
Comprehensive API tests for LexiLearn backend
"""
import pytest
import sys
import os

# Ensure test environment is set
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["DATABASE_URL"] = "sqlite:///test_lexi.db"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuth:
    """Authentication endpoint tests"""
    
    def test_register_user(self):
        """Test user registration"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "full_name": "Test User"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_user(self):
        """Test user login"""
        # First register
        client.post("/auth/register", json={
            "email": "test2@example.com",
            "username": "testuser2",
            "password": "TestPassword123"
        })
        
        # Then login
        response = client.post("/auth/login", json={
            "email": "test2@example.com",
            "password": "TestPassword123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_invalid_credentials(self):
        """Test invalid login credentials"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 400

class TestChat:
    """Chat endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/auth/register", json={
            "email": "chattest@example.com",
            "username": "chattest",
            "password": "TestPassword123"
        })
        response = client.post("/auth/login", json={
            "email": "chattest@example.com",
            "password": "TestPassword123"
        })
        return response.json()["access_token"]
    
    def test_send_chat_message(self, auth_token):
        """Test sending chat message"""
        response = client.post(
            "/api/chat/message",
            json={"message": "Hello, I need help with reading"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "ai_analysis" in response.json()
    
    def test_get_chat_history(self, auth_token):
        """Test getting chat history"""
        response = client.get(
            "/api/chat/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert "history" in response.json()
    
    def test_clear_chat_history(self, auth_token):
        """Test clearing chat history"""
        response = client.delete(
            "/api/chat/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

class TestUserStats:
    """User statistics endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/auth/register", json={
            "email": "stats@example.com",
            "username": "statsuser",
            "password": "TestPassword123"
        })
        response = client.post("/auth/login", json={
            "email": "stats@example.com",
            "password": "TestPassword123"
        })
        return response.json()["access_token"]
    
    def test_get_user_stats(self, auth_token):
        """Test getting user statistics"""
        response = client.get(
            "/api/user/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "exercises_completed" in data
        assert "accuracy" in data
        assert "skill_progress" in data
    
    def test_get_user_profile(self, auth_token):
        """Test getting user profile"""
        response = client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data

class TestExercises:
    """Exercise endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/auth/register", json={
            "email": "exercise@example.com",
            "username": "exerciseuser",
            "password": "TestPassword123"
        })
        response = client.post("/auth/login", json={
            "email": "exercise@example.com",
            "password": "TestPassword123"
        })
        return response.json()["access_token"]
    
    def test_generate_exercise(self, auth_token):
        """Test generating an exercise"""
        response = client.get(
            "/api/exercises/generate",
            params={"skill_area": "phonics", "exercise_type": "word_building", "difficulty": "beginner"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "skill_area" in data
        assert "exercise_type" in data
    
    def test_get_adaptive_exercises(self, auth_token):
        """Test getting adaptive exercises"""
        response = client.get(
            "/api/exercises/adaptive",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert "exercises" in response.json()

class TestProgress:
    """Progress tracking endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/auth/register", json={
            "email": "progress@example.com",
            "username": "progressuser",
            "password": "TestPassword123"
        })
        response = client.post("/auth/login", json={
            "email": "progress@example.com",
            "password": "TestPassword123"
        })
        return response.json()["access_token"]
    
    def test_submit_progress(self, auth_token):
        """Test submitting progress"""
        response = client.post(
            "/api/progress",
            json={
                "lesson_id": 1,
                "accuracy": 85.5,
                "speed": 120,
                "errors": [],
                "session_duration": 300
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

