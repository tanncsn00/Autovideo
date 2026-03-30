## 1. Phân Tích Hiện Trạng

### 1.1 Kiến Trúc Hiện Tại

- **Backend:** FastAPI (API server trên port 8080)
- **Frontend:** Streamlit (Web UI trên port 8501)
- **Video Processing:** MoviePy + FFmpeg
- **State Management:** In-memory hoặc Redis
- **Task Queue:** Thread-based với configurable concurrency

### 1.2 Pipeline Tạo Video (6 Bước)

```
[1] Script Generation (LLM)
        ↓
[2] Search Terms Generation (LLM)
        ↓
[3] Audio/Voice Generation (TTS)
        ↓
[4] Subtitle Generation (Whisper/Edge TTS)
        ↓
[5] Video Material Sourcing (Pexels/Pixabay/Local)
        ↓
[6] Video Composition & Rendering (MoviePy)
```

### 1.3 API Providers Hiện Có

| Loại | Providers |
|------|-----------|
| **LLM (16)** | OpenAI, Azure OpenAI, Moonshot, Qwen, DeepSeek, Gemini, Ollama, G4F, OneAPI, Cloudflare AI, ERNIE, ModelScope, Pollinations AI |
| **TTS (4)** | Edge TTS, Azure Speech (v1 & v2), SiliconFlow (CosyVoice2), Gemini TTS |
| **Video Sources (3)** | Pexels, Pixabay, Local files |
| **Subtitles (2)** | Whisper (local), Edge TTS |

### 1.4 Video Capabilities Hiện Có

- Aspect ratio: 16:9, 9:16, 1:1
- Transitions: Fade In/Out, Slide In/Out, Shuffle
- Audio: Voice + BGM layering, volume control
- Subtitles: Positioning (top/bottom/center/custom), font styling, stroke
- Images: Zoom effect (Ken Burns cơ bản)
- Codec: H.264/AAC, 30fps, multi-thread rendering

### 1.5 Điểm Yếu Cần Cải Thiện

| Vấn Đề | Chi Tiết |
|---------|----------|
| Video source hạn chế | Chỉ có Pexels + Pixabay, keyword search cơ bản |
| TTS thiếu đa dạng | Không voice cloning, không emotion control |
| Video effects nghèo nàn | 5 transitions, không text animation, không filters |
| Không có template | Không có hệ thống template, mỗi video phải config từ đầu |
| Không auto-publish | Phải tự upload video lên các platform |
| Subtitle cơ bản | Không animated captions, không word-highlight |
| UI/UX lỗi thời | Streamlit hạn chế về customization |
| Không desktop native | Chạy qua browser, phụ thuộc terminal |
| Không offline hoàn toàn | Nhiều provider cần internet |
| Config không an toàn | API keys lưu plain text trong config.toml |

---

