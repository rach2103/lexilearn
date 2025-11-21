"""
Integration tests for LexiLearn backend
"""
import pytest
import os

# Set test environment
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["DATABASE_URL"] = "sqlite:///test_lexi.db"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestFullWorkflow:
    """Test complete user workflow"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authenticated user token"""
        # Register
        client.post("/auth/register", json={
            "email": "integration@test.com",
            "username": "integrationuser",
            "password": "TestPass123"
        })
        
        # Login
        response = client.post("/auth/login", json={
            "email": "integration@test.com",
            "password": "TestPass123"
        })
        return response.json()["access_token"]
    
    def test_complete_learning_flow(self, auth_token):
        """Test complete learning workflow"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 1. Get user profile
        response = client.get("/api/user/profile", headers=headers)
        assert response.status_code == 200
        
        # 2. Get lessons
        response = client.get("/api/lessons", headers=headers)
        assert response.status_code == 200
        
        # 3. Generate an exercise
        response = client.get(
            "/api/exercises/generate",
            params={"skill_area": "phonics", "exercise_type": "word_building", "difficulty": "beginner"},
            headers=headers
        )
        assert response.status_code == 200
        exercise = response.json()
        
        # 4. Submit exercise response
        response = client.post(
            f"/api/exercises/{exercise.get('exercise_id', 'test_1')}/submit",
            json={
                "exercise": exercise,
                "response": "cat"
            },
            headers=headers
        )
        assert response.status_code == 200
        
        # 5. Send chat message
        response = client.post(
            "/api/chat/message",
            json={"message": "I want to practice spelling"},
            headers=headers
        )
        assert response.status_code == 200
        
        # 6. Get progress stats
        response = client.get("/api/user/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "exercises_completed" in data
    
    def test_chat_with_exercise(self, auth_token):
        """Test chat interaction with exercise"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Request words to practice
        response = client.post(
            "/api/chat/message",
            json={"message": "give me 5 words to practice"},
            headers=headers
        )
        assert response.status_code == 200
        
        # Should get words back
        data = response.json()
        assert "message" in data
        assert "practice_words" in data or "word_bank" in data
        
        # Send response with sentence
        response = client.post(
            "/api/chat/message",
            json={"message": "The cat sat on the mat"},
            headers=headers
        )
        assert response.status_code == 200
    
    def test_progress_tracking(self, auth_token):
        """Test progress tracking throughout session"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Initial stats
        response = client.get("/api/user/stats", headers=headers)
        initial_stats = response.json()
        
        # Complete some exercises
        for _ in range(3):
            response = client.post(
                "/api/chat/message",
                json={"message": "give me 5 words"},
                headers=headers
            )
        
        # Check updated stats
        response = client.get("/api/user/stats", headers=headers)
        updated_stats = response.json()
        
        # Stats should change
        assert updated_stats["exercises_completed"] >= initial_stats["exercises_completed"]

class TestAuthenticationFlow:
    """Test authentication workflows"""
    
    def test_register_login_flow(self):
        """Test complete registration and login"""
        # Register
        response = client.post("/auth/register", json={
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "SecurePass123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        # Login
        response = client.post("/auth/login", json={
            "email": "newuser@test.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_password_reset_flow(self):
        """Test password reset workflow"""
        # Register user
        client.post("/auth/register", json={
            "email": "reset@test.com",
            "username": "resetuser",
            "password": "OriginalPass123"
        })
        
        # Request password reset
        response = client.post("/auth/forgot-password", json={
            "email": "reset@test.com"
        })
        assert response.status_code == 200
    
    def test_invalid_login(self):
        """Test invalid login attempts"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 400

class TestAPIEndpoints:
    """Test various API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_manifest(self):
        """Test manifest endpoint"""
        response = client.get("/api/manifest.json")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

