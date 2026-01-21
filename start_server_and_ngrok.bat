@echo off
echo ========================================
echo Starting Server and ngrok
echo ========================================
echo.

REM Check if server is already running
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo Server is already running on port 8000!
    echo.
) else (
    echo Starting server...
    start "Arcus Server" cmd /k "cd /d %~dp0 && python run_app.py"
    echo Waiting for server to start...
    timeout /t 3 /nobreak >nul
)

REM Check if ngrok is available
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: ngrok is not found!
    echo.
    echo Please:
    echo 1. Download ngrok from: https://ngrok.com/download
    echo 2. Extract ngrok.exe
    echo 3. Put ngrok.exe in this folder OR add it to your PATH
    echo.
    pause
    exit /b 1
)

echo Starting ngrok...
start "ngrok Tunnel" cmd /k "ngrok http 8000"

echo.
echo ========================================
echo Both are starting!
echo ========================================
echo.
echo Terminal 1: Server (python run_app.py)
echo Terminal 2: ngrok (ngrok http 8000)
echo.
echo IMPORTANT:
echo 1. Wait for ngrok to show the HTTPS URL
echo 2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
echo 3. Update Google Apps Script with that URL
echo 4. Keep both terminals open!
echo.
echo Press any key to open ngrok web interface...
pause >nul
start http://127.0.0.1:4040
