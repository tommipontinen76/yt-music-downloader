# Maintainer: Tommi <tommi@example.com>
pkgname=yt-music-downloader
pkgver=0.3
pkgrel=1
pkgdesc="A modern PyQt6 GUI for downloading YouTube Music playlists and tracks, featuring a local PO Token provider"
arch=('any')
url="https://github.com/tommipontinen76/yt-music-downloader"
license=('MIT')
depends=('python' 'python-pyqt6' 'yt-dlp' 'ffmpeg' 'python-mutagen' 'nodejs')
makedepends=('npm')
source=("ytmusic-downloader.py"
        "yt-music-downloader.desktop"
        "yt-music-downloader-wrapper.sh"
        "bgutil-download.sh")
sha256sums=('SKIP'
            'SKIP'
            'SKIP'
            'SKIP')

prepare() {
    # Fetch and build the local POT provider if it doesn't exist in the source
    if [ ! -d "bgutil-ytdlp-pot-provider" ]; then
        bash bgutil-download.sh
        # Stop the server if it started during build
        PID_FILE="$HOME/.cache/yt-music-downloader/server.pid"
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") || true
            rm "$PID_FILE"
        fi
    fi
}

package() {
    # Install the main python script
    install -Dm755 "${srcdir}/ytmusic-downloader.py" "${pkgdir}/usr/share/${pkgname}/ytmusic-downloader.py"

    # Install the wrapper script
    install -Dm755 "${srcdir}/yt-music-downloader-wrapper.sh" "${pkgdir}/usr/bin/${pkgname}"

    # Install the desktop entry
    install -Dm644 "${srcdir}/yt-music-downloader.desktop" "${pkgdir}/usr/share/applications/${pkgname}.desktop"

    # Install the POT provider and its script
    install -Dm755 "${srcdir}/bgutil-download.sh" "${pkgdir}/usr/share/${pkgname}/bgutil-download.sh"
    
    cp -r "${srcdir}/bgutil-ytdlp-pot-provider" "${pkgdir}/usr/share/${pkgname}/"
}
