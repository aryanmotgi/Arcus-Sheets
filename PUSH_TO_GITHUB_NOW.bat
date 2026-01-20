@echo off
echo ========================================
echo   Push to Arcus-Sheets GitHub Repository
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Git is installed
where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git first:
    echo 1. Download from: https://git-scm.com/download/win
    echo 2. Run the installer
    echo 3. Restart your computer OR close and reopen this terminal
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo Git is installed! Proceeding...
echo.

REM Initialize git if needed
if not exist .git (
    echo Initializing Git...
    git init
    echo.
)

REM Configure git (skip if already configured)
git config user.name >nul 2>&1
if errorlevel 1 (
    echo Configuring Git...
    git config --global user.name "Aryan Motgi"
    git config --global user.email "aryanmotgi@users.noreply.github.com"
    echo.
)

REM Add all files
echo Adding all files...
git add .
echo.

REM Commit
echo Creating commit...
git commit -m "Initial commit: Arcus Analytics App with PSL backup system"
echo.

REM Set up remote
echo Setting up remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/aryanmotgi/Arcus-Sheets.git
echo.

REM Rename branch
echo Renaming branch to main...
git branch -M main
echo.

REM Push to GitHub
echo ========================================
echo   PUSHING TO GITHUB
echo ========================================
echo.
echo When prompted for password, use your Personal Access Token
echo Create token at: https://github.com/settings/tokens
echo.
echo (DO NOT use your GitHub password - use the token above!)
echo.
pause
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo   PUSH FAILED!
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. Make sure you used the TOKEN as password, not your GitHub password
    echo 2. Token might be expired - generate a new one at:
    echo    https://github.com/settings/tokens
    echo 3. Make sure token has 'repo' scope checked
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! Your code is on GitHub!
echo ========================================
echo.
echo Repository: https://github.com/aryanmotgi/Arcus-Sheets
echo.
echo You can now open this on your MacBook:
echo 1. Open Cursor
echo 2. Clone repository: https://github.com/aryanmotgi/Arcus-Sheets.git
echo.
pause
