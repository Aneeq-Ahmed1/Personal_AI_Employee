@echo off
echo ============================================================
echo SILVER TIER - Personal AI Employee
echo ============================================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start Dashboard API
echo [2/4] Starting Dashboard API Server...
start "Dashboard API" cmd /k "cd silver\skills\dashboard-api && python api_server.py"
timeout /t 3 /nobreak >nul

REM Start Dashboard Frontend
echo [3/4] Starting Dashboard Frontend...
start "Dashboard Frontend" cmd /k "cd dashboard && npm run dev"
timeout /t 3 /nobreak >nul

echo [4/4] Servers started!
echo.
echo ============================================================
echo SERVERS RUNNING:
echo ============================================================
echo   Dashboard:    http://localhost:3000
echo   API:          http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo ============================================================
echo.
echo To start watchers manually:
echo   - Gmail:      cd silver\skills\gmail_watcher ^&^& python gmail_watcher.py
echo   - Filesystem: cd silver\skills\filesystem_watcher ^&^& python filesystem_watcher.py
echo   - Reasoning:  cd silver\skills\reasoning-engine ^&^& python reasoning_engine.py
echo.
echo Press any key to exit this window...
pause >nul
