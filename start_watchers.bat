@echo off
echo ============================================================
echo SILVER TIER - WATCHERS STARTER
echo ============================================================
echo.
echo Available Watchers:
echo   1. WhatsApp  - WhatsApp Web messages monitor
echo   2. Gmail     - Gmail inbox/spam monitor
echo   3. Filesystem - Folder file monitor
echo   4. LinkedIn  - LinkedIn activity monitor
echo.
echo ============================================================
echo SELECT OPTION:
echo ============================================================
echo.
echo   A) Run ALL watchers together
echo   W) Run WhatsApp only
echo   G) Run Gmail only
echo   F) Run Filesystem only
echo   L) Run LinkedIn only
echo   Q) Quit
echo.
echo ============================================================

set /p choice="Enter your choice (A/W/G/F/L/Q): "

if /i "%choice%"=="A" (
    echo.
    echo Starting ALL watchers...
    echo.
    python silver\watchers\run_all_watchers.py
) else if /i "%choice%"=="W" (
    echo.
    echo Starting WhatsApp Watcher...
    echo.
    start "WhatsApp Watcher" cmd /k "cd silver\watchers && python whatsapp_watcher_fixed.py"
    echo WhatsApp watcher started in new window!
) else if /i "%choice%"=="G" (
    echo.
    echo Starting Gmail Watcher...
    echo.
    start "Gmail Watcher" cmd /k "cd silver\watchers && python gmail_watcher.py"
    echo Gmail watcher started in new window!
) else if /i "%choice%"=="F" (
    echo.
    echo Starting Filesystem Watcher...
    echo.
    start "Filesystem Watcher" cmd /k "cd silver\watchers && python filesystem_watcher.py"
    echo Filesystem watcher started in new window!
) else if /i "%choice%"=="L" (
    echo.
    echo Starting LinkedIn Watcher...
    echo.
    start "LinkedIn Watcher" cmd /k "cd silver\watchers && python linkedin_watcher.py"
    echo LinkedIn watcher started in new window!
) else if /i "%choice%"=="Q" (
    echo.
    echo Exiting...
    exit /b
) else (
    echo.
    echo Invalid choice! Please run again and select A/W/G/F/L/Q
)

echo.
echo ============================================================
echo Done!
echo ============================================================
echo.
pause
