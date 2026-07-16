import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import os
import sys
import json
import shutil

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("yt-dlp GUI Downloader")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        self.config_file = os.path.join(os.path.expanduser("~"), ".youtube_downloader_config.json")
        self.download_path = self.load_config()
        self.ensure_output_directories()
        self.is_downloading = False
        self.current_processes = {}
        self.process_lock = threading.Lock()
        
        self.setup_ui()
        
    def load_config(self):
        """저장된 폴더 경로 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    path = config.get('download_path')
                    if path and os.path.exists(path):
                        return path
        except Exception as e:
            print(f"Config 로드 오류: {e}")
        
        # 기본값
        return os.path.expanduser("~/Downloads")
    
    def save_config(self):
        """폴더 경로 저장"""
        try:
            config = {'download_path': self.download_path}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Config 저장 오류: {e}")

    def ensure_output_directories(self):
        """선택한 폴더 아래에 MP3와 MP4 저장 폴더를 만든다."""
        for format_type in ("mp3", "mp4"):
            os.makedirs(os.path.join(self.download_path, format_type), exist_ok=True)

    def get_ffmpeg_location(self):
        """ffmpeg 실행 파일이 들어 있는 폴더를 찾는다."""
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return os.path.dirname(ffmpeg_path)

        winget_packages = os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages"
        )
        if os.path.isdir(winget_packages):
            for root, _, files in os.walk(winget_packages):
                if "ffmpeg.exe" in files:
                    return root
        return None
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # YouTube URL 입력
        ttk.Label(main_frame, text="YouTube URL", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=80)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        # 화질 선택
        ttk.Label(main_frame, text="화질 선택", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value="1080")
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        qualities = [("1080", "1080"), ("720", "720"), ("480", "480"), ("360", "360"), ("최고화질", "best")]
        for text, value in qualities:
            ttk.Radiobutton(quality_frame, text=text, variable=self.quality_var, value=value).pack(side=tk.LEFT, padx=5)
        
        # 다운로드 형식
        ttk.Label(main_frame, text="다운로드 형식", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        self.mp4_var = tk.BooleanVar(value=True)
        self.mp3_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(format_frame, text="MP4 (동영상)", variable=self.mp4_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(format_frame, text="MP3 (음악만)", variable=self.mp3_var).pack(side=tk.LEFT, padx=5)
        
        # 저장 폴더 선택
        ttk.Label(main_frame, text="저장 위치", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        self.folder_label = ttk.Label(folder_frame, text=self.download_path, foreground="blue")
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="변경", command=self.select_folder, width=10).pack(side=tk.RIGHT, padx=5)
        
        # 다운로드 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.download_btn = ttk.Button(button_frame, text="다운로드", command=self.start_download, width=20)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="중지", command=self.stop_download, width=20, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="초기화", command=self.reset_all, width=20).pack(side=tk.LEFT, padx=5)
        
        # 진행률 표시
        ttk.Label(main_frame, text="진행 상황", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 상태 메시지
        self.status_text = tk.Text(main_frame, height=10, width=80, state=tk.DISABLED)
        self.status_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=7, column=3, sticky=(tk.N, tk.S))
        self.status_text.config(yscrollcommand=scrollbar.set)
        
    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.ensure_output_directories()
            self.folder_label.config(text=folder)
            self.save_config()
    
    def add_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def start_download(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("오류", "YouTube URL을 입력해주세요.")
            return
        
        if not self.mp4_var.get() and not self.mp3_var.get():
            messagebox.showerror("오류", "최소 하나의 형식을 선택해주세요.")
            return
        
        if self.is_downloading:
            messagebox.showwarning("알림", "이미 다운로드 중입니다.")
            return
        
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.download_video, args=(url,), daemon=True)
        thread.start()
    
    def download_video(self, url):
        try:
            self.add_status(f"다운로드 시작: {url}")
            
            quality = self.quality_var.get()
            download_mp4 = self.mp4_var.get()
            download_mp3 = self.mp3_var.get()
            results = {}

            def run_format(format_name):
                self.add_status(f"\n=== {format_name} 다운로드 시작 ===")
                results[format_name.upper()] = self.download_format(
                    url, quality, format_name
                )

            tasks = []
            if download_mp3:
                tasks.append(threading.Thread(target=run_format, args=("mp3",)))
            if download_mp4:
                tasks.append(threading.Thread(target=run_format, args=("mp4",)))

            # MP3와 MP4는 각각 별도 yt-dlp 프로세스로 동시에 실행한다.
            for task in tasks:
                task.start()
            for task in tasks:
                task.join()

            if not self.is_downloading:
                self.add_status("\n⏹ 다운로드가 중지되었습니다.")
                return
            
            completed_formats = [name for name, succeeded in results.items() if succeeded]
            failed_formats = [name for name, succeeded in results.items() if not succeeded]
            if failed_formats:
                self.add_status(f"\n✗ 실패: {', '.join(failed_formats)}")
                self.add_status(f"✓ 완료: {', '.join(completed_formats) or '없음'}")
                messagebox.showwarning("일부 실패", "일부 다운로드가 실패했습니다. 상태창을 확인해주세요.")
            else:
                self.add_status(f"\n✓ 모든 다운로드 완료: {', '.join(completed_formats)}")
                messagebox.showinfo("완료", "선택한 MP3와 MP4 다운로드가 완료되었습니다.")
        
        except Exception as e:
            self.add_status(f"\n✗ 오류 발생: {str(e)}")
            messagebox.showerror("오류", f"오류 발생: {str(e)}")
        
        finally:
            self.is_downloading = False
            with self.process_lock:
                self.current_processes.clear()
            self.download_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def download_format(self, url, quality, format_type):
        """MP4 또는 MP3 다운로드"""
        try:
            ffmpeg_location = self.get_ffmpeg_location()
            if not ffmpeg_location:
                raise RuntimeError(
                    "ffmpeg를 찾을 수 없습니다. 프로그램을 종료한 뒤 다시 실행해주세요."
                )

            self.add_status(f"ffmpeg 사용 위치: {ffmpeg_location}")
            output_directory = os.path.join(self.download_path, format_type)
            os.makedirs(output_directory, exist_ok=True)
            output_template = os.path.join(output_directory, "%(title)s.%(ext)s")

            if format_type == "mp3":
                # MP3 추출 - 명시적으로 mp3 포맷 지정
                cmd = [
                    "yt-dlp",
                    "--ffmpeg-location", ffmpeg_location,
                    "-f", "best",
                    "-x",  # 오디오만 추출
                    "--audio-format", "mp3",
                    "--audio-quality", "0",  # 최고 품질
                    "-o", output_template,
                    url
                ]
                self.add_status("형식: MP3 (음악만 추출, m4a→mp3 자동 변환)")
            else:
                # MP4 다운로드 - 오디오 포함 필수
                if quality == "best":
                    # 최고 품질 MP4 (오디오 필수)
                    format_str = "(bestvideo[ext=mp4]+bestaudio[ext=m4a])/(bestvideo[ext=mp4]+bestaudio)/best[ext=mp4]/best"
                else:
                    # 지정된 화질 MP4 (오디오 필수)
                    format_str = f"(bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a])/(bestvideo[height<={quality}][ext=mp4]+bestaudio)/best[height<={quality}][ext=mp4]/best"
                
                cmd = [
                    "yt-dlp",
                    "--ffmpeg-location", ffmpeg_location,
                    "-f", format_str,
                    "--merge-output-format", "mp4",
                    "-o", output_template,
                    url
                ]
                self.add_status(f"형식: MP4 (화질: {quality}p, 오디오 포함)")
            
            self.add_status(f"저장 위치: {output_directory}")
            self.add_status("다운로드 중...\n")
            
            # 프로세스 실행
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            with self.process_lock:
                self.current_processes[format_type] = process
            
            for line in process.stdout:
                if not self.is_downloading:
                    process.terminate()
                    return False
                line = line.strip()
                if line:
                    self.add_status(line)
                    if "%" in line and "ETA" in line:
                        try:
                            percent_str = line.split("%")[0].split()[-1]
                            percent = float(percent_str)
                            self.progress_var.set(min(percent, 100))
                        except:
                            pass
            
            process.wait()
            
            if process.returncode == 0:
                self.add_status(f"✓ {format_type.upper()} 다운로드 완료!")
                return True
            else:
                self.add_status(f"✗ {format_type.upper()} 다운로드 실패!")
                return False
        
        except FileNotFoundError:
            self.add_status("\n✗ 오류: yt-dlp가 설치되지 않았습니다.")
            self.add_status("pip install yt-dlp 로 설치해주세요.")
            messagebox.showerror("오류", "yt-dlp가 설치되지 않았습니다.\npip install yt-dlp 를 실행해주세요.")
            return False
        
        except Exception as e:
            self.add_status(f"\n✗ 오류 발생: {str(e)}")
            return False
        finally:
            with self.process_lock:
                self.current_processes.pop(format_type, None)
    
    def stop_download(self):
        if self.is_downloading:
            self.is_downloading = False
            self.add_status("\n⏹ 다운로드 중지 중...")
            with self.process_lock:
                processes = list(self.current_processes.values())
            for process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            messagebox.showinfo("알림", "다운로드가 중지되었습니다.")
    
    def reset_all(self):
        """모든 내용 초기화"""
        if self.is_downloading:
            messagebox.showwarning("알림", "다운로드 중에는 초기화할 수 없습니다.")
            return
        
        # 텍스트 박스 초기화
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        # 진행률 초기화
        self.progress_var.set(0)
        
        messagebox.showinfo("알림", "모든 내용이 초기화되었습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
