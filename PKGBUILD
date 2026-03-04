# Maintainer: Tommi <tommi@example.com>
pkgname=yt-music-downloader
pkgver=0.2
pkgrel=1
pkgdesc="A modern PyQt6 GUI for downloading YouTube Music playlists and tracks"
arch=('any')
url="https://github.com/tommipontinen76/yt-music-downloader"
license=('MIT')
depends=('python' 'python-pyqt6' 'yt-dlp' 'ffmpeg' 'python-mutagen')
source=("ytmusic-downloader.py"
        "yt-music-downloader.desktop"
        "yt-music-downloader-wrapper.sh")
sha256sums=('SKIP'
            'SKIP'
            'SKIP')

package() {
    # Install the main python script
    install -Dm755 "${srcdir}/ytmusic-downloader.py" "${pkgdir}/usr/share/${pkgname}/ytmusic-downloader.py"

    # Install the wrapper script
    install -Dm755 "${srcdir}/yt-music-downloader-wrapper.sh" "${pkgdir}/usr/bin/${pkgname}"

    # Install the desktop entry
    install -Dm644 "${srcdir}/yt-music-downloader.desktop" "${pkgdir}/usr/share/applications/${pkgname}.desktop"
}
