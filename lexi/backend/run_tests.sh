#!/bin/bash

# Comprehensive Test Runner for LexiLearn Backend

echo "🧪 Running LexiLearn Backend Test Suite"
echo "==========================================="

# Run tests with coverage
echo ""
echo "📊 Running tests with coverage..."
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Show coverage summary
echo ""
echo "📈 Coverage Summary:"
coverage report

# Open coverage report if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "📄 Opening coverage report in browser..."
    open htmlcov/index.html
fi

echo ""
echo "✅ Tests completed!"
echo ""
echo "To run specific test files:"
echo "  pytest tests/test_api.py -v"
echo "  pytest tests/test_ai_tutor.py -v"
echo "  pytest tests/test_exercise_generator.py -v"
echo ""
echo "To run with specific markers:"
echo "  pytest -m slow"
echo "  pytest -m integration"

