# 1. Rebuild and restart ONLY the dashboard container
Write-Host "Rebuilding and updating the Dashboard service..." -ForegroundColor Cyan
docker compose up --build -d dashboard

Write-Host "`n Dashboard updated!" -ForegroundColor Green
Write-Host "Dashboard available at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "------------------------------------------------"
docker compose ps dashboard
