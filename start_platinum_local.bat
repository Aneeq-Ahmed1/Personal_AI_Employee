@echo off
echo ========================================
echo PLATINUM TIER - LOCAL AGENT
echo (Final Actions Mode)
echo ========================================
echo.
echo Starting Local Orchestrator...
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0silver"

python local\local_orchestrator.py

pause
