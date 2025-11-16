@echo off
echo MPTI Chatbase Quick Start
echo =========================

REM Install minimal dependencies
pip install flask flask-cors requests beautifulsoup4 python-dotenv

REM Start the application
python app.py

pause