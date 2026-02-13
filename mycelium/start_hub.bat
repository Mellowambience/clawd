@echo off
cd /d C:\Users\nator\clawd

REM Start gateway (if available)
call scripts\start_moltbot_on_boot.bat

REM Stop any existing process on 8765 (stale mycelium server)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765') do taskkill /PID %%a /F >nul 2>&1

REM Stop any existing process on 18789 (stale gateway)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :18789') do taskkill /PID %%a /F >nul 2>&1

REM Open dashboard + start pulse server in a new window
start "MIST Hub" "http://127.0.0.1:8765/"
start "MIST Pulse" cmd /k "python mycelium\mycelium_pulse.py"
