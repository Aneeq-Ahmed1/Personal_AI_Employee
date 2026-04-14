@echo off
echo ========================================
echo PLATINUM TIER - FULL SYSTEM
echo (Cloud + Local + Dashboard)
echo ========================================
echo.
echo This will start:
echo 1. Dashboard API (port 8000)
echo 2. Cloud Agent (draft-only)
echo 3. Local Agent (final actions)
echo 4. Dashboard Frontend (port 3000)
echo.
echo Press any key to continue...
pause > nul
echo.

REM Start Dashboard API
echo [1/4] Starting Dashboard API...
start "Dashboard API" cmd /k "cd /d %~dp0silver\skills\dashboard-api && python api_server.py"
timeout /t 3 /nobreak > nul

REM Start Cloud Agent
echo [2/4] Starting Cloud Agent...
start "Cloud Agent" cmd /k "cd /d %~dp0silver && python cloud\cloud_orchestrator.py"
timeout /t 2 /nobreak > nul

REM Start Local Agent
echo [3/4] Starting Local Agent...
start "Local Agent" cmd /k "cd /d %~dp0silver && python local\local_orchestrator.py"
timeout /t 2 /nobreak > nul

REM Start Dashboard Frontend
echo [4/4] Starting Dashboard Frontend...
start "Dashboard Frontend" cmd /k "cd /d %~dp0dashboard && npm run dev"

echo.
echo ========================================
echo ALL SYSTEMS STARTED!
echo ========================================
echo.
echo Dashboard: http://localhost:3000
echo API:       http://localhost:8000
echo.
echo Check status at: http://localhost:8000/api/platinum/status
echo.
echo Press any key to exit this window...
pause > nul
