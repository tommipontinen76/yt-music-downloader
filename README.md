# YT Music Downloader v0.2

A modern, fast, and feature-rich PyQt6 GUI for downloading YouTube Music playlists and individual tracks as high-quality audio files. This tool leverages the power of `yt-dlp` and `ffmpeg` to provide a seamless downloading experience.
macOS version is unsupported but I don't see why it wouldn't work.

Made with AI for my own use, expect some bugs.

![Version](https://img.shields.io/badge/version-0.2-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Playlist Support:** Effortlessly download entire YouTube Music playlists.
- **High-Quality Audio:** Supports multiple formats (MP3, M4A, WAV, FLAC, OPUS) with various quality presets.
- **Parallel Downloads:** Download multiple tracks simultaneously for maximum speed (configurable in settings).
- **Metadata & Cover Art:** Automatically embeds track title, artist, album, and high-resolution thumbnails into your files.
- **Smart Metadata Parsing:** Can extract "Year" and "Genre" information directly from video titles and descriptions.
- **Advanced Authentication:** 
    - **Browser Cookies:** Supports extracting cookies from Chrome, Firefox, Edge, and more to bypass age restrictions.
    - **PO Tokens:** Support for manual GVS PO Tokens to resolve HTTP 403 errors and "n challenge" failures.
- **Remote Challenge Solver:** Integrated support for `yt-dlp` remote components (EJS) to solve complex JavaScript challenges.
- **Customizable File Naming:** Flexible filename templates (e.g., `%(playlist_index)s - %(artist)s - %(track)s`).
- **User-Friendly Interface:**
    - Dark-themed modern UI.
    - Dynamic UI scaling for different screen resolutions.
    - Quick "Open Folder" button after downloads complete.
    - Real-time logging and progress tracking.

## 🛠 Prerequisites

To run the script from source, you will need:

- **Python 3.8+**
- **FFmpeg:** Required for audio extraction and thumbnail embedding.
    - **Linux:** `sudo apt install ffmpeg` or install from your manage manager e.g. `yay -S ffmpeg`
    - **macOS:** `brew install ffmpeg`
    - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system PATH.
- **Dependencies:**
    ```bash
    pip install PyQt6 yt-dlp mutagen
    ```
    Or from your package manager (e.g. on Arch)
    ```bash
    yay -S python-pyqt6 yt-dlp python-mutagen
    ```

## 🚀 Usage

1. **Run the script:**
   ```bash
   python3 ytmusic-downloader.py
   ```
2. **Paste a URL:** Enter a YouTube Music playlist or track link.
3. **Choose Format:** Select your preferred audio format and quality.
4. **Set Destination:** Pick a folder where you want your music saved.
5. **Start:** Click **START DOWNLOAD** and watch the magic happen!

## 📦 Compilation (Linux)

A helper script is provided to compile the application into a standalone Linux binary:

```bash
python3 linux-binary-compile.py
```

This will create a single executable file in the `dist/` directory (e.g., `yt-music-downloader-v0-2`).

## 📦 Installation (Arch Linux / AUR)

For Arch Linux users, a `PKGBUILD` is provided. You can build and install the package using `makepkg`:

1.  **Clone the repository or download the source.**
2.  **Navigate to the directory.**
3.  **Build and install:**
    ```bash
    makepkg -si
    ```
This will install the application system-wide with all required dependencies (`python-pyqt6`, `yt-dlp`, `ffmpeg`). You can then launch it from your application menu or by running `yt-music-downloader` in the terminal.

## ⚙️ Settings Location

The application saves your preferences (default folder, quality, scaling, etc.) in platform-standard locations:

- **Linux:** `~/.config/yt-music-downloader/ytmusic-downloader.conf`
- **Windows:** `Documents/yt-music-downloader/ytmusic-downloader.ini`
- **macOS:** `~/Library/Preferences/yt-music-downloader/ytmusic-downloader.conf`

## ⚖️ License

This project is open-source and available under the [MIT License](LICENSE).
