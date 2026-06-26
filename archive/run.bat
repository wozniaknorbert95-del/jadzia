@echo off
echo ============================================================
echo   JADZIA - Uruchamianie
echo ============================================================

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo BLAD: Brak srodowiska wirtualnego!
    echo Uruchom najpierw: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Sprawdzam zaleznosci...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Instaluje zaleznosci...
    pip install fastapi uvicorn httpx paramiko anthropic python-dotenv pydantic
)

echo.
echo Uruchamiam JADZIA API...
echo.

python main.py

pause