@echo off
echo Pushing to GitHub...
echo.

cd /d "%~dp0"

REM Try to find Git
set "GIT_PATH="
if exist "C:\Program Files\Git\bin\git.exe" set "GIT_PATH=C:\Program Files\Git\bin\git.exe"
if exist "C:\Program Files (x86)\Git\bin\git.exe" set "GIT_PATH=C:\Program Files (x86)\Git\bin\git.exe"

if defined GIT_PATH (
    echo Found Git at: %GIT_PATH%
    set "GIT_CMD=%GIT_PATH%"
) else (
    REM Try git command
    where git >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Git is not installed!
        echo.
        echo Install Git from: https://git-scm.com/download/win
        echo Then restart this script.
        pause
        exit /b 1
    )
    set "GIT_CMD=git"
)

echo.

REM Initialize if needed
if not exist .git (
    echo Initializing Git...
    %GIT_CMD% init
)

REM Configure
echo Configuring Git...
%GIT_CMD% config --global user.name "Aryan Motgi" 2>nul
%GIT_CMD% config --global user.email "aryanmotgi@users.noreply.github.com" 2>nul

REM Add files
echo Adding files...
%GIT_CMD% add .

REM Commit
echo Committing...
%GIT_CMD% commit -m "Initial commit: Arcus Analytics App" 2>nul || %GIT_CMD% commit -m "Update: Arcus Analytics App"

REM Remote
echo Setting remote...
%GIT_CMD% remote remove origin 2>nul
%GIT_CMD% remote add origin https://github.com/aryanmotgi/Arcus-Sheets.git

REM Branch
echo Setting branch...
%GIT_CMD% branch -M main 2>nul

REM Push
echo.
echo PUSHING TO GITHUB...
echo.
echo Username: aryanmotgi
echo Password: USE THIS TOKEN (copy it):
echo.
echo (Use your Personal Access Token from https://github.com/settings/tokens)
echo.
echo.
%GIT_CMD% push -u origin main

echo.
echo Done!
pause
