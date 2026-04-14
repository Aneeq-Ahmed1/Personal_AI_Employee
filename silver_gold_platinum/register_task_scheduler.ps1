# Silver Tier - Windows Task Scheduler Registration
# This PowerShell script registers Silver Tier to start on Windows login

$projectRoot = Split-Path -Parent $PSScriptRoot
$taskName = "SilverTier_AI_Employee"
$batchFile = Join-Path $projectRoot "silver\start_all.bat"
$logFile = Join-Path $projectRoot "silver\task_scheduler.log"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SILVER TIER - WINDOWS TASK SCHEDULER REGISTRATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project Root: $projectRoot"
Write-Host "Batch File: $batchFile"
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create task action
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batchFile`"" -WorkingDirectory $projectRoot

# Create trigger (at logon)
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 24)

# Create principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Silver Tier Personal AI Employee - Auto-start on login" `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "TASK REGISTERED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Name: $taskName"
    Write-Host ""
    Write-Host "The Silver Tier AI Employee will now start automatically:"
    Write-Host "  - When you log in to Windows"
    Write-Host "  - All services will run in background"
    Write-Host ""
    Write-Host "To manually start: schtasks /run /tn `"$taskName`""
    Write-Host "To disable: schtasks /change /tn `"$taskName`" /disable"
    Write-Host "To enable: schtasks /change /tn `"$taskName`" /enable"
    Write-Host "To remove: schtasks /delete /tn `"$taskName`" /f"
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "ERROR REGISTERING TASK!" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Make sure you run this script as Administrator."
    Write-Host ""
}
