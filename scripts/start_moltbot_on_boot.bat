@echo off
echo Starting Moltbot on boot...

REM Change to the moltbot workspace directory
cd /d "C:\Users\nator\clawd"

REM Start the moltbot gateway service
echo Starting Moltbot gateway...
start /min python -c "import sys; sys.path.insert(0, '.'); import moltbot.gateway.server; moltbot.gateway.server.main()" || ^
python -m moltbot.gateway.server || ^
python -c "import subprocess; subprocess.run(['python', '-m', 'pip', 'install', '.']); import moltbot.gateway.server; moltbot.gateway.server.main()" || ^
echo Failed to start Moltbot - checking if it needs installation

REM Alternative: Try running moltbot if installed locally
echo Attempting to start moltbot gateway...
if exist "C:\Users\nator\.gemini\antigravity\scratch\clawdbot\moltbot\gateway\server.py" (
    echo Starting moltbot from development directory...
    cd /d "C:\Users\nator\.gemini\antigravity\scratch\clawdbot"
    start /min python -m moltbot.gateway --port 18789
)

REM Wait a moment to ensure the service starts
timeout /t 5 /nobreak >nul

echo Moltbot startup script completed.