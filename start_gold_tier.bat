@echo off
REM Gold Tier MCP Servers - Start All
REM Starts all Gold Tier MCP servers and services

echo ============================================================
echo GOLD TIER MCP SERVERS - START ALL
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [1/5] Starting Odoo MCP Server (Port 5001)...
start "Odoo MCP Server" cmd /k "cd /d %~dp0silver\mcp && python odoo_mcp_server.py"
timeout /t 3 >nul

echo [2/5] Starting Social Media MCP Server (Port 5002)...
start "Social Media MCP Server" cmd /k "cd /d %~dp0silver\mcp && python social_media_mcp_server.py"
timeout /t 3 >nul

echo [3/5] Starting Dashboard API (Port 8000)...
start "Dashboard API" cmd /k "cd /d %~dp0silver\skills\dashboard-api && python api_server.py"
timeout /t 3 >nul

echo [4/5] Starting Next.js Dashboard (Port 3000)...
start "Next.js Dashboard" cmd /k "cd /d %~dp0dashboard && npm run dev"
timeout /t 5 >nul

echo [5/5] Ralph Wiggum Loop available (on-demand)...
echo Ralph Wiggum Loop runs on-demand (not auto-started)
timeout /t 1 >nul

echo.
echo ============================================================
echo ALL GOLD TIER SERVERS STARTED
echo ============================================================
echo.
echo Services running:
echo   - Odoo MCP Server:      http://localhost:5001
echo   - Social Media MCP:     http://localhost:5002
echo   - Dashboard API:        http://localhost:8000
echo   - Next.js Dashboard:    http://localhost:3000
echo   - Ralph Wiggum Loop:    On-demand (silver/ralph_wiggum_loop.py)
echo   - Audit Logger:         On-demand (silver/audit_logger.py)
echo.
echo Dashboards:
echo   - Silver Tier:          http://localhost:3000
echo   - Gold Tier:            http://localhost:3000/gold-tier
echo   - Odoo Admin:           http://localhost:8069
echo.
echo To stop all servers:
echo   1. Close each terminal window
echo   2. Or press Ctrl+C in each window
echo.
echo Press any key to view this help again...
pause >nul
