@echo off
echo ========================================
echo MPTI Chatbase AI Backend Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install setuptools first
echo Installing setuptools...
pip install setuptools wheel

REM Install requirements one by one to handle errors
echo Installing core dependencies...
pip install flask==2.3.3
pip install flask-cors==4.0.0
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install python-dotenv==1.0.0

echo Installing optional AI dependencies...
pip install openai==1.3.0 || echo Warning: OpenAI installation failed - continuing with basic functionality

REM Set environment variables
echo Setting up environment...
set FLASK_APP=app.py
set FLASK_ENV=development
set HOST=0.0.0.0
set PORT=5000

REM Check if .env file exists and load OpenAI key
if exist ".env" (
    echo Loading environment variables from .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="OPENAI_API_KEY" set OPENAI_API_KEY=%%b
    )
)

echo.
echo ========================================
echo Starting MPTI Chatbase AI Backend
echo ========================================
echo Server will be available at: http://localhost:5000
echo Health check: http://localhost:5000/health
echo.
echo Features enabled:
echo - Comprehensive MPTI website scraping
echo - Enhanced content extraction
echo - Intelligent search and matching
echo - Real-time content refresh
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the Flask application
python app.py

echo.
echo Backend stopped.
pause