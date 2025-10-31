@echo off
REM YouTube 다운로더 Windows 실행 파일 빌드 스크립트

echo ======================================
echo YouTube 다운로더 빌드 시작
echo ======================================
echo.

REM 의존성 설치 확인
echo 의존성을 확인하는 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo 오류: 의존성 설치 실패
    pause
    exit /b 1
)

echo.
echo PyInstaller로 실행 파일 생성 중...
echo.

REM PyInstaller로 실행 파일 생성
pyinstaller --onefile --windowed --name "YouTube다운로더" --icon=NONE youtube_downloader_gui.py

if errorlevel 1 (
    echo 오류: 빌드 실패
    pause
    exit /b 1
)

echo.
echo ======================================
echo 빌드 완료!
echo ======================================
echo.
echo 실행 파일 위치: dist\YouTube다운로더.exe
echo.

pause
