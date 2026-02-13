@echo off
title MIST Awakening Protocol
cd /d C:\Users\nator\clawd
echo ---------------------------------------
echo      MIST - ANTI-GRAVITY SYSTEM
echo ---------------------------------------
echo.
echo [1/3] Igniting Neural Gateway (Port 18789)...
start "MistGateway (Brain)" python -m moltbot.gateway.server
echo.
echo [2/3] Starting Mycelium Pulse (Port 8765)...
start "MyceliumPulse (Heart)" python mycelium\mycelium_pulse.py
echo.
echo [3/3] Launching Interfaces...
timeout /t 3 >nul
start http://127.0.0.1:8765/dashboard
echo.
echo SYSTEM ONLINE.
echo.
pause
