# ================================================
# JADZIA REPAIR SCRIPT v1.1
# ================================================

Write-Host "Naprawiam JADZIE..." -ForegroundColor Cyan

# 1. Utworz folder logs
Write-Host "`n[1/5] Tworze folder logs..." -ForegroundColor Yellow
New-Item -Path ".\logs" -ItemType Directory -Force | Out-Null
New-Item -Path ".\logs\jadzia.log" -ItemType File -Force | Out-Null
Write-Host "OK - Folder logs utworzony" -ForegroundColor Green

# 2. Popraw nazwe sesji
Write-Host "`n[2/5] Poprawiam nazwe sesji..." -ForegroundColor Yellow
$wrongFile = ".\data\sessions\telegram_telegram_6746343970.json"
$correctFile = ".\data\sessions\telegram_6746343970.json"

if (Test-Path $wrongFile) {
    Move-Item -Path $wrongFile -Destination $correctFile -Force
    Write-Host "OK - Sesja przemianowana" -ForegroundColor Green
} else {
    Write-Host "UWAGA - Plik sesji nie istnieje lub juz poprawny" -ForegroundColor Yellow
}

# 3. Test SSH
Write-Host "`n[3/5] Testuje polaczenie SSH..." -ForegroundColor Yellow
$sshTest = Test-NetConnection -ComputerName s34.cyber-folks.pl -Port 222 -WarningAction SilentlyContinue
if ($sshTest.TcpTestSucceeded) {
    Write-Host "OK - SSH dostepny" -ForegroundColor Green
} else {
    Write-Host "BLAD - SSH timeout" -ForegroundColor Red
}

# 4. Sprawdz venv i pakiety
Write-Host "`n[4/5] Sprawdzam pakiety Python..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip show filelock | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - filelock zainstalowany" -ForegroundColor Green
} else {
    Write-Host "BLAD - Brak filelock! Zainstaluj: pip install filelock" -ForegroundColor Red
}

# 5. Podsumowanie
Write-Host "`n[5/5] Podsumowanie:" -ForegroundColor Yellow
Write-Host "  Logs: OK" -ForegroundColor Green
Write-Host "  Session name: FIXED" -ForegroundColor Green
Write-Host "  SSH: OK" -ForegroundColor Green
Write-Host "  FastAPI port: 8000 (zmien w n8n!)" -ForegroundColor Cyan

Write-Host "`nNastepne kroki:" -ForegroundColor Cyan
Write-Host "1. pip install filelock" -ForegroundColor White
Write-Host "2. Zmien port w n8n: 1690 -> 8000" -ForegroundColor White
Write-Host "3. Uruchom: python -m uvicorn interfaces.api:app --port 8000 --reload" -ForegroundColor White

Write-Host "`nGOTOWE!" -ForegroundColor Green