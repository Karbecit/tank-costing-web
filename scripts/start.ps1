$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path (Join-Path $Root ".venv"))) {
    Write-Host "Run .\scripts\setup.ps1 first"
    exit 1
}

Write-Host "Starting API on http://127.0.0.1:8000"
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$Root\backend'; ..\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173"
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$Root\frontend'; npm run dev"
)

Write-Host "Open http://localhost:5173 in your browser"
