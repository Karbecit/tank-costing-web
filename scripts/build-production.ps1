# Production build — run before uploading to cPanel
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Building frontend..."
Push-Location (Join-Path $Root "frontend")
npm ci
npm run build
Pop-Location

Write-Host "Frontend output: frontend/dist/"
Write-Host ""
Write-Host "Deploy checklist:"
Write-Host "  1. Upload frontend/dist/* to public_html"
Write-Host "  2. Upload backend/ to ~/tank-costing-api (outside web root)"
Write-Host "  3. cPanel Setup Python App -> passenger_wsgi.py"
Write-Host "  4. Set env vars: JWT_SECRET, DATABASE_PATH, ADMIN_EMAIL, ADMIN_PASSWORD"
Write-Host "  5. pip install -r backend/requirements.txt in virtualenv"
Write-Host "  6. Configure reverse proxy /api -> Python app"
Write-Host "  7. See DEPLOYMENT.md for full steps"
