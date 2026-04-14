@echo off
REM ============================================================
REM SILVER TIER DASHBOARD API - START
REM ============================================================

echo ============================================================
echo SILVER TIER DASHBOARD API - STARTING
echo ============================================================
echo.

cd /d "%~dp0"
set PROJECT_ROOT=%CD%\..\..\..\..
set VENV=%PROJECT_ROOT%\venv
set PYTHON=%VENV%\Scripts\python.exe

echo Project Root: %PROJECT_ROOT%
echo Python: %PYTHON%
echo.

REM Check if virtual environment exists
if not exist "%VENV%" (
    echo ERROR: Virtual environment not found at %VENV%
    echo Please setup virtual environment first
    pause
    exit /b 1
)

echo Starting Dashboard API Server...
echo.
echo Server will start on: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

"%PYTHON%" api_server.py
