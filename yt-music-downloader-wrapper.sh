#!/bin/bash
# Wrapper script for yt-music-downloader
# Installed at /usr/bin/yt-music-downloader
exec /usr/bin/python3 /usr/share/yt-music-downloader/ytmusic-downloader.py "$@"
