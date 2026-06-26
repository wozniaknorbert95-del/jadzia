# run.ps1 - Uruchomienie JADZIA w PowerShell

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  JADZIA - Uruchamianie" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

# Aktywuj venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "BLAD: Brak srodowiska wirtualnego!" -ForegroundColor Red
    Write-Host "Uruchom: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Uruchamiam JADZIA API..." -ForegroundColor Green
Write-Host ""

python main.py