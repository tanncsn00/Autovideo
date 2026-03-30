## 11. Tham Khảo & Nguồn Học Hỏi

### 11.1 Feature-by-Feature

| Feature | Học Từ | Chi Tiết |
|---------|--------|----------|
| Animated captions | **Opus Clip, CapCut** | Word-by-word highlight, color change, bounce effect |
| Template system | **FlexClip** (6000+ templates) | JSON-based template engine, visual editor |
| Semantic matching | **Pictory** | CLIP model thay keyword search |
| Auto-publish | **quso.ai** (formerly vidyo.ai) | Multi-platform API integration, scheduling |
| Voice quality | **ElevenLabs** | API integration + GPT-SoVITS local alternative |
| Desktop UX | **CapCut Desktop** | Clean UI, timeline view, drag-drop, real-time preview |
| Plugin system | **VS Code Extensions** | Marketplace model, community contributions |
| Long→Short | **Opus Clip** | AI scene detection, virality scoring |
| Batch processing | **quso.ai** | Queue management, priority system |
| Analytics | **TubeBuddy** | Performance tracking, keyword research |

### 11.2 Tech Stack Tham Khảo

| Component | Công Nghệ | Tại Sao |
|-----------|-----------|---------|
| Desktop Framework | **Tauri** | Nhẹ, bảo mật, cross-platform |
| Frontend | **React + TailwindCSS** | Ecosystem lớn, component library phong phú |
| Backend | **FastAPI (giữ nguyên)** | Đã proven, async support tốt |
| Video Processing | **MoviePy + FFmpeg (giữ nguyên)** | Mature, đầy đủ features |
| AI Video Gen | **LTX-2 via ComfyUI** | Best open-source video generation |
| Voice Clone | **GPT-SoVITS** | Best open-source voice cloning |
| Semantic Search | **CLIP (OpenAI)** | Best vision-language model |
| Local LLM | **llama.cpp / Ollama** | Đã support, cần optimize |
| Local TTS | **Piper TTS** | Nhẹ, nhanh, 30+ ngôn ngữ |
| Database | **SQLite** | Embedded, không cần server |
| Auto-Update | **Tauri Updater** | Built-in, delta updates |

### 11.3 Open-Source Repos Tham Khảo

| Repo | Link | Học Gì |
|------|------|--------|
| ShortGPT | github.com/RayVentura/ShortGPT | Framework structure, ElevenLabs integration |
| Open-Sora | github.com/hpcaitech/Open-Sora | Text-to-video pipeline |
| GPT-SoVITS | github.com/RVC-Boss/GPT-SoVITS | Voice cloning integration |
| Piper | github.com/rhasspy/piper | Offline TTS integration |
| ComfyUI | github.com/comfyanonymous/ComfyUI | AI video generation workflow |
| yt-dlp | github.com/yt-dlp/yt-dlp | Video download integration |
| Whisper | github.com/openai/whisper | Subtitle generation (đã có) |

---
