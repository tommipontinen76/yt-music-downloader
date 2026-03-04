#!/usr/bin/env python3
"""
Compilation script to create a standalone macOS App Bundle (.app) for YT Music Downloader.
Note: This script should be run on a macOS machine.
It uses PyInstaller to bundle the application and its dependencies.
"""

import subprocess
import sys
import os
import re
from pathlib import Path

def run_command(command, description):
    print(f"--- {description} ---")
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command)
        print("Success!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}: {e}")
        sys.exit(1)

def main():
    # 0. Check Platform
    if sys.platform != "darwin":
        print("Error: This script must be run on macOS to create a .app bundle.")
        print(f"Current platform: {sys.platform}")
        sys.exit(1)

    # 1. Define paths
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "ytmusic-downloader.py"
    venv_dir = script_dir / "venv-mac"
    
    if not main_script.exists():
        print(f"Error: {main_script} not found!")
        sys.exit(1)

    # 1.5 Extract Version from main script
    version = "0.2" # Current project version
    try:
        with open(main_script, 'r', encoding='utf-8') as f:
            content = f.read()
            version_match = re.search(r'YT Music Downloader v([\d\.]+)', content)
            if version_match:
                version = version_match.group(1)
                print(f"Detected version: {version}")
    except Exception as e:
        print(f"Warning: Could not detect version from {main_script}, using default {version}")
    
    # macOS binary and app bundle name
    safe_version = version.replace(".", "-")
    app_name = f"yt-music-downloader-mac-v{safe_version}"

    # 2. Setup Virtual Environment
    if not venv_dir.exists():
        run_command([sys.executable, "-m", "venv", str(venv_dir)], "Creating virtual environment")
    
    # Define pip and pyinstaller paths inside venv
    pip_path = venv_dir / "bin" / "pip"
    pyinstaller_path = venv_dir / "bin" / "pyinstaller"

    # 3. Install Dependencies
    run_command([str(pip_path), "install", "--upgrade", "pip"], "Upgrading pip")
    run_command([str(pip_path), "install", "pyinstaller", "PyQt6", "yt-dlp", "mutagen"], "Installing dependencies")

    # 4. Run PyInstaller
    # Flags:
    # --windowed: Create a Mac .app bundle
    # --name: The name of the app
    # --clean: Clean cache
    # --target-arch: For universal binary support (optional: "universal2", "x86_64", "arm64")
    
    # On macOS, --windowed (or -w) combined with --name results in an app bundle.
    # We do NOT use --onefile here for the app bundle because --windowed handles the bundle structure.
    
    build_command = [
        str(pyinstaller_path),
        "--windowed",
        "--name", app_name,
        "--clean",
        str(main_script)
    ]

    run_command(build_command, "Compiling to macOS App Bundle")

    # 5. Result
    dist_dir = script_dir / "dist"
    app_bundle_path = dist_dir / f"{app_name}.app"
    
    if app_bundle_path.exists():
        print("==================================================")
        print(" COMPILATION COMPLETE!")
        print(f" App Bundle location: {app_bundle_path}")
        print("==================================================")
        print("\nYou can now find the .app bundle in the 'dist' folder.")
    else:
        print("Error: App bundle was not created. Check the output above.")

if __name__ == "__main__":
    main()
