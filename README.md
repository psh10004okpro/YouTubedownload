# YouTube 다운로더

YouTube 비디오를 다운로드할 수 있는 간편한 Python 프로그램입니다.

**GUI 버전과 CLI 버전 모두 제공됩니다!**

## 주요 기능

- YouTube 비디오 다운로드
- 해상도 선택 기능 (144p ~ 8K)
- 자막 다운로드 지원 (수동 자막 및 자동 생성 자막)
- 다운로드 진행 상태 표시
- **사용자 친화적인 Windows GUI 인터페이스** ⭐ (새로 추가!)
- CLI 버전도 함께 제공

## 설치 방법

### 1. Python 설치 확인
Python 3.7 이상이 필요합니다.

```bash
python3 --version
```

### 2. 저장소 클론

```bash
git clone <repository-url>
cd YouTubedownload
```

### 3. 의존성 설치

#### 방법 A: 자동 설치 (Windows 추천) ⭐

파일 탐색기에서 `install.bat`을 더블 클릭하거나:

```bash
install.bat
```

이 스크립트가 자동으로 필요한 패키지를 모두 설치합니다.

#### 방법 B: 수동 설치

```bash
pip install -r requirements.txt
```

또는:

```bash
pip install yt-dlp colorama
```

## 사용 방법

### 빠른 시작 (Windows) 🚀

1. `install.bat` 실행 (처음 한 번만)
2. `run_gui.bat` 실행
3. YouTube URL 입력하고 다운로드!

### 방법 1: GUI 버전 (Windows 추천) ⭐

**Windows:**

파일 탐색기에서 `run_gui.bat`을 더블 클릭하거나:

```bash
run_gui.bat
```

**참고:** 처음 실행 시 필요한 패키지가 자동으로 설치됩니다.

또는:
```bash
python youtube_downloader_gui.py
```

**Linux/Mac:**
```bash
python3 youtube_downloader_gui.py
```

#### Windows 실행 파일 (.exe) 만들기:

Python이 설치되어 있지 않은 다른 컴퓨터에서 사용하려면 실행 파일을 만들 수 있습니다:

```bash
build_exe.bat
```

실행 파일은 `dist\YouTube다운로더.exe`에 생성됩니다.

### 방법 2: CLI 버전 (명령줄)

**Windows:**
```bash
run_cli.bat
```

또는:
```bash
python youtube_downloader.py
```

**Linux/Mac:**
```bash
python3 youtube_downloader.py
```

프로그램을 실행하면 다음과 같은 절차로 진행됩니다:

1. YouTube URL 입력
2. 비디오 정보 확인 (제목, 채널, 길이)
3. 사용 가능한 해상도 목록 표시
4. 원하는 해상도 선택
5. 자막 다운로드 여부 선택
6. 다운로드 시작

### GUI 버전 사용법

1. **프로그램 실행**
   - `run_gui.bat`을 더블 클릭하거나 `python youtube_downloader_gui.py` 실행

2. **URL 입력**
   - YouTube URL을 입력하고 "정보 가져오기" 버튼 클릭

3. **비디오 정보 확인**
   - 제목, 채널, 길이, 조회수, 사용 가능한 자막 확인

4. **다운로드 설정**
   - 저장 위치 선택 (기본: 내 문서/Downloads/YouTube)
   - 해상도 선택 (드롭다운 메뉴)
   - 자막 다운로드 옵션 설정

5. **다운로드 시작**
   - "다운로드 시작" 버튼 클릭
   - 진행 상태 바에서 실시간 진행 상황 확인

### CLI 버전 사용 예시

```
YouTube URL을 입력하세요: https://www.youtube.com/watch?v=example

비디오 정보를 가져오는 중...

제목: Example Video
채널: Example Channel
길이: 5분 30초

사용 가능한 해상도:
------------------------------------------------------------
1. 1920x1080 (1080p) - mp4 - 50.5 MB
2. 1280x720 (720p) - mp4 - 25.3 MB
3. 854x480 (480p) - mp4 - 15.2 MB
4. 640x360 (360p) - mp4 - 8.5 MB
0. 최고 화질 (자동 선택)
------------------------------------------------------------

선택 (0-4): 2

사용 가능한 자막:
------------------------------------------------------------
1. ko (수동)
2. en (자동생성)
------------------------------------------------------------

자막을 다운로드하시겠습니까? (y/n): y
언어 코드 입력 (쉼표로 구분, 엔터는 한국어/영어): ko

다운로드 시작...
진행: 100% | 속도: 2.5 MB/s | 남은 시간: 00:00
다운로드 완료!
저장 위치: /path/to/YouTubedownload/downloads
```

## 다운로드 위치

- **GUI 버전**: 기본적으로 `내 문서/Downloads/YouTube` 폴더 (변경 가능)
- **CLI 버전**: 프로그램이 있는 폴더의 `downloads/` 하위 폴더

## 자막 다운로드

- 한국어 자막: `ko`
- 영어 자막: `en`
- 일본어 자막: `ja`
- 중국어 자막: `zh-Hans` 또는 `zh-Hant`

여러 언어를 다운로드하려면 쉼표로 구분하여 입력하세요:
```
ko, en, ja
```

자막은 `.srt` 형식으로 비디오와 같은 폴더에 저장됩니다.

## 주의사항

- 저작권이 있는 콘텐츠를 다운로드할 때는 저작권법을 준수하세요
- 개인적인 용도로만 사용하세요
- 일부 비디오는 다운로드가 제한될 수 있습니다

## 문제 해결

### "No module named 'yt_dlp'" 오류

이 오류가 발생하면:

1. `install.bat`을 실행하세요
2. 또는 수동으로 설치: `python -m pip install yt-dlp colorama`

**참고:** `run_gui.bat`과 `run_cli.bat`은 이제 자동으로 패키지를 설치합니다.

### 한글이 깨져서 나오는 경우

이 문제는 수정되었습니다. 최신 버전의 배치 파일을 사용하세요.

### ffmpeg 관련 오류

일부 포맷을 병합하려면 ffmpeg가 필요합니다:

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
[ffmpeg 다운로드 페이지](https://ffmpeg.org/download.html)에서 다운로드

### 다운로드 실패

- 인터넷 연결 확인
- YouTube URL이 올바른지 확인
- 비디오가 비공개 또는 삭제되지 않았는지 확인

## 파일 구조

```
YouTubedownload/
├── youtube_downloader_gui.py    # GUI 버전 (Windows용)
├── youtube_downloader.py         # CLI 버전 (명령줄)
├── requirements.txt              # 필요한 패키지 목록
├── install.bat                   # ⭐ 설치 스크립트 (처음 한 번 실행)
├── run_gui.bat                   # GUI 실행 스크립트 (Windows)
├── run_cli.bat                   # CLI 실행 스크립트 (Windows)
├── build_exe.bat                 # 실행 파일 빌드 스크립트
├── README.md                     # 사용 설명서
└── .gitignore                    # Git 제외 파일 목록
```

## 라이선스

이 프로젝트는 교육 목적으로 만들어졌습니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.
