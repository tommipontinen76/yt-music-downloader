#!/usr/bin/env python3
"""
Compilation script to create a standalone Linux binary for YT Music Downloader.
This script uses PyInstaller to bundle the application and its dependencies.
"""

import subprocess
import sys
import os
import shutil
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
    # 1. Define paths
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "ytmusic-downloader.py"
    venv_dir = script_dir / "venv"
    
    if not main_script.exists():
        print(f"Error: {main_script} not found!")
        sys.exit(1)

    # 2. Setup Virtual Environment
    if not venv_dir.exists():
        run_command([sys.executable, "-m", "venv", str(venv_dir)], "Creating virtual environment")
    
    # Define pip and pyinstaller paths inside venv
    pip_path = venv_dir / "bin" / "pip"
    pyinstaller_path = venv_dir / "bin" / "pyinstaller"

    # 3. Install Dependencies
    run_command([str(pip_path), "install", "--upgrade", "pip"], "Upgrading pip")
    run_command([str(pip_path), "install", "pyinstaller", "PyQt6", "yt-dlp"], "Installing dependencies")

    # 4. Run PyInstaller
    # Flags explained:
    # --onefile: Create a single executable file.
    # --windowed: Do not show a console window (important for GUI apps).
    # --name: Set the output binary name.
    # --clean: Clean PyInstaller cache and remove temporary files before building.
    # --hidden-import: Ensure yt-dlp is correctly included if dynamic imports fail.
    
    build_command = [
        str(pyinstaller_path),
        "--onefile",
        "--windowed",
        "--name", "ytmusic-downloader",
        "--clean",
        str(main_script)
    ]

    run_command(build_command, "Compiling to Linux binary")

    # 5. Cleanup and Result
    dist_dir = script_dir / "dist"
    binary_path = dist_dir / "ytmusic-downloader"
    
    if binary_path.exists():
        print("==================================================")
        print(" COMPILATION COMPLETE!")
        print(f" Binary location: {binary_path}")
        print("==================================================")
        print("\nYou can now run the application using:")
        print(f"./dist/ytmusic-downloader")
    else:
        print("Error: Binary was not created. Check the output above.")

if __name__ == "__main__":
    main()
