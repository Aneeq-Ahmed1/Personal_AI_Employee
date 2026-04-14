@echo off
REM Silver Tier - Stop All Services
REM This script stops all Silver Tier services

echo ============================================================
echo SILVER TIER PERSONAL AI EMPLOYEE - STOPPING ALL SERVICES
echo ============================================================
echo.

echo Stopping services...
echo.

REM Stop processes by window title
taskkill /FI "WindowTitle eq Gmail Watcher*" /F 2>nul
taskkill /FI "WindowTitle eq WhatsApp Watcher*" /F 2>nul
taskkill /FI "WindowTitle eq MCP Server*" /F 2>nul
taskkill /FI "WindowTitle eq Plan Executor*" /F 2>nul

REM Also kill by process name if needed
taskkill /FI "ImageName eq python.exe" /FI "WindowTitle eq *Watcher*" /F 2>nul
taskkill /FI "ImageName eq python.exe" /FI "WindowTitle eq *Server*" /F 2>nul

echo.
echo ============================================================
echo ALL SERVICES STOPPED!
echo ============================================================
echo.
echo Press any key to exit this window...
pause >nul
