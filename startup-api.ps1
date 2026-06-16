# 1. Rebuild and restart services
Write-Host "Updating services (API and Dashboard)..." -ForegroundColor Cyan
docker compose up --build -d api dashboard

# 2. Health Check Logic for API
Write-Host "Waiting for the API to pass health checks..." -ForegroundColor Yellow
$maxRetries = 12
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/health" -Method Get -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $healthy = $true
        }
    } catch {
        # Container is swapping or booting
    }

    if (-not $healthy) {
        Write-Host "..." -NoNewline
        Start-Sleep -Seconds 3
        $retryCount++
    }
}

if ($healthy) {
    Write-Host "`n Services updated and API verified healthy!" -ForegroundColor Green
    Write-Host "Dashboard available at: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "------------------------------------------------"
    docker compose ps api dashboard
} else {
    Write-Host "`n Health check timed out for API. Pulling recent error traces:" -ForegroundColor Red
    docker compose logs api --tail 20
}
