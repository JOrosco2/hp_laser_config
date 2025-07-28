@echo off
setlocal enabledelayedexpansion

echo === HP Laser Config Test Environment Setup ===

REM Step 1: Try known install paths (skip WindowsApps)
set PYTHON_EXE=

if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe
) else if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    set PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe
) else if exist "%LocalAppData%\Programs\Python\Python313\python.exe" (
    set PYTHON_EXE=%LocalAppData%\Programs\Python\Python313\python.exe
) else if exist "C:\Python311\python.exe" (
    set PYTHON_EXE=C:\Python311\python.exe
) else if exist "C:\Python312\python.exe" (
    set PYTHON_EXE=C:\Python312\python.exe
)

if not defined PYTHON_EXE (
    echo [!] Python could not be found in known locations.
    echo     Please install Python manually from https://python.org
    pause
    exit /b 1
)

echo [✓] Found Python: %PYTHON_EXE%

REM Step 2: Create virtual environment if missing
if not exist venv (
    echo [*] Creating virtual environment...
    "%PYTHON_EXE%" -m venv venv
)

REM Step 3: Activate virtual environment
call venv\Scripts\activate.bat

REM Step 4: Install dependencies
echo [*] Installing dependencies...
python -m pip install --upgrade pip
pip install --force-reinstall --no-cache-dir -r requirements.txt

REM Step 5: Run the test app
echo [*] Launching HP Laser Config Test App...
python main.py

pause
