# 1. Clean up everything (Remove containers and old volumes)
Write-Host "Wiping old environment and volumes..." -ForegroundColor Cyan
docker compose down -v

# 2. Build and Start in detached mode
Write-Host "Building and starting containers..." -ForegroundColor Cyan
docker compose up --build -d

# 3. Health Check Logic
Write-Host "Waiting for API to be healthy..." -ForegroundColor Yellow
$maxRetries = 10
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/health" -Method Get -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $healthy = $true
        }
    } catch {
        # API not up yet
    }

    if (-not $healthy) {
        Write-Host "..." -NoNewline
        Start-Sleep -Seconds 5
        $retryCount++
    }
}

if ($healthy) {
    Write-Host "`nSystem is UP and running!" -ForegroundColor Green
    Write-Host "Dashboard available at: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "------------------------------------------------"
    docker compose ps
} else {
    Write-Host "`nHealth check timed out. Check 'docker compose logs api' for errors." -ForegroundColor Red
}