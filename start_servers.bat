@echo off
echo ====================================
echo   Arcus App Server Starter
echo ====================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Installing dependencies (if needed)...
pip install -r requirements.txt --quiet
echo.

echo Starting Backend Server on port 8000...
start "Arcus Backend" cmd /k "python run_app.py"
timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend Server on port 8080...
cd frontend
start "Arcus Frontend" cmd /k "python -m http.server 8080"
cd ..

echo.
echo ====================================
echo   Servers Started!
echo ====================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8080
echo.
echo On your phone: http://192.168.1.242:8080
echo.
echo Press any key to open the app in your browser...
pause >nul
start http://localhost:8080

