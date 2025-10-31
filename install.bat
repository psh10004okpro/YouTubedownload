@echo off
chcp 65001 > nul
echo ========================================
echo YouTube Downloader - Installation
echo ========================================
echo.

echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
echo.

echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now run:
echo - run_gui.bat (GUI version)
echo - run_cli.bat (CLI version)
echo.
pause
