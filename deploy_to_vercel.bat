@echo off
echo ============================================
echo   VERCEL DEPLOYMENT - Dashboard Frontend
echo ============================================
echo.

cd dashboard

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Vercel CLI not found. Installing...
    call npm i -g vercel
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install Vercel CLI. Please install manually:
        echo        npm i -g vercel
        pause
        exit /b 1
    )
)

REM Check if logged in
echo [INFO] Checking Vercel authentication...
vercel whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Not logged in. Opening browser login...
    vercel login
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Login failed. Please try again.
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Deploying to Vercel...
echo.
echo Choose deployment type:
echo   1. Preview deployment (testing)
echo   2. Production deployment (live)
echo.
set /p deploy_type="Enter choice (1 or 2): "

if "%deploy_type%"=="1" (
    echo [INFO] Deploying PREVIEW...
    vercel
) else if "%deploy_type%"=="2" (
    echo [INFO] Deploying to PRODUCTION...
    vercel --prod
) else (
    echo [ERROR] Invalid choice. Deploying PREVIEW...
    vercel
)

echo.
echo ============================================
echo   DEPLOYMENT COMPLETE
echo ============================================
echo.
echo Next steps:
echo 1. Set environment variable in Vercel dashboard:
echo    NEXT_PUBLIC_API_URL=https://your-space.hf.space
echo 2. Redeploy after setting env var
echo.
pause
