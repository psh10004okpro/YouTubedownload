@echo off
chcp 65001 > nul

echo ======================================
echo YouTube Downloader - Build EXE
echo ======================================
echo.

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable with PyInstaller...
echo.

REM Build with PyInstaller
pyinstaller --onefile --windowed --name "YouTubeDownloader" --icon=NONE youtube_downloader_gui.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ======================================
echo Build Complete!
echo ======================================
echo.
echo Executable location: dist\YouTubeDownloader.exe
echo.

pause
