@echo off
chcp 65001 > nul

echo ========================================
echo FFmpeg Installation Helper
echo ========================================
echo.

REM Check if ffmpeg is already installed
ffmpeg -version > nul 2>&1
if not errorlevel 1 (
    echo FFmpeg is already installed!
    echo.
    ffmpeg -version
    echo.
    pause
    exit /b 0
)

echo FFmpeg is not installed.
echo.
echo To download and install FFmpeg:
echo.
echo 1. Visit: https://github.com/BtbN/FFmpeg-Builds/releases
echo 2. Download the latest "ffmpeg-master-latest-win64-gpl.zip"
echo 3. Extract the ZIP file
echo 4. Copy ffmpeg.exe from bin folder to one of these locations:
echo    - C:\Windows\System32
echo    - Or the folder where this script is located
echo.
echo After installation, run this script again to verify.
echo.

REM Ask if user wants to open the download page
set /p choice="Open download page in browser? (y/n): "
if /i "%choice%"=="y" (
    start https://github.com/BtbN/FFmpeg-Builds/releases
)

echo.
pause
