# Fix Tests - Quick Guide

## Error Fixed: Missing `email-validator`

The tests were failing due to missing `email-validator` dependency.

## What Was Fixed

### 1. Added Missing Dependency
**File:** `backend/requirements.txt`

Added:
```txt
email-validator==2.1.0
pydantic[email]==2.5.0
```

### 2. Fixed Test Configuration
**File:** `backend/tests/conftest.py`

- Set environment variables before importing app
- Added cleanup fixture to remove test database
- Fixed import order

### 3. Fixed Test Imports
Updated all test files to set environment variables before importing:

**Files Modified:**
- `test_api.py`
- `test_integration.py`  
- `test_performance.py`
- `test_security.py`

## How to Fix

### Step 1: Install Missing Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Or specifically:
```bash
pip install email-validator==2.1.0
```

### Step 2: Run Tests Again
```bash
pytest tests/ -v
```

### Step 3: Check Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Expected Results

After fixing:
- ✅ All tests should import successfully
- ✅ Coverage should increase from 15% to ~30-40%
- ✅ No import errors

## Next Steps to Increase Coverage

Once tests run successfully:

1. **Fill in test implementations**
   - Many tests are stubs that need actual logic
   - Add real assertions and validations

2. **Add more edge case tests**
   - Boundary conditions
   - Error scenarios
   - Invalid inputs

3. **Expand existing tests**
   - More scenarios per test
   - Better assertions
   - Cleanup after tests

4. **Add integration tests**
   - End-to-end workflows
   - Multi-step processes
   - Real user scenarios

## Current Coverage: 15%

**Target:** 60-70%

## Files Needing Tests

Based on coverage report:

1. **main.py** - 3% coverage (needs most work)
2. **ai_tutor.py** - 13% coverage
3. **database.py** - 31% coverage  
4. **exercise_generator.py** - 13% coverage
5. **text_analysis.py** - 22% coverage

## Quick Win

Focus on `main.py` - it's the largest file with 3% coverage:
- API endpoints need testing
- Authentication flows
- Chat message processing
- Exercise handling

