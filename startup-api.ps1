# 1. Rebuild and restart ONLY the api container
Write-Host "Rebuilding and updating the API service..." -ForegroundColor Cyan
docker compose up --build -d api

# 2. Health Check Logic
Write-Host "Waiting for the new API instance to pass health checks..." -ForegroundColor Yellow
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
        # API container is swapping or booting
    }

    if (-not $healthy) {
        Write-Host "..." -NoNewline
        Start-Sleep -Seconds 3
        $retryCount++
    }
}

if ($healthy) {
    Write-Host "`n API updated and verified healthy!" -ForegroundColor Green
    Write-Host "------------------------------------------------"
    docker compose ps api
} else {
    Write-Host "`n Health check timed out. Pulling recent error traces:" -ForegroundColor Red
    docker compose logs api --tail 20
}