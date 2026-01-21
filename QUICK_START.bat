@echo off
echo ========================================
echo   Google Sheets AI Agent - Quick Start
echo ========================================
echo.
echo Starting server and ngrok...
echo.
echo IMPORTANT: After ngrok starts, copy the HTTPS URL
echo (looks like: https://abc123.ngrok.io)
echo.
echo Then update GOOGLE_SHEETS_SCRIPT.js with that URL
echo.
echo ========================================
echo.

REM Start the FastAPI server in background
start "FastAPI Server" cmd /k "python run_app.py"

REM Wait a bit for server to start
timeout /t 3 /nobreak >nul

REM Start ngrok
start "ngrok" cmd /k "cd credentials\ngrok-v3-stable-windows-amd64 && ngrok http 8000"

echo.
echo ========================================
echo   Server and ngrok are starting...
echo ========================================
echo.
echo Next steps:
echo 1. Wait for ngrok to show the HTTPS URL
echo 2. Copy that URL
echo 3. Open GOOGLE_SHEETS_SCRIPT.js
echo 4. Replace YOUR_NGROK_URL_HERE with your URL
echo 5. Save and refresh Google Sheets
echo.
echo Press any key to open the setup guide...
pause >nul

REM Open the quick start guide
start notepad QUICK_START_AGENT.md
