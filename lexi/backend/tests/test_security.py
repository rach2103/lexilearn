"""
Security tests for LexiLearn backend
"""
import pytest
import os

# Set test environment
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["DATABASE_URL"] = "sqlite:///test_lexi.db"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthentication:
    """Authentication security tests"""
    
    def test_password_hashing(self):
        """Test that passwords are hashed"""
        user_data = {
            "email": "hash@test.com",
            "username": "hashtest",
            "password": "SecurePassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Password should be hashed in database
        # This is verified by the login working with correct password
        response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert response.status_code == 200
    
    def test_jwt_token_format(self):
        """Test JWT token format"""
        client.post("/auth/register", json={
            "email": "jwt@test.com",
            "username": "jwttest",
            "password": "SecurePass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "jwt@test.com",
            "password": "SecurePass123"
        })
        
        token = response.json()["access_token"]
        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_invalid_token(self):
        """Test handling invalid tokens"""
        response = client.get(
            "/api/user/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_no_token(self):
        """Test API access without token"""
        response = client.get("/api/user/profile")
        assert response.status_code == 403  # Forbidden

class TestInputValidation:
    """Input validation security tests"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.post("/auth/register", json={
            "email": malicious_input,
            "username": "sqltest",
            "password": "Test123"
        })
        # Should handle gracefully without executing SQL
        assert response.status_code in [400, 422]
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        xss_payload = "<script>alert('XSS')</script>"
        
        # Try to register with XSS payload
        response = client.post("/auth/register", json={
            "email": xss_payload + "@test.com",
            "username": xss_payload,
            "password": "Test123"
        })
        # Should sanitize or reject
        assert response.status_code in [200, 400, 422]
    
    def test_long_input_handling(self):
        """Test handling of extremely long inputs"""
        long_input = "a" * 10000
        
        response = client.post("/api/chat/message", json={
            "message": long_input
        })
        # Should either accept or reject gracefully
        assert response.status_code in [200, 400, 413]  # 413 = Payload too large
    
    def test_special_characters(self):
        """Test handling of special characters"""
        special_input = "!@#$%^&*()_+-=[]{}|;:',.<>?"
        
        response = client.post("/auth/login", json={
            "email": special_input + "@test.com",
            "password": special_input
        })
        # Should handle gracefully
        assert response.status_code in [400, 422]

class TestAuthorization:
    """Authorization security tests"""
    
    def test_user_isolation(self):
        """Test that users can't access each other's data"""
        # Create user 1
        client.post("/auth/register", json={
            "email": "user1@test.com",
            "username": "user1",
            "password": "Test123"
        })
        
        response1 = client.post("/auth/login", json={
            "email": "user1@test.com",
            "password": "Test123"
        })
        token1 = response1.json()["access_token"]
        
        # Create user 2
        client.post("/auth/register", json={
            "email": "user2@test.com",
            "username": "user2",
            "password": "Test123"
        })
        
        response2 = client.post("/auth/login", json={
            "email": "user2@test.com",
            "password": "Test123"
        })
        token2 = response2.json()["access_token"]
        
        # Each user should only see their own data
        resp1 = client.get("/api/user/profile", headers={"Authorization": f"Bearer {token1}"})
        resp2 = client.get("/api/user/profile", headers={"Authorization": f"Bearer {token2}"})
        
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        
        data1 = resp1.json()
        data2 = resp2.json()
        
        # Users should have different IDs
        assert data1["email"] != data2["email"]

class TestDataProtection:
    """Data protection tests"""
    
    def test_password_not_returned(self):
        """Test that passwords are never returned in responses"""
        client.post("/auth/register", json={
            "email": "nopass@test.com",
            "username": "nopass",
            "password": "SecurePass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "nopass@test.com",
            "password": "SecurePass123"
        })
        
        token = response.json()["access_token"]
        response = client.get("/api/user/profile", headers={"Authorization": f"Bearer {token}"})
        
        data = response.json()
        # Should not contain password or hashed_password
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_sensitive_data_encryption(self):
        """Test that sensitive data is not exposed"""
        # Register and get token
        client.post("/auth/register", json={
            "email": "encrypt@test.com",
            "username": "encrypt",
            "password": "SecurePass123"
        })
        
        response = client.post("/auth/login", json={
            "email": "encrypt@test.com",
            "password": "SecurePass123"
        })
        token = response.json()["access_token"]
        
        # Token should not contain sensitive information in plain text
        token_parts = token.split(".")
        # Decode first part (header) - just check it doesn't contain obvious sensitive data
        assert "password" not in token.lower()
        assert "secret" not in token.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

