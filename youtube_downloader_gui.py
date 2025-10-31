#!/usr/bin/env python3
"""
YouTube 다운로더 - GUI 버전
Windows용 그래픽 인터페이스
"""

import os
import sys
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yt_dlp


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 다운로더")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # 변수 초기화
        self.download_path = StringVar(value=str(Path.home() / "Downloads" / "YouTube"))
        self.url_var = StringVar()
        self.resolution_var = StringVar(value="최고 화질")
        self.download_subtitles_var = BooleanVar(value=False)
        self.subtitle_langs_var = StringVar(value="ko,en")
        self.video_info = None
        self.formats = []
        self.is_downloading = False

        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')

        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 제목
        title_label = Label(main_frame, text="YouTube 다운로더",
                          font=("맑은 고딕", 16, "bold"), fg="#1a73e8")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # URL 입력
        row = 1
        ttk.Label(main_frame, text="YouTube URL:", font=("맑은 고딕", 10)).grid(
            row=row, column=0, sticky=W, pady=5)
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=row, column=1, sticky=(W, E), pady=5, padx=5)
        ttk.Button(main_frame, text="정보 가져오기",
                  command=self.fetch_video_info).grid(row=row, column=2, pady=5)

        # 비디오 정보 표시 영역
        row += 1
        info_frame = ttk.LabelFrame(main_frame, text="비디오 정보", padding="10")
        info_frame.grid(row=row, column=0, columnspan=3, sticky=(W, E), pady=10)
        info_frame.columnconfigure(0, weight=1)

        self.info_text = scrolledtext.ScrolledText(info_frame, height=6, width=70,
                                                   font=("맑은 고딕", 9), state='disabled')
        self.info_text.grid(row=0, column=0, sticky=(W, E))

        # 저장 위치
        row += 1
        ttk.Label(main_frame, text="저장 위치:", font=("맑은 고딕", 10)).grid(
            row=row, column=0, sticky=W, pady=5)
        ttk.Entry(main_frame, textvariable=self.download_path, width=50).grid(
            row=row, column=1, sticky=(W, E), pady=5, padx=5)
        ttk.Button(main_frame, text="찾아보기",
                  command=self.browse_folder).grid(row=row, column=2, pady=5)

        # 해상도 선택
        row += 1
        ttk.Label(main_frame, text="해상도:", font=("맑은 고딕", 10)).grid(
            row=row, column=0, sticky=W, pady=5)
        self.resolution_combo = ttk.Combobox(main_frame, textvariable=self.resolution_var,
                                            state='readonly', width=47)
        self.resolution_combo['values'] = ("최고 화질",)
        self.resolution_combo.grid(row=row, column=1, sticky=(W, E), pady=5, padx=5)

        # 자막 다운로드 옵션
        row += 1
        subtitle_frame = ttk.LabelFrame(main_frame, text="자막 설정", padding="10")
        subtitle_frame.grid(row=row, column=0, columnspan=3, sticky=(W, E), pady=10)

        ttk.Checkbutton(subtitle_frame, text="자막 다운로드",
                       variable=self.download_subtitles_var,
                       command=self.toggle_subtitle_options).grid(row=0, column=0, sticky=W)

        ttk.Label(subtitle_frame, text="언어 (쉼표로 구분):").grid(
            row=1, column=0, sticky=W, pady=5)
        self.subtitle_entry = ttk.Entry(subtitle_frame, textvariable=self.subtitle_langs_var,
                                       width=30, state='disabled')
        self.subtitle_entry.grid(row=1, column=1, sticky=W, pady=5, padx=5)

        ttk.Label(subtitle_frame, text="예: ko,en,ja",
                 font=("맑은 고딕", 8), foreground="gray").grid(
            row=2, column=1, sticky=W)

        # 진행 상태
        row += 1
        progress_frame = ttk.LabelFrame(main_frame, text="다운로드 진행 상태", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(W, E), pady=10)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=600)
        self.progress_bar.grid(row=0, column=0, sticky=(W, E), pady=5)

        self.status_label = Label(progress_frame, text="대기 중...",
                                 font=("맑은 고딕", 9), anchor=W)
        self.status_label.grid(row=1, column=0, sticky=(W, E))

        # 로그 영역
        row += 1
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(W, E, N, S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70,
                                                 font=("맑은 고딕", 9), state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(W, E, N, S))

        # 다운로드 버튼
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        self.download_button = ttk.Button(button_frame, text="다운로드 시작",
                                         command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=5)

        ttk.Button(button_frame, text="로그 지우기",
                  command=self.clear_log).grid(row=0, column=1, padx=5)

        # 초기 로그
        self.log("YouTube 다운로더가 시작되었습니다.")
        self.log("YouTube URL을 입력하고 '정보 가져오기'를 클릭하세요.")

    def toggle_subtitle_options(self):
        """자막 옵션 토글"""
        if self.download_subtitles_var.get():
            self.subtitle_entry.config(state='normal')
        else:
            self.subtitle_entry.config(state='disabled')

    def browse_folder(self):
        """저장 폴더 선택"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
            self.log(f"저장 위치 변경: {folder}")

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

    def update_info_text(self, text):
        """비디오 정보 업데이트"""
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state='disabled')

    def fetch_video_info(self):
        """비디오 정보 가져오기"""
        url = self.url_var.get().strip()

        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력하세요.")
            return

        self.log("비디오 정보를 가져오는 중...")
        self.status_label.config(text="비디오 정보를 가져오는 중...")

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

            info_text = f"제목: {title}\n"
            info_text += f"채널: {uploader}\n"
            info_text += f"길이: {duration_str}\n"
            info_text += f"조회수: {view_count:,}\n"

            # 자막 정보
            subtitles = self.video_info.get('subtitles', {})
            auto_captions = self.video_info.get('automatic_captions', {})
            all_subs = set(list(subtitles.keys()) + list(auto_captions.keys()))

            if all_subs:
                info_text += f"사용 가능한 자막: {', '.join(sorted(all_subs))}"

            self.root.after(0, self.update_info_text, info_text)

            # 포맷 정보 가져오기
            self.formats = self._get_available_formats()

            # 해상도 콤보박스 업데이트
            format_options = ["최고 화질"]
            for fmt in self.formats:
                format_options.append(f"{fmt['resolution']} ({fmt['height']}p) - {fmt['ext']}")

            self.root.after(0, lambda: self.resolution_combo.config(values=format_options))
            self.root.after(0, lambda: self.resolution_var.set("최고 화질"))

            self.root.after(0, self.log, f"비디오 정보를 가져왔습니다: {title}")
            self.root.after(0, self.log, f"사용 가능한 해상도: {len(self.formats)}개")
            self.root.after(0, lambda: self.status_label.config(text="준비 완료"))

        except Exception as e:
            error_msg = f"오류 발생: {str(e)}"
            self.root.after(0, self.log, error_msg)
            self.root.after(0, lambda: self.status_label.config(text="오류 발생"))
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
        self.download_button.config(state='disabled')
        self.progress_var.set(0)

        # 별도 스레드에서 다운로드
        thread = threading.Thread(target=self._download_thread,
                                 args=(self.url_var.get(), format_id, download_subs, subtitle_langs))
        thread.daemon = True
        thread.start()

    def _download_thread(self, url, format_id, download_subs, subtitle_langs):
        """다운로드 (스레드)"""
        try:
            ydl_opts = {
                'outtmpl': str(Path(self.download_path.get()) / '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }

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

            self.root.after(0, self.log, "다운로드 시작...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.root.after(0, self.log, "다운로드 완료!")
            self.root.after(0, lambda: self.status_label.config(text="다운로드 완료!"))
            self.root.after(0, messagebox.showinfo, "완료",
                          f"다운로드가 완료되었습니다!\n저장 위치: {self.download_path.get()}")

        except Exception as e:
            error_msg = f"다운로드 오류: {str(e)}"
            self.root.after(0, self.log, error_msg)
            self.root.after(0, lambda: self.status_label.config(text="다운로드 실패"))
            self.root.after(0, messagebox.showerror, "오류", error_msg)

        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.download_button.config(state='normal'))
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
            status_text = f"다운로드 중... 속도: {speed} | 남은 시간: {eta}"
            self.root.after(0, lambda: self.status_label.config(text=status_text))

        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_label.config(text="변환 중..."))
            self.root.after(0, self.log, "다운로드 완료, 파일 변환 중...")


def main():
    """메인 함수"""
    root = Tk()
    app = YouTubeDownloaderGUI(root)

    # 윈도우 아이콘 설정 (선택 사항)
    try:
        # ico 파일이 있으면 설정
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            root.iconbitmap(icon_path)
    except:
        pass

    root.mainloop()


if __name__ == "__main__":
    main()
