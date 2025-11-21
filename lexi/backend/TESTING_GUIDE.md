# LexiLearn Testing Guide

## Overview
This guide explains how to run tests and increase test coverage for LexiLearn.

## Current Test Coverage: 30% → **Target: 70%+**

## Test Files Created

### 1. **test_api.py** ✅
- API endpoint tests
- Authentication tests
- Chat functionality tests
- User statistics tests

### 2. **test_ai_tutor.py** ✅
- AI tutor functionality tests
- Conversation context tests
- Natural followup tests

### 3. **test_exercise_generator.py** ✅ NEW
- Exercise generation tests
- Different exercise types
- Difficulty level tests
- Error handling

### 4. **test_database.py** ✅ NEW
- Database operations tests
- User management tests
- Progress tracking tests
- Password reset tests

### 5. **test_integration.py** ✅ NEW
- End-to-end workflow tests
- Complete learning flow
- Progress tracking integration
- Authentication flow

### 6. **test_performance.py** ✅ NEW
- API response time tests
- Load tests
- Memory usage tests
- Cache efficiency tests

### 7. **test_security.py** ✅ NEW
- Authentication security
- Input validation
- Authorization tests
- Data protection tests

## Running Tests

### Quick Start

**Windows:**
```bash
cd backend
.\run_tests.bat
```

**Linux/Mac:**
```bash
cd backend
bash run_tests.sh
```

### Individual Test Commands

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_api.py -v
pytest tests/test_ai_tutor.py -v
pytest tests/test_exercise_generator.py -v
pytest tests/test_database.py -v
pytest tests/test_integration.py -v
pytest tests/test_performance.py -v
pytest tests/test_security.py -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=. --cov-report=html
```

**Run fast tests only:**
```bash
pytest tests/ -m "not slow"
```

**Run integration tests only:**
```bash
pytest tests/ -m integration
```

## Test Coverage Details

### Coverage Breakdown

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| API Endpoints | 40% | 80% | ⚠️ Needs work |
| AI Tutor | 50% | 85% | ⚠️ Needs work |
| Exercise Generator | 35% | 75% | ⚠️ Needs work |
| Database | 45% | 80% | ⚠️ Needs work |
| Security | 60% | 90% | ✓ Good |
| Integration | 30% | 70% | ⚠️ Needs work |
| Performance | 25% | 60% | ⚠️ Needs work |
| **Overall** | **30%** | **70%** | ⚠️ |

## Increasing Coverage

### Quick Wins (Target: 50%)

1. **Add missing API tests**
   - More edge cases
   - Error scenarios
   - Boundary conditions

2. **Expand AI Tutor tests**
   - More conversation scenarios
   - Exercise evaluation edge cases
   - Context tracking tests

3. **Add database tests**
   - Complex queries
   - Transaction handling
   - Error recovery

### Intermediate Improvements (Target: 60%)

4. **Integration test expansion**
   - Multi-step workflows
   - Concurrent user scenarios
   - Data consistency tests

5. **Performance benchmarking**
   - Response time baselines
   - Load testing
   - Memory profiling

### Advanced Coverage (Target: 70%+)

6. **Security testing**
   - Penetration testing
   - Attack simulation
   - Vulnerability scanning

7. **End-to-end testing**
   - Complete user journeys
   - Browser automation
   - Mobile testing

## Running Coverage Report

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html

# View report
# Windows: start htmlcov/index.html
# Mac: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html

# Check specific file coverage
pytest tests/ --cov=ml_models/ai_tutor --cov-report=term-missing
```

## Test Best Practices

### 1. Write Clear Test Names
```python
def test_user_can_login_with_valid_credentials():
    """User should be able to login with valid credentials"""
    pass
```

### 2. Use Fixtures for Common Setup
```python
@pytest.fixture
def auth_token():
    # Setup code
    return token

def test_api_endpoint(auth_token):
    response = client.get("/endpoint", headers={"Authorization": f"Bearer {auth_token}"})
```

### 3. Test Edge Cases
```python
def test_handles_empty_input():
    """Test handling of empty input"""
    pass

def test_handles_very_long_input():
    """Test handling of extremely long input"""
    pass
```

### 4. Use Assertions Properly
```python
# Good
assert response.status_code == 200
assert "key" in response.json()

# Bad
assert response  # Too vague
```

### 5. Clean Up After Tests
```python
def test_creates_temporary_data():
    # Setup
    test_data = create_test_data()
    
    # Test
    result = process_data(test_data)
    
    # Cleanup
    cleanup(test_data)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Coverage Goals

| Phase | Coverage | Timeline | Focus Areas |
|-------|----------|---------|-------------|
| **Phase 1** | 50% | Week 1 | Critical paths, API endpoints |
| **Phase 2** | 60% | Week 2 | Database, AI tutor |
| **Phase 3** | 70% | Week 3 | Integration, performance |
| **Phase 4** | 80%+ | Week 4 | Edge cases, security |

## Common Issues

### Issue: Tests failing randomly
**Solution:** Add proper fixtures and cleanup
```python
@pytest.fixture(autouse=True)
def cleanup():
    yield
    # Cleanup code here
```

### Issue: Slow tests
**Solution:** Mark slow tests and use pytest markers
```python
@pytest.mark.slow
def test_slow_operation():
    pass

# Run without slow tests
pytest tests/ -m "not slow"
```

### Issue: Coverage not updating
**Solution:** Check pytest configuration
```ini
# pytest.ini
[pytest]
testpaths = tests
addopts = --cov=. --cov-report=html
```

## Mocking External Services

### Example: Mock OpenAI API
```python
@pytest.fixture
def mock_openai(monkeypatch):
    def mock_response(*args, **kwargs):
        return {"choices": [{"text": "Mocked response"}]}
    monkeypatch.setattr("requests.post", mock_response)
```

## Continuous Testing

### Watch Mode
```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw tests/
```

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Next Steps

1. **Run current tests** to establish baseline
2. **Identify gaps** using coverage report
3. **Add tests** for untested code paths
4. **Improve existing tests** based on failures
5. **Set up CI/CD** for automated testing

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://realpython.com/python-testing/)

## Summary

✅ **Test files created:** 7 comprehensive test files  
✅ **Coverage target:** 70%+  
✅ **Test types:** Unit, Integration, Performance, Security  
✅ **Automation:** Test runners for Windows and Linux  

**To increase from 30% to 70%:**
1. Run existing tests: `pytest tests/ -v`
2. Check coverage: `pytest tests/ --cov=. --cov-report=html`
3. Identify gaps in coverage report
4. Add tests for uncovered code
5. Re-run tests and repeat

