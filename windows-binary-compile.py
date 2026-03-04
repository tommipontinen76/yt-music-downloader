#!/usr/bin/env python3
"""
Compilation script to create a standalone Windows binary (.exe) for YT Music Downloader.
Note: This script should be run on a Windows machine.
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
        subprocess.check_call(command, shell=(os.name == 'nt'))
        print("Success!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}: {e}")
        sys.exit(1)

def main():
    # 0. Check Platform
    if os.name != "nt":
        print("Error: This script must be run on Windows to create a .exe binary.")
        print(f"Current OS: {os.name}")
        sys.exit(1)

    # 1. Define paths
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "ytmusic-downloader.py"
    venv_dir = script_dir / "venv-win"
    
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
    
    safe_version = version.replace(".", "-")
    binary_name = f"yt-music-downloader-win-v{safe_version}"

    # 2. Setup Virtual Environment
    if not venv_dir.exists():
        run_command([sys.executable, "-m", "venv", str(venv_dir)], "Creating virtual environment")
    
    # Define pip and pyinstaller paths inside venv for Windows
    if os.name == 'nt':
        pip_path = venv_dir / "Scripts" / "pip.exe"
        pyinstaller_path = venv_dir / "Scripts" / "pyinstaller.exe"
    else:
        # Fallback for cross-platform logic (though PyInstaller needs to run on target OS)
        pip_path = venv_dir / "bin" / "pip"
        pyinstaller_path = venv_dir / "bin" / "pyinstaller"

    # 3. Install Dependencies
    run_command([str(pip_path), "install", "--upgrade", "pip"], "Upgrading pip")
    run_command([str(pip_path), "install", "pyinstaller", "PyQt6", "yt-dlp", "mutagen"], "Installing dependencies")

    # 4. Run PyInstaller
    # Flags:
    # --onefile: Single .exe file
    # --windowed: No console window
    # --name: Output filename
    # --clean: Clean cache
    
    build_command = [
        str(pyinstaller_path),
        "--onefile",
        "--windowed",
        "--name", f"{binary_name}.exe",
        "--clean",
        str(main_script)
    ]

    run_command(build_command, "Compiling to Windows binary")

    # 5. Result
    dist_dir = script_dir / "dist"
    binary_path = dist_dir / f"{binary_name}.exe"
    
    if binary_path.exists():
        print("==================================================")
        print(" COMPILATION COMPLETE!")
        print(f" Binary location: {binary_path}")
        print("==================================================")
        print("\nYou can now find the .exe in the 'dist' folder.")
    else:
        print("Error: Binary was not created. Check the output above.")

if __name__ == "__main__":
    main()
