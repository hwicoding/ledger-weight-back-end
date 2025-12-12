# Ledger Weight Backend Server Start Script
# UTF-8 Encoding Fix

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ledger Weight Backend Server Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found. Please create it first." -ForegroundColor Yellow
    Write-Host "python -m venv venv" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  - HTTP: http://localhost:8080" -ForegroundColor White
Write-Host "  - WebSocket: ws://localhost:8080" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host ""

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

