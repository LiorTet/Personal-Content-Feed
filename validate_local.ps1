# Local Validation Script for Personal-Content-Feed
# Mirrors the CI Quality Gate

Write-Host "--- Starting Local Validation ---" -ForegroundColor Cyan

# 1. Linting with Ruff
Write-Host "[1/4] Running Ruff (Linting)..." -ForegroundColor Yellow
uv run ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "Ruff failed!" -ForegroundColor Red; exit $LASTEXITCODE }

# 2. Formatting check with Ruff
Write-Host "[2/4] Checking Formatting..." -ForegroundColor Yellow
uv run ruff format --check .
if ($LASTEXITCODE -ne 0) { Write-Host "Formatting check failed! Run 'uv run ruff format .' to fix." -ForegroundColor Red; exit $LASTEXITCODE }

# 3. Type checking with Mypy
Write-Host "[3/4] Running Mypy (Type Safety)..." -ForegroundColor Yellow
uv run mypy .
if ($LASTEXITCODE -ne 0) { Write-Host "Mypy failed!" -ForegroundColor Red; exit $LASTEXITCODE }

# 4. Unit Tests with Pytest
Write-Host "[4/4] Running Pytest (Unit Tests)..." -ForegroundColor Yellow
$env:MISTRAL_API_KEY="mock-key-for-testing"
$env:DATABASE_URL="postgresql+asyncpg://placeholder:5432/db"
$env:OUTPUT_FEEDS_DIR="feeds"
$env:ENV="testing"

uv run pytest
if ($LASTEXITCODE -ne 0) { Write-Host "Tests failed!" -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "--- All Checks Passed! ---" -ForegroundColor Green
