## 3. Kế Hoạch Phát Triển

### Phase 1: Nền Tảng Desktop (4-6 Tuần)

#### 1.1 Desktop Application Framework

- **Chọn Tauri (Rust-based)** thay vì Electron
  - Nhẹ hơn Electron 10x (installer ~5MB vs ~150MB)
  - Bảo mật tốt hơn (sandbox built-in)
  - Dùng native webview, tiết kiệm RAM
- Giữ FastAPI backend, nhúng vào Tauri process
- Frontend mới bằng React + TailwindCSS (thay Streamlit)
- Build installer cho Windows, macOS, Linux

#### 1.2 Plugin Architecture

```
┌─────────────────────────────────────┐
│           Plugin Manager            │
├──────────┬──────────┬───────────────┤
│ LLM      │ TTS      │ Video Source  │
│ Plugins  │ Plugins  │ Plugins       │
├──────────┼──────────┼───────────────┤
│ Publisher │ Effect   │ Template      │
│ Plugins  │ Plugins  │ Plugins       │
└──────────┴──────────┴───────────────┘
```

- Strategy pattern cho mỗi loại provider
- Interface chuẩn (Python ABC) để community đóng góp
- Hot-reload plugins không cần restart app
- Plugin marketplace (Phase 5)

#### 1.3 Secure Configuration

- Encrypted API key storage (OS keychain integration)
- Config migration tool từ config.toml cũ
- Environment-based config profiles (dev/prod)
- Dynamic config reload không cần restart

#### 1.4 Auto-Update System

- Built-in updater (Tauri có sẵn)
- Delta updates (chỉ download phần thay đổi)
- Changelog display khi có update mới

---

### Phase 2: Mở Rộng API Providers (2-3 Tuần)

#### 2.1 LLM Providers Mới

| Provider | Lý Do | Ưu Tiên |
|----------|-------|---------|
| **Claude (Anthropic)** | Chất lượng script tốt nhất, context window lớn | Cao |
| **Llama 3.x (llama.cpp)** | Offline hoàn toàn, miễn phí | Cao |
| **Groq** | Tốc độ nhanh nhất (500+ tokens/s) | Trung bình |
| **Mistral** | Mạnh cho multilingual content | Trung bình |
| **Cohere Command R+** | Tốt cho long-form content | Thấp |
| **Perplexity** | Có search built-in, tốt cho research topics | Thấp |

#### 2.2 TTS Providers Mới

| Provider | Lý Do | Ưu Tiên |
|----------|-------|---------|
| **ElevenLabs** | Giọng realistic nhất thị trường, voice cloning | Cao |
| **OpenAI TTS** | Chất lượng cao, đơn giản integrate | Cao |
| **GPT-SoVITS** | Voice cloning local/offline, miễn phí | Cao |
| **Piper TTS** | Offline, nhẹ, 30+ ngôn ngữ, nhanh | Cao |
| **Fish Speech** | Open-source voice cloning, multilingual | Trung bình |
| **Bark (Suno)** | Có emotion/sound effects trong speech | Trung bình |
| **XTTS v2 (Coqui)** | Voice cloning, 17 ngôn ngữ | Trung bình |
| **KittenTTS** | Local, lightweight | Thấp |

#### 2.3 Video/Image Sources Mới

| Source | Lý Do | Ưu Tiên |
|--------|-------|---------|
| **Storyblocks API** | Thư viện lớn, chất lượng cao | Cao |
| **Unsplash** | Ảnh chất lượng → video (Ken Burns) | Cao |
| **LTX-2 (Local AI Gen)** | Tạo video từ text, chạy local | Cao |
| **Stable Diffusion** | Tạo ảnh từ text → video | Trung bình |
| **Videvo** | Free stock footage | Trung bình |
| **Coverr** | Free stock footage | Thấp |
| **YouTube CC Search** | Creative Commons videos | Thấp |

#### 2.4 Music/Audio Sources Mới

| Source | Lý Do | Ưu Tiên |
|--------|-------|---------|
| **Mubert API** | AI-generated music, royalty-free | Cao |
| **Epidemic Sound** | Thư viện nhạc lớn nhất | Trung bình |
| **Pixabay Music** | Free, dễ integrate | Trung bình |
| **Suno AI** | AI tạo nhạc từ text prompt | Thấp |
| **Local library** | User quản lý nhạc riêng | Cao |

---

### Phase 3: Nâng Cấp Chất Lượng Video (3-4 Tuần)

#### 3.1 Template System

```
templates/
├── tiktok/
│   ├── trending-facts.json
│   ├── motivation-quotes.json
│   └── product-review.json
├── youtube-shorts/
│   ├── tutorial.json
│   ├── news-recap.json
│   └── story-time.json
├── instagram-reels/
│   ├── lifestyle.json
│   └── behind-scenes.json
├── corporate/
│   ├── product-demo.json
│   └── company-intro.json
└── education/
    ├── explainer.json
    └── quiz.json
```

- 50+ templates mặc định
- Template bao gồm: layout, font, colors, transition style, subtitle style, pacing
- Template editor visual (drag & drop)
- Export/import templates (JSON format)
- Community template sharing

#### 3.2 Video Transitions Mới (15+)

| Category | Effects |
|----------|---------|
| **Basic** | Fade, Dissolve, Cut |
| **Directional** | Slide (4 hướng), Wipe (4 hướng), Push |
| **Zoom** | Zoom In, Zoom Out, Zoom Through |
| **Creative** | Morph, Glitch, Film Burn, Light Leak |
| **3D** | Flip, Cube Rotate, Page Turn |

#### 3.3 Text Animations

| Effect | Mô Tả |
|--------|--------|
| **Typewriter** | Chữ xuất hiện từng ký tự |
| **Slide In** | Chữ trượt vào từ cạnh |
| **Bounce** | Chữ nảy lên khi xuất hiện |
| **Pop** | Chữ zoom từ nhỏ → to |
| **Glow** | Chữ phát sáng |
| **Wave** | Chữ chuyển động dạng sóng |
| **Karaoke** | Highlight từng từ theo audio |

#### 3.4 Animated Captions (Kiểu CapCut/Opus Clip)

- Word-by-word highlight sync với audio
- Color change khi từ được đọc
- Scale animation cho từ đang active
- Multiple preset styles:
  - "Hormozi" style (bold, centered, color pop)
  - "Documentary" style (bottom bar, clean)
  - "TikTok Viral" style (large, bouncy, colorful)
  - "Corporate" style (subtle, professional)

#### 3.5 Video Effects & Filters

- Color grading presets (cinematic, warm, cool, vintage, noir)
- Brightness/contrast/saturation adjustment
- Speed ramp & slow motion
- Picture-in-picture overlay
- Watermark/branding overlay (logo, text)
- Vignette effect
- Film grain effect
- Blur background (cho ảnh portrait)

#### 3.6 Semantic Footage Matching

- Tích hợp CLIP model (OpenAI) để match script → video clip
- Thay keyword search bằng semantic similarity search
- Scoring system: relevance × quality × diversity
- Fallback: CLIP local → keyword search nếu không có GPU

```
Script: "The sun rises over the mountain, casting golden light..."

Keyword search: "sun" "mountain" "sunrise" → generic results
Semantic search: Finds clips of actual mountain sunrises with warm lighting → much better match
```

---

### Phase 4: Auto-Publishing & Workflow (2-3 Tuần)

#### 4.1 Multi-Platform Publishing

| Platform | API | Features |
|----------|-----|----------|
| **YouTube** | YouTube Data API v3 | Upload, title, description, tags, thumbnail, schedule |
| **TikTok** | TikTok Content Posting API | Upload, caption, auto-hashtags |
| **Instagram** | Instagram Graph API | Reels upload, caption, hashtags |
| **Facebook** | Facebook Graph API | Video upload, post scheduling |
| **X (Twitter)** | X API v2 | Video upload, tweet text |
| **LinkedIn** | LinkedIn API | Video upload, post text |

#### 4.2 Smart Scheduling

- Content calendar view (daily/weekly/monthly)
- Best time to post suggestions (per platform)
- Queue system: tạo videos trước, publish theo schedule
- Timezone support
- Holiday/event awareness

#### 4.3 Batch Production

```
Input: topics.csv
┌────────────────────────────────────────┐
│ topic,          style,    platform     │
│ "AI trends",    tech,     youtube      │
│ "Cooking tips", lifestyle, tiktok      │
│ "Stock market", finance,  instagram    │
│ ... (50-100 topics)                    │
└────────────────────────────────────────┘
        ↓ Batch Processor
[Video 1] [Video 2] [Video 3] ... [Video N]
        ↓ Auto-Publisher
[YouTube] [TikTok] [Instagram] [Facebook]
```

- Import topic list từ CSV/Excel
- Parallel processing (tùy CPU/GPU)
- Priority queue management
- Error recovery & retry
- Progress dashboard

#### 4.4 Analytics Dashboard

- Views, likes, comments tracking per video
- Performance comparison across platforms
- Best performing topics/styles analysis
- Revenue tracking (nếu monetized)
- A/B testing: 2 versions cùng content, so sánh performance
- Export reports (PDF/CSV)

---

### Phase 5: AI Nâng Cao (4-6 Tuần)

#### 5.1 Multi-Modal Input

| Input | Output | Mô Tả |
|-------|--------|--------|
| **URL** | Video | Paste link bài viết → auto extract → video |
| **Podcast/Audio** | Video | Upload audio → auto transcript → video |
| **Long Video** | Short Clips | Upload video dài → AI cắt highlights → shorts |
| **PDF/Slides** | Video | Upload presentation → animated video |
| **Images** | Video | Upload ảnh → slideshow video with effects |
| **RSS Feed** | Video Series | Auto-generate videos từ blog feed |

#### 5.2 AI Director

- Auto-chọn template phù hợp content type
- Auto-chọn nhạc nền theo mood/emotion của script
- Auto-pacing: đoạn hồi hộp → nhanh hơn, đoạn giải thích → chậm hơn
- Auto-chọn transition style phù hợp
- Suggest thumbnail từ video frames
- AI title & hashtag generation cho mỗi platform

#### 5.3 Voice Cloning

- Clone voice từ 30 giây sample audio
- Consistent voice across tất cả videos
- Voice style transfer (calm, energetic, professional)
- Multi-language với cùng voice characteristics

#### 5.4 AI Video Generation (Local)

- Tích hợp LTX-2 model chạy local
- Text prompt → video clip generation
- Thay thế hoàn toàn stock footage nếu cần
- Cần GPU: NVIDIA RTX 3060+ (12GB VRAM)

---

