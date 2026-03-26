# ─── AI Model Startup Script ─────────────────────────────────────────────────
# Activates the dedicated AI Model virtual environment and launches the FastAPI server.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPath  = Join-Path $scriptDir ".venv\Scripts\Activate.ps1"
$envFile   = Join-Path $scriptDir ".env"

# Check venv exists
if (-not (Test-Path $venvPath)) {
    Write-Error "Virtual environment not found. Run: python -m venv .venv && .\.venv\Scripts\pip install -r requirements.txt"
    exit 1
}

# Check .env exists
if (-not (Test-Path $envFile)) {
    Write-Warning ".env file not found. Copying from .env.example..."
    Copy-Item (Join-Path $scriptDir ".env.example") $envFile
    Write-Warning "Please edit .env and set your GEMINI_API_KEY before starting."
    exit 1
}

Write-Host "Activating AI Model virtual environment..." -ForegroundColor Cyan
& $venvPath

Write-Host "Starting Document Validator AI API on port 8001..." -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
