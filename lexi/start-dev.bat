@echo off
echo Starting Lexi Development Environment...

echo.
echo [1/3] Starting Backend Server...
start "Backend" cmd /k "cd lexi\backend && venv\Scripts\activate && python main.py"

echo.
echo [2/3] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] Starting Frontend Server...
start "Frontend" cmd /k "cd lexi\frontend && npm start"

echo.
echo Development servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul