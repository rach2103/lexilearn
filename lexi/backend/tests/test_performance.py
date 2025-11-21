"""
Performance and load tests for LexiLearn backend
"""
import pytest
import time
import os

# Set test environment
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["DATABASE_URL"] = "sqlite:///test_lexi.db"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestPerformance:
    """Performance tests"""
    
    def test_api_response_time(self):
        """Test API response time"""
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second
    
    def test_chat_response_time(self):
        """Test chat message response time"""
        # Create a user first
        client.post("/auth/register", json={
            "email": "perf@test.com",
            "username": "perfuser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "perf@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        start = time.time()
        response = client.post(
            "/api/chat/message",
            json={"message": "Hello"},
            headers=headers
        )
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Should respond in under 2 seconds
    
    def test_exercise_generation_time(self):
        """Test exercise generation performance"""
        client.post("/auth/register", json={
            "email": "exercise@test.com",
            "username": "exerciseuser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "exercise@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        start = time.time()
        response = client.get(
            "/api/exercises/generate",
            params={"skill_area": "phonics", "exercise_type": "word_building"},
            headers=headers
        )
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0
    
    def test_database_query_performance(self):
        """Test database query performance"""
        client.post("/auth/register", json={
            "email": "db@test.com",
            "username": "dbuser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "db@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        start = time.time()
        response = client.get("/api/user/stats", headers=headers)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 0.5  # Database queries should be fast

class TestLoad:
    """Load testing"""
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        # Create user
        client.post("/auth/register", json={
            "email": "concurrent@test.com",
            "username": "concurrentuser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "concurrent@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send multiple requests
        start = time.time()
        responses = []
        for i in range(10):
            resp = client.get("/api/user/stats", headers=headers)
            responses.append(resp.status_code == 200)
        duration = time.time() - start
        
        # All requests should succeed
        assert all(responses)
        # Should handle 10 requests in reasonable time
        assert duration < 5.0
    
    def test_chat_message_load(self):
        """Test chat message handling under load"""
        client.post("/auth/register", json={
            "email": "load@test.com",
            "username": "loaduser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "load@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        start = time.time()
        success_count = 0
        for _ in range(5):
            resp = client.post(
                "/api/chat/message",
                json={"message": "Test message"},
                headers=headers
            )
            if resp.status_code == 200:
                success_count += 1
        
        duration = time.time() - start
        assert success_count == 5
        assert duration < 10.0

class TestMemory:
    """Memory usage tests"""
    
    def test_conversation_memory(self):
        """Test conversation history memory management"""
        client.post("/auth/register", json={
            "email": "memory@test.com",
            "username": "memoryuser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "memory@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send multiple messages
        for i in range(20):
            client.post(
                "/api/chat/message",
                json={"message": f"Message {i}"},
                headers=headers
            )
        
        # Get history
        response = client.get("/api/chat/history", headers=headers)
        assert response.status_code == 200
        # Should have limited history
        history = response.json()["history"]
        assert isinstance(history, list)
    
    def test_cache_efficiency(self):
        """Test cache efficiency"""
        client.post("/auth/register", json={
            "email": "cache@test.com",
            "username": "cacheuser",
            "password": "TestPass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "cache@test.com",
            "password": "TestPass123"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # First request
        start = time.time()
        response1 = client.get("/api/user/stats", headers=headers)
        duration1 = time.time() - start
        
        # Second request (should be cached)
        start = time.time()
        response2 = client.get("/api/user/stats", headers=headers)
        duration2 = time.time() - start
        
        # Second request should be faster or equal
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert duration2 <= duration1 * 1.5  # Cached request shouldn't be much slower

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

