"""Build Python sidecar as standalone executable using PyInstaller"""
import subprocess
import sys
import shutil
import platform
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "desktop" / "src-tauri" / "binaries"


def get_target_triple():
    machine = platform.machine().lower()
    if sys.platform == "win32":
        arch = "x86_64" if machine in ("amd64", "x86_64") else machine
        return f"{arch}-pc-windows-msvc"
    elif sys.platform == "darwin":
        arch = "aarch64" if machine == "arm64" else machine
        return f"{arch}-apple-darwin"
    else:
        return f"{machine}-unknown-linux-gnu"


def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "python-backend",
        "--distpath", str(OUTPUT),
        "--workpath", str(ROOT / "build" / "pyinstaller"),
        "--specpath", str(ROOT / "build"),
        "--add-data", f"{ROOT / 'resource'}{os.pathsep}resource",
        "--hidden-import", "edge_tts",
        "--hidden-import", "faster_whisper",
        "--hidden-import", "moviepy",
        "--hidden-import", "app.services.llm",
        "--hidden-import", "app.services.voice",
        "--hidden-import", "app.services.video",
        "--hidden-import", "app.services.material",
        "--hidden-import", "app.services.subtitle",
        "--hidden-import", "app.services.task",
        "--hidden-import", "app.plugins.builtin.llm.openai_plugin",
        "--hidden-import", "app.plugins.builtin.tts.edge_tts_plugin",
        "--hidden-import", "app.plugins.builtin.material.pexels_plugin",
        "--collect-all", "edge_tts",
        str(ROOT / "main.py"),
    ]

    print(f"Building sidecar...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Rename for Tauri sidecar convention
    target_triple = get_target_triple()
    ext = ".exe" if sys.platform == "win32" else ""
    src = OUTPUT / f"python-backend{ext}"
    dst = OUTPUT / f"python-backend-{target_triple}{ext}"

    if src.exists():
        if dst.exists():
            dst.unlink()
        shutil.move(str(src), str(dst))
        print(f"Sidecar built: {dst}")
        print(f"Size: {dst.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print(f"ERROR: Expected output not found: {src}")
        sys.exit(1)


if __name__ == "__main__":
    import os
    build()
