"""Build Python sidecar as standalone executable using PyInstaller"""
import os
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
        # Bundle resource files
        "--add-data", f"{ROOT / 'resource'}{os.pathsep}resource",
        "--add-data", f"{ROOT / 'config.example.toml'}{os.pathsep}.",
        # Collect entire app package
        "--collect-all", "app",
        "--collect-all", "edge_tts",
        # Hidden imports for all modules uvicorn needs
        "--hidden-import", "uvicorn",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.http.h11_impl",
        "--hidden-import", "uvicorn.protocols.http.httptools_impl",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off",
        "--hidden-import", "fastapi",
        "--hidden-import", "starlette",
        "--hidden-import", "pydantic",
        "--hidden-import", "toml",
        "--hidden-import", "tomli_w",
        "--hidden-import", "httpx",
        "--hidden-import", "edge_tts",
        "--hidden-import", "moviepy",
        "--hidden-import", "PIL",
        "--hidden-import", "requests",
        "--hidden-import", "aiohttp",
        "--hidden-import", "multipart",
        "--hidden-import", "python_multipart",
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
    build()
