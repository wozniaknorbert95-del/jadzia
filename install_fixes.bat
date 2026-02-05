@echo off
REM ============================================================
REM JADZIA - Instalacja naprawek
REM ============================================================

echo.
echo ============================================================
echo   JADZIA - Instalacja naprawek
echo ============================================================
echo.

REM Sprawdź czy jesteśmy w katalogu Jadzia
if not exist "agent\state.py" (
    echo BLAD: Musisz uruchomic ten skrypt z katalogu C:\Projekty\Jadzia
    echo Aktualna lokalizacja: %CD%
    pause
    exit /b 1
)

echo [1/6] Tworze backup...
set BACKUP_DIR=backup_%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir %BACKUP_DIR% 2>nul
copy agent\state.py %BACKUP_DIR%\state.py.bak
copy agent\agent.py %BACKUP_DIR%\agent.py.bak
echo    Backup utworzony: %BACKUP_DIR%

echo.
echo [2/6] Kopiuje naprawione pliki...
copy /Y state.py agent\state.py
if errorlevel 1 (
    echo BLAD: Nie mozna skopiowac state.py
    pause
    exit /b 1
)

copy /Y helpers.py agent\helpers.py
if errorlevel 1 (
    echo BLAD: Nie mozna skopiowac helpers.py
    pause
    exit /b 1
)

copy /Y agent.py agent\agent.py
if errorlevel 1 (
    echo BLAD: Nie mozna skopiowac agent.py
    pause
    exit /b 1
)

echo    Pliki skopiowane pomyslnie

echo.
echo [3/6] Czyszcze stary stan...
if exist data\.agent_state.json del data\.agent_state.json
if exist data\.agent.lock del data\.agent.lock
echo    Stan wyczyszczony

echo.
echo [4/6] Sprawdzam skladnie Python...
python -m py_compile agent\state.py
if errorlevel 1 (
    echo BLAD: Blad skladni w state.py!
    pause
    exit /b 1
)

python -m py_compile agent\helpers.py
if errorlevel 1 (
    echo BLAD: Blad skladni w helpers.py!
    pause
    exit /b 1
)

python -m py_compile agent\agent.py
if errorlevel 1 (
    echo BLAD: Blad skladni w agent.py!
    pause
    exit /b 1
)

echo    Skladnia OK

echo.
echo [5/6] Test importu...
python -c "from agent.state import store_new_contents; from agent.helpers import clean_code_for_file; print('Import OK')"
if errorlevel 1 (
    echo BLAD: Problem z importem!
    pause
    exit /b 1
)

echo.
echo [6/6] Test funkcji clean_code_for_file...
python -c "from agent.helpers import clean_code_for_file; test = '```php\n<?php echo \"test\"; ?>\n```'; result = clean_code_for_file(test, 'test.php'); assert '```' not in result; print('Test OK')"
if errorlevel 1 (
    echo BLAD: Test funkcji clean_code_for_file nieudany!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   INSTALACJA ZAKONCZONA POMYSLNIE!
echo ============================================================
echo.
echo NASTEPNE KROKI:
echo 1. Uruchom JADZIA: .\run.bat
echo 2. Przetestuj: Wyslij prosba "Dodaj komentarz w style.css"
echo 3. Sprawdz logi: curl http://localhost:8000/debug-state
echo.
echo Backup znajduje sie w: %BACKUP_DIR%
echo.
echo W razie problemow:
echo - Przywroc backup: copy %BACKUP_DIR%\*.bak agent\
echo - Sprawdz logi w: data\agent_changes.jsonl
echo.
pause
