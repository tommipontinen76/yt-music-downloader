#!/usr/bin/env python3
"""
YT Music Playlist Downloader
A PyQt6 GUI for downloading YouTube Music playlists via yt-dlp + ffmpeg.
"""
# ... existing code ...
import sys
import os
import threading
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
    QProgressBar, QTextEdit, QFrame, QSizePolicy, QSlider,
    QGroupBox, QSpacerItem, QCheckBox, QTabWidget, QFormLayout, QSpinBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSettings, QUrl
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QDesktopServices

def get_base_path():
    """Get the base path for resources, handling both source and PyInstaller environments."""
    if getattr(sys, 'frozen', False):
        # Running as a bundled binary (PyInstaller)
        return sys._MEIPASS
    else:
        # Running from source
        return os.path.dirname(os.path.abspath(__file__))

# Ensure yt-dlp availability is defined before the UI references it
try:
    import yt_dlp  # type: ignore

    YT_DLP_AVAILABLE = True
except Exception:
    YT_DLP_AVAILABLE = False

# ─────────────────────────── Stylesheet ───────────────────────────

STYLE = """
QMainWindow, QWidget {
    background-color: #0f0f13;
    color: #e8e6f0;
    font-family: "Segoe UI", "Ubuntu", sans-serif;
    font-size: 13px;
}

/* Labels should not paint a solid rectangle behind text (fixes “black boxes” on gradients/panels) */
QLabel {
    background-color: transparent;
}

QGroupBox {
    background-color: #17171f;
    border: 1px solid #2a2a3a;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    font-weight: 600;
    font-size: 12px;
    color: #7c6af5;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -1px;
    padding: 0 6px;
    background-color: #17171f;
}

QLineEdit {
    background-color: #1e1e2a;
    border: 1px solid #2e2e42;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e8e6f0;
    font-size: 13px;
    selection-background-color: #5a48d4;
}
QLineEdit:focus {
    border: 1px solid #7c6af5;
    background-color: #22223a;
}
QLineEdit::placeholder {
    color: #55536a;
}

QPushButton {
    background-color: #2a2a3a;
    border: 1px solid #3a3a52;
    border-radius: 6px;
    padding: 8px 18px;
    color: #c8c4e8;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #32324a;
    border-color: #5a48d4;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #3a3a55;
}
QPushButton:disabled {
    background-color: #1a1a24;
    color: #44425a;
    border-color: #22222e;
}

QPushButton#downloadBtn {
    background-color: #5a48d4;
    border: none;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    padding: 10px 28px;
    border-radius: 7px;
    letter-spacing: 0.5px;
}
QPushButton#downloadBtn:hover {
    background-color: #6d5ae8;
}
QPushButton#downloadBtn:pressed {
    background-color: #4a3aaa;
}
QPushButton#downloadBtn:disabled {
    background-color: #2a2640;
    color: #5a5278;
}

QTextEdit {
    background-color: #1e1e2a;
    border: 1px solid #2e2e42;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e8e6f0;
    font-size: 13px;
    selection-background-color: #5a48d4;
}
QTextEdit:focus {
    border: 1px solid #7c6af5;
    background-color: #22223a;
}

QListWidget {
    background-color: #1e1e2a;
    border: 1px solid #2e2e42;
    border-radius: 6px;
    color: #e8e6f0;
    font-size: 13px;
    padding: 5px;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #2a2a3a;
}
QListWidget::item:selected {
    background-color: #2a2a3a;
    color: #7c6af5;
}

QPushButton#cancelBtn {
    background-color: #3a1a2a;
    border: 1px solid #6a2a42;
    color: #e88a9a;
    font-weight: 600;
}
QPushButton#cancelBtn:hover {
    background-color: #4a2030;
    border-color: #e86070;
    color: #ffaaaa;
}

QComboBox {
    background-color: #1e1e2a;
    border: 1px solid #2e2e42;
    border-radius: 6px;
    padding: 7px 12px;
    color: #e8e6f0;
    font-size: 13px;
    min-width: 120px;
}
QComboBox:focus {
    border-color: #7c6af5;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #7c6af5;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2a;
    border: 1px solid #5a48d4;
    selection-background-color: #3a2a80;
    color: #e8e6f0;
    outline: none;
}

QProgressBar {
    background-color: #1a1a26;
    border: 1px solid #2a2a3a;
    border-radius: 5px;
    height: 10px;
    text-align: center;
    font-size: 11px;
    color: #a09ac8;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5a48d4, stop:0.5 #7c6af5, stop:1 #a088ff);
    border-radius: 4px;
}

QTextEdit {
    background-color: #0d0d14;
    border: 1px solid #1e1e2e;
    border-radius: 6px;
    padding: 8px;
    color: #9a98b8;
    font-family: "Consolas", "Fira Mono", "Ubuntu Mono", monospace;
    font-size: 12px;
    selection-background-color: #3a2a80;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #5a5278;
    letter-spacing: 1px;
}
QLabel#statusLabel {
    font-size: 12px;
    color: #7c6af5;
    font-style: italic;
}

QFrame#divider {
    background-color: #2a2a3a;
    max-height: 1px;
}
QFrame#headerFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1830, stop:1 #0f0f13);
    border-bottom: 1px solid #2a2a3a;
    border-radius: 0px;
}
"""
STYLE = STYLE + """
QTextEdit {
    background-color: #17171f;
    border: 1px solid #1e1e2e;
}
"""
STYLE = STYLE + """
QGroupBox {
    background-color: transparent;
}
QGroupBox::title {
    background-color: #0f0f13; /* match main window so the title doesn't sit on a panel */
}
"""


# ─────────────────────────── Worker ───────────────────────────────

class SearchWorker(QObject):
    finished = pyqtSignal(list, str)  # results, error_message

    def __init__(self, query, cookies_browser="None"):
        super().__init__()
        self.query = query
        self.cookies_browser = cookies_browser

    def run(self):
        if not YT_DLP_AVAILABLE:
            self.finished.emit([], "yt-dlp is not installed.")
            return

        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "no_warnings": True,
            }
            if self.cookies_browser and self.cookies_browser != "None":
                ydl_opts["cookiesfrombrowser"] = (self.cookies_browser,)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for top 10 results
                info = ydl.extract_info(f"ytsearch10:{self.query}", download=False)
                results = []
                if info and "entries" in info:
                    for entry in info["entries"]:
                        if entry:
                            results.append({
                                "title": entry.get("title", "Unknown Title"),
                                "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                "uploader": entry.get("uploader", "Unknown Artist"),
                                "duration": entry.get("duration"),
                                "id": entry.get("id"),
                            })
                self.finished.emit(results, "")
        except Exception as e:
            self.finished.emit([], str(e))


class DownloadWorker(QObject):
    progress = pyqtSignal(float, float, str)  # current_pct, overall_pct, speed/eta string
    track_started = pyqtSignal(str, int, int)  # title, current, total
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    playlist_info = pyqtSignal(int, str)  # count, playlist title

    def __init__(self, url, output_dir, audio_format, audio_quality, options=None):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.audio_format = audio_format
        self.audio_quality = audio_quality
        self.options = options or {}
        self._cancelled = False
        self._current_track = 0
        self._total_tracks = 0
        self._progress_lock = threading.Lock()

    def cancel(self):
        self._cancelled = True

    def _safe_folder_name(self, name: str) -> str:
        """
        Make a playlist title safe to use as a folder name across platforms.
        """
        import re
        name = (name or "").strip()
        name = re.sub(r'[\\/:*?"<>|]+', "_", name)  # Windows-illegal chars + path separators
        name = re.sub(r"\s+", " ", name).strip()
        if not name:
            name = "Playlist"

        name = name[:120].rstrip(" .")  # avoid trailing dots/spaces (Windows)

        # Windows reserved device names (case-insensitive)
        reserved = {
            "CON", "PRN", "AUX", "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10)),
        }
        base = name.split(".")[0].upper()
        if base in reserved:
            name = f"_{name}"

        return name

    def _truncate_metadata(self, entry: dict, max_len: int = 80) -> dict:
        """
        Truncate metadata fields in the entry to prevent 'File name too long' errors.
        This modifies a copy of the entry.
        """
        if not entry:
            return entry
        
        entry = entry.copy()
        # Fields often used in filename templates or metadata embedding
        fields = [
            "title", "track", "artist", "uploader", "album", "alt_title", "creator", 
            "playlist_title", "series", "season", "episode", "track_number", "artist_list"
        ]
        
        # Prioritize first artist for long artist lists
        for field in ["artist", "uploader", "creator"]:
            val = entry.get(field)
            if isinstance(val, str) and len(val) > max_len:
                # Try to split by common separators and take the first one
                # Standard YouTube Music artist strings often use comma or &
                for sep in [", ", " & ", " / ", " · "]:
                    if sep in val:
                        first_artist = val.split(sep)[0]
                        entry[field] = first_artist[:max_len].strip()
                        break
                else:
                    # Fallback to simple truncation
                    entry[field] = val[:max_len].strip()
        
        # Truncate other fields simply
        for field in fields:
            if field in ["artist", "uploader", "creator"]:
                continue # Already handled above
            val = entry.get(field)
            if isinstance(val, str) and len(val) > max_len:
                entry[field] = val[:max_len].strip()
                    
        return entry

    def _format_speed(self, speed_bps):
        if not speed_bps or speed_bps <= 0:
            return ""
        units = ["B/s", "KiB/s", "MiB/s", "GiB/s"]
        v = float(speed_bps)
        i = 0
        while v >= 1024.0 and i < len(units) - 1:
            v /= 1024.0
            i += 1
        return f"{v:.1f} {units[i]}"

    def _format_eta(self, eta_seconds):
        if eta_seconds is None:
            return ""
        try:
            eta_seconds = int(eta_seconds)
        except Exception:
            return ""
        m, s = divmod(max(0, eta_seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

    def _music_url(self, entry) -> str:
        """
        Return a music.youtube.com URL for the entry so yt-dlp follows
        Music-side redirects for tracks that are "unavailable" on regular YouTube
        but still playable on YouTube Music (e.g. after distributor changes).
        """
        video_id = entry.get('id') or entry.get('url', '')
        # Strip any existing URL down to just the ID if needed
        if '/' in video_id or '?' in video_id:
            import re
            m = re.search(r'(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})', video_id)
            video_id = m.group(1) if m else video_id
        if video_id and len(video_id) == 11:
            return f"https://music.youtube.com/watch?v={video_id}"
        # Fallback to whatever was in the entry
        return entry.get('webpage_url') or entry.get('url') or video_id

    def _inject_index(self, tmpl, index):
        # Explicitly inject playlist_index into the template to ensure it's preserved
        # even after yt-dlp re-extraction in process_ie_result.
        for key in ['playlist_index', 'playlist_autonumber']:
            # This regex matches %(key) followed by optional formatting, ending with a type character
            pattern = r'%\(' + key + r'\)([-+ #0]*\d*[diouxXeEfFgGcrsat])'

            def repl(match):
                fmt = match.group(1)
                try:
                    return ("%" + fmt) % index
                except Exception:
                    return str(index)

            tmpl = re.sub(pattern, repl, tmpl)
            # Handle cases that didn't match the standard format (e.g. malformed or simple %(key)s)
            tmpl = tmpl.replace(f'%({key})s', str(index))
            tmpl = tmpl.replace(f'%({key})', str(index))
        return tmpl

    def run(self):
        if not YT_DLP_AVAILABLE:
            self.finished.emit(False, "yt-dlp is not installed. Run: pip install yt-dlp")
            return

        # Check for ffmpeg
        import shutil
        if not shutil.which("ffmpeg"):
            self.finished.emit(False, "ffmpeg is not found. Please install it and add it to your PATH.")
            return

        # Quality map: label → yt-dlp audioquality value (0=best, 9=worst for VBR)
        quality_map = {
            "Best": "0",
            "320 kbps": "0",
            "256 kbps": "3",
            "192 kbps": "5",
            "128 kbps": "7",
            "Worst": "9",
        }
        q_value = quality_map.get(self.audio_quality, "0")

        # Postprocessor args per format
        postprocessor_args = []
        if self.audio_format in ["mp3", "aac"]:
            if self.audio_quality == "320 kbps":
                postprocessor_args = ["-b:a", "320k"]
            elif self.audio_quality == "256 kbps":
                postprocessor_args = ["-b:a", "256k"]
            elif self.audio_quality == "192 kbps":
                postprocessor_args = ["-b:a", "192k"]
            elif self.audio_quality == "128 kbps":
                postprocessor_args = ["-b:a", "128k"]

        create_playlist_folder = bool(self.options.get("create_playlist_folder", True))
        filename_template = (
                self.options.get("filename_template")
                or "%(playlist_index)s - %(artist,uploader)s - %(track,title)s.%(ext)s"
        ).strip()
        embed_metadata = bool(self.options.get("embed_metadata", True))
        embed_thumbnail = bool(self.options.get("embed_thumbnail", False))
        parse_extra_metadata = bool(self.options.get("parse_extra_metadata", True))
        skip_existing = bool(self.options.get("skip_existing", True))
        cookies_browser = self.options.get("cookies_browser", "None")
        retries = int(self.options.get("retries", 10) or 10)
        ratelimit_kib = int(self.options.get("ratelimit_kib", 0) or 0)
        parallel_downloads = int(self.options.get("parallel_downloads", 1) or 1)
        po_token = self.options.get("po_token", "").strip()
        enable_remote_components = bool(self.options.get("enable_remote_components", True))
        use_local_pot_provider = bool(self.options.get("use_local_pot_provider", False))
        fallback_on_unavailable = bool(self.options.get("fallback_on_unavailable", True))

        try:
            # 1) Fetch playlist info FIRST (so we can create a playlist-named subfolder)
            self.log.emit("🔍 Fetching playlist info...")

            # Fetch info with cookies if set
            info_opts = {
                "quiet": True,
                "no_warnings": False,
                "logger": self._YDLLogger(self),
                "extract_flat": "in_playlist",  # Speeds up playlist fetching significantly
            }
            if cookies_browser and cookies_browser != "None":
                info_opts["cookiesfrombrowser"] = (cookies_browser,)

            if enable_remote_components:
                info_opts["remote_components"] = ["ejs:github"]
            
            if use_local_pot_provider:
                # Add plugin directory to yt-dlp
                base_path = get_base_path()
                plugin_dir = os.path.join(base_path, "bgutil-ytdlp-pot-provider", "plugin")
                if not os.path.exists(plugin_dir):
                    # Try system-wide location
                    plugin_dir = "/usr/share/yt-music-downloader/bgutil-ytdlp-pot-provider/plugin"
                
                if os.path.exists(plugin_dir):
                    info_opts["plugin_dirs"] = [plugin_dir]
                
                # Configure the plugin to use the local server
                if "extractor_args" not in info_opts:
                    info_opts["extractor_args"] = {}
                
                # The plugin uses youtubepot-bgutilhttp:base_url
                info_opts["extractor_args"]["youtubepot-bgutilhttp"] = {"base_url": ["http://127.0.0.1:4416"]}

            # web_music accesses Music-only tracks; web is the cookie-compatible fallback.
            # ios is intentionally excluded — yt-dlp silently skips it when cookies are set.
            clients = ["mweb", "web"]
            if "extractor_args" not in info_opts:
                info_opts["extractor_args"] = {}
            if "youtube" not in info_opts["extractor_args"]:
                info_opts["extractor_args"]["youtube"] = {}
            info_opts["extractor_args"]["youtube"]["player_client"] = clients
            if po_token:
                info_opts["extractor_args"]["youtube"]["po_token"] = [po_token]

            if self._cancelled:
                self.finished.emit(False, "Cancelled.")
                return

            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                if info is None:
                    self.finished.emit(False, "Could not retrieve playlist info.")
                    return

            playlist_title = info.get("title", "Unknown Playlist")
            safe_title = self._safe_folder_name(playlist_title)

            entries = info.get("entries", [info])
            entries = [e for e in entries if e]
            self._total_tracks = len(entries)
            self.playlist_info.emit(self._total_tracks, playlist_title)
            self.log.emit(f"📀 Playlist: {playlist_title}  ({self._total_tracks} tracks)")

            # ── Pre-flight: skip playlist if all tracks already exist ──────────
            if skip_existing and create_playlist_folder:
                expected_playlist_dir = Path(self.output_dir) / safe_title
                audio_exts = {".mp3", ".m4a", ".opus", ".flac", ".wav", ".ogg", ".mka", ".webm"}
                if expected_playlist_dir.exists():
                    existing_audio = [f for f in expected_playlist_dir.iterdir()
                                      if f.is_file() and f.suffix.lower() in audio_exts]
                    if len(existing_audio) >= self._total_tracks:
                        self.log.emit(
                            f"  ⏭  Skipping playlist (all {self._total_tracks} tracks already exist): {playlist_title}")
                        self.finished.emit(True, f"✅ Skipped (already downloaded): {playlist_title}")
                        return

            # 2) Choose actual output directory
            if create_playlist_folder:
                playlist_dir = Path(self.output_dir) / safe_title
                playlist_dir.mkdir(parents=True, exist_ok=True)
                self.output_dir = str(playlist_dir)
            else:
                Path(self.output_dir).mkdir(parents=True, exist_ok=True)

            outtmpl = str(Path(self.output_dir) / filename_template)

            # 2.5) Prepare for skip_existing check
            # We determine the expected extension once here
            expected_ext = self.audio_format
            if expected_ext == "bestaudio":
                expected_ext = "mka" if embed_thumbnail else None

            postprocessors = []
            if self.audio_format != "bestaudio":
                postprocessors.append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": q_value,
                })

            if embed_metadata:
                postprocessors.append({"key": "FFmpegMetadata"})

            if embed_thumbnail:
                # Convert to png — universally supported by ffmpeg unlike jpg (mjpeg encoder
                # is absent in some distro builds and causes "Encoder not found" errors).
                postprocessors.append({"key": "FFmpegThumbnailsConvertor", "format": "png"})
                # If bestaudio is used, yt-dlp might download webm which doesn't support embedding.
                # In that case, we remux it to mka (Matroska Audio) which supports it losslessly.
                if self.audio_format == "bestaudio":
                    postprocessors.append({"key": "FFmpegVideoConvertor", "preferedformat": "mka"})
                # Requires ffmpeg, and works best when yt-dlp can retrieve a thumbnail
                postprocessors.append({"key": "EmbedThumbnail"})

            stop_on_error = self.options.get("stop_on_error", False)

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "outtmpl_na_placeholder": "",  # don't write "NA" when metadata field is missing
                "noplaylist": False,
                "progress_hooks": [self._progress_hook],
                "postprocessors": postprocessors,
                "quiet": True,
                "no_warnings": False,
                "logger": self._YDLLogger(self),
                "retries": retries,
                "writethumbnail": False,  # Initially False to prevent download during extraction
                "ignoreerrors": not stop_on_error,  # don't stop the whole playlist if one song fails, unless requested
                "trim_file_name": 120, # Limit filename length to 120 characters to avoid OS limits
            }

            if parse_extra_metadata:
                # Add metadata parsing from title/description if requested
                # This helps with videos that aren't properly tagged in YT Music but have info in the title/description
                ydl_opts["parse_metadata"] = [
                    "title:%(title)s",
                    "description:%(description)s",
                    # Try to extract year from title like (2023) or [2023]
                    r":(?P<release_year>(?:19|20)\d{2})",
                ]

            if cookies_browser and cookies_browser != "None":
                ydl_opts["cookiesfrombrowser"] = (cookies_browser,)

            if enable_remote_components:
                ydl_opts["remote_components"] = ["ejs:github"]
            if use_local_pot_provider:
                # Add plugin directory to yt-dlp
                base_path = get_base_path()
                plugin_dir = os.path.join(base_path, "bgutil-ytdlp-pot-provider", "plugin")
                if not os.path.exists(plugin_dir):
                    # Try system-wide location
                    plugin_dir = "/usr/share/yt-music-downloader/bgutil-ytdlp-pot-provider/plugin"
                
                if os.path.exists(plugin_dir):
                    ydl_opts["plugin_dirs"] = [plugin_dir]
                
                # Configure the plugin to use the local server
                if "extractor_args" not in ydl_opts:
                    ydl_opts["extractor_args"] = {}
                
                # The plugin uses youtubepot-bgutilhttp:base_url
                ydl_opts["extractor_args"]["youtubepot-bgutilhttp"] = {"base_url": ["http://127.0.0.1:4416"]}

            # web_music accesses Music-only tracks; web is the cookie-compatible fallback.
            # ios is intentionally excluded — yt-dlp silently skips it when cookies are set.
            clients = ["mweb", "web"]
            if "extractor_args" not in ydl_opts:
                ydl_opts["extractor_args"] = {}
            if "youtube" not in ydl_opts["extractor_args"]:
                ydl_opts["extractor_args"]["youtube"] = {}
            ydl_opts["extractor_args"]["youtube"]["player_client"] = clients
            if po_token:
                ydl_opts["extractor_args"]["youtube"]["po_token"] = [po_token]

            if skip_existing:
                ydl_opts["nooverwrites"] = True
            if ratelimit_kib > 0:
                ydl_opts["ratelimit"] = ratelimit_kib * 1024
            if postprocessor_args:
                if "postprocessor_args" not in ydl_opts:
                    ydl_opts["postprocessor_args"] = {}
                ydl_opts["postprocessor_args"]["ffmpegextractaudio"] = postprocessor_args

            if self._cancelled:
                self.finished.emit(False, "Cancelled.")
                return

            self.log.emit(f"⬇  Starting download to: {self.output_dir}\n")

            if parallel_downloads > 1:
                from concurrent.futures import ThreadPoolExecutor
                self.log.emit(f"🚀 Parallel mode enabled: {parallel_downloads} concurrent downloads")

                def download_entry(data):
                    index, entry = data
                    if self._cancelled:
                        return

                    # Ensure playlist_index is present for consistent filenames
                    # We always set it based on its index in the playlist to be sure
                    entry["playlist_index"] = index + 1

                    # Create a new ydl_opts for this specific entry to avoid state issues
                    entry_opts = ydl_opts.copy()
                    entry_opts["noplaylist"] = True

                    # Inject index directly into outtmpl to survive re-extraction
                    entry_opts["outtmpl"] = self._inject_index(ydl_opts["outtmpl"], index + 1)

                    with yt_dlp.YoutubeDL(entry_opts) as ydl_inner:
                        try:
                            # 1) Get full metadata first (without downloading thumbnails)
                            # This ensures we have enough info for prepare_filename to be accurate
                            original_url = self._music_url(entry)
                            self.log.emit(f"🔍 Extracting: {original_url}")
                            full_entry = ydl_inner.extract_info(original_url, download=False)
                            if not full_entry:
                                raise Exception("Could not extract metadata")

                            # Merge full entry back into entry for consistency
                            entry.update(full_entry)
                            entry["playlist_index"] = index + 1
                            
                            # Truncate long metadata to avoid "File name too long" errors
                            entry = self._truncate_metadata(entry)
                        except Exception as e:
                            # 1.5) Fallback search if original is unavailable
                            is_unavailable = any(term in str(e).lower() for term in ["unavailable", "not available", "available in your country"])
                            if fallback_on_unavailable and is_unavailable:
                                title = entry.get('title') or entry.get('id')
                                if title:
                                    self.log.emit(f"  🔍 '{title}' is unavailable. Searching for fallback...")
                                    search_opts = ydl_opts.copy()
                                    search_opts.update({
                                        "quiet": True,
                                        "extract_flat": True,
                                        "noplaylist": True,
                                    })
                                    with yt_dlp.YoutubeDL(search_opts) as ydl_s:
                                        try:
                                            # Try searching with title
                                            search_result = ydl_s.extract_info(f"ytsearch1:{title}", download=False)
                                            
                                            # If not found or low quality match, try adding artist/uploader if available
                                            artist = entry.get('artist') or entry.get('uploader')
                                            if (not search_result or not search_result.get('entries')) and artist and artist not in title:
                                                self.log.emit(f"  🔍 Not found with title. Trying '{artist} - {title}'...")
                                                search_result = ydl_s.extract_info(f"ytsearch1:{artist} - {title}", download=False)

                                            if search_result and 'entries' in search_result and search_result['entries']:
                                                best_match = search_result['entries'][0]
                                                new_url = best_match.get('url') or f"https://www.youtube.com/watch?v={best_match.get('id')}"
                                                self.log.emit(f"  ✅ Found fallback: {best_match.get('title')} ({new_url})")
                                                # Try extraction again with the new URL
                                                full_entry = ydl_inner.extract_info(new_url, download=False)
                                                if full_entry:
                                                    # Completely update the entry with new metadata
                                                    entry.clear()
                                                    entry.update(full_entry)
                                                    entry["playlist_index"] = index + 1
                                                    
                                                    # Truncate long metadata to avoid "File name too long" errors
                                                    entry = self._truncate_metadata(entry)
                                                    # Update original_url so subsequent logic uses the working one
                                                    original_url = new_url
                                                else:
                                                    raise Exception("Could not extract metadata from fallback")
                                            else:
                                                raise Exception(f"No fallback found for '{title}'")
                                        except Exception as se:
                                            self.log.emit(f"  ✖ Fallback failed: {se}")
                                            raise e # Re-raise original "unavailable" error
                                else:
                                    raise e
                            else:
                                raise e

                        try:
                            # Ensure we have a valid YouTube URL for processing (not a direct googlevideo.com link)
                            if 'googlevideo.com' in entry.get('url', ''):
                                entry['url'] = original_url

                            if skip_existing:
                                filename = ydl_inner.prepare_filename(entry)
                                # If we have an expected extension, check for that too
                                if expected_ext and "%(ext)s" in entry_opts["outtmpl"]:
                                    ext_filename = filename.rsplit(".", 1)[0] + "." + expected_ext
                                    if os.path.exists(ext_filename):
                                        filename = ext_filename

                                if os.path.exists(filename):
                                    self.log.emit(f"  ⏭  Skipping (already exists): {os.path.basename(filename)}")
                                    with self._progress_lock:
                                        self._current_track += 1
                                        current = self._current_track
                                        total = self._total_tracks
                                    self.track_started.emit(os.path.basename(filename), current, total)
                                    return

                                # Fallback: check with other possible audio extensions if bestaudio is used
                                if expected_ext == "mka":
                                    for alt_ext in ["mp3", "m4a", "opus", "flac", "wav"]:
                                        alt_filename = filename.rsplit(".", 1)[0] + "." + alt_ext
                                        if os.path.exists(alt_filename):
                                            self.log.emit(
                                                f"  ⏭  Skipping (already exists as {alt_ext}): {os.path.basename(alt_filename)}")
                                            with self._progress_lock:
                                                self._current_track += 1
                                                current = self._current_track
                                                total = self._total_tracks
                                            self.track_started.emit(os.path.basename(alt_filename), current, total)
                                            return

                            # 2) Enable thumbnails if requested and proceed to download
                            if embed_thumbnail:
                                ydl_inner.params['writethumbnail'] = True

                            result = ydl_inner.process_ie_result(entry, download=True)
                            # If result is None, it usually means ignoreerrors was triggered or video is unavailable
                            if result is None:
                                title = entry.get('title') or entry.get('id') or "Unknown track"
                                self.log.emit(f"  ✖  Failed (unavailable): {title}")
                                if stop_on_error:
                                    self._cancelled = True
                                with self._progress_lock:
                                    self._current_track += 1
                                    current = self._current_track
                                    total = self._total_tracks
                                self.track_started.emit(title, current, total)
                                return
                        except Exception as e:
                            title = entry.get('title') or entry.get('id') or "Unknown track"
                            self.log.emit(f"  ✖  Error processing {title}: {e}")
                            if stop_on_error:
                                self._cancelled = True
                            with self._progress_lock:
                                self._current_track += 1
                                current = self._current_track
                                total = self._total_tracks
                            self.track_started.emit(title, current, total)

                with ThreadPoolExecutor(max_workers=parallel_downloads) as executor:
                    list(executor.map(download_entry, enumerate(entries)))
            else:
                # Even for serial downloads, we process entries one by one if skip_existing is enabled
                # to ensure we can skip them correctly before any thumbnail download starts.
                if skip_existing:
                    for i, entry in enumerate(entries):
                        if self._cancelled: break

                        # Ensure playlist_index is present
                        # We always set it based on its index in the playlist to be sure
                        entry["playlist_index"] = i + 1

                        entry_opts = ydl_opts.copy()
                        entry_opts["noplaylist"] = True

                        # Inject index directly into outtmpl to survive re-extraction
                        entry_opts["outtmpl"] = self._inject_index(ydl_opts["outtmpl"], i + 1)

                        with yt_dlp.YoutubeDL(entry_opts) as ydl_inner:
                            try:
                                # 1) Get full metadata first (without downloading thumbnails)
                                original_url = self._music_url(entry)
                                self.log.emit(f"🔍 Extracting: {original_url}")
                                full_entry = ydl_inner.extract_info(original_url, download=False)
                                if not full_entry:
                                    raise Exception("Could not extract metadata")

                                entry.update(full_entry)
                                entry["playlist_index"] = i + 1
                                
                                # Truncate long metadata to avoid "File name too long" errors
                                entry = self._truncate_metadata(entry)
                            except Exception as e:
                                # 1.5) Fallback search if original is unavailable
                                is_unavailable = any(term in str(e).lower() for term in ["unavailable", "not available", "available in your country"])
                                if fallback_on_unavailable and is_unavailable:
                                    title = entry.get('title') or entry.get('id')
                                    if title:
                                        self.log.emit(f"  🔍 '{title}' is unavailable. Searching for fallback...")
                                        search_opts = ydl_opts.copy()
                                        search_opts.update({
                                            "quiet": True,
                                            "extract_flat": True,
                                            "noplaylist": True,
                                        })
                                        with yt_dlp.YoutubeDL(search_opts) as ydl_s:
                                            try:
                                                search_result = ydl_s.extract_info(f"ytsearch1:{title}", download=False)
                                                
                                                # If not found or low quality match, try adding artist/uploader if available
                                                artist = entry.get('artist') or entry.get('uploader')
                                                if (not search_result or not search_result.get('entries')) and artist and artist not in title:
                                                    self.log.emit(f"  🔍 Not found with title. Trying '{artist} - {title}'...")
                                                    search_result = ydl_s.extract_info(f"ytsearch1:{artist} - {title}", download=False)

                                                if search_result and 'entries' in search_result and search_result['entries']:
                                                    best_match = search_result['entries'][0]
                                                    new_url = best_match.get('url') or f"https://www.youtube.com/watch?v={best_match.get('id')}"
                                                    self.log.emit(f"  ✅ Found fallback: {best_match.get('title')} ({new_url})")
                                                    # Try extraction again with the new URL
                                                    full_entry = ydl_inner.extract_info(new_url, download=False)
                                                    if full_entry:
                                                        # Completely update the entry with new metadata
                                                        entry.clear()
                                                        entry.update(full_entry)
                                                        entry["playlist_index"] = i + 1
                                                        
                                                        # Truncate long metadata to avoid "File name too long" errors
                                                        entry = self._truncate_metadata(entry)
                                                        # Update original_url so subsequent logic uses the working one
                                                        original_url = new_url
                                                    else:
                                                        raise Exception("Could not extract metadata from fallback")
                                                else:
                                                    raise Exception(f"No fallback found for '{title}'")
                                            except Exception as se:
                                                self.log.emit(f"  ✖ Fallback failed: {se}")
                                                raise e  # Re-raise original "unavailable" error
                                    else:
                                        raise e
                                else:
                                    raise e

                            try:
                                # Ensure we have a valid YouTube URL for processing (not a direct googlevideo.com link)
                                if 'googlevideo.com' in entry.get('url', ''):
                                    entry['url'] = original_url

                                filename = ydl_inner.prepare_filename(entry)
                                # If we have an expected extension, check for that too
                                if expected_ext and "%(ext)s" in entry_opts["outtmpl"]:
                                    ext_filename = filename.rsplit(".", 1)[0] + "." + expected_ext
                                    if os.path.exists(ext_filename):
                                        filename = ext_filename

                                if os.path.exists(filename):
                                    self.log.emit(f"  ⏭  Skipping (already exists): {os.path.basename(filename)}")
                                    with self._progress_lock:
                                        self._current_track += 1
                                        current = self._current_track
                                        total = self._total_tracks
                                    self.track_started.emit(os.path.basename(filename), current, total)
                                    continue

                                # Fallback: check with other possible audio extensions if bestaudio is used
                                if expected_ext == "mka":
                                    for alt_ext in ["mp3", "m4a", "opus", "flac", "wav"]:
                                        alt_filename = filename.rsplit(".", 1)[0] + "." + alt_ext
                                        if os.path.exists(alt_filename):
                                            self.log.emit(
                                                f"  ⏭  Skipping (already exists as {alt_ext}): {os.path.basename(alt_filename)}")
                                            with self._progress_lock:
                                                self._current_track += 1
                                                current = self._current_track
                                                total = self._total_tracks
                                            self.track_started.emit(os.path.basename(alt_filename), current, total)
                                            break
                                    else:
                                        # only continue if break was not hit (i.e. no alt file found)
                                        pass
                                    if self._current_track > i:  # if we incremented it, we skipped
                                        continue

                                # 2) Enable thumbnails if requested and proceed to download
                                if embed_thumbnail:
                                    ydl_inner.params['writethumbnail'] = True

                                result = ydl_inner.process_ie_result(entry, download=True)
                                if result is None:
                                    title = entry.get('title') or entry.get('id') or "Unknown track"
                                    self.log.emit(f"  ✖  Failed (unavailable): {title}")
                                    if stop_on_error:
                                        self._cancelled = True
                                        break
                                    with self._progress_lock:
                                        self._current_track += 1
                                        current = self._current_track
                                        total = self._total_tracks
                                    self.track_started.emit(title, current, total)
                                    continue
                            except Exception as e:
                                title = entry.get('title') or entry.get('id') or "Unknown track"
                                self.log.emit(f"  ✖  Error processing {title}: {e}")
                                if stop_on_error:
                                    self._cancelled = True
                                    break
                                with self._progress_lock:
                                    self._current_track += 1
                                    current = self._current_track
                                    total = self._total_tracks
                                self.track_started.emit(title, current, total)
                                continue
                else:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([self.url])

        except Exception as e:
            if self._cancelled:
                self.finished.emit(False, "Download cancelled.")
            else:
                self.finished.emit(False, f"Error: {e}")
            return

        if self._cancelled:
            self.finished.emit(False, "Download cancelled.")
        else:
            self.finished.emit(True, f"✅ Done! {self._total_tracks} tracks saved to:\n{self.output_dir}")

    def _progress_hook(self, d):
        if self._cancelled:
            raise yt_dlp.utils.DownloadCancelled()

        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)

            speed_str = d.get("_speed_str", "") or self._format_speed(d.get("speed"))
            eta_str = d.get("_eta_str", "") or self._format_eta(d.get("eta"))

            filename = d.get("filename", "")
            title = Path(filename).stem if filename else "Unknown"

            if total > 0:
                pct = downloaded / total * 100
            else:
                pct = 0

            overall_pct = 0
            if self._total_tracks > 0:
                overall_pct = (self._current_track + (pct / 100.0)) / self._total_tracks * 100

            parts = []
            if speed_str:
                parts.append(speed_str)
            if eta_str:
                parts.append(f"ETA {eta_str}")
            info_str = "  ".join(parts)

            self.progress.emit(pct, overall_pct, info_str)

        elif status == "finished":
            filename = d.get("filename", "")
            title = Path(filename).stem if filename else "Track"

            with self._progress_lock:
                self._current_track += 1
                current = self._current_track
                total = self._total_tracks

            self.track_started.emit(title, current, total)
            self.log.emit(f"  ✔ [{current}/{total}] {title}")

            overall_pct = (current / total * 100) if total > 0 else 100
            self.progress.emit(100.0, overall_pct, "Converting...")

    class _YDLLogger:
        def __init__(self, worker):
            self.worker = worker
            import re
            self._ansi_re = re.compile(r"\x1b\[[0-9;]*m")

        def _clean(self, msg: str) -> str:
            return self._ansi_re.sub("", msg or "")

        def debug(self, msg):
            import re
            msg = self._clean(msg)
            if msg.startswith("[download] Downloading item"):
                # Inform the user what's happening during playlist processing
                item_match = re.search(r"Downloading item (\d+) of (\d+)", msg)
                if item_match:
                    curr, total = item_match.groups()
                    self.worker.log.emit(f"📋 Processing playlist item {curr}/{total}...")
                else:
                    self.worker.log.emit(msg)
            elif msg.startswith("[download]") or msg.startswith("[ExtractAudio]") or msg.startswith(
                    "[ThumbnailsConvertor]") or msg.startswith("[EmbedThumbnail]"):
                self.worker.log.emit(msg)

        def warning(self, msg):
            self.worker.log.emit(f"⚠ {self._clean(msg)}")

        def error(self, msg):
            self.worker.log.emit(f"✖ {self._clean(msg)}")


# ─────────────────────────── Main Window ──────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Music Downloader v0.2")
        self.setMinimumSize(800, 750)
        self.resize(1451, 1047)

        self._pot_provider_process = None

        # Settings: Using QSettings to save/load user choices
        # On Linux: ~/.config/yt-music-downloader/ytmusic-downloader.conf
        # On Windows: Documents/yt-music-downloader/ytmusic-downloader.ini
        if sys.platform == "win32":
            # On Windows, save settings in the Documents folder as requested
            docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
            settings_dir = os.path.join(docs_dir, "yt-music-downloader")
            os.makedirs(settings_dir, exist_ok=True)
            settings_path = os.path.join(settings_dir, "ytmusic-downloader.ini")
            self.settings = QSettings(settings_path, QSettings.Format.IniFormat)
        else:
            self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "yt-music-downloader",
                                      "ytmusic-downloader")

        self._worker = None
        self._thread = None
        self._last_output_dir_used = ""
        self._download_queue = []
        self._is_downloading = False

        self._ui_scale = 1.0
        self._build_ui()
        self._load_settings()

        # If local POT provider is enabled in settings, start it on launch
        if self.use_local_pot_provider.isChecked():
            import threading
            threading.Thread(target=self._start_pot_provider, daemon=True).start()

    def _apply_ui_scale(self, percent: int):
        """
        Scale the UI by adjusting the application's stylesheet font-size.
        """
        percent = max(75, min(150, int(percent)))
        self._ui_scale = percent / 100.0

        # Update the value label if it exists
        if hasattr(self, "ui_scale_value_label"):
            self.ui_scale_value_label.setText(f"{percent}%")

        # Dynamically update the stylesheet with the new base font sizes
        def scale_match(match):
            size = int(match.group(1))
            return f"font-size: {int(size * self._ui_scale)}px;"

        final_style = re.sub(r"font-size:\s*(\d+)px;", scale_match, STYLE)
        self.setStyleSheet(final_style)

    def _browse_default_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Output Folder",
            self.default_out_dir.text() or os.path.expanduser("~/Music"),
        )
        if folder:
            self.default_out_dir.setText(folder)
            self._save_settings()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─── Header Section ───
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 35, 30, 30)
        header_layout.setSpacing(4)

        title = QLabel("YT MUSIC DOWNLOADER v0.2")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)

        subtitle = QLabel("Script for downloading YouTube music playlists (and normal YouTube videos as audio files)")
        subtitle.setObjectName("subtitleLabel")
        header_layout.addWidget(subtitle)

        root.addWidget(header_frame)

        # ─── Content Tabs ───
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; padding: 20px; background-color: #0f0f13; }
            QTabBar::tab {
                background-color: #17171f;
                padding: 10px 24px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #5a5278;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #0f0f13;
                color: #7c6af5;
                border-bottom: 2px solid #7c6af5;
            }
            QTabBar::tab:hover:!selected { background-color: #1e1e2a; color: #9a98b8; }
        """)
        root.addWidget(self.tabs)

        # 1) DOWNLOAD TAB
        download_tab = QWidget()
        download_layout = QVBoxLayout(download_tab)
        download_layout.setSpacing(16)
        download_layout.setContentsMargins(0, 0, 0, 0)

        # URL Input
        url_group = QGroupBox("Target Playlist or Song URLs (One per line)")
        url_layout = QVBoxLayout(url_group)

        url_row = QHBoxLayout()
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Paste YouTube Music URLs here (one per line)...")
        self.url_input.setFixedHeight(100)
        self.url_input.setToolTip("Enter one or more YouTube Music playlist or video URLs, each on its own line")

        clear_url_btn = QPushButton("✕")
        clear_url_btn.setFixedWidth(40)
        clear_url_btn.setToolTip("Clear URLs")
        clear_url_btn.clicked.connect(self.url_input.clear)

        url_row.addWidget(self.url_input)
        url_row.addWidget(clear_url_btn, 0, Qt.AlignmentFlag.AlignTop)
        url_layout.addLayout(url_row)
        download_layout.addWidget(url_group)

        # Output folder selection
        folder_group = QGroupBox("Storage Destination")
        folder_layout = QHBoxLayout(folder_group)
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select where to save files...")
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)
        download_layout.addWidget(folder_group)

        # Format & Quality
        settings_row = QHBoxLayout()
        fmt_group = QGroupBox("Audio Format")
        fmt_layout = QVBoxLayout(fmt_group)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "m4a", "aac", "wav", "flac", "opus", "bestaudio"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        fmt_layout.addWidget(self.format_combo)
        settings_row.addWidget(fmt_group)

        qual_group = QGroupBox("Quality")
        qual_layout = QVBoxLayout(qual_group)
        self.quality_combo = QComboBox()
        qual_layout.addWidget(self.quality_combo)
        settings_row.addWidget(qual_group)
        download_layout.addLayout(settings_row)

        # Actions
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("🚀 START DOWNLOAD")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self._start_download)

        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_download)

        self.open_folder_btn = QPushButton("📂 OPEN FOLDER")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)

        btn_layout.addWidget(self.download_btn, 3)
        btn_layout.addWidget(self.cancel_btn, 1)
        btn_layout.addWidget(self.open_folder_btn, 1)
        download_layout.addLayout(btn_layout)

        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.status_label = QLabel("Ready to download")
        self.status_label.setObjectName("statusLabel")
        progress_layout.addWidget(self.status_label)

        self.track_progress = QProgressBar()
        self.track_progress.setValue(0)
        progress_layout.addWidget(self.track_progress)

        self.overall_progress = QProgressBar()
        self.overall_progress.setValue(0)
        self.overall_progress.setFormat("Overall: %p%")
        progress_layout.addWidget(self.overall_progress)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        progress_layout.addWidget(self.info_label)

        download_layout.addWidget(progress_group)
        self.tabs.addTab(download_tab, "DOWNLOAD")

        # 2) QUEUE TAB
        queue_tab = QWidget()
        queue_layout = QVBoxLayout(queue_tab)

        queue_group = QGroupBox("Pending Downloads")
        queue_inner_layout = QVBoxLayout(queue_group)

        self.queue_list = QListWidget()
        queue_inner_layout.addWidget(self.queue_list)

        queue_btns = QHBoxLayout()
        self.remove_queue_btn = QPushButton("🗑 REMOVE SELECTED")
        self.remove_queue_btn.clicked.connect(self._remove_selected_queue)
        self.clear_queue_btn = QPushButton("🧹 CLEAR QUEUE")
        self.clear_queue_btn.clicked.connect(self._clear_queue)

        queue_btns.addWidget(self.remove_queue_btn)
        queue_btns.addWidget(self.clear_queue_btn)
        queue_inner_layout.addLayout(queue_btns)

        queue_layout.addWidget(queue_group)
        self.tabs.addTab(queue_tab, "QUEUE")

        # 3) SETTINGS TAB
        settings_tab = QWidget()
        settings_scroll_layout = QVBoxLayout(settings_tab)

        gen_group = QGroupBox("General")
        gen_form = QFormLayout(gen_group)
        self.default_out_dir = QLineEdit()
        browse_def_btn = QPushButton("...")
        browse_def_btn.setFixedWidth(40)
        browse_def_btn.clicked.connect(self._browse_default_folder)

        def_dir_row = QHBoxLayout()
        def_dir_row.addWidget(self.default_out_dir)
        def_dir_row.addWidget(browse_def_btn)
        gen_form.addRow("Default Folder:", def_dir_row)

        self.create_playlist_folder = QCheckBox("Create subfolder for playlists")
        self.create_playlist_folder.setChecked(True)
        gen_form.addRow("", self.create_playlist_folder)

        self.skip_existing = QCheckBox("Skip already existing files")
        self.skip_existing.setChecked(True)
        gen_form.addRow("", self.skip_existing)

        self.stop_on_error = QCheckBox("Stop download if an error is detected")
        self.stop_on_error.setChecked(False)
        gen_form.addRow("", self.stop_on_error)

        self.fallback_on_unavailable = QCheckBox("Fallback search if video is unavailable")
        self.fallback_on_unavailable.setToolTip("If a video is unavailable, search YouTube for the song title and download the best match.")
        self.fallback_on_unavailable.setChecked(True)
        gen_form.addRow("", self.fallback_on_unavailable)

        settings_scroll_layout.addWidget(gen_group)

        meta_group = QGroupBox("Metadata")
        meta_form = QFormLayout(meta_group)
        self.embed_metadata = QCheckBox("Embed tags (title, artist, album)")
        self.embed_metadata.setChecked(True)
        meta_form.addRow("", self.embed_metadata)

        self.embed_thumbnail = QCheckBox("Embed cover art (thumbnail)")
        self.embed_thumbnail.setChecked(False)
        meta_form.addRow("", self.embed_thumbnail)

        self.parse_extra_metadata = QCheckBox("Parse Year/Genre from title/description")
        self.parse_extra_metadata.setChecked(True)
        meta_form.addRow("", self.parse_extra_metadata)

        self.enable_remote_components = QCheckBox("Enable remote challenge solver (EJS)")
        self.enable_remote_components.setToolTip("Recommended for avoiding 'n challenge' failures and JS challenges.")
        self.enable_remote_components.setChecked(True)
        meta_form.addRow("", self.enable_remote_components)

        self.use_local_pot_provider = QCheckBox("Use local PO Token provider")
        self.use_local_pot_provider.setToolTip("Use the local bgutil-ytdlp-pot-provider server if it is running.")
        self.use_local_pot_provider.setChecked(False)
        meta_form.addRow("", self.use_local_pot_provider)

        self.filename_tmpl = QLineEdit("%(playlist_index)s - %(artist,uploader)s - %(track,title)s.%(ext)s")
        meta_form.addRow("Filename Pattern:", self.filename_tmpl)
        settings_scroll_layout.addWidget(meta_group)

        # Advanced/Performance group
        perf_group = QGroupBox("Performance & Auth")
        perf_form = QFormLayout(perf_group)

        self.parallel_downloads = QSpinBox()
        self.parallel_downloads.setRange(1, 10)
        self.parallel_downloads.setValue(1)
        perf_form.addRow("Parallel downloads:", self.parallel_downloads)

        self.parallel_note = QLabel("Note: Having parallel downloads enabled breaks playlist numbering.")
        self.parallel_note.setStyleSheet("font-size: 11px; color: #5a5278; font-style: italic;")
        self.parallel_note.setWordWrap(True)
        perf_form.addRow("", self.parallel_note)

        self.cookies_browser = QComboBox()
        self.cookies_browser.addItems(["None", "chrome", "firefox", "edge", "safari", "opera", "vivaldi"])
        perf_form.addRow("Cookies from browser:", self.cookies_browser)

        self.po_token = QLineEdit()
        self.po_token.setPlaceholderText("web_music.gvs+XXX")
        self.po_token.setToolTip("Manually pass a GVS PO Token for web_music client (prevents HTTP 403 errors).")
        perf_form.addRow("YouTube PO Token:", self.po_token)

        token_guide = QLabel(
            "<a href='https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide' style='color: #7c6af5;'>PO Token Guide & Generator</a>")
        token_guide.setOpenExternalLinks(True)
        token_guide.setStyleSheet("font-size: 11px;")
        perf_form.addRow("", token_guide)

        settings_scroll_layout.addWidget(perf_group)

        # Scaling Settings
        scale_group = QGroupBox("UI Scaling")
        scale_layout = QHBoxLayout(scale_group)
        self.ui_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.ui_scale_slider.setRange(75, 150)
        self.ui_scale_slider.setValue(100)
        self.ui_scale_value_label = QLabel("100%")
        self.ui_scale_slider.valueChanged.connect(self._apply_ui_scale)
        scale_layout.addWidget(QLabel("Scale:"))
        scale_layout.addWidget(self.ui_scale_slider)
        scale_layout.addWidget(self.ui_scale_value_label)
        settings_scroll_layout.addWidget(scale_group)

        # Save Button
        self.save_settings_btn = QPushButton("💾 Save Settings")
        self.save_settings_btn.clicked.connect(self._save_settings_clicked)
        settings_scroll_layout.addWidget(self.save_settings_btn)

        settings_scroll_layout.addStretch()
        self.tabs.addTab(settings_tab, "SETTINGS")

        # 3) SEARCH TAB
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_layout.setSpacing(16)

        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for songs on YouTube...")
        self.search_input.returnPressed.connect(self._perform_search)
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self._perform_search)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_btn)
        search_layout.addLayout(search_input_layout)

        self.search_results_list = QListWidget()
        self.search_results_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.search_results_list.setAlternatingRowColors(True)
        self.search_results_list.setStyleSheet("""
            QListWidget { background-color: #17171f; border-radius: 6px; padding: 5px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #252533; }
            QListWidget::item:selected { background-color: #2a2a3a; color: #7c6af5; }
        """)
        search_layout.addWidget(self.search_results_list)

        search_actions_layout = QHBoxLayout()
        self.add_to_queue_btn = QPushButton("➕ Add to Download Queue")
        self.add_to_queue_btn.clicked.connect(self._add_search_to_queue)
        self.copy_url_btn = QPushButton("🔗 Copy URL")
        self.copy_url_btn.clicked.connect(self._copy_search_url)
        search_actions_layout.addWidget(self.add_to_queue_btn)
        search_actions_layout.addWidget(self.copy_url_btn)
        search_layout.addLayout(search_actions_layout)

        self.tabs.addTab(search_tab, "SEARCH")

        # 4) LOG TAB
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)

        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.setFixedWidth(100)
        clear_log_btn.clicked.connect(self.log_output.clear)
        log_layout.addWidget(clear_log_btn)

        self.tabs.addTab(log_tab, "LOG")

    def _perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.search_btn.setEnabled(False)
        self.search_btn.setText("Searching...")
        self.search_results_list.clear()
        self._log(f"🔎 Searching for: {query}")

        self._search_thread = QThread()
        self._search_worker = SearchWorker(query, self.cookies_browser.currentText())
        self._search_worker.moveToThread(self._search_thread)
        self._search_thread.started.connect(self._search_worker.run)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_thread.start()

    def _on_search_finished(self, results, error):
        self._search_thread.quit()
        self._search_thread.wait()
        self.search_btn.setEnabled(True)
        self.search_btn.setText("🔍 Search")

        if error:
            self._log(f"✖ Search error: {error}")
            return

        if not results:
            self._log("No results found.")
            return

        for res in results:
            duration_str = ""
            if res['duration']:
                m, s = divmod(int(res['duration']), 60)
                duration_str = f" [{m:d}:{s:02d}]"
            
            item_text = f"{res['title']} - {res['uploader']}{duration_str}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, res['url'])
            self.search_results_list.addItem(item)
        
        self._log(f"✅ Found {len(results)} results.")

    def _add_search_to_queue(self):
        items = self.search_results_list.selectedItems()
        if not items:
            return
        
        urls_added = 0
        for item in items:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                current_urls = self.url_input.toPlainText().strip()
                if current_urls:
                    self.url_input.setPlainText(current_urls + "\n" + url)
                else:
                    self.url_input.setPlainText(url)
                urls_added += 1
        
        if urls_added > 0:
            self._log(f"Added {urls_added} URL(s) to the download list.")
            # Switch to Download tab
            self.tabs.setCurrentIndex(0)

    def _copy_search_url(self):
        items = self.search_results_list.selectedItems()
        if not items:
            return
        
        urls = [item.data(Qt.ItemDataRole.UserRole) for item in items]
        if urls:
            QApplication.clipboard().setText("\n".join(urls))
            self._log(f"Copied {len(urls)} URL(s) to clipboard.")

    def _on_format_changed(self, fmt):
        self._update_quality_options(fmt)

    def _open_output_folder(self):
        folder = self.folder_input.text() or self._last_output_dir_used
        if folder and os.path.exists(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _update_quality_options(self, fmt):
        self.quality_combo.clear()
        if fmt == "bestaudio":
            self.quality_combo.addItems(["Auto (Best)"])
        elif fmt in ["wav", "flac"]:
            self.quality_combo.addItems(["Lossless"])
        elif fmt == "opus":
            self.quality_combo.addItems(["Best", "192 kbps", "128 kbps", "Worst"])
        else:  # mp3, m4a, aac
            self.quality_combo.addItems(["Best", "320 kbps", "256 kbps", "192 kbps", "128 kbps", "Worst"])

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder",
                                                  self.folder_input.text() or os.path.expanduser("~/Music"))
        if folder:
            self.folder_input.setText(folder)

    def _load_settings(self):
        self.default_out_dir.setText(self.settings.value("default_out_dir", os.path.expanduser("~/Music")))
        self.folder_input.setText(self.default_out_dir.text())
        self.create_playlist_folder.setChecked(self.settings.value("create_playlist_folder", True, type=bool))
        self.skip_existing.setChecked(self.settings.value("skip_existing", True, type=bool))
        self.stop_on_error.setChecked(self.settings.value("stop_on_error", False, type=bool))
        self.fallback_on_unavailable.setChecked(self.settings.value("fallback_on_unavailable", True, type=bool))
        self.embed_metadata.setChecked(self.settings.value("embed_metadata", True, type=bool))
        self.embed_thumbnail.setChecked(self.settings.value("embed_thumbnail", False, type=bool))
        self.parse_extra_metadata.setChecked(self.settings.value("parse_extra_metadata", True, type=bool))
        self.enable_remote_components.setChecked(self.settings.value("enable_remote_components", True, type=bool))
        self.use_local_pot_provider.setChecked(self.settings.value("use_local_pot_provider", False, type=bool))
        self.filename_tmpl.setText(
            self.settings.value("filename_tmpl", "%(playlist_index)s - %(artist,uploader)s - %(track,title)s.%(ext)s"))

        fmt = self.settings.value("format", "mp3")
        self.format_combo.setCurrentText(fmt)
        self._update_quality_options(fmt)
        self.quality_combo.setCurrentText(self.settings.value("quality", "Best"))

        self.parallel_downloads.setValue(int(self.settings.value("parallel_downloads", 1)))
        self.cookies_browser.setCurrentText(self.settings.value("cookies_browser", "None"))
        self.po_token.setText(self.settings.value("po_token", ""))

        scale = int(self.settings.value("ui_scale", 100))
        self.ui_scale_slider.setValue(scale)
        self._apply_ui_scale(scale)

    def _save_settings(self):
        self.settings.setValue("default_out_dir", self.default_out_dir.text())
        self.settings.setValue("create_playlist_folder", self.create_playlist_folder.isChecked())
        self.settings.setValue("skip_existing", self.skip_existing.isChecked())
        self.settings.setValue("stop_on_error", self.stop_on_error.isChecked())
        self.settings.setValue("fallback_on_unavailable", self.fallback_on_unavailable.isChecked())
        self.settings.setValue("embed_metadata", self.embed_metadata.isChecked())
        self.settings.setValue("embed_thumbnail", self.embed_thumbnail.isChecked())
        self.settings.setValue("parse_extra_metadata", self.parse_extra_metadata.isChecked())
        self.settings.setValue("enable_remote_components", self.enable_remote_components.isChecked())
        self.settings.setValue("use_local_pot_provider", self.use_local_pot_provider.isChecked())
        self.settings.setValue("filename_tmpl", self.filename_tmpl.text())
        self.settings.setValue("format", self.format_combo.currentText())
        self.settings.setValue("quality", self.quality_combo.currentText())
        self.settings.setValue("parallel_downloads", self.parallel_downloads.value())
        self.settings.setValue("cookies_browser", self.cookies_browser.currentText())
        self.settings.setValue("po_token", self.po_token.text().strip())
        self.settings.setValue("ui_scale", self.ui_scale_slider.value())
        self.settings.sync()

    def closeEvent(self, event):
        self._stop_pot_provider()
        event.accept()

    def _start_pot_provider(self):
        base_path = get_base_path()
        
        # Check potential locations for the script
        locations = [
            os.path.join(base_path, "pkg", "bgutil-download.sh"),
            os.path.join(base_path, "bgutil-download.sh"),
            "/usr/share/yt-music-downloader/pkg/bgutil-download.sh",
            "/usr/share/yt-music-downloader/bgutil-download.sh"
        ]
        
        script_path = None
        for loc in locations:
            if os.path.exists(loc):
                script_path = loc
                break

        if not script_path:
            self._log(f"✖ POT provider script not found in searched locations.")
            return

        self._log("🚀 Starting local POT provider...")
        import subprocess
        try:
            # Determine working directory (important for cloning/building if needed)
            # If we are in /usr/share or frozen, we might not have write access to base_path.
            # bgutil-download.sh should handle this or we should point it to a writable dir.
            # For now, we'll try to run it where it is.
            env = os.environ.copy()
            # Pass the base path to the script so it knows where to look for existing files
            env["APP_BASE_PATH"] = base_path
            
            subprocess.run(["bash", script_path], check=True, capture_output=True, text=True, env=env)
            self._log("✅ Local POT provider server started.")
        except Exception as e:
            self._log(f"✖ Failed to start local POT provider: {e}")

    def _stop_pot_provider(self):
        # The script saves PID in bgutil-ytdlp-pot-provider/server.pid
        # We need to find where that pid file might be.
        base_path = get_base_path()
        
        # Try a few locations for the PID file
        locations = [
            os.path.join(os.path.expanduser("~/.cache/yt-music-downloader"), "server.pid"),
            os.path.join(base_path, "bgutil-ytdlp-pot-provider", "server.pid"),
        ]
        
        pid_file = None
        for loc in locations:
            if os.path.exists(loc):
                pid_file = loc
                break

        if pid_file and os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())
                
                self._log(f"🛑 Stopping local POT provider (PID {pid})...")
                import signal
                os.kill(pid, signal.SIGTERM)
                os.remove(pid_file)
                self._log("✅ Local POT provider stopped.")
            except Exception as e:
                self._log(f"✖ Error stopping POT provider: {e}")

    def _save_settings_clicked(self):
        self._save_settings()
        self._log("Settings saved to disk.")
        self.save_settings_btn.setText("✅ Settings Saved!")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.save_settings_btn.setText("💾 Save Settings"))

        # If local POT provider was just enabled, try to start it
        if self.use_local_pot_provider.isChecked():
            # Run in a thread or separate process to not block UI if it's slow
            import threading
            threading.Thread(target=self._start_pot_provider, daemon=True).start()
        else:
            self._stop_pot_provider()

    def _log(self, msg):
        self.log_output.append(msg)

    def _remove_selected_queue(self):
        for item in self.queue_list.selectedItems():
            row = self.queue_list.row(item)
            self.queue_list.takeItem(row)
            if row < len(self._download_queue):
                self._download_queue.pop(row)
        self._log(f"Removed selected items from queue. Queue size: {len(self._download_queue)}")

    def _clear_queue(self):
        self.queue_list.clear()
        self._download_queue.clear()
        self._log("Queue cleared.")

    def _start_download(self):
        if self._is_downloading:
            return

        urls_text = self.url_input.toPlainText().strip()
        if not urls_text:
            if not self._download_queue:
                self._log("✖ Error: Please enter at least one URL.")
                return
        else:
            urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
            for url in urls:
                self._download_queue.append(url)
                self.queue_list.addItem(url)
            self.url_input.clear()

        if not self._download_queue:
            return

        self._process_queue()

    def _process_queue(self):
        if not self._download_queue:
            self._is_downloading = False
            self.download_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("All downloads finished")
            return

        self._is_downloading = True
        url = self._download_queue[0]

        # Update queue UI
        item = self.queue_list.item(0)
        if item:
            item.setSelected(True)
            item.setText(f"⏳ {url}")

        out_dir = self.folder_input.text().strip()
        if not out_dir:
            out_dir = self.default_out_dir.text().strip() or os.path.expanduser("~/Music")
            self.folder_input.setText(out_dir)

        options = {
            "create_playlist_folder": self.create_playlist_folder.isChecked(),
            "skip_existing": self.skip_existing.isChecked(),
            "stop_on_error": self.stop_on_error.isChecked(),
            "fallback_on_unavailable": self.fallback_on_unavailable.isChecked(),
            "embed_metadata": self.embed_metadata.isChecked(),
            "embed_thumbnail": self.embed_thumbnail.isChecked(),
            "parse_extra_metadata": self.parse_extra_metadata.isChecked(),
            "filename_template": self.filename_tmpl.text(),
            "parallel_downloads": self.parallel_downloads.value(),
            "cookies_browser": self.cookies_browser.currentText(),
            "po_token": self.po_token.text().strip(),
            "enable_remote_components": self.enable_remote_components.isChecked(),
            "use_local_pot_provider": self.use_local_pot_provider.isChecked(),
        }

        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(False)
        self.status_label.setText(f"Initializing: {url}")
        self.track_progress.setValue(0)
        self.overall_progress.setValue(0)
        self.info_label.setText("")

        self._thread = QThread()
        self._worker = DownloadWorker(
            url, out_dir,
            self.format_combo.currentText(),
            self.quality_combo.currentText(),
            options
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.track_started.connect(self._on_track_started)
        self._worker.log.connect(self._log)
        self._worker.playlist_info.connect(self._on_playlist_info)
        self._worker.finished.connect(self._on_download_finished)

        self._thread.start()

    def _on_playlist_info(self, count, title):
        url_info = f" ({self._download_queue[0]})" if self._download_queue else ""
        self.status_label.setText(f"Processing: {title}{url_info}")
        self.overall_progress.setMaximum(100)

    def _on_progress(self, pct, overall_pct, info):
        self.track_progress.setValue(int(pct))
        self.overall_progress.setValue(int(overall_pct))
        self.info_label.setText(info)

    def _on_track_started(self, title, current, total):
        url_info = f" ({self._download_queue[0]})" if self._download_queue else ""
        self.status_label.setText(f"Downloading [{current}/{total}]: {title}{url_info}")

    def _on_download_finished(self, success, message):
        self._thread.quit()
        self._thread.wait()

        if success:
            self._last_output_dir_used = self._worker.output_dir
            self.track_progress.setValue(100)
            self.overall_progress.setValue(100)
            self.status_label.setText("Finished")
            self._log(message)
        else:
            self.status_label.setText("Error")
            self._log(f"✖ {message}")

        # Move to next in queue
        if self._download_queue:
            self._download_queue.pop(0)
            self.queue_list.takeItem(0)

        self.open_folder_btn.setEnabled(success)

        # Stop entirely if error detected and stop_on_error is enabled
        if not success and self.stop_on_error.isChecked():
            self._log("Stopping all downloads due to error.")
            self._download_queue.clear()
            self.queue_list.clear()

        self._process_queue()

    def _cancel_download(self):
        if self._worker:
            self._worker.cancel()
            self._log("⌛ Cancellation requested...")
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("Cancelling...")
            # Clear remaining queue on cancel?
            # For now, let's just clear the queue to stop everything.
            self._download_queue.clear()
            self.queue_list.clear()
            self._is_downloading = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("yt-music-downloader")
    app.setApplicationName("ytmusic-downloader")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())