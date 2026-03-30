"""
MoneyPrinterTurbo — All-in-One Installer Builder

Creates a single .exe installer that includes:
1. Python embedded (portable, no system install needed)
2. All Python dependencies
3. FFmpeg binary
4. Desktop app (Tauri/React)
5. Resource files (fonts, songs)
6. Auto-start script

Output: dist/MoneyPrinterTurbo-Setup.exe
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
BUNDLE = DIST / "MoneyPrinterTurbo"

# Python embedded version
PYTHON_VERSION = "3.12.10"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"

# FFmpeg
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"


def clean():
    """Clean previous build"""
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir(parents=True)
    print("Cleaned dist/")


def download_file(url: str, dest: Path, desc: str = ""):
    """Download a file with progress"""
    print(f"Downloading {desc or url}...")
    if dest.exists():
        print(f"  Already exists: {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest))
    print(f"  Done: {dest} ({dest.stat().st_size / 1024 / 1024:.1f} MB)")


def setup_python():
    """Download and setup embedded Python"""
    print("\n=== Setting up Python Embedded ===")
    python_zip = DIST / "python-embed.zip"
    python_dir = BUNDLE / "python"

    download_file(PYTHON_URL, python_zip, "Python Embedded")

    # Extract
    python_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(python_zip, "r") as z:
        z.extractall(python_dir)

    # Enable pip: edit python312._pth to uncomment import site
    pth_files = list(python_dir.glob("python*._pth"))
    if pth_files:
        pth = pth_files[0]
        content = pth.read_text()
        content = content.replace("#import site", "import site")
        pth.write_text(content)

    # Install pip
    get_pip = DIST / "get-pip.py"
    download_file("https://bootstrap.pypa.io/get-pip.py", get_pip, "get-pip.py")

    python_exe = python_dir / "python.exe"
    subprocess.run([str(python_exe), str(get_pip), "--no-warn-script-location"], check=True)

    print("Python embedded ready")
    return python_exe


def install_dependencies(python_exe: Path):
    """Install all Python packages"""
    print("\n=== Installing Python Dependencies ===")
    req_file = ROOT / "requirements.txt"

    subprocess.run([
        str(python_exe), "-m", "pip", "install",
        "--no-warn-script-location",
        "-r", str(req_file),
    ], check=True)

    # Install extra deps
    extras = ["platformdirs", "tomli_w", "anthropic", "trafilatura", "youtube-transcript-api"]
    subprocess.run([
        str(python_exe), "-m", "pip", "install",
        "--no-warn-script-location",
    ] + extras, check=True)

    print("Dependencies installed")


def setup_ffmpeg():
    """Download FFmpeg"""
    print("\n=== Setting up FFmpeg ===")
    ffmpeg_zip = DIST / "ffmpeg.zip"
    ffmpeg_dir = BUNDLE / "ffmpeg"

    download_file(FFMPEG_URL, ffmpeg_zip, "FFmpeg")

    # Extract
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ffmpeg_zip, "r") as z:
        for member in z.namelist():
            if member.endswith(("ffmpeg.exe", "ffprobe.exe")):
                # Extract to ffmpeg/ directly
                filename = os.path.basename(member)
                target = ffmpeg_dir / filename
                with z.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())
                print(f"  Extracted: {filename}")

    print("FFmpeg ready")


def copy_app_files():
    """Copy application files"""
    print("\n=== Copying Application Files ===")

    # Copy Python app code
    app_dir = BUNDLE / "app"
    shutil.copytree(ROOT / "app", app_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # Copy plugins
    # (already inside app/)

    # Copy templates
    if (ROOT / "templates").exists():
        shutil.copytree(ROOT / "templates", BUNDLE / "templates", dirs_exist_ok=True)

    # Copy resources
    if (ROOT / "resource").exists():
        shutil.copytree(ROOT / "resource", BUNDLE / "resource", dirs_exist_ok=True)

    # Copy main entry point
    shutil.copy2(ROOT / "main.py", BUNDLE / "main.py")

    # Copy config
    if (ROOT / "config.example.toml").exists():
        shutil.copy2(ROOT / "config.example.toml", BUNDLE / "config.toml")

    print("App files copied")


def create_launcher():
    """Create launcher scripts"""
    print("\n=== Creating Launcher ===")

    # Main launcher .bat
    launcher = BUNDLE / "MoneyPrinterTurbo.bat"
    launcher.write_text(f"""@echo off
title MoneyPrinterTurbo
cd /d "%~dp0"

set PATH=%~dp0python;%~dp0python\\Scripts;%~dp0ffmpeg;%PATH%
set IMAGEIO_FFMPEG_EXE=%~dp0ffmpeg\\ffmpeg.exe

echo Starting MoneyPrinterTurbo...
echo.
echo API docs: http://127.0.0.1:18080/docs
echo Web UI: http://127.0.0.1:8501
echo.

python\\python.exe main.py --port 18080 --mode desktop
pause
""", encoding="utf-8")

    # Streamlit launcher (legacy web UI)
    streamlit_launcher = BUNDLE / "Start-WebUI.bat"
    streamlit_launcher.write_text(f"""@echo off
title MoneyPrinterTurbo WebUI
cd /d "%~dp0"

set PATH=%~dp0python;%~dp0python\\Scripts;%~dp0ffmpeg;%PATH%
set IMAGEIO_FFMPEG_EXE=%~dp0ffmpeg\\ffmpeg.exe

echo Starting MoneyPrinterTurbo WebUI...
echo Open: http://localhost:8501
echo.

python\\python.exe -m streamlit run webui\\Main.py
pause
""", encoding="utf-8")

    # Copy webui if exists
    if (ROOT / "webui").exists():
        shutil.copytree(ROOT / "webui", BUNDLE / "webui", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".streamlit"))

    print("Launchers created")


def create_readme():
    """Create README for the installer"""
    readme = BUNDLE / "README.txt"
    readme.write_text("""
╔══════════════════════════════════════════════════════╗
║           MoneyPrinterTurbo v2.0                     ║
║           AI Video Generator                         ║
╚══════════════════════════════════════════════════════╝

QUICK START:
1. Double-click "MoneyPrinterTurbo.bat" to start
2. Open http://127.0.0.1:18080/docs in your browser
3. Or use the Desktop App (if installed)

FILES:
- MoneyPrinterTurbo.bat  → Start the server
- Start-WebUI.bat        → Start Streamlit web UI
- config.toml            → Settings (API keys, etc.)

SETUP:
1. Edit config.toml and add your API keys:
   - LLM: OpenAI, Gemini, Claude, etc.
   - Video: Pexels API key (free at pexels.com/api)
2. Run MoneyPrinterTurbo.bat
3. Create videos!

SUPPORT:
- GitHub: https://github.com/harry0703/MoneyPrinterTurbo
""", encoding="utf-8")


def create_zip():
    """Create final zip file"""
    print("\n=== Creating Distribution Package ===")
    zip_path = DIST / "MoneyPrinterTurbo-v2-Windows-x64"
    shutil.make_archive(str(zip_path), "zip", DIST, "MoneyPrinterTurbo")
    size = (Path(str(zip_path) + ".zip").stat().st_size / 1024 / 1024)
    print(f"Package created: {zip_path}.zip ({size:.0f} MB)")


def main():
    print("=" * 60)
    print("  MoneyPrinterTurbo — Installer Builder")
    print("=" * 60)

    clean()
    python_exe = setup_python()
    install_dependencies(python_exe)
    setup_ffmpeg()
    copy_app_files()
    create_launcher()
    create_readme()
    create_zip()

    print("\n" + "=" * 60)
    print("  BUILD COMPLETE!")
    print(f"  Output: dist/MoneyPrinterTurbo-v2-Windows-x64.zip")
    print("=" * 60)
    print("\nUser chi can:")
    print("  1. Download zip")
    print("  2. Giai nen")
    print("  3. Chay MoneyPrinterTurbo.bat")
    print("  Khong can cai Python, FFmpeg, hay bat ky thu gi!")


if __name__ == "__main__":
    main()
