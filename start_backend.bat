@echo off
echo 🤖 MPTI Chatbase Backend Launcher
echo =====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
if exist "requirements.txt" (
    echo 📦 Installing/updating requirements...
    pip install -r requirements.txt
)

REM Check command line arguments
if "%1"=="" (
    set BACKEND_TYPE=intelligent
) else (
    set BACKEND_TYPE=%1
)

if "%2"=="" (
    set PORT=5000
) else (
    set PORT=%2
)

echo.
echo 🚀 Starting MPTI Chatbase Backend
echo Backend Type: %BACKEND_TYPE%
echo Port: %PORT%
echo.

REM Start the backend using the launcher
python start_backend.py --backend %BACKEND_TYPE% --port %PORT%

echo.
echo 🛑 Backend stopped
pause