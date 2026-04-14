@echo off
echo ================================================================================
echo RESTART ALL GOLD TIER SERVERS (Updated with Instagram Fix)
echo ================================================================================
echo.
echo Yeh script:
echo 1. Purane servers band karegi (agar chal rahe hain)
echo 2. Updated code load karegi (Instagram fix included)
echo 3. Sab servers restart karegi
echo.
echo Servers:
echo - Dashboard API (Port 8000) - Instagram fix updated
echo - Next.js Dashboard (Port 3000) - Frontend
echo - Social Media MCP (Port 5002)
echo - Odoo MCP (Port 5001)
echo.
echo Press any key to restart all servers...
pause >nul

echo.
echo ================================================================================
echo STEP 1: Stopping old servers (if running)
echo ================================================================================
echo.

REM Kill old server windows
taskkill /FI "WINDOWTITLE eq Dashboard API*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Next.js Dashboard*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Social Media MCP Server*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Odoo MCP Server*" /T /F >nul 2>&1

echo ✅ Old servers stopped!
timeout /t 2 >nul

echo.
echo ================================================================================
echo STEP 2: Starting Updated Servers
echo ================================================================================
echo.

REM Start Odoo MCP Server
echo [1/4] Starting Odoo MCP Server (Port 5001)...
start "Odoo MCP Server" cmd /k "cd /d %~dp0silver\mcp && python odoo_mcp_server.py"
timeout /t 2 >nul

REM Start Social Media MCP Server
echo [2/4] Starting Social Media MCP Server (Port 5002)...
start "Social Media MCP Server" cmd /k "cd /d %~dp0silver\mcp && python social_media_mcp_server.py"
timeout /t 2 >nul

REM Start Dashboard API (WITH INSTAGRAM FIX)
echo [3/4] Starting Dashboard API with Instagram Fix (Port 8000)...
start "Dashboard API" cmd /k "cd /d %~dp0silver\skills\dashboard-api && python api_server.py"
timeout /t 3 >nul

REM Start Next.js Dashboard
echo [4/4] Starting Next.js Dashboard (Port 3000)...
start "Next.js Dashboard" cmd /k "cd /d %~dp0dashboard && npm run dev"
timeout /t 5 >nul

echo.
echo ================================================================================
echo ✅ ALL SERVERS STARTED SUCCESSFULLY!
echo ================================================================================
echo.
echo Servers running:
echo   ✅ Dashboard API:        http://localhost:8000 (Instagram fix updated!)
echo   ✅ Next.js Dashboard:    http://localhost:3000
echo   ✅ Social Media MCP:     http://localhost:5002
echo   ✅ Odoo MCP:             http://localhost:5001
echo.
echo ================================================================================
echo HOW TO USE FROM DASHBOARD:
echo ================================================================================
echo.
echo 1. Open browser: http://localhost:3000
echo.
echo 2. Go to "Social Media" tab
echo.
echo 3. Enter your message (or use AI Generate)
echo.
echo 4. Check ☑️ Instagram (and/or other platforms)
echo.
echo 5. Click "🚀 Post to Social Media"
echo.
echo 6. Browser will open automatically
echo    - Instagram will load
echo    - Login manually (90 seconds available)
echo    - Automation continues after login
echo    - Post submitted!
echo.
echo ================================================================================
echo INSTAGRAM FIX STATUS: ✅ UPDATED
echo ================================================================================
echo.
echo The following fixes are now active:
echo ✅ 90-second manual login detection
echo ✅ 5-second page stabilization after login
echo ✅ Automatic popup dismissal
echo ✅ 3-method Create button detection
echo ✅ Better caption entry
echo ✅ Share button with fallbacks
echo ✅ Detailed logging + screenshots
echo.
echo Screenshots saved to: vault\Browser_Automation_Screenshots\
echo.
echo Press any key to open Dashboard in browser...
pause >nul

start http://localhost:3000
