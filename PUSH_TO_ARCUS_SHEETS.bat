@echo off
echo ========================================
echo   Push to Arcus-Sheets GitHub Repository
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Checking if Git is installed...
where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git first:
    echo 1. Download from: https://git-scm.com/download/win
    echo 2. Install Git
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
)
echo Git is installed!
echo.

echo Step 2: Checking if Git is initialized...
if not exist .git (
    echo Initializing Git...
    git init
) else (
    echo Git already initialized.
)
echo.

echo Step 3: Checking Git configuration...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo Git user name not set.
    set /p GIT_NAME="Enter your name: "
    git config --global user.name "%GIT_NAME%"
)

git config user.email >nul 2>&1
if errorlevel 1 (
    echo Git user email not set.
    set /p GIT_EMAIL="Enter your email: "
    git config --global user.email "%GIT_EMAIL%"
)
echo.

echo Step 4: Adding all files...
git add .
echo.

echo Step 5: Checking status...
git status
echo.

echo Step 6: Making commit...
git commit -m "Initial commit: Arcus Analytics App"
echo.

echo Step 7: Setting up remote repository...
echo Repository URL: https://github.com/aryanmotgi/Arcus-Sheets.git
git remote remove origin 2>nul
git remote add origin https://github.com/aryanmotgi/Arcus-Sheets.git
echo.

echo Step 8: Renaming branch to main...
git branch -M main
echo.

echo Step 9: Pushing to GitHub...
echo.
echo IMPORTANT: When prompted for password, use a Personal Access Token!
echo To create one: https://github.com/settings/tokens
echo.
pause
git push -u origin main
echo.

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Common issues:
    echo 1. Make sure you're using a Personal Access Token, not your password
    echo 2. Generate token at: https://github.com/settings/tokens
    echo 3. Make sure token has 'repo' scope checked
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   Success! Your code is on GitHub!
echo ========================================
echo.
echo Repository: https://github.com/aryanmotgi/Arcus-Sheets
echo.
pause
