@echo off
echo Checking Node.js installation...
where node
if %errorlevel% neq 0 (
    echo Node.js not found in PATH
    echo Adding common Node.js paths...
    set PATH=%PATH%;C:\Program Files\nodejs;C:\Program Files (x86)\nodejs
    where node
)
echo.
echo Current PATH:
echo %PATH%
pause