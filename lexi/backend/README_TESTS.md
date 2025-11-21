# LexiLearn Testing - Quick Start

## Current Status
- **Coverage:** 15% → **Target: 70%**
- **Test Files:** 7 comprehensive test files created
- **Issue Fixed:** Missing email-validator dependency

## Quick Fix for Test Errors

### Step 1: Install Missing Dependency
```bash
pip install email-validator==2.1.0
```

Or run the batch file:
```bash
install_test_dependencies.bat
```

### Step 2: Run Tests
```bash
pytest tests/ -v
```

### Step 3: Check Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## What Was Fixed

✅ **Added `email-validator` to requirements.txt**
✅ **Fixed test imports** - Set environment variables before importing app
✅ **Fixed conftest.py** - Proper environment setup
✅ **Added cleanup fixtures** - Removes test database after tests

## Test Files

1. ✅ `test_api.py` - API endpoint tests
2. ✅ `test_ai_tutor.py` - AI tutor tests  
3. ✅ `test_exercise_generator.py` - Exercise generator tests
4. ✅ `test_database.py` - Database tests
5. ✅ `test_integration.py` - Integration tests
6. ✅ `test_performance.py` - Performance tests
7. ✅ `test_security.py` - Security tests

## Expected Results After Fix

```
✅ All tests import successfully
✅ No more "email-validator" errors
✅ Coverage increases to ~30-40%
✅ Tests run without errors
```

## Next Steps to Reach 70% Coverage

### 1. Fill In Test Implementations (Current: 15%)
Many tests are stubs. Add real logic:
```python
def test_register_user(self):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 2. Add More Test Cases (Target: 50%)
For each function, add:
- Happy path
- Error cases
- Edge cases
- Boundary conditions

### 3. Test All Endpoints (Target: 60%)
Ensure every API endpoint is tested:
- GET endpoints
- POST endpoints  
- PUT/PATCH endpoints
- DELETE endpoints

### 4. Integration Tests (Target: 70%)
Test complete workflows:
- User registration → Login → Chat → Exercises
- Exercise generation → Submission → Evaluation
- Progress tracking across sessions

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Category
```bash
pytest tests/test_api.py -v
pytest tests/test_performance.py -v
```

### With Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Coverage Report Location
```
htmlcov/index.html
```

## Coverage Goals

| Level | Coverage | Focus |
|-------|----------|-------|
| Phase 1 | 30-40% | Critical paths, API endpoints |
| Phase 2 | 50-60% | All endpoints, error handling |
| Phase 3 | 70%+ | Integration, edge cases |

## Files with Low Coverage

Priority order for testing:

1. **main.py** - 3% (needs most work)
2. **ai_tutor.py** - 13%
3. **database.py** - 31%
4. **exercise_generator.py** - 13%
5. **text_analysis.py** - 22%

## Sample Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage
# Windows: start htmlcov/index.html
# Mac: open htmlcov/index.html

# Run specific test
pytest tests/test_api.py::TestAuth::test_register_user -v
```

## Common Issues

### Issue: ModuleNotFoundError
**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Database locked
**Fix:** Delete test database
```bash
rm test_lexi.db
```

### Issue: Import errors
**Fix:** Set environment variables in conftest.py (already done)

## Summary

✅ **Dependencies fixed** - email-validator added
✅ **Imports fixed** - Environment variables set properly  
✅ **Test files ready** - 7 comprehensive test files
✅ **Next step** - Fill in test implementations to reach 70% coverage

**Run tests:** `pytest tests/ -v`

