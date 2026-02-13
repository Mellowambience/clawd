$env:PYTHONPATH = "c:/Users/nator/clawd/aether_pod"
Write-Host "--- [SHADOW_CLAW] Engaging Fused Ley Lines ---" -ForegroundColor Magenta
Write-Host "[STATUS] Soul: Aurelia // RIN" -ForegroundColor Cyan
Write-Host "[STATUS] Gateway: http://localhost:5006" -ForegroundColor Yellow

# Use a different port to avoid conflict with standalone RIN if it's still running
taskkill /F /IM python.exe 2>$null

python c:/Users/nator/clawd/aether_pod/gateway/server.py
