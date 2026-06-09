# Start backend API and frontend dev server
$root = $PSScriptRoot

Write-Host "Starting Canonical Infrastructure Runtime..." -ForegroundColor Cyan

# Backend
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root'; pip install -r backend/requirements.txt -q; uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

# Frontend
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root\frontend'; npm install; npm run dev"
)

Write-Host ""
Write-Host "  API:       http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "  Dashboard: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host ""
