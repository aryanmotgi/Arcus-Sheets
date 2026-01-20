@echo off
echo ========================================
echo   Arcus App - Push to GitHub Helper
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Checking if Git is initialized...
if not exist .git (
    echo Initializing Git...
    git init
) else (
    echo Git already initialized.
)
echo.

echo Step 2: Checking Git configuration...
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

echo Step 3: Adding all files...
git add .
echo.

echo Step 4: Checking status...
git status
echo.

echo Step 5: Making commit...
git commit -m "Initial commit: Arcus Analytics App"
echo.

echo Step 6: Repository setup
echo.
echo IMPORTANT: First create a repository on GitHub!
echo.
echo 1. Go to: https://github.com/new
echo 2. Create a new repository
echo 3. Copy the repository URL
echo.
set /p REPO_URL="Paste your GitHub repository URL here: "

echo.
echo Step 7: Adding remote repository...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
echo.

echo Step 8: Pushing to GitHub...
git branch -M main
git push -u origin main
echo.

echo ========================================
echo   Done! Check GitHub to see your files
echo ========================================
echo.
pause
