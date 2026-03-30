<div align="center">

# AutoVideo

**AI Video Generator & Auto Publisher**

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg?style=flat-square)](https://python.org)
[![Tauri](https://img.shields.io/badge/Tauri-v2-orange.svg?style=flat-square)](https://tauri.app)

</div>

---

Turn any topic into a ready-to-publish short video in minutes. AI script writing, stock footage, voice narration, subtitles, background music, and auto-publishing to TikTok — all in one app.

## Download

Go to [**Releases**](../../releases) and download the installer for your OS:

| OS | File |
|---|---|
| Windows | `AutoVideo_x.x.x_x64-setup.exe` |
| macOS (Apple Silicon) | `AutoVideo_x.x.x_aarch64.dmg` |
| macOS (Intel) | `AutoVideo_x.x.x_x64.dmg` |
| Linux | `AutoVideo_x.x.x_amd64.AppImage` |

> **Note:** You also need [Python 3.11+](https://python.org/downloads/) and [ImageMagick](https://imagemagick.org/script/download.php) installed on your system.

### First Launch

1. Install and open the app
2. Go to **Settings** and add your API keys:
   - **LLM** — e.g., [Google Gemini](https://aistudio.google.com/apikey) (free)
   - **Video source** — e.g., [Pexels](https://www.pexels.com/api/) (free)
3. Go to **Create** and enter a topic — done!

## Key Features

- **End-to-end video generation** — Topic to finished video, fully automated
- **10+ LLM providers** — OpenAI, Gemini, DeepSeek, Moonshot, Ollama, Claude, Groq, Mistral, Qwen, Cloudflare
- **400+ voices** — Edge TTS (free), Azure, ElevenLabs, FPT.AI, VBee
- **Free stock footage** — Pexels, Pixabay (royalty-free, HD)
- **Auto subtitles** — Synced to audio, customizable font/color/position/stroke
- **TikTok auto-upload** — Login once, publish or schedule posts automatically
- **Content scheduler** — Schedule posts for automatic publishing
- **Batch production** — Generate multiple videos at once
- **Plugin architecture** — Extensible LLM, TTS, Material, Publisher plugins
- **14 prompt templates** — Motivation, storytelling, education, news, product review, and more
- **Resource manager** — Templates, BGM, fonts, and local materials

## Tech Stack

| | |
|---|---|
| **Desktop** | Tauri v2 (Rust + WebView) |
| **Frontend** | React 19, Vite 6, TailwindCSS v4 |
| **Backend** | Python FastAPI (sidecar) |
| **Video** | MoviePy + FFmpeg + ImageMagick |
| **Publishing** | Playwright (browser automation) |

## Development

For developers who want to build from source:

```bash
git clone <repo-url>
cd AutoVideo

# Python backend
pip install -r requirements.txt

# Desktop app
cd desktop && npm install && cd ..

# Copy config
cp config.example.toml config.toml

# Run (Windows)
run-desktop.bat

# Run (macOS/Linux)
cd desktop && npm run dev &
python main.py --mode desktop --port 18080
```

**Other run modes:**

```bash
webui.bat          # Web UI (Windows)
sh webui.sh        # Web UI (macOS/Linux)
docker-compose up  # Docker
python main.py     # API only → http://127.0.0.1:8080/docs
```

## License

[MIT](LICENSE)
