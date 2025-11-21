@echo off
echo 🚀 Starting Enhanced MPTI Chatbot
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt

REM Start the application
echo 🌐 Starting server...
python app.py

pause