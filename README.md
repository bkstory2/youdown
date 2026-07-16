# YouTube 다운로더 - Python GUI 버전

캡처 이미지의 프로그램을 Python으로 완벽하게 재구현했습니다.

## 설치 방법

### 1단계: Python 설치
Python 3.7 이상이 필요합니다. [python.org](https://www.python.org)에서 다운로드하세요.

### 2단계: yt-dlp 설치
터미널(명령 프롬프트)을 열고 다음 명령어를 실행하세요:

```bash
pip install yt-dlp
```

### 3단계: ffmpeg 설치 (필수)
MP4로 변환하려면 ffmpeg가 필요합니다:

**Windows:**
```bash
pip install ffmpeg-python
```

또는 [ffmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 직접 다운로드할 수 있습니다.

## 실행 방법

터미널에서 다음 명령어를 실행하세요:

```bash
python youtube_downloader.py
```

또는 파일 탐색기에서 `youtube_downloader.py` 파일을 더블 클릭하면 됩니다.

## 사용 방법

1. **YouTube URL 입력** - 다운로드할 영상의 URL을 붙여넣기합니다.
2. **화질 선택** - 1080, 720, 480, 360, 최고화질 중 선택합니다.
3. **다운로드 형식 선택**:
   - MP4: 동영상 파일 (선택한 화질)
   - MP3: 음악만 추출 (MP3 파일)
4. **저장 위치** - 기본값은 다운로드 폴더입니다. "변경" 버튼으로 다른 폴더 선택 가능
5. **다운로드** - 다운로드 버튼을 클릭하면 진행률이 표시됩니다.

## 주요 기능

✅ **1080p 화질 지원** - 고화질 다운로드 가능  
✅ **화질 선택** - 1080, 720, 480, 360p 중 선택  
✅ **MP3 추출** - 동영상에서 음악만 추출  
✅ **진행률 표시** - 다운로드 진행상황 실시간 표시  
✅ **폴더 선택** - 저장 위치 자유롭게 설정  

## 문제 해결

### "yt-dlp가 설치되지 않았습니다" 오류
```bash
pip install --upgrade yt-dlp
```

### ffmpeg 오류
```bash
pip install ffmpeg-python
```

### 권한 거부 오류
관리자 권한으로 터미널을 다시 열고 실행해보세요.

## 기술 스펙

- **언어**: Python 3.7+
- **GUI**: tkinter (기본 내장)
- **의존성**: yt-dlp, ffmpeg
- **호환성**: Windows, macOS, Linux

---

문제 발생 시 터미널 출력 메시지를 확인해주세요!
