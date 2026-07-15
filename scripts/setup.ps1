$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Creating Python virtual environment"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$python = Join-Path $Root ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip -q
& $python -m pip install -r backend\requirements-dev.txt -q

Write-Host "==> Seeding database"
Set-Location backend
& $python seed_db.py
Set-Location $Root

Write-Host "==> Installing frontend dependencies"
Set-Location frontend
if (Test-Path package-lock.json) {
    npm ci
} else {
    npm install
}
Set-Location $Root

Write-Host "==> Running tests"
Set-Location backend
& $python -m pytest -q
Set-Location $Root

Write-Host "Setup complete."
