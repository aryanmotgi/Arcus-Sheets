@echo off
echo Creating .env file...
echo.

cd /d "%~dp0"

if exist .env (
    echo .env file already exists!
    echo Opening it in Notepad...
    notepad .env
    exit /b
)

(
echo # Instagram API Credentials
echo INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
echo INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here
echo.
echo # TikTok API Credentials
echo TIKTOK_CLIENT_KEY=your_tiktok_client_key_here
echo TIKTOK_CLIENT_SECRET=your_tiktok_client_secret_here
echo TIKTOK_ACCESS_TOKEN=your_tiktok_access_token_here
) > .env

echo .env file created successfully!
echo Opening it in Notepad so you can fill in your credentials...
echo.
notepad .env
