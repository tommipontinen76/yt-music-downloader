# YT Music Downloader v0.3

A modern, fast, and feature-rich PyQt6 GUI for downloading YouTube Music playlists and individual tracks as high-quality audio files. This tool leverages the power of `yt-dlp` and `ffmpeg` to provide a seamless downloading experience.
Now featuring automated search and a local PO Token provider for enhanced reliability.
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Playlist Support:** Effortlessly download entire YouTube Music playlists.
- **High-Quality Audio:** Supports multiple formats (MP3, M4A, WAV, FLAC, OPUS) with various quality presets.
- **Parallel Downloads:** Download multiple tracks simultaneously for maximum speed (configurable in settings).
- **Metadata & Cover Art:** Automatically embeds track title, artist, album, and high-resolution thumbnails into your files.
- **Smart Metadata Parsing:** Can extract "Year" and "Genre" information directly from video titles and descriptions.
- **Manual & Fallback Search:** New **SEARCH** tab for manual song selection, and automated fallback searching for unavailable videos.
- **Local PO Token Provider:** Integrated `bgutil-ytdlp-pot-provider` server to solve YouTube challenges locally.
- **Advanced Authentication:** 
    - **Browser Cookies:** Supports extracting cookies from Chrome, Firefox, Edge, and more.
    - **PO Tokens:** Support for manual GVS PO Tokens and automated local provider.
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
- **Node.js 16+ & npm:** Required for the local PO Token provider server.
- **Dependencies:**
    ```bash
    pip install PyQt6 yt-dlp mutagen bgutil-ytdlp-pot-provider
    ```
    Or from your package manager (e.g. on Arch)
    ```bash
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    yay -S python-pyqt6 yt-dlp python-mutagen python-bgutil-ytdlp-pot-provider
=======
    yay -S python-pyqt6 yt-dlp python-mutagen nodejs npm
>>>>>>> Stashed changes
=======
    yay -S python-pyqt6 yt-dlp python-mutagen nodejs npm
>>>>>>> Stashed changes
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

## 📦 Compilation

Helper scripts are provided to compile the application into a standalone binary for different platforms. Note that you must run each script on its respective operating system.

### Linux
```bash
python3 linux-binary-compile.py
```
This will create a single executable file in the `dist/` directory.

### Windows
```bash
python windows-binary-compile.py
```
This will create a standalone `.exe` file in the `dist/` directory.

### macOS
```bash
python3 macos-binary-compile.py
```
This will create a macOS App Bundle (`.app`) in the `dist/` directory.

## 📦 Installation (Arch Linux / AUR)

For Arch Linux users, a `PKGBUILD` is provided. You can build and install the package using `makepkg`:

1.  **Clone the repository or download the source.**
2.  **Navigate to the directory.**
3.  **Build and install:**
    ```bash
    makepkg -si
    ```
This will install the application system-wide with all required dependencies (`python-pyqt6`, `yt-dlp`, `ffmpeg`). You can then launch it from your application menu or by running `yt-music-downloader` in the terminal.

## ⚙️ Local PO Token Provider

To use the local PO Token provider (recommended for higher success rates):
1. Ensure **Node.js** and **npm** are installed.
2. Go to the **SETTINGS** tab in the application.
3. Check **"Use local PO Token provider"**.
4. Click **SAVE SETTINGS**.
The application will automatically manage the provider server in the background.

## 🔎 Search Tab

Use the **SEARCH** tab to find songs directly. You can:
- Type a query and see top 10 results.
- Select multiple items and click **Add to Download Queue**.
- Right-click to copy a song's URL.

## ⚙️ Settings Location

The application saves your preferences (default folder, quality, scaling, etc.) in platform-standard locations:

- **Linux:** `~/.config/yt-music-downloader/ytmusic-downloader.conf`
- **Windows:** `Documents/yt-music-downloader/ytmusic-downloader.ini`
- **macOS:** `~/Library/Preferences/yt-music-downloader/ytmusic-downloader.conf`

## ⚖️ License

This project is open-source and available under the [MIT License](LICENSE).
