"""
Pytest configuration and fixtures
"""
import pytest
import os

# Set test environment before importing app
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["DATABASE_URL"] = "sqlite:///test_lexi.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

@pytest.fixture(scope="session")
def app():
    """Create test application"""
    from main import app
    return app

@pytest.fixture
def db():
    """Database fixture"""
    from database.database import db_manager
    return db_manager

@pytest.fixture
def cleanup():
    """Cleanup after tests"""
    yield
    # Cleanup code here
    try:
        os.remove("test_lexi.db")
    except:
        pass

def pytest_configure(config):
    """Configure pytest"""
    # Test environment already set in module initialization
    pass

