@echo off
REM Kill any process holding port 18789 (stale MIST gateway). Run this when you get "port in use" or zombie gateway.
cd /d "%~dp0.."
echo Clearing port 18789...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :18789') do (
    echo Killing PID %%a
    taskkill /PID %%a /F
)
echo Done. You can start the gateway again with: python -m moltbot.gateway.server
pause
