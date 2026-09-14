@echo off
setlocal
cd /d "%~dp0"

echo =========================================================
echo    Classical Maze - Quick Setup and Launcher (Windows)
echo =========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.8+ from https://www.python.org/ and check "Add Python to PATH".
    pause
    exit /b 1
)

python setup.py

echo.
set /p RUN_NOW="Would you like to run the simulation now? (Y/N, default Y): "
if /i "%RUN_NOW%"=="" set RUN_NOW=Y
if /i "%RUN_NOW%"=="Y" (
    echo.
    echo [*] Starting simulation...
    if exist ".venv\Scripts\python.exe" (
        ".venv\Scripts\python.exe" main.py
    ) else (
        python main.py
    )
)

endlocal
