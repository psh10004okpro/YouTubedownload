@echo off
chcp 65001 > nul

echo ========================================
echo YouTube Downloader - CLI Version
echo ========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if yt-dlp is installed
python -c "import yt_dlp" 2> nul
if errorlevel 1 (
    echo Installing required packages...
    echo Please wait...
    python -m pip install --quiet yt-dlp colorama
    echo.
)

echo Starting YouTube Downloader CLI...
echo.
python youtube_downloader.py
pause
