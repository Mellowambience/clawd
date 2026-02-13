@echo off
echo Setting up Moltbot to start automatically on boot...

REM Create a PowerShell script to start moltbot as a service
set POWERSHELL_SCRIPT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\start_moltbot.ps1

echo # PowerShell script to start Moltbot on startup > "%POWERSHELL_SCRIPT%"
echo cd "C:\Users\nator\clawd" >> "%POWERSHELL_SCRIPT%"
echo Write-Host "Starting Moltbot..." >> "%POWERSHELL_SCRIPT%"
echo Start-Process -FilePath "cmd" -ArgumentList "/c", "moltbot gateway start" -WindowStyle Hidden >> "%POWERSHELL_SCRIPT%"

REM Create a batch file as backup method
set BATCH_FILE=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\start_moltbot.bat
echo @echo off > "%BATCH_FILE%"
echo echo Starting Moltbot... >> "%BATCH_FILE%"
echo cd /d "C:\Users\nator\clawd" >> "%BATCH_FILE%"
echo start /min moltbot gateway start >> "%BATCH_FILE%"

echo.
echo Moltbot startup configuration completed!
echo Moltbot will now start automatically when you boot your computer.
echo.
pause