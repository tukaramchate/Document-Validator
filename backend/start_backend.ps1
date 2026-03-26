# ─── Backend API Startup Script ──────────────────────────────────────────────
# Activates the BACKEND-ONLY virtual environment and starts the Flask server.
# This environment does NOT include torch, FastAPI, or ML packages.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPath  = Join-Path $scriptDir "venv\Scripts\Activate.ps1"
$envFile   = Join-Path $scriptDir ".env"

# Check venv exists
if (-not (Test-Path $venvPath)) {
    Write-Error "Backend virtual environment not found at '$venvPath'."
    Write-Error "Create it by running: python -m venv venv && .\venv\Scripts\pip install -r requirements.txt"
    exit 1
}

# Check .env exists
if (-not (Test-Path $envFile)) {
    Write-Warning ".env not found. Copy from .env.example and fill in your values."
    exit 1
}

Write-Host "============================================" -ForegroundColor DarkCyan
Write-Host "  Starting Document Validator BACKEND API   " -ForegroundColor Cyan
Write-Host "  Environment: backend\venv (Flask only)    " -ForegroundColor DarkGray
Write-Host "  Port: 5000                                " -ForegroundColor DarkGray
Write-Host "============================================" -ForegroundColor DarkCyan

& $venvPath

python app.py
