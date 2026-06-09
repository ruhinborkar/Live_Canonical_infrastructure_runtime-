# Single command to start API + React frontend (Windows)
$root = $PSScriptRoot
$nodeDir = "C:\Program Files\nodejs"
$apiPort = 8002

Write-Host ""
Write-Host "  Canonical Infrastructure Runtime" -ForegroundColor Cyan
Write-Host "  Starting backend + frontend..." -ForegroundColor Cyan
Write-Host ""

# Backend (new window)
$apiCmd = @"
Set-Location '$root'
pip install -r backend/requirements.txt -q
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port $apiPort
"@

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $apiCmd)

Start-Sleep -Seconds 3

# Frontend (new window) — cmd.exe + npm.cmd avoids PATH and PS policy issues
Start-Process cmd -ArgumentList @("/k", "`"$root\frontend\dev.bat`"")

Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:5173"

Write-Host "  API:       http://127.0.0.1:$apiPort" -ForegroundColor Green
Write-Host "  API docs:  http://127.0.0.1:$apiPort/docs" -ForegroundColor Green
Write-Host "  Dashboard: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "  Login:     admin / runtime" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Two terminal windows opened. Press Ctrl+C in each to stop." -ForegroundColor Gray
Write-Host ""
