@echo off
REM ============================================================
REM SILVER TIER DASHBOARD - START DEVELOPMENT SERVER
REM ============================================================

echo ============================================================
echo SILVER TIER DASHBOARD - STARTING
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting Next.js Development Server...
echo.
echo Dashboard will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
