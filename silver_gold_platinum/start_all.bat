@echo off
REM ============================================================
REM SILVER TIER - START ALL SERVICES
REM One command to start everything!
REM ============================================================

echo ============================================================
echo SILVER TIER PERSONAL AI EMPLOYEE - STARTING ALL SERVICES
echo ============================================================
echo.

cd /d "%~dp0.."
set PROJECT_ROOT=%CD%
set VENV=%PROJECT_ROOT%\venv
set PYTHON=%VENV%\Scripts\python.exe
set SILVER=%PROJECT_ROOT%\silver

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

echo Starting services...
echo.

REM [1] Start Gmail Watcher (background)
echo [1/4] Starting Gmail Watcher...
start /MIN "Gmail Watcher" "%PYTHON%" "%SILVER%\watchers\gmail_watcher.py"
timeout /t 2 /nobreak >nul

REM [2] Start WhatsApp Watcher (background)
echo [2/4] Starting WhatsApp Watcher...
start "WhatsApp Watcher" "%PYTHON%" "%SILVER%\watchers\whatsapp_watcher_fixed.py"
timeout /t 2 /nobreak >nul

REM [3] Start MCP Server (background)
echo [3/4] Starting MCP Server...
start /MIN "MCP Server" "%PYTHON%" "%SILVER%\mcp_server.py"
timeout /t 2 /nobreak >nul

REM [4] Start Plan Executor (background)
echo [4/4] Starting Plan Executor...
start /MIN "Plan Executor" "%PYTHON%" "%SILVER%\plan_executor.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo ALL SERVICES STARTED!
echo ============================================================
echo.
echo Running Services (Background):
echo   ✓ Gmail Watcher - Checking emails every 60 seconds
echo   ✓ WhatsApp Watcher - Checking messages every 30 seconds  
echo   ✓ MCP Server - API endpoints ready
echo   ✓ Plan Executor - Executing AI plans
echo.
echo Windows Taskbar mein dekho - 4 windows minimize hongi
echo.
echo Services band karne ke liye:
echo   → Run: stop_all.bat
echo   → Ya Task Manager se Python processes end karo
echo.
echo ============================================================
echo.
echo Yeh window ab band ho jayegi...
timeout /t 5 /nobreak >nul
