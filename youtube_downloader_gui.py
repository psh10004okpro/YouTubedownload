#!/usr/bin/env python3
"""
YouTube 다운로더 - 개선된 GUI 버전
Windows용 사용자 친화적 그래픽 인터페이스
"""

import os
import sys
import threading
import io
import urllib.request
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yt_dlp

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 다운로더 v2.0")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        # 색상 테마
        self.colors = {
            'primary': '#FF0000',      # YouTube 빨강
            'secondary': '#282828',    # 어두운 회색
            'bg': '#FFFFFF',           # 흰색 배경
            'text': '#030303',         # 거의 검정
            'success': '#065F46',      # 녹색
            'warning': '#DC2626',      # 빨강
            'info': '#1E40AF',         # 파랑
        }

        # 변수 초기화
        self.download_path = StringVar(value=str(Path.home() / "Downloads" / "YouTube"))
        self.url_var = StringVar()
        self.resolution_var = StringVar(value="최고 화질")
        self.download_subtitles_var = BooleanVar(value=False)
        self.subtitle_langs_var = StringVar(value="ko,en")
        self.video_info = None
        self.formats = []
        self.is_downloading = False
        self.thumbnail_image = None

        # UI 설정
        self.setup_styles()
        self.setup_ui()

        # 클립보드 모니터링 시작
        self.check_clipboard()

    def setup_styles(self):
        """스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')

        # 버튼 스타일
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('맑은 고딕', 10, 'bold'))

        style.configure('Secondary.TButton',
                       background='#F3F4F6',
                       foreground=self.colors['text'],
                       borderwidth=1,
                       font=('맑은 고딕', 9))

    def setup_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        main_container = Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 제목 영역
        self.create_header(main_container)

        # URL 입력 영역
        self.create_url_section(main_container)

        # 비디오 정보 및 썸네일 영역
        self.create_info_section(main_container)

        # 다운로드 설정 영역
        self.create_settings_section(main_container)

        # 진행 상태 영역
        self.create_progress_section(main_container)

        # 로그 영역
        self.create_log_section(main_container)

        # 액션 버튼 영역
        self.create_action_buttons(main_container)

        # 초기 로그
        self.log("✨ YouTube 다운로더가 시작되었습니다!")
        self.log("📝 YouTube URL을 입력하고 '정보 가져오기'를 클릭하세요.")

    def create_header(self, parent):
        """헤더 생성"""
        header_frame = Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=X, pady=(0, 20))

        title = Label(header_frame,
                     text="📺 YouTube 다운로더",
                     font=('맑은 고딕', 24, 'bold'),
                     fg=self.colors['primary'],
                     bg=self.colors['bg'])
        title.pack()

        subtitle = Label(header_frame,
                        text="유튜브 영상을 쉽고 빠르게 다운로드하세요",
                        font=('맑은 고딕', 10),
                        fg='#6B7280',
                        bg=self.colors['bg'])
        subtitle.pack()

    def create_url_section(self, parent):
        """URL 입력 섹션"""
        url_frame = LabelFrame(parent, text="  📌 YouTube URL  ",
                              font=('맑은 고딕', 11, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'],
                              padx=15, pady=15)
        url_frame.pack(fill=X, pady=(0, 15))

        # URL 입력 필드
        input_frame = Frame(url_frame, bg=self.colors['bg'])
        input_frame.pack(fill=X)

        url_entry = Entry(input_frame,
                         textvariable=self.url_var,
                         font=('맑은 고딕', 11),
                         relief=SOLID,
                         borderwidth=1)
        url_entry.pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0, 10))

        # 붙여넣기 버튼
        paste_btn = Button(input_frame,
                          text="📋 붙여넣기",
                          command=self.paste_from_clipboard,
                          font=('맑은 고딕', 9),
                          bg='#F3F4F6',
                          relief=FLAT,
                          cursor='hand2',
                          padx=15, pady=8)
        paste_btn.pack(side=LEFT, padx=(0, 5))

        # 정보 가져오기 버튼
        fetch_btn = Button(input_frame,
                          text="🔍 정보 가져오기",
                          command=self.fetch_video_info,
                          font=('맑은 고딕', 9, 'bold'),
                          bg=self.colors['primary'],
                          fg='white',
                          relief=FLAT,
                          cursor='hand2',
                          padx=15, pady=8)
        fetch_btn.pack(side=LEFT)

    def create_info_section(self, parent):
        """비디오 정보 섹션"""
        info_frame = LabelFrame(parent, text="  ℹ️  비디오 정보  ",
                               font=('맑은 고딕', 11, 'bold'),
                               bg=self.colors['bg'],
                               fg=self.colors['text'],
                               padx=15, pady=15)
        info_frame.pack(fill=BOTH, expand=True, pady=(0, 15))

        # 썸네일과 정보를 담을 컨테이너
        content_frame = Frame(info_frame, bg=self.colors['bg'])
        content_frame.pack(fill=BOTH, expand=True)

        # 썸네일 영역 (왼쪽)
        self.thumbnail_label = Label(content_frame,
                                    text="🎬\n\n썸네일이 여기에\n표시됩니다",
                                    font=('맑은 고딕', 10),
                                    bg='#F3F4F6',
                                    fg='#9CA3AF',
                                    width=30,
                                    height=10,
                                    relief=SOLID,
                                    borderwidth=1)
        self.thumbnail_label.pack(side=LEFT, padx=(0, 15))

        # 정보 텍스트 영역 (오른쪽)
        self.info_text = scrolledtext.ScrolledText(content_frame,
                                                   height=10,
                                                   font=('맑은 고딕', 10),
                                                   relief=SOLID,
                                                   borderwidth=1,
                                                   state='disabled')
        self.info_text.pack(side=LEFT, fill=BOTH, expand=True)

    def create_settings_section(self, parent):
        """다운로드 설정 섹션"""
        settings_frame = LabelFrame(parent, text="  ⚙️  다운로드 설정  ",
                                   font=('맑은 고딕', 11, 'bold'),
                                   bg=self.colors['bg'],
                                   fg=self.colors['text'],
                                   padx=15, pady=15)
        settings_frame.pack(fill=X, pady=(0, 15))

        # 저장 위치
        path_frame = Frame(settings_frame, bg=self.colors['bg'])
        path_frame.pack(fill=X, pady=(0, 10))

        Label(path_frame, text="💾 저장 위치:",
              font=('맑은 고딕', 10, 'bold'),
              bg=self.colors['bg']).pack(side=LEFT, padx=(0, 10))

        path_entry = Entry(path_frame,
                          textvariable=self.download_path,
                          font=('맑은 고딕', 9),
                          relief=SOLID,
                          borderwidth=1)
        path_entry.pack(side=LEFT, fill=X, expand=True, ipady=5, padx=(0, 10))

        Button(path_frame, text="📁 찾아보기",
              command=self.browse_folder,
              font=('맑은 고딕', 9),
              bg='#F3F4F6',
              relief=FLAT,
              cursor='hand2',
              padx=10, pady=5).pack(side=LEFT, padx=(0, 5))

        Button(path_frame, text="📂 폴더 열기",
              command=self.open_download_folder,
              font=('맑은 고딕', 9),
              bg='#F3F4F6',
              relief=FLAT,
              cursor='hand2',
              padx=10, pady=5).pack(side=LEFT)

        # 해상도 선택
        resolution_frame = Frame(settings_frame, bg=self.colors['bg'])
        resolution_frame.pack(fill=X, pady=(0, 10))

        Label(resolution_frame, text="🎥 해상도:",
              font=('맑은 고딕', 10, 'bold'),
              bg=self.colors['bg']).pack(side=LEFT, padx=(0, 10))

        self.resolution_combo = ttk.Combobox(resolution_frame,
                                            textvariable=self.resolution_var,
                                            state='readonly',
                                            font=('맑은 고딕', 10),
                                            width=40)
        self.resolution_combo['values'] = ("최고 화질",)
        self.resolution_combo.pack(side=LEFT, ipady=3)

        # 자막 설정
        subtitle_frame = Frame(settings_frame, bg=self.colors['bg'])
        subtitle_frame.pack(fill=X)

        Checkbutton(subtitle_frame,
                   text="📝 자막 다운로드",
                   variable=self.download_subtitles_var,
                   command=self.toggle_subtitle_options,
                   font=('맑은 고딕', 10, 'bold'),
                   bg=self.colors['bg'],
                   activebackground=self.colors['bg']).pack(side=LEFT, padx=(0, 10))

        Label(subtitle_frame, text="언어:",
              font=('맑은 고딕', 9),
              bg=self.colors['bg']).pack(side=LEFT, padx=(0, 5))

        self.subtitle_entry = Entry(subtitle_frame,
                                    textvariable=self.subtitle_langs_var,
                                    font=('맑은 고딕', 9),
                                    width=20,
                                    state='disabled',
                                    relief=SOLID,
                                    borderwidth=1)
        self.subtitle_entry.pack(side=LEFT, ipady=3)

        Label(subtitle_frame, text="(예: ko,en,ja)",
              font=('맑은 고딕', 8),
              fg='#6B7280',
              bg=self.colors['bg']).pack(side=LEFT, padx=(10, 0))

    def create_progress_section(self, parent):
        """진행 상태 섹션"""
        progress_frame = LabelFrame(parent, text="  📊 다운로드 진행 상태  ",
                                   font=('맑은 고딕', 11, 'bold'),
                                   bg=self.colors['bg'],
                                   fg=self.colors['text'],
                                   padx=15, pady=15)
        progress_frame.pack(fill=X, pady=(0, 15))

        # 진행률 바
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=800,
                                           mode='determinate')
        self.progress_bar.pack(fill=X, pady=(0, 10))

        # 상태 텍스트
        self.status_label = Label(progress_frame,
                                 text="⏸️  대기 중...",
                                 font=('맑은 고딕', 10),
                                 bg=self.colors['bg'],
                                 fg='#6B7280',
                                 anchor=W)
        self.status_label.pack(fill=X)

    def create_log_section(self, parent):
        """로그 섹션"""
        log_frame = LabelFrame(parent, text="  📋 로그  ",
                              font=('맑은 고딕', 11, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'],
                              padx=15, pady=15)
        log_frame.pack(fill=BOTH, expand=True, pady=(0, 15))

        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 height=6,
                                                 font=('맑은 고딕', 9),
                                                 relief=SOLID,
                                                 borderwidth=1,
                                                 state='disabled')
        self.log_text.pack(fill=BOTH, expand=True)

    def create_action_buttons(self, parent):
        """액션 버튼 섹션"""
        button_frame = Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=X)

        # 다운로드 버튼 (크고 눈에 띄게)
        self.download_button = Button(button_frame,
                                     text="⬇️  다운로드 시작",
                                     command=self.start_download,
                                     font=('맑은 고딕', 12, 'bold'),
                                     bg=self.colors['primary'],
                                     fg='white',
                                     relief=FLAT,
                                     cursor='hand2',
                                     padx=30,
                                     pady=12)
        self.download_button.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

        # 로그 지우기 버튼
        Button(button_frame,
              text="🗑️  로그 지우기",
              command=self.clear_log,
              font=('맑은 고딕', 10),
              bg='#F3F4F6',
              relief=FLAT,
              cursor='hand2',
              padx=20,
              pady=12).pack(side=LEFT)

    def check_clipboard(self):
        """클립보드에서 YouTube URL 확인"""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard and 'youtube.com' in clipboard or 'youtu.be' in clipboard:
                current_url = self.url_var.get()
                if not current_url or current_url != clipboard:
                    # 클립보드에 새로운 YouTube URL이 있음을 표시
                    pass
        except:
            pass

        # 1초마다 체크
        self.root.after(1000, self.check_clipboard)

    def paste_from_clipboard(self):
        """클립보드에서 붙여넣기"""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard:
                self.url_var.set(clipboard)
                self.log("📋 클립보드에서 URL을 붙여넣었습니다.")

                # YouTube URL이면 자동으로 정보 가져오기 제안
                if 'youtube.com' in clipboard or 'youtu.be' in clipboard:
                    self.log("✅ YouTube URL이 감지되었습니다!")
        except:
            messagebox.showwarning("경고", "클립보드가 비어있습니다.")

    def browse_folder(self):
        """저장 폴더 선택"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
            self.log(f"💾 저장 위치 변경: {folder}")

    def open_download_folder(self):
        """다운로드 폴더 열기"""
        path = Path(self.download_path.get())
        if path.exists():
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
            self.log(f"📂 폴더 열기: {path}")
        else:
            messagebox.showwarning("경고", "폴더가 존재하지 않습니다.")

    def toggle_subtitle_options(self):
        """자막 옵션 토글"""
        if self.download_subtitles_var.get():
            self.subtitle_entry.config(state='normal')
        else:
            self.subtitle_entry.config(state='disabled')

    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.config(state='normal')
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)
        self.log_text.config(state='disabled')

    def clear_log(self):
        """로그 지우기"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, END)
        self.log_text.config(state='disabled')
        self.log("🗑️  로그가 지워졌습니다.")

    def update_info_text(self, text):
        """비디오 정보 업데이트"""
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state='disabled')

    def load_thumbnail(self, url):
        """썸네일 다운로드 및 표시"""
        if not PIL_AVAILABLE:
            return

        try:
            # 썸네일 다운로드
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()

            # 이미지 처리
            image = Image.open(io.BytesIO(raw_data))

            # 리사이즈 (비율 유지)
            image.thumbnail((300, 200), Image.Resampling.LANCZOS)

            # PhotoImage로 변환
            self.thumbnail_image = ImageTk.PhotoImage(image)

            # 레이블에 표시
            self.root.after(0, lambda: self.thumbnail_label.config(
                image=self.thumbnail_image,
                text="",
                bg=self.colors['bg']
            ))

        except Exception as e:
            self.log(f"⚠️  썸네일 로드 실패: {str(e)}")

    def fetch_video_info(self):
        """비디오 정보 가져오기"""
        url = self.url_var.get().strip()

        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력하세요.")
            return

        self.log("🔍 비디오 정보를 가져오는 중...")
        self.status_label.config(text="🔍 비디오 정보를 가져오는 중...")

        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._fetch_video_info_thread, args=(url,))
        thread.daemon = True
        thread.start()

    def _fetch_video_info_thread(self, url):
        """비디오 정보 가져오기 (스레드)"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)

            # 비디오 정보 표시
            title = self.video_info.get('title', 'Unknown')
            uploader = self.video_info.get('uploader', 'Unknown')
            duration = self.video_info.get('duration', 0)
            duration_str = f"{duration // 60}분 {duration % 60}초"
            view_count = self.video_info.get('view_count', 0)
            upload_date = self.video_info.get('upload_date', 'Unknown')

            # 날짜 포맷
            if upload_date != 'Unknown' and len(upload_date) == 8:
                upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

            info_text = f"📺 제목: {title}\n\n"
            info_text += f"👤 채널: {uploader}\n\n"
            info_text += f"⏱️  길이: {duration_str}\n\n"
            info_text += f"👁️  조회수: {view_count:,}회\n\n"
            info_text += f"📅 업로드: {upload_date}\n\n"

            # 자막 정보
            subtitles = self.video_info.get('subtitles', {})
            auto_captions = self.video_info.get('automatic_captions', {})
            all_subs = set(list(subtitles.keys()) + list(auto_captions.keys()))

            if all_subs:
                info_text += f"📝 자막: {', '.join(sorted(all_subs))}"
            else:
                info_text += "📝 자막: 없음"

            self.root.after(0, self.update_info_text, info_text)

            # 썸네일 로드
            thumbnail_url = self.video_info.get('thumbnail')
            if thumbnail_url:
                threading.Thread(target=self.load_thumbnail, args=(thumbnail_url,), daemon=True).start()

            # 포맷 정보 가져오기
            self.formats = self._get_available_formats()

            # 해상도 콤보박스 업데이트
            format_options = ["최고 화질"]
            for fmt in self.formats:
                format_options.append(f"{fmt['resolution']} ({fmt['height']}p) - {fmt['ext']}")

            self.root.after(0, lambda: self.resolution_combo.config(values=format_options))
            self.root.after(0, lambda: self.resolution_var.set("최고 화질"))

            self.root.after(0, self.log, f"✅ 비디오 정보를 가져왔습니다: {title}")
            self.root.after(0, self.log, f"🎥 사용 가능한 해상도: {len(self.formats)}개")
            self.root.after(0, lambda: self.status_label.config(text="✅ 준비 완료 - 다운로드를 시작할 수 있습니다"))

        except Exception as e:
            error_msg = f"❌ 오류 발생: {str(e)}"
            self.root.after(0, self.log, error_msg)
            self.root.after(0, lambda: self.status_label.config(text="❌ 오류 발생"))
            self.root.after(0, messagebox.showerror, "오류", error_msg)

    def _get_available_formats(self):
        """사용 가능한 포맷 정리"""
        formats = []
        seen_resolutions = set()

        for f in self.video_info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                resolution = f.get('resolution', 'Unknown')
                height = f.get('height', 0)
                ext = f.get('ext', 'mp4')

                if resolution not in seen_resolutions and height > 0:
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': resolution,
                        'height': height,
                        'ext': ext,
                    })
                    seen_resolutions.add(resolution)

        formats.sort(key=lambda x: x['height'], reverse=True)
        return formats

    def start_download(self):
        """다운로드 시작"""
        if self.is_downloading:
            messagebox.showinfo("알림", "이미 다운로드 중입니다.")
            return

        if not self.video_info:
            messagebox.showwarning("경고", "먼저 비디오 정보를 가져오세요.")
            return

        # 저장 폴더 생성
        download_dir = Path(self.download_path.get())
        download_dir.mkdir(parents=True, exist_ok=True)

        # 포맷 선택
        format_id = None
        selected_resolution = self.resolution_var.get()

        if selected_resolution != "최고 화질":
            for idx, fmt in enumerate(self.formats):
                format_str = f"{fmt['resolution']} ({fmt['height']}p) - {fmt['ext']}"
                if format_str == selected_resolution:
                    format_id = fmt['format_id']
                    break

        # 다운로드 설정
        download_subs = self.download_subtitles_var.get()
        subtitle_langs = None

        if download_subs:
            langs_str = self.subtitle_langs_var.get().strip()
            if langs_str:
                subtitle_langs = [lang.strip() for lang in langs_str.split(',')]

        self.is_downloading = True
        self.download_button.config(state='disabled', bg='#9CA3AF')
        self.progress_var.set(0)

        # 별도 스레드에서 다운로드
        thread = threading.Thread(target=self._download_thread,
                                 args=(self.url_var.get(), format_id, download_subs, subtitle_langs))
        thread.daemon = True
        thread.start()

    def check_ffmpeg(self):
        """ffmpeg 설치 확인"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'],
                                  capture_output=True,
                                  timeout=5)
            return result.returncode == 0
        except:
            return False

    def _download_thread(self, url, format_id, download_subs, subtitle_langs):
        """다운로드 (스레드)"""
        try:
            ydl_opts = {
                'outtmpl': str(Path(self.download_path.get()) / '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }

            # ffmpeg 확인
            has_ffmpeg = self.check_ffmpeg()

            if not has_ffmpeg:
                self.root.after(0, self.log, "⚠️  ffmpeg가 설치되어 있지 않습니다.")
                self.root.after(0, self.log, "📦 단일 파일 포맷으로 다운로드합니다. (화질이 제한될 수 있습니다)")
                # ffmpeg 없이 다운로드 가능한 최고 품질 단일 파일 선택
                ydl_opts['format'] = 'best[ext=mp4]/best'
            else:
                # ffmpeg 있으면 최고 화질 비디오+오디오 병합
                if format_id:
                    ydl_opts['format'] = f'{format_id}+bestaudio/best'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

            if download_subs:
                ydl_opts['writesubtitles'] = True
                ydl_opts['writeautomaticsub'] = True
                if subtitle_langs:
                    ydl_opts['subtitleslangs'] = subtitle_langs
                ydl_opts['subtitlesformat'] = 'srt/best'

            self.root.after(0, self.log, "⬇️  다운로드 시작...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.root.after(0, self.log, "🎉 다운로드 완료!")
            self.root.after(0, lambda: self.status_label.config(text="🎉 다운로드 완료!"))

            # ffmpeg 없으면 설치 안내 추가
            if not has_ffmpeg:
                self.root.after(0, messagebox.showinfo, "완료",
                              f"다운로드가 완료되었습니다!\n\n저장 위치:\n{self.download_path.get()}\n\n"
                              f"💡 팁: ffmpeg를 설치하면 더 높은 화질로 다운로드할 수 있습니다.\n"
                              f"자세한 내용은 README.md를 참고하세요.")
            else:
                self.root.after(0, messagebox.showinfo, "완료",
                              f"다운로드가 완료되었습니다!\n\n저장 위치:\n{self.download_path.get()}")

        except Exception as e:
            error_msg = f"❌ 다운로드 오류: {str(e)}"
            self.root.after(0, self.log, error_msg)
            self.root.after(0, lambda: self.status_label.config(text="❌ 다운로드 실패"))

            # ffmpeg 관련 오류인지 확인
            if 'ffmpeg' in str(e).lower():
                self.root.after(0, messagebox.showerror, "오류",
                              f"ffmpeg가 필요합니다!\n\n"
                              f"해결 방법:\n"
                              f"1. Windows: https://github.com/BtbN/FFmpeg-Builds/releases 에서 다운로드\n"
                              f"2. 압축 해제 후 ffmpeg.exe를 시스템 PATH에 추가\n"
                              f"3. 또는 README.md의 설치 가이드를 참고하세요")
            else:
                self.root.after(0, messagebox.showerror, "오류", error_msg)

        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.download_button.config(
                state='normal',
                bg=self.colors['primary']
            ))
            self.root.after(0, lambda: self.progress_var.set(0))

    def progress_hook(self, d):
        """다운로드 진행 상태"""
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 1)
                percent = (downloaded / total) * 100
                self.root.after(0, lambda: self.progress_var.set(percent))

            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            percent_str = d.get('_percent_str', 'N/A')
            status_text = f"⬇️  다운로드 중... {percent_str} | 속도: {speed} | 남은 시간: {eta}"
            self.root.after(0, lambda: self.status_label.config(text=status_text))

        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_label.config(text="🔄 파일 변환 중..."))
            self.root.after(0, self.log, "✅ 다운로드 완료, 파일 변환 중...")


def main():
    """메인 함수"""
    root = Tk()

    # 윈도우 아이콘 설정 (선택 사항)
    try:
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            root.iconbitmap(icon_path)
    except:
        pass

    app = YouTubeDownloaderGUI(root)

    # 윈도우 중앙 정렬
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
