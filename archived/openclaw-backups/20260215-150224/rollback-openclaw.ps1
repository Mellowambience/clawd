$ErrorActionPreference = "Stop"
$targetVersion = "2026.1.30"
Write-Host "Rolling back OpenClaw to $targetVersion ..."
$env:OPENCLAW_SKIP_COMPLETION_SETUP = "1"
npm install -g "openclaw@$targetVersion" --no-audit --no-fund
Write-Host "Rollback complete. Current version:" (openclaw --version)
