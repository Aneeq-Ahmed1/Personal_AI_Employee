@echo off
echo ========================================
echo PLATINUM TIER - CLOUD AGENT
echo (Draft-Only Mode)
echo ========================================
echo.
echo Starting Cloud Orchestrator...
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0silver"

python cloud\cloud_orchestrator.py

pause
