#!/usr/bin/env python3
"""
YouTube 다운로더
해상도 선택 및 자막 다운로드 기능 포함
"""

import os
import sys
from pathlib import Path
import yt_dlp
from colorama import init, Fore, Style

# colorama 초기화
init(autoreset=True)


class YouTubeDownloader:
    def __init__(self, download_path="downloads"):
        """
        YouTube 다운로더 초기화

        Args:
            download_path: 다운로드할 디렉토리 경로
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)

    def get_video_info(self, url):
        """
        비디오 정보 및 사용 가능한 포맷 가져오기

        Args:
            url: YouTube 비디오 URL

        Returns:
            dict: 비디오 정보
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"{Fore.RED}오류 발생: {str(e)}")
            return None

    def get_available_formats(self, info):
        """
        사용 가능한 포맷 정리

        Args:
            info: 비디오 정보 딕셔너리

        Returns:
            list: 포맷 리스트
        """
        formats = []
        seen_resolutions = set()

        for f in info.get('formats', []):
            # 비디오와 오디오가 모두 있는 포맷만 선택
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                resolution = f.get('resolution', 'Unknown')
                height = f.get('height', 0)
                ext = f.get('ext', 'mp4')
                filesize = f.get('filesize', 0)

                if resolution not in seen_resolutions and height > 0:
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': resolution,
                        'height': height,
                        'ext': ext,
                        'filesize': filesize,
                    })
                    seen_resolutions.add(resolution)

        # 해상도 높은 순으로 정렬
        formats.sort(key=lambda x: x['height'], reverse=True)

        return formats

    def format_filesize(self, size):
        """
        파일 크기를 읽기 쉬운 형식으로 변환

        Args:
            size: 바이트 단위 크기

        Returns:
            str: 형식화된 크기
        """
        if not size:
            return "Unknown"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_available_subtitles(self, info):
        """
        사용 가능한 자막 목록 가져오기

        Args:
            info: 비디오 정보 딕셔너리

        Returns:
            dict: 자막 정보
        """
        subtitles = info.get('subtitles', {})
        automatic_captions = info.get('automatic_captions', {})

        all_subtitles = {}

        # 수동 자막
        for lang, subs in subtitles.items():
            all_subtitles[lang] = {'type': 'manual', 'formats': subs}

        # 자동 생성 자막
        for lang, subs in automatic_captions.items():
            if lang not in all_subtitles:
                all_subtitles[lang] = {'type': 'auto', 'formats': subs}

        return all_subtitles

    def check_ffmpeg(self):
        """
        ffmpeg 설치 확인

        Returns:
            bool: ffmpeg가 설치되어 있으면 True
        """
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'],
                                  capture_output=True,
                                  timeout=5)
            return result.returncode == 0
        except:
            return False

    def download_video(self, url, format_id=None, download_subtitles=False, subtitle_langs=None):
        """
        비디오 다운로드

        Args:
            url: YouTube 비디오 URL
            format_id: 포맷 ID (None이면 최고 화질)
            download_subtitles: 자막 다운로드 여부
            subtitle_langs: 다운로드할 자막 언어 리스트
        """
        ydl_opts = {
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }

        # ffmpeg 확인
        has_ffmpeg = self.check_ffmpeg()

        if not has_ffmpeg:
            print(f"\n{Fore.YELLOW}⚠️  경고: ffmpeg가 설치되어 있지 않습니다.")
            print(f"{Fore.YELLOW}📦 단일 파일 포맷으로 다운로드합니다. (화질이 제한될 수 있습니다)")
            print(f"{Fore.CYAN}💡 최고 화질을 원하시면 ffmpeg를 설치하세요. (README.md 참고)")
            # ffmpeg 없이 다운로드 가능한 최고 품질 단일 파일 선택
            ydl_opts['format'] = 'best[ext=mp4]/best'
        else:
            # ffmpeg 있으면 최고 화질 비디오+오디오 병합
            if format_id:
                # 선택한 포맷 + 최고 품질 오디오
                ydl_opts['format'] = f'{format_id}+bestaudio/best'
            else:
                # 최고 화질
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

        # 자막 다운로드 설정
        if download_subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            if subtitle_langs:
                ydl_opts['subtitleslangs'] = subtitle_langs
            else:
                ydl_opts['subtitleslangs'] = ['ko', 'en']  # 기본값: 한국어, 영어
            ydl_opts['subtitlesformat'] = 'srt/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"\n{Fore.GREEN}다운로드 시작...")
                ydl.download([url])
                print(f"\n{Fore.GREEN}다운로드 완료!")
                print(f"{Fore.CYAN}저장 위치: {self.download_path.absolute()}")

                if not has_ffmpeg:
                    print(f"\n{Fore.YELLOW}💡 팁: ffmpeg를 설치하면 더 높은 화질로 다운로드할 수 있습니다.")
        except Exception as e:
            error_msg = str(e)
            print(f"\n{Fore.RED}다운로드 오류: {error_msg}")

            # ffmpeg 관련 오류 안내
            if 'ffmpeg' in error_msg.lower():
                print(f"\n{Fore.YELLOW}해결 방법:")
                print(f"{Fore.CYAN}Windows: https://github.com/BtbN/FFmpeg-Builds/releases")
                print(f"{Fore.CYAN}자세한 내용은 README.md를 참고하세요.")

    def progress_hook(self, d):
        """
        다운로드 진행 상태 표시

        Args:
            d: 진행 상태 딕셔너리
        """
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\r{Fore.YELLOW}진행: {percent} | 속도: {speed} | 남은 시간: {eta}", end='')
        elif d['status'] == 'finished':
            print(f"\n{Fore.GREEN}다운로드 완료, 변환 중...")


def main():
    """메인 함수"""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 60)
    print("YouTube 다운로더")
    print("=" * 60)
    print(Style.RESET_ALL)

    downloader = YouTubeDownloader()

    # URL 입력
    url = input(f"\n{Fore.CYAN}YouTube URL을 입력하세요: {Style.RESET_ALL}").strip()

    if not url:
        print(f"{Fore.RED}URL이 입력되지 않았습니다.")
        return

    # 비디오 정보 가져오기
    print(f"\n{Fore.YELLOW}비디오 정보를 가져오는 중...")
    info = downloader.get_video_info(url)

    if not info:
        return

    # 비디오 정보 표시
    print(f"\n{Fore.GREEN}{Style.BRIGHT}제목: {info.get('title', 'Unknown')}")
    print(f"{Fore.GREEN}채널: {info.get('uploader', 'Unknown')}")
    print(f"{Fore.GREEN}길이: {info.get('duration', 0) // 60}분 {info.get('duration', 0) % 60}초")

    # 사용 가능한 포맷 표시
    formats = downloader.get_available_formats(info)

    if not formats:
        print(f"\n{Fore.YELLOW}사용 가능한 포맷이 없습니다. 기본 포맷으로 다운로드합니다.")
        format_id = None
    else:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}사용 가능한 해상도:")
        print("-" * 60)

        for idx, fmt in enumerate(formats, 1):
            filesize_str = downloader.format_filesize(fmt['filesize'])
            print(f"{idx}. {fmt['resolution']} ({fmt['height']}p) - {fmt['ext']} - {filesize_str}")

        print(f"0. 최고 화질 (자동 선택)")
        print("-" * 60)

        # 해상도 선택
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}선택 (0-{len(formats)}): {Style.RESET_ALL}").strip()
                choice_num = int(choice)

                if choice_num == 0:
                    format_id = None
                    print(f"{Fore.GREEN}최고 화질 선택됨")
                    break
                elif 1 <= choice_num <= len(formats):
                    format_id = formats[choice_num - 1]['format_id']
                    print(f"{Fore.GREEN}{formats[choice_num - 1]['resolution']} 선택됨")
                    break
                else:
                    print(f"{Fore.RED}올바른 번호를 입력하세요.")
            except ValueError:
                print(f"{Fore.RED}숫자를 입력하세요.")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}취소되었습니다.")
                return

    # 자막 다운로드 옵션
    download_subs = False
    subtitle_langs = None

    subtitles = downloader.get_available_subtitles(info)

    if subtitles:
        print(f"\n{Fore.CYAN}사용 가능한 자막:")
        print("-" * 60)

        subtitle_list = []
        for idx, (lang, sub_info) in enumerate(sorted(subtitles.items()), 1):
            sub_type = "수동" if sub_info['type'] == 'manual' else "자동생성"
            print(f"{idx}. {lang} ({sub_type})")
            subtitle_list.append(lang)

        print("-" * 60)

        sub_choice = input(f"\n{Fore.CYAN}자막을 다운로드하시겠습니까? (y/n): {Style.RESET_ALL}").strip().lower()

        if sub_choice == 'y':
            download_subs = True
            lang_input = input(f"{Fore.CYAN}언어 코드 입력 (쉼표로 구분, 엔터는 한국어/영어): {Style.RESET_ALL}").strip()

            if lang_input:
                subtitle_langs = [lang.strip() for lang in lang_input.split(',')]
                print(f"{Fore.GREEN}선택된 자막: {', '.join(subtitle_langs)}")
            else:
                subtitle_langs = ['ko', 'en']
                print(f"{Fore.GREEN}기본 자막 선택됨: 한국어, 영어")
    else:
        print(f"\n{Fore.YELLOW}사용 가능한 자막이 없습니다.")

    # 다운로드 시작
    downloader.download_video(url, format_id, download_subs, subtitle_langs)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}프로그램이 중단되었습니다.")
        sys.exit(0)
