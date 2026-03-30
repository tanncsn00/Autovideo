import os
import sys
import shutil
import socket

import toml
from loguru import logger

if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle — use exe directory, not temp folder
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = f"{root_dir}/config.toml"


def load_config():
    # fix: IsADirectoryError: [Errno 21] Is a directory: '/MoneyPrinterTurbo/config.toml'
    if os.path.isdir(config_file):
        shutil.rmtree(config_file)

    if not os.path.isfile(config_file):
        example_file = f"{root_dir}/config.example.toml"
        if os.path.isfile(example_file):
            shutil.copyfile(example_file, config_file)
            logger.info("copy config.example.toml to config.toml")
        else:
            # No config file at all (PyInstaller bundle) — create minimal config
            logger.warning(f"No config file found, creating empty config at {config_file}")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write('[app]\nllm_provider = "gemini"\nvideo_source = "pexels"\n\n[whisper]\n\n[proxy]\n\n[azure]\n\n[siliconflow]\n\n[ui]\nhide_log = false\n')

    logger.info(f"load config from file: {config_file}")

    try:
        _config_ = toml.load(config_file)
    except Exception as e:
        logger.warning(f"load config failed: {str(e)}, creating default config")
        _config_ = {"app": {}, "whisper": {}, "proxy": {}, "azure": {}, "siliconflow": {}, "ui": {"hide_log": False}}
    return _config_


def save_config():
    with open(config_file, "w", encoding="utf-8") as f:
        _cfg["app"] = app
        _cfg["azure"] = azure
        _cfg["siliconflow"] = siliconflow
        _cfg["ui"] = ui
        f.write(toml.dumps(_cfg))


_cfg = load_config()
app = _cfg.get("app", {})
whisper = _cfg.get("whisper", {})
proxy = _cfg.get("proxy", {})
azure = _cfg.get("azure", {})
siliconflow = _cfg.get("siliconflow", {})
ui = _cfg.get(
    "ui",
    {
        "hide_log": False,
    },
)

hostname = socket.gethostname()

log_level = _cfg.get("log_level", "DEBUG")
listen_host = _cfg.get("listen_host", "0.0.0.0")
listen_port = _cfg.get("listen_port", 8080)
project_name = _cfg.get("project_name", "MoneyPrinterTurbo")
project_description = _cfg.get(
    "project_description",
    "<a href='https://github.com/harry0703/MoneyPrinterTurbo'>https://github.com/harry0703/MoneyPrinterTurbo</a>",
)
project_version = _cfg.get("project_version", "1.2.6")
reload_debug = False

imagemagick_path = app.get("imagemagick_path", "")
if imagemagick_path and os.path.isfile(imagemagick_path):
    os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path

ffmpeg_path = app.get("ffmpeg_path", "")
if ffmpeg_path and os.path.isfile(ffmpeg_path):
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path

logger.info(f"{project_name} v{project_version}")


def get_mode() -> str:
    """Detect running mode: 'api' (default) or 'desktop'"""
    return os.environ.get("MPT_MODE", "api")

def is_desktop_mode() -> bool:
    return get_mode() == "desktop"

def get_api_key(key_name: str) -> str:
    """Get API key with fallback: env var -> ConfigManager (persistent) -> config.toml [app] -> [ui]"""
    env_key = f"MPT_{key_name.upper()}"
    env_val = os.environ.get(env_key, "")
    if env_val:
        return env_val
    # Check persistent config (desktop mode)
    if is_desktop_mode():
        try:
            from app.config.config_v2 import ConfigManager
            cm = ConfigManager()
            val = cm.get("app", key_name, "")
            if val:
                return val
        except Exception:
            pass
    val = app.get(key_name, "")
    if val:
        return val
    return ui.get(key_name, "")
