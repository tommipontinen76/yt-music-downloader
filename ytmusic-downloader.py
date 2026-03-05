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

class DownloadWorker(QObject):
    progress = pyqtSignal(float, float, str)  # current_pct, overall_pct, speed/eta string
    track_started = pyqtSignal(str, int, int)  # title, current, total
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)      # success, message
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
        name = re.sub(r'[\\/:*?"<>|]+', "_", name)   # Windows-illegal chars + path separators
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

        try:
            # 1) Fetch playlist info FIRST (so we can create a playlist-named subfolder)
            with yt_dlp.YoutubeDL({
                "quiet": True,
                "no_warnings": False,
                "logger": self._YDLLogger(self),
            }) as ydl:
                if self._cancelled:
                    self.finished.emit(False, "Cancelled.")
                    return

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
                
                if po_token:
                    info_opts["extractor_args"] = {"youtube": {"po_token": [po_token]}}
                
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

            # 2) Choose actual output directory
            if create_playlist_folder:
                playlist_dir = Path(self.output_dir) / safe_title
                playlist_dir.mkdir(parents=True, exist_ok=True)
                self.output_dir = str(playlist_dir)
            else:
                Path(self.output_dir).mkdir(parents=True, exist_ok=True)

            outtmpl = str(Path(self.output_dir) / filename_template)

            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": q_value,
                }
            ]
            if embed_metadata:
                postprocessors.append({"key": "FFmpegMetadata"})
            
            if embed_thumbnail:
                # Ensure thumbnail is in a compatible format (jpg) before embedding
                postprocessors.append({"key": "FFmpegThumbnailsConvertor", "format": "jpg"})
                # Requires ffmpeg, and works best when yt-dlp can retrieve a thumbnail
                postprocessors.append({"key": "EmbedThumbnail"})

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
                "writethumbnail": embed_thumbnail,
                "ignoreerrors": True, # don't stop the whole playlist if one song fails
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

            if po_token:
                # Merge with existing extractor_args if any (though currently none)
                if "extractor_args" not in ydl_opts:
                    ydl_opts["extractor_args"] = {}
                ydl_opts["extractor_args"]["youtube"] = {"po_token": [po_token]}

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
                
                # We need a separate YDL instance per thread if we want true parallelism 
                # or we use the 'concurrent_fragment_downloads' for speed but here we want parallel tracks.
                # Actually, yt-dlp doesn't support multiple tracks in parallel in one ydl.download() call.
                # So we must call ydl.download() on each entry.
                
                def download_entry(entry):
                    if self._cancelled:
                        return
                    
                    # Create a new ydl_opts for this specific entry to avoid state issues
                    entry_opts = ydl_opts.copy()
                    # We don't want it to try to download the whole playlist, just this entry
                    entry_opts["noplaylist"] = True
                    
                    with yt_dlp.YoutubeDL(entry_opts) as ydl_inner:
                        # Using process_ie_result instead of download([url]) to preserve 
                        # the playlist metadata (like playlist_index) already extracted.
                        ydl_inner.process_ie_result(entry, download=True)

                with ThreadPoolExecutor(max_workers=parallel_downloads) as executor:
                    list(executor.map(download_entry, entries))
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
            elif msg.startswith("[download]") or msg.startswith("[ExtractAudio]") or msg.startswith("[ThumbnailsConvertor]") or msg.startswith("[EmbedThumbnail]"):
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
            self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "yt-music-downloader", "ytmusic-downloader")

        self._worker = None
        self._thread = None
        self._last_output_dir_used = ""
        self._download_queue = []
        self._is_downloading = False

        self._ui_scale = 1.0
        self._build_ui()
        self._load_settings()

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
        self.format_combo.addItems(["mp3", "m4a", "aac", "wav", "flac", "opus"])
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
        
        token_guide = QLabel("<a href='https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide' style='color: #7c6af5;'>PO Token Guide & Generator</a>")
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

        # 3) LOG TAB
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

    def _on_format_changed(self, fmt):
        self._update_quality_options(fmt)

    def _open_output_folder(self):
        folder = self.folder_input.text() or self._last_output_dir_used
        if folder and os.path.exists(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _update_quality_options(self, fmt):
        self.quality_combo.clear()
        if fmt in ["wav", "flac"]:
            self.quality_combo.addItems(["Lossless"])
        elif fmt == "opus":
            self.quality_combo.addItems(["Best", "192 kbps", "128 kbps", "Worst"])
        else: # mp3, m4a, aac
            self.quality_combo.addItems(["Best", "320 kbps", "256 kbps", "192 kbps", "128 kbps", "Worst"])

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.folder_input.text() or os.path.expanduser("~/Music"))
        if folder:
            self.folder_input.setText(folder)

    def _load_settings(self):
        self.default_out_dir.setText(self.settings.value("default_out_dir", os.path.expanduser("~/Music")))
        self.folder_input.setText(self.default_out_dir.text())
        self.create_playlist_folder.setChecked(self.settings.value("create_playlist_folder", True, type=bool))
        self.skip_existing.setChecked(self.settings.value("skip_existing", True, type=bool))
        self.embed_metadata.setChecked(self.settings.value("embed_metadata", True, type=bool))
        self.embed_thumbnail.setChecked(self.settings.value("embed_thumbnail", False, type=bool))
        self.parse_extra_metadata.setChecked(self.settings.value("parse_extra_metadata", True, type=bool))
        self.enable_remote_components.setChecked(self.settings.value("enable_remote_components", True, type=bool))
        self.filename_tmpl.setText(self.settings.value("filename_tmpl", "%(playlist_index)s - %(artist,uploader)s - %(track,title)s.%(ext)s"))
        
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
        self.settings.setValue("embed_metadata", self.embed_metadata.isChecked())
        self.settings.setValue("embed_thumbnail", self.embed_thumbnail.isChecked())
        self.settings.setValue("parse_extra_metadata", self.parse_extra_metadata.isChecked())
        self.settings.setValue("enable_remote_components", self.enable_remote_components.isChecked())
        self.settings.setValue("filename_tmpl", self.filename_tmpl.text())
        self.settings.setValue("format", self.format_combo.currentText())
        self.settings.setValue("quality", self.quality_combo.currentText())
        self.settings.setValue("parallel_downloads", self.parallel_downloads.value())
        self.settings.setValue("cookies_browser", self.cookies_browser.currentText())
        self.settings.setValue("po_token", self.po_token.text().strip())
        self.settings.setValue("ui_scale", self.ui_scale_slider.value())
        self.settings.sync()

    def _save_settings_clicked(self):
        self._save_settings()
        self._log("Settings saved to disk.")
        self.save_settings_btn.setText("✅ Settings Saved!")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.save_settings_btn.setText("💾 Save Settings"))

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
            "embed_metadata": self.embed_metadata.isChecked(),
            "embed_thumbnail": self.embed_thumbnail.isChecked(),
            "parse_extra_metadata": self.parse_extra_metadata.isChecked(),
            "filename_template": self.filename_tmpl.text(),
            "parallel_downloads": self.parallel_downloads.value(),
            "cookies_browser": self.cookies_browser.currentText(),
            "po_token": self.po_token.text().strip(),
            "enable_remote_components": self.enable_remote_components.isChecked(),
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
