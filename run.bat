@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating a fresh Python virtual environment...
    py -3.13 -m venv .venv
    if errorlevel 1 python -m venv .venv
    if not exist ".venv\Scripts\python.exe" goto fail
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail

".venv\Scripts\python.exe" app.py
if errorlevel 1 goto fail
exit /b 0

:fail
echo.
echo Could not start Island Rose Flower Shop. Check the error above.
pause
exit /b 1
