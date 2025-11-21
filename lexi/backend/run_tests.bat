@echo off
REM Windows Test Runner for LexiLearn Backend

echo 🧪 Running LexiLearn Backend Test Suite
echo ===========================================

REM Run tests with coverage
echo.
echo 📊 Running tests with coverage...
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

REM Show coverage summary
echo.
echo 📈 Coverage Summary:
coverage report

echo.
echo ✅ Tests completed!
echo.
echo To run specific test files:
echo   pytest tests/test_api.py -v
echo   pytest tests/test_ai_tutor.py -v
echo   pytest tests/test_exercise_generator.py -v
echo.
echo To view coverage report:
echo   start htmlcov/index.html

pause

