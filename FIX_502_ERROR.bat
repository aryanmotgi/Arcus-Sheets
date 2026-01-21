@echo off
echo ========================================
echo  Fixing 502 Bad Gateway Error
echo ========================================
echo.

echo Step 1: Stopping any existing servers...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo Step 2: Starting fresh server...
start "Arcus Server" cmd /k "cd /d %~dp0 && python run_app.py"
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo Step 3: Starting ngrok...
start "ngrok Tunnel" cmd /k "cd /d %~dp0 && credentials\ngrok-v3-stable-windows-amd64\ngrok http 8000"

echo.
echo ========================================
echo  Server and ngrok are starting...
echo ========================================
echo.
echo IMPORTANT:
echo 1. Wait 10 seconds for server to fully start
echo 2. Check the server terminal for "Application startup complete"
echo 3. If you see errors, let me know what they are
echo 4. Once server is running, test at: http://localhost:8000
echo.
echo Press any key to open server test page...
pause >nul
start http://localhost:8000
