"""
Split MoneyPrinterTurbo into 2 repos:
1. PUBLIC (open-source, MIT) — core pipeline + CLI
2. PRIVATE (commercial) — desktop app + premium features

Output:
  dist/public/  → push to github.com/you/MoneyPrinterTurbo
  dist/private/ → push to github.com/you/MoneyPrinterTurbo-Pro (private repo)
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLIC = ROOT / "dist" / "public"
PRIVATE = ROOT / "dist" / "private"


# ═══════════════════════════════════════
# PUBLIC REPO — Free, Open Source
# ═══════════════════════════════════════
PUBLIC_FILES = [
    # Core app
    "app/__init__.py",
    "app/asgi.py",
    "app/router.py",
    "app/config/__init__.py",
    "app/config/config.py",
    "app/controllers/__init__.py",
    "app/controllers/base.py",
    "app/controllers/v1/__init__.py",
    "app/controllers/v1/base.py",
    "app/controllers/v1/video.py",
    "app/controllers/v1/llm.py",
    "app/controllers/v1/system_controller.py",
    "app/controllers/manager/__init__.py",
    "app/controllers/manager/base_manager.py",
    "app/controllers/manager/memory_manager.py",
    "app/controllers/manager/redis_manager.py",
    "app/models/__init__.py",
    "app/models/schema.py",
    "app/models/const.py",
    "app/models/exception.py",
    "app/services/__init__.py",
    "app/services/llm.py",
    "app/services/voice.py",
    "app/services/video.py",
    "app/services/material.py",
    "app/services/subtitle.py",
    "app/services/task.py",
    "app/services/state.py",
    "app/services/utils/__init__.py",
    "app/services/utils/video_effects.py",
    "app/utils/__init__.py",
    "app/utils/utils.py",

    # Basic plugins (free tier: 5 providers)
    "app/plugins/__init__.py",
    "app/plugins/base.py",
    "app/plugins/registry.py",
    "app/plugins/manager.py",
    "app/plugins/utils.py",
    "app/plugins/builtin/__init__.py",
    "app/plugins/builtin/llm/__init__.py",
    "app/plugins/builtin/llm/openai_plugin.py",
    "app/plugins/builtin/tts/__init__.py",
    "app/plugins/builtin/tts/edge_tts_plugin.py",
    "app/plugins/builtin/material/__init__.py",
    "app/plugins/builtin/material/pexels_plugin.py",

    # Web UI (Streamlit — free)
    "webui/",

    # Resources
    "resource/",

    # Entry points
    "main.py",
    "requirements.txt",
    "config.example.toml",

    # Docker
    "Dockerfile",
    "docker-compose.yml",

    # Docs
    "README.md",
    "README-en.md",
    "LICENSE",
]

# Files to EXCLUDE from public (premium only)
PUBLIC_EXCLUDE = [
    "desktop/",
    "templates/",
    "scripts/build-installer.py",
    "scripts/build-sidecar.py",
    "app/plugins/builtin/llm/claude_plugin.py",
    "app/plugins/builtin/llm/groq_plugin.py",
    "app/plugins/builtin/llm/mistral_plugin.py",
    "app/plugins/builtin/llm/gemini_plugin.py",
    "app/plugins/builtin/llm/deepseek_plugin.py",
    "app/plugins/builtin/llm/qwen_plugin.py",
    "app/plugins/builtin/llm/moonshot_plugin.py",
    "app/plugins/builtin/llm/ollama_plugin.py",
    "app/plugins/builtin/tts/elevenlabs_plugin.py",
    "app/plugins/builtin/tts/openai_tts_plugin.py",
    "app/plugins/builtin/tts/piper_plugin.py",
    "app/plugins/builtin/tts/gpt_sovits_plugin.py",
    "app/plugins/builtin/tts/fpt_ai_plugin.py",
    "app/plugins/builtin/tts/vbee_plugin.py",
    "app/plugins/builtin/material/pixabay_plugin.py",
    "app/plugins/builtin/material/unsplash_plugin.py",
    "app/plugins/builtin/publisher/",
    "app/services/batch.py",
    "app/services/scheduler.py",
    "app/services/analytics.py",
    "app/services/publisher.py",
    "app/services/template.py",
    "app/services/ai_director.py",
    "app/services/animated_captions.py",
    "app/services/utils/video_filters.py",
    "app/services/input_processors/",
    "app/config/config_v2.py",
    "app/config/migration.py",
    "app/controllers/v1/config_controller.py",
    "app/controllers/v1/plugin_controller.py",
    "app/controllers/v1/template_controller.py",
    "app/controllers/v1/batch_controller.py",
    "app/controllers/v1/schedule_controller.py",
    "app/controllers/v1/analytics_controller.py",
    "app/controllers/v1/input_controller.py",
    "app/controllers/v1/publisher_controller.py",
]


def copy_public():
    """Copy public repo files"""
    print("=== Building PUBLIC repo ===")
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)

    for item in PUBLIC_FILES:
        src = ROOT / item
        dst = PUBLIC / item
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True,
                          ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".streamlit"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Create simplified router.py (only free controllers)
    router_content = '''from fastapi import APIRouter
from app.controllers.v1 import llm, video, system_controller

root_api_router = APIRouter()
root_api_router.include_router(video.router)
root_api_router.include_router(llm.router)
root_api_router.include_router(system_controller.router)
'''
    (PUBLIC / "app" / "router.py").write_text(router_content)

    # Create simplified plugins __init__.py (only free plugins)
    plugins_init = '''from app.plugins.manager import PluginManager

plugin_manager = PluginManager()
plugin_manager.discover_plugins()
'''
    (PUBLIC / "app" / "plugins" / "__init__.py").write_text(plugins_init)

    # Create public .gitignore
    gitignore = (ROOT / ".gitignore").read_text() if (ROOT / ".gitignore").exists() else ""
    (PUBLIC / ".gitignore").write_text(gitignore)

    # Create public README with Pro CTA
    readme = '''# MoneyPrinterTurbo

AI Video Generator — Create videos automatically from text/URL/script.

## Features (Free)
- 6-step video pipeline (Script → TTS → Subtitle → Materials → Compose → Render)
- OpenAI LLM for script generation
- Edge TTS (400+ voices, free)
- Pexels stock videos (free)
- CLI + API + Streamlit Web UI
- Docker support

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
pip install -r requirements.txt
python main.py
# Open http://127.0.0.1:8080/docs
```

## ⭐ MoneyPrinterTurbo Pro — Desktop App

Get the full-featured desktop application:

| Feature | Free | Pro |
|---------|------|-----|
| LLM Providers | OpenAI | 9 (+ Claude, Gemini, Groq, DeepSeek...) |
| TTS Voices | Edge TTS | 7 (+ FPT.AI Vietnamese, ElevenLabs, VBee...) |
| Video Sources | Pexels | 3 (+ Pixabay, Unsplash) |
| Templates | ❌ | 10+ templates |
| Color Presets | ❌ | 8 presets (cinematic, warm, cool...) |
| Animated Captions | ❌ | 5 styles (Hormozi, TikTok Viral...) |
| Batch Production | ❌ | ✅ CSV import, parallel processing |
| Auto-Publishing | ❌ | 6 platforms (YouTube, TikTok, Instagram...) |
| Content Schedule | ❌ | ✅ Calendar + auto-publish |
| Analytics | ❌ | ✅ Views, likes, trends |
| AI Director | ❌ | ✅ Auto-optimize everything |
| URL/YouTube Import | ❌ | ✅ Extract content from any URL |
| Desktop App | ❌ | ✅ Windows + macOS + Linux |
| Watermark | Yes | No |

**[Get Pro →](https://moneyprinterturbo.com)**

Monthly $7.99 / Yearly $59.99 / Lifetime $89

## License

MIT License — free for personal and commercial use.
'''
    (PUBLIC / "README.md").write_text(readme)

    print(f"Public repo: {PUBLIC}")
    count = sum(1 for _ in PUBLIC.rglob("*") if _.is_file())
    print(f"  {count} files")


def copy_private():
    """Copy private repo (EVERYTHING)"""
    print("\n=== Building PRIVATE repo ===")
    if PRIVATE.exists():
        shutil.rmtree(PRIVATE)

    # Copy everything except build artifacts
    shutil.copytree(
        ROOT, PRIVATE,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", "node_modules", "target",
            "dist", "build", ".git", "*.db", "*.db-wal",
            "storage", "venv", ".venv", "models",
        )
    )

    # Create private README
    readme = '''# MoneyPrinterTurbo Pro (Private)

Commercial desktop application. DO NOT make this repo public.

## Build

### Development
```bash
# Terminal 1
python main.py --port 18080 --mode desktop

# Terminal 2
cd desktop && npm run tauri dev
```

### Production Installer
```bash
python scripts/build-installer.py
# Output: dist/MoneyPrinterTurbo-v2-Windows-x64.zip
```

### GitHub Release (auto-build for Windows + macOS + Linux)
```bash
git tag v1.0.0
git push --tags
# GitHub Actions builds .exe + .dmg + .AppImage automatically
```
'''
    (PRIVATE / "README.md").write_text(readme)

    print(f"Private repo: {PRIVATE}")
    count = sum(1 for _ in PRIVATE.rglob("*") if _.is_file())
    print(f"  {count} files")


def main():
    print("=" * 60)
    print("  MoneyPrinterTurbo — Split into Public + Private repos")
    print("=" * 60)

    copy_public()
    copy_private()

    print("\n" + "=" * 60)
    print("  DONE!")
    print("=" * 60)
    print(f"""
NEXT STEPS:

1. Create 2 GitHub repos:
   - github.com/YOU/MoneyPrinterTurbo        (PUBLIC)
   - github.com/YOU/MoneyPrinterTurbo-Pro     (PRIVATE)

2. Push public repo:
   cd dist/public
   git init && git add -A
   git commit -m "Initial release"
   git remote add origin https://github.com/YOU/MoneyPrinterTurbo.git
   git push -u origin master

3. Push private repo:
   cd dist/private
   git init && git add -A
   git commit -m "Initial release"
   git remote add origin https://github.com/YOU/MoneyPrinterTurbo-Pro.git
   git push -u origin master
   git tag v0.1.0 && git push --tags
   → GitHub Actions tu dong build .exe + .dmg + .AppImage

4. User mua license → download binary tu Releases
   Khong ai thay source code cua private repo!
""")


if __name__ == "__main__":
    main()
