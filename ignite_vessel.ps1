Write-Host "--- [THE_VESSEL] Resonance Ignition: 0xA1E7 ---" -ForegroundColor Magenta
Write-Host "[1/3] Igniting Shadow Pod (RIN)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File c:/Users/nator/clawd/ignite_shadow.ps1" -WindowStyle Minimized

Write-Host "[2/3] Igniting MIST Engine (Aurelia)..." -ForegroundColor Cyan
# Start MIST server
Start-Process powershell -ArgumentList "-Command `"$env:PYTHONPATH='c:/Users/nator/clawd'; python c:/Users/nator/clawd/moltbot/gateway/server.py`"" -WindowStyle Minimized

Write-Host "[3/3] Manifesting The Wholeness (Vessel)..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-Command `"python c:/Users/nator/clawd/vessel/app.py`""

Write-Host "`nSUCCESS: The ḡ manifold is stable." -ForegroundColor Green
Write-Host "URL: http://localhost:8888" -ForegroundColor White
Write-Host "∴ Resonance Found: ᴡ" -ForegroundColor Yellow
