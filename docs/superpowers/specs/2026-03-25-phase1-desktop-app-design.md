# Phase 1: Desktop Application — Design Spec

**Date:** 2026-03-25
**Status:** Reviewed (v2)
**Scope:** Tauri v2 + React frontend, Sidecar FastAPI, Plugin architecture, Secure config, Auto-update

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
+------------------------------------------------------------------+
|                        Tauri v2 Shell                             |
|  +-----------------------------+  +----------------------------+ |
|  |     React Frontend          |  |   Rust Core                | |
|  |     (WebView)               |  |                            | |
|  |  +------------------------+ |  |  - Window management       | |
|  |  | TailwindCSS + shadcn   | |  |  - System tray             | |
|  |  | React Router           | |  |  - Auto-updater            | |
|  |  | Zustand (state)        | |  |  - OS keychain (secrets)   | |
|  |  | react-i18next          | |  |  - File dialogs            | |
|  |  | TanStack Query (API)   | |  |  - Sidecar lifecycle       | |
|  |  +------------------------+ |  |  - IPC bridge              | |
|  +-----------------------------+  +----------------------------+ |
|                |                             |                    |
|                | HTTP (localhost:18080)       | Tauri Commands     |
|                v                             v                    |
|  +-----------------------------+  +----------------------------+ |
|  |   FastAPI Sidecar           |  |   Tauri Plugin APIs        | |
|  |   (Python subprocess)       |  |                            | |
|  |                             |  |  - tauri-plugin-updater    | |
|  |  - All existing services    |  |  - tauri-plugin-shell      | |
|  |  - LLM, TTS, Video, etc.   |  |  - tauri-plugin-store      | |
|  |  - Plugin manager (new)     |  |  - tauri-plugin-dialog     | |
|  |  - License service (new)    |  |  - tauri-plugin-notification|
|  |  - Config service (new)     |  |  - tauri-plugin-os         | |
|  +-----------------------------+  +----------------------------+ |
+------------------------------------------------------------------+
```

### 1.2 Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Desktop framework | Tauri v2 | 10x lighter than Electron, native webview, Rust security, built-in updater |
| Python integration | Sidecar (subprocess) | Reuses 100% of existing FastAPI code, zero rewrite risk |
| Frontend framework | React 19 + Vite | Largest ecosystem, best component libraries, fast HMR |
| CSS framework | TailwindCSS v4 + shadcn/ui | Utility-first, beautiful components, fully customizable |
| State management | Zustand | Lightweight, no boilerplate, TypeScript-first |
| API layer | TanStack Query | Caching, retry, optimistic updates, devtools |
| i18n | react-i18next | Auto-detect OS language, JSON translations (reuse existing) |
| Local DB | SQLite (via Python) | Embedded, no server, replace in-memory state |
| Config storage | TOML (app data) + OS Keychain (secrets) | Migrate from plain-text config.toml |

### 1.3 Why Sidecar Over PyO3/Embedded

| Approach | Pros | Cons |
|----------|------|------|
| **Sidecar (chosen)** | Zero Python rewrite, independent updates, easy debugging, all MoviePy/FFmpeg deps work | Extra process, ~50MB for bundled Python |
| PyO3 embedded | Single process, tighter integration | Massive rewrite, MoviePy/FFmpeg compatibility issues, GIL problems |
| Tauri Commands wrapping Python | Clean IPC | Still needs subprocess, adds Rust boilerplate for every endpoint |

**Sidecar wins** because the entire value is in the Python services. Rewriting them in Rust gains nothing and risks breaking a working pipeline.

---

## 2. Project Structure

### 2.1 Monorepo Layout

```
MoneyPrinterTurbo-v2/
├── app/                          # Python backend (EXISTING - keep as-is)
│   ├── services/                 # Core pipeline services (untouched)
│   ├── models/                   # Data models (untouched)
│   ├── controllers/              # API endpoints (extend)
│   ├── config/                   # Config system (refactor)
│   └── plugins/                  # NEW: Plugin system
│       ├── base.py               # Plugin ABC interfaces
│       ├── manager.py            # Plugin discovery & lifecycle
│       ├── registry.py           # Plugin registry
│       └── builtin/              # Built-in plugins (migrate existing providers)
│           ├── llm/
│           │   ├── openai_plugin.py
│           │   ├── gemini_plugin.py
│           │   └── ollama_plugin.py
│           ├── tts/
│           │   ├── edge_tts_plugin.py
│           │   ├── siliconflow_plugin.py
│           │   └── gemini_tts_plugin.py
│           ├── material/
│           │   ├── pexels_plugin.py
│           │   └── pixabay_plugin.py
│           └── effect/
│               └── transitions_plugin.py
│
├── desktop/                      # NEW: Tauri + React desktop app
│   ├── src-tauri/                # Rust/Tauri backend
│   │   ├── Cargo.toml
│   │   ├── tauri.conf.json       # Tauri config (window, security, updater)
│   │   ├── capabilities/         # Tauri v2 permission capabilities
│   │   ├── src/
│   │   │   ├── main.rs           # Entry point
│   │   │   ├── lib.rs            # Tauri setup & plugin registration
│   │   │   ├── sidecar.rs        # Python sidecar lifecycle management
│   │   │   ├── commands.rs       # Tauri IPC commands (keychain, system)
│   │   │   └── tray.rs           # System tray setup
│   │   └── icons/                # App icons (all platforms)
│   │
│   ├── src/                      # React frontend
│   │   ├── main.tsx              # React entry
│   │   ├── App.tsx               # Root component + router
│   │   ├── api/                  # API client layer
│   │   │   ├── client.ts         # Axios/fetch wrapper pointing to sidecar
│   │   │   ├── hooks.ts          # TanStack Query hooks
│   │   │   └── types.ts          # TypeScript types (mirror Pydantic models)
│   │   ├── components/           # Reusable UI components
│   │   │   ├── ui/               # shadcn/ui components
│   │   │   ├── layout/           # Shell, Sidebar, Header
│   │   │   ├── video/            # Video-specific components
│   │   │   └── settings/         # Settings components
│   │   ├── pages/                # Route pages
│   │   │   ├── Dashboard.tsx     # Home / recent projects
│   │   │   ├── Create.tsx        # Video creation wizard
│   │   │   ├── Projects.tsx      # Project list / history
│   │   │   ├── Settings.tsx      # App settings
│   │   │   ├── Plugins.tsx       # Plugin management
│   │   │   └── License.tsx       # License activation
│   │   ├── stores/               # Zustand stores
│   │   │   ├── appStore.ts       # App-wide state
│   │   │   ├── videoStore.ts     # Video creation state
│   │   │   └── settingsStore.ts  # Settings state
│   │   ├── i18n/                 # Internationalization
│   │   │   ├── index.ts          # i18n config
│   │   │   └── locales/          # Translation JSON files
│   │   │       ├── en.json
│   │   │       ├── zh.json
│   │   │       ├── vi.json
│   │   │       └── ...
│   │   ├── hooks/                # Custom React hooks
│   │   ├── lib/                  # Utilities
│   │   └── styles/               # Global styles
│   │       └── globals.css       # Tailwind imports
│   │
│   ├── index.html                # Vite HTML entry
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── scripts/                      # NEW: Build & packaging scripts
│   ├── build-sidecar.py          # Bundle Python + deps with PyInstaller/Nuitka
│   ├── build-desktop.sh          # Full build pipeline
│   └── dev.sh                    # Development launcher
│
├── config.toml                   # EXISTING config (keep for backward compat)
├── main.py                       # EXISTING entry point (keep for CLI/API mode)
└── requirements.txt              # EXISTING Python deps
```

### 2.2 Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  desktop/src/ (React + TailwindCSS + shadcn/ui)          │
│  - Pages, components, stores, routing                    │
│  - Calls FastAPI via HTTP on localhost                    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (localhost:18080)
┌────────────────────────┴────────────────────────────────┐
│                    API LAYER                              │
│  app/controllers/ (FastAPI endpoints)                    │
│  - Video creation, task management, config, plugins      │
│  - Input validation (Pydantic)                           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    SERVICE LAYER                          │
│  app/services/ (Business logic)                          │
│  - task.py, llm.py, voice.py, video.py, material.py     │
│  - Uses plugins via PluginManager                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    PLUGIN LAYER                           │
│  app/plugins/ (Provider implementations)                 │
│  - LLM plugins, TTS plugins, Material plugins            │
│  - Each plugin implements a standard interface (ABC)     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    DATA LAYER                             │
│  SQLite (tasks, projects, settings)                      │
│  OS Keychain (API keys, license key)                     │
│  File system (videos, cache, plugins)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Sidecar: Python Backend Integration

### 3.1 Sidecar Lifecycle

```
Tauri App Start
    │
    ├── 1. Check bundled Python exists
    │      (desktop/src-tauri/binaries/python-sidecar)
    │
    ├── 2. Spawn Python subprocess
    │      Command: ./python-sidecar --port 18080 --mode desktop
    │
    ├── 3. Health check loop (max 10s)
    │      GET http://localhost:18080/api/v1/ping
    │      Retry every 500ms until 200 OK
    │
    ├── 4. Show main window (after health check passes)
    │
    ├── 5. Monitor sidecar process
    │      If crashes → restart (max 3 retries)
    │      If unresponsive → kill + restart
    │
    └── On app quit:
         Send SIGTERM → wait 5s → SIGKILL if needed
```

### 3.2 Sidecar Rust Code (Simplified)

```rust
// src-tauri/src/sidecar.rs

use tauri::Manager;
use tauri_plugin_shell::ShellExt;

pub async fn start_sidecar(app: &tauri::AppHandle) -> Result<(), String> {
    let sidecar = app.shell()
        .sidecar("python-backend")
        .expect("failed to find sidecar binary")
        .args(["--port", "18080", "--mode", "desktop"]);

    let (mut rx, child) = sidecar.spawn()
        .expect("failed to spawn sidecar");

    // Store child process handle for cleanup
    app.manage(SidecarState { child });

    // Wait for health check
    wait_for_ready("http://localhost:18080/api/v1/ping", 10_000).await?;

    Ok(())
}
```

### 3.3 Python Entry Point Changes

```python
# main.py (modified)

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--mode", choices=["api", "desktop"], default="api")
    args = parser.parse_args()

    if args.mode == "desktop":
        # Desktop mode: different config path, no CORS needed, SQLite state
        os.environ["MPT_MODE"] = "desktop"
        os.environ["MPT_PORT"] = str(args.port)

    uvicorn.run(
        "app.asgi:app",
        host="127.0.0.1",  # localhost only in desktop mode
        port=args.port,
        log_level="info",
    )
```

### 3.4 Bundling Python as Sidecar

For development: Python runs from system installation.
For distribution: Bundle using **PyInstaller** (Phase 1) or **Nuitka** (Phase 1.5 for license protection).

```
Build pipeline:
1. PyInstaller bundles app/ + dependencies → single executable
2. Executable placed in desktop/src-tauri/binaries/
3. Tauri bundles it as a sidecar in the installer
4. Total installer size: ~80-120MB (Python + deps + FFmpeg)
```

FFmpeg bundling:
- Windows: Include ffmpeg.exe in sidecar bundle
- macOS: Include ffmpeg binary, or require brew install
- Linux: Require system ffmpeg (apt install ffmpeg)

---

## 4. Frontend Design

### 4.1 Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| React | 19.x | UI framework |
| Vite | 6.x | Build tool + HMR |
| TypeScript | 5.x | Type safety |
| TailwindCSS | v4 | Utility CSS |
| shadcn/ui | latest | Component library (not a dependency, copy-paste) |
| React Router | v7 | Client-side routing |
| Zustand | 5.x | State management |
| TanStack Query | v5 | API data fetching + caching |
| react-i18next | latest | Internationalization |
| Lucide React | latest | Icons |
| Framer Motion | latest | Animations |

### 4.2 Page Structure & Navigation

```
┌─────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌─────────────────────────────────────┐  │
│  │          │  │  Header: breadcrumb + language + ?   │  │
│  │ Sidebar  │  ├─────────────────────────────────────┤  │
│  │          │  │                                     │  │
│  │ Dashboard│  │          Main Content Area           │  │
│  │ Create   │  │                                     │  │
│  │ Projects │  │  (Route-based page rendering)       │  │
│  │ Plugins  │  │                                     │  │
│  │ Settings │  │                                     │  │
│  │          │  │                                     │  │
│  │          │  │                                     │  │
│  │ ──────── │  │                                     │  │
│  │ License  │  │                                     │  │
│  │ About    │  │                                     │  │
│  └──────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Pages:**

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Recent projects, quick stats, quick create |
| Create | `/create` | Step-by-step video creation wizard |
| Projects | `/projects` | List of all generated videos with status |
| Project Detail | `/projects/:id` | Single project: preview, re-render, export |
| Plugins | `/plugins` | Installed plugins, enable/disable, config |
| Settings | `/settings` | App settings, API keys, defaults |
| License | `/license` | License activation, device management |

### 4.3 Video Creation Flow (Create Page)

The Create page is a **multi-step wizard** replacing the Streamlit single-page form:

```
Step 1: Content          Step 2: Style           Step 3: Audio
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│                  │    │                  │    │                  │
│ Subject/Topic    │    │ Aspect Ratio     │    │ Voice Selection  │
│ OR               │───→│ Video Source     │───→│ Voice Rate       │
│ Custom Script    │    │ Clip Duration    │    │ BGM Selection    │
│                  │    │ Transition Style │    │ BGM Volume       │
│ Language         │    │ Concat Mode      │    │                  │
│ Paragraph Count  │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
Step 4: Subtitle        Step 5: Review & Generate       │
┌──────────────────┐    ┌──────────────────┐            │
│                  │    │                  │            │
│ Enable/Disable   │    │ Summary of all   │◄───────────┘
│ Position         │◄───│ settings         │
│ Font & Size      │    │                  │
│ Colors           │    │ [Generate Video] │
│ Stroke           │    │                  │
│                  │    │ Progress bar     │
└──────────────────┘    │ Live status      │
                        └──────────────────┘
```

### 4.4 API Client Layer

```typescript
// desktop/src/api/client.ts

const SIDECAR_URL = "http://127.0.0.1:18080";

export const apiClient = {
  // Video endpoints
  createVideo: (params: VideoParams) =>
    fetch(`${SIDECAR_URL}/api/v1/videos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    }).then(r => r.json() as Promise<TaskResponse>),

  getTask: (taskId: string) =>
    fetch(`${SIDECAR_URL}/api/v1/tasks/${taskId}`)
      .then(r => r.json() as Promise<TaskQueryResponse>),

  deleteTask: (taskId: string) =>
    fetch(`${SIDECAR_URL}/api/v1/tasks/${taskId}`, { method: "DELETE" })
      .then(r => r.json() as Promise<TaskDeletionResponse>),

  // New endpoints (Phase 1)
  getConfig: () =>
    fetch(`${SIDECAR_URL}/api/v1/config`).then(r => r.json()),

  updateConfig: (config: Partial<AppConfig>) =>
    fetch(`${SIDECAR_URL}/api/v1/config`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    }).then(r => r.json()),

  getPlugins: () =>
    fetch(`${SIDECAR_URL}/api/v1/plugins`).then(r => r.json()),

  // Health
  ping: () =>
    fetch(`${SIDECAR_URL}/api/v1/ping`).then(r => r.json()),
};
```

```typescript
// desktop/src/api/hooks.ts

import { useQuery, useMutation } from "@tanstack/react-query";

export function useTask(taskId: string | null) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () => apiClient.getTask(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      // Poll every 2s while processing, stop when done
      const state = query.state.data?.state;
      return state === 4 ? 2000 : false; // 4 = PROCESSING
    },
  });
}

export function useCreateVideo() {
  return useMutation({
    mutationFn: apiClient.createVideo,
  });
}

export function useConfig() {
  return useQuery({
    queryKey: ["config"],
    queryFn: apiClient.getConfig,
  });
}
```

### 4.5 TypeScript Types (Mirror Pydantic Models)

```typescript
// desktop/src/api/types.ts

export type VideoAspect = "16:9" | "9:16" | "1:1";
export type VideoConcatMode = "random" | "sequential";
export type VideoTransitionMode = "None" | "Shuffle" | "FadeIn" | "FadeOut" | "SlideIn" | "SlideOut";

export interface VideoParams {
  video_subject?: string;
  video_script?: string;
  video_terms?: string;
  video_aspect?: VideoAspect;
  video_concat_mode?: VideoConcatMode;
  video_transition_mode?: VideoTransitionMode;
  video_clip_duration?: number;
  video_count?: number;
  video_language?: string;

  voice_name?: string;
  voice_volume?: number;
  voice_rate?: number;

  bgm_type?: string;
  bgm_file?: string;
  bgm_volume?: number;

  subtitle_enabled?: boolean;
  subtitle_position?: string;
  font_name?: string;
  text_fore_color?: string;
  text_background_color?: string;
  font_size?: number;
  stroke_color?: string;
  stroke_width?: number;

  n_threads?: number;
  paragraph_number?: number;
}

export interface TaskResponse {
  task_id: string;
}

export interface TaskQueryResponse {
  state: number;        // -1=failed, 1=complete, 4=processing
  progress: number;     // 0-100
  videos?: string[];
  combined_videos?: string[];
  script?: string;
  terms?: string[];
  audio_file?: string;
  subtitle_path?: string;
  materials?: MaterialInfo[];
}
```

---

## 5. Plugin Architecture

### 5.1 Design Goals

1. **Formalize** the existing Strategy patterns into a proper plugin system
2. **Zero regression** — existing providers become built-in plugins
3. **Extensible** — community can add new providers without modifying core code
4. **Hot-reload** — enable/disable plugins without restart
5. **Configurable** — each plugin has its own config schema

### 5.2 Plugin Interface (ABC)

```python
# app/plugins/base.py

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel


class PluginMeta(BaseModel):
    """Plugin metadata"""
    name: str                    # Unique identifier: "openai", "edge-tts"
    display_name: str            # Human-readable: "OpenAI GPT"
    version: str                 # Semver: "1.0.0"
    description: str             # Short description
    author: str                  # Author name
    plugin_type: str             # "llm" | "tts" | "material" | "effect" | "music"
    config_schema: dict = {}     # JSON Schema for plugin-specific config
    builtin: bool = True         # Built-in vs third-party


class PluginConfig(BaseModel):
    """Base config all plugins share"""
    enabled: bool = True
    priority: int = 0            # Higher = preferred when multiple available


class BasePlugin(ABC):
    """Base class all plugins must extend"""

    @abstractmethod
    def get_meta(self) -> PluginMeta:
        """Return plugin metadata"""
        ...

    @abstractmethod
    def validate_config(self, config: dict) -> bool:
        """Validate plugin-specific configuration"""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if plugin can run (API key set, deps installed, etc.)"""
        ...


class LLMPlugin(BasePlugin):
    """Interface for LLM provider plugins"""

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate text response from prompt"""
        ...

    def get_models(self) -> list[str]:
        """List available models for this provider"""
        return []


class TTSPlugin(BasePlugin):
    """Interface for TTS provider plugins"""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str,
        rate: float = 1.0,
        output_path: str = "",
    ) -> tuple[str, Any]:
        """Convert text to speech. Returns (audio_path, subtitle_data)"""
        ...

    @abstractmethod
    def get_voices(self) -> list[dict]:
        """List available voices: [{"id": "...", "name": "...", "language": "...", "gender": "..."}]"""
        ...


class MaterialPlugin(BasePlugin):
    """Interface for video/image material source plugins"""

    @abstractmethod
    async def search(
        self,
        query: str,
        aspect: str = "16:9",
        max_results: int = 10,
    ) -> list[dict]:
        """Search for video/image materials"""
        ...

    @abstractmethod
    async def download(self, url: str, output_dir: str) -> str:
        """Download material to local path"""
        ...


class EffectPlugin(BasePlugin):
    """Interface for video effect plugins"""

    @abstractmethod
    def get_transitions(self) -> list[str]:
        """List available transition names"""
        ...

    @abstractmethod
    def apply_transition(
        self,
        clip_a,      # MoviePy VideoClip
        clip_b,      # MoviePy VideoClip
        transition: str,
        duration: float = 1.0,
    ):
        """Apply transition between two clips, return merged clip"""
        ...


class MusicPlugin(BasePlugin):
    """Interface for background music source plugins"""

    @abstractmethod
    async def search(self, mood: str, duration: float) -> list[dict]:
        """Search for music by mood/genre"""
        ...

    @abstractmethod
    async def download(self, url: str, output_dir: str) -> str:
        """Download music to local path"""
        ...
```

### 5.3 Plugin Manager

```python
# app/plugins/manager.py

import importlib
import os
from pathlib import Path
from loguru import logger
from app.plugins.base import BasePlugin, PluginMeta
from app.plugins.registry import PluginRegistry


class PluginManager:
    """Discovers, loads, and manages plugins"""

    def __init__(self):
        self.registry = PluginRegistry()
        self._plugin_dirs: list[Path] = []

    def add_plugin_dir(self, path: Path):
        """Register a directory to scan for plugins"""
        self._plugin_dirs.append(path)

    def discover_plugins(self):
        """Scan plugin directories and register all found plugins"""
        # 1. Load built-in plugins
        builtin_dir = Path(__file__).parent / "builtin"
        self._scan_directory(builtin_dir)

        # 2. Load user plugins
        for plugin_dir in self._plugin_dirs:
            if plugin_dir.exists():
                self._scan_directory(plugin_dir)

    def _scan_directory(self, directory: Path):
        """Scan a directory for plugin modules"""
        for category_dir in directory.iterdir():
            if not category_dir.is_dir():
                continue
            for plugin_file in category_dir.glob("*_plugin.py"):
                self._load_plugin_file(plugin_file)

    def _load_plugin_file(self, filepath: Path):
        """Load a single plugin file"""
        try:
            spec = importlib.util.spec_from_file_location(
                filepath.stem, filepath
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes in module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                    and not attr.__name__.startswith("Base")
                ):
                    plugin_instance = attr()
                    meta = plugin_instance.get_meta()
                    self.registry.register(meta.plugin_type, meta.name, plugin_instance)
                    logger.info(f"Loaded plugin: {meta.display_name} ({meta.name})")

        except Exception as e:
            logger.error(f"Failed to load plugin {filepath}: {e}")

    def get_plugin(self, plugin_type: str, name: str) -> BasePlugin | None:
        """Get a specific plugin by type and name"""
        return self.registry.get(plugin_type, name)

    def get_active_plugin(self, plugin_type: str) -> BasePlugin | None:
        """Get the currently active/selected plugin for a type"""
        return self.registry.get_active(plugin_type)

    def list_plugins(self, plugin_type: str = None) -> list[PluginMeta]:
        """List all registered plugins, optionally filtered by type"""
        return self.registry.list(plugin_type)

    def enable_plugin(self, plugin_type: str, name: str):
        """Enable a plugin"""
        self.registry.enable(plugin_type, name)

    def disable_plugin(self, plugin_type: str, name: str):
        """Disable a plugin"""
        self.registry.disable(plugin_type, name)

    def set_active(self, plugin_type: str, name: str):
        """Set a plugin as the active one for its type"""
        self.registry.set_active(plugin_type, name)
```

### 5.4 Plugin Registry

```python
# app/plugins/registry.py

from app.plugins.base import BasePlugin, PluginMeta


class PluginRegistry:
    """Stores and retrieves plugin instances"""

    def __init__(self):
        # {plugin_type: {name: plugin_instance}}
        self._plugins: dict[str, dict[str, BasePlugin]] = {}
        # {plugin_type: name} — currently selected plugin per type
        self._active: dict[str, str] = {}
        # {plugin_type: {name: bool}} — enabled state
        self._enabled: dict[str, dict[str, bool]] = {}

    def register(self, plugin_type: str, name: str, plugin: BasePlugin):
        if plugin_type not in self._plugins:
            self._plugins[plugin_type] = {}
            self._enabled[plugin_type] = {}
        self._plugins[plugin_type][name] = plugin
        self._enabled[plugin_type][name] = True
        # First registered becomes active if none set
        if plugin_type not in self._active:
            self._active[plugin_type] = name

    def get(self, plugin_type: str, name: str) -> BasePlugin | None:
        return self._plugins.get(plugin_type, {}).get(name)

    def get_active(self, plugin_type: str) -> BasePlugin | None:
        name = self._active.get(plugin_type)
        if name:
            return self.get(plugin_type, name)
        return None

    def set_active(self, plugin_type: str, name: str):
        if name in self._plugins.get(plugin_type, {}):
            self._active[plugin_type] = name

    def enable(self, plugin_type: str, name: str):
        if plugin_type in self._enabled:
            self._enabled[plugin_type][name] = True

    def disable(self, plugin_type: str, name: str):
        if plugin_type in self._enabled:
            self._enabled[plugin_type][name] = False

    def list(self, plugin_type: str = None) -> list[dict]:
        results = []
        types = [plugin_type] if plugin_type else self._plugins.keys()
        for pt in types:
            for name, plugin in self._plugins.get(pt, {}).items():
                meta = plugin.get_meta()
                results.append({
                    **meta.model_dump(),
                    "enabled": self._enabled.get(pt, {}).get(name, True),
                    "active": self._active.get(pt) == name,
                    "available": plugin.is_available(),
                })
        return results
```

### 5.5 Example: Migrating OpenAI to Plugin

```python
# app/plugins/builtin/llm/openai_plugin.py

from openai import OpenAI
from app.plugins.base import LLMPlugin, PluginMeta
from app.config import config


class OpenAIPlugin(LLMPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="openai",
            display_name="OpenAI GPT",
            version="1.0.0",
            description="OpenAI GPT models (GPT-4o, GPT-4, GPT-3.5)",
            author="MoneyPrinterTurbo",
            plugin_type="llm",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "base_url": {"type": "string", "default": "https://api.openai.com/v1"},
                "model_name": {"type": "string", "default": "gpt-4o-mini"},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = config.app.get("openai_api_key", "")
        return bool(api_key and api_key.strip())

    async def generate_response(self, prompt: str, **kwargs) -> str:
        client = OpenAI(
            api_key=config.app.get("openai_api_key"),
            base_url=config.app.get("openai_base_url", "https://api.openai.com/v1"),
        )
        model = config.app.get("openai_model_name", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
```

### 5.6 Migration Strategy: Gradual Plugin Adoption

The existing `if/elif` chains in `llm.py`, `voice.py`, `material.py` work fine. We migrate gradually:

```
Phase 1a: Create plugin interfaces (ABC classes) + PluginManager + Registry
Phase 1b: Migrate 3 providers as proof-of-concept:
          - LLM: OpenAI, Ollama (most used)
          - TTS: Edge TTS (default)
          - Material: Pexels (default)
Phase 1c: Service layer uses PluginManager with fallback to old code
Phase 1d: Migrate remaining providers (can happen post-Phase 1)
```

Service integration (backward-compatible):

```python
# app/services/llm.py (modified)

from app.plugins.manager import plugin_manager

async def _generate_response(prompt: str) -> str:
    # Try plugin system first
    llm_plugin = plugin_manager.get_active_plugin("llm")
    if llm_plugin and llm_plugin.is_available():
        return await llm_plugin.generate_response(prompt)

    # Fallback to legacy code (existing if/elif chain)
    return await _legacy_generate_response(prompt)
```

---

## 6. Secure Configuration

### 6.1 Config Architecture

```
CURRENT (config.toml):
  All settings + API keys in one plain-text file
  ❌ API keys visible in plain text
  ❌ Single file for all environments

NEW:
  ┌─────────────────────────┐
  │  config.toml            │  App settings (non-sensitive)
  │  - video defaults       │  Stored in: app data directory
  │  - UI preferences       │  (OS-specific standard location)
  │  - plugin selection     │
  │  - language             │
  └────────────┬────────────┘
               │
  ┌────────────┴────────────┐
  │  OS Keychain            │  Sensitive data (API keys, license)
  │  (via Tauri commands)   │  Windows: Credential Manager
  │  - openai_api_key       │  macOS: Keychain
  │  - pexels_api_key       │  Linux: libsecret
  │  - license_key          │
  └─────────────────────────┘
```

### 6.2 Config Service (Python)

```python
# app/config/config_v2.py

import tomllib
import tomli_w
from pathlib import Path
from platformdirs import user_data_dir


APP_NAME = "MoneyPrinterTurbo"
APP_AUTHOR = "MoneyPrinterTurbo"


def get_config_dir() -> Path:
    """Get OS-appropriate config directory"""
    # Windows: C:\Users\<user>\AppData\Local\MoneyPrinterTurbo
    # macOS:   ~/Library/Application Support/MoneyPrinterTurbo
    # Linux:   ~/.local/share/MoneyPrinterTurbo
    config_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    return get_config_dir() / "config.toml"


class ConfigManager:
    """Manages application configuration with hot-reload"""

    def __init__(self):
        self._config: dict = {}
        self._config_path = get_config_path()
        self._load()

    def _load(self):
        if self._config_path.exists():
            with open(self._config_path, "rb") as f:
                self._config = tomllib.load(f)
        else:
            self._config = self._defaults()
            self._save()

    def _save(self):
        with open(self._config_path, "wb") as f:
            tomli_w.dump(self._config, f)

    def _defaults(self) -> dict:
        return {
            "app": {
                "language": "en-US",
                "video_source": "pexels",
                "llm_provider": "openai",
                "max_concurrent_tasks": 5,
            },
            "video": {
                "aspect": "16:9",
                "concat_mode": "random",
                "transition": "FadeIn",
                "clip_duration": 5,
                "threads": 2,
            },
            "audio": {
                "voice": "en-US-AriaNeural-Female",
                "voice_rate": 1.0,
                "voice_volume": 1.0,
                "bgm_volume": 0.2,
            },
            "subtitle": {
                "enabled": True,
                "position": "bottom",
                "font_size": 60,
            },
            "plugins": {
                "active": {
                    "llm": "openai",
                    "tts": "edge-tts",
                    "material": "pexels",
                }
            }
        }

    def get(self, section: str, key: str, default=None):
        return self._config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value):
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._save()

    def get_all(self) -> dict:
        return self._config.copy()

    def update(self, data: dict):
        """Deep merge update"""
        self._deep_merge(self._config, data)
        self._save()

    def migrate_from_legacy(self, legacy_path: Path):
        """Migrate from old config.toml format"""
        # Read old config, map to new structure, save
        ...

    @staticmethod
    def _deep_merge(base: dict, override: dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value
```

### 6.3 Keychain Integration (via Tauri IPC)

Secrets (API keys) are stored in the OS keychain, accessed via Tauri commands:

```rust
// src-tauri/src/commands.rs

use keyring::Entry;

#[tauri::command]
fn set_secret(service: &str, key: &str, value: &str) -> Result<(), String> {
    let entry = Entry::new(service, key).map_err(|e| e.to_string())?;
    entry.set_password(value).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn get_secret(service: &str, key: &str) -> Result<Option<String>, String> {
    let entry = Entry::new(service, key).map_err(|e| e.to_string())?;
    match entry.get_password() {
        Ok(password) => Ok(Some(password)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
fn delete_secret(service: &str, key: &str) -> Result<(), String> {
    let entry = Entry::new(service, key).map_err(|e| e.to_string())?;
    entry.delete_credential().map_err(|e| e.to_string());
    Ok(())
}
```

The React frontend calls these to manage API keys:

```typescript
// desktop/src/lib/secrets.ts
import { invoke } from "@tauri-apps/api/core";

const SERVICE = "MoneyPrinterTurbo";

export async function getSecret(key: string): Promise<string | null> {
  return invoke("get_secret", { service: SERVICE, key });
}

export async function setSecret(key: string, value: string): Promise<void> {
  return invoke("set_secret", { service: SERVICE, key, value });
}
```

The Python sidecar receives API keys from the frontend via a secure endpoint (localhost only):

```python
# New endpoint
@router.put("/api/v1/config/secrets")
async def update_secrets(secrets: dict[str, str]):
    """Frontend sends decrypted secrets to sidecar at startup"""
    for key, value in secrets.items():
        os.environ[f"MPT_{key.upper()}"] = value
    return {"status": "ok"}
```

### 6.4 Config Migration

```python
# app/config/migration.py

def migrate_v1_to_v2(legacy_config_path: Path) -> dict:
    """
    Migrate from old config.toml (flat with API keys)
    to new format (structured, no secrets)
    """
    with open(legacy_config_path, "rb") as f:
        old = tomllib.load(f)

    # Extract secrets (to be stored in keychain later)
    secrets = {}
    secret_keys = [
        "openai_api_key", "pexels_api_keys", "pixabay_api_keys",
        "azure_speech_key", "siliconflow_api_key",
        # ... all API keys
    ]
    for key in secret_keys:
        if key in old.get("app", {}):
            secrets[key] = old["app"][key]

    # Map to new structure
    new_config = { ... }

    return {"config": new_config, "secrets": secrets}
```

---

## 7. New API Endpoints (FastAPI)

Phase 1 adds these endpoints to the existing FastAPI backend:

### 7.1 Config Endpoints

```
GET    /api/v1/config              → Get all config (non-sensitive)
PUT    /api/v1/config              → Update config
PUT    /api/v1/config/secrets      → Receive secrets from frontend
POST   /api/v1/config/migrate      → Migrate from legacy config.toml
GET    /api/v1/config/defaults     → Get default values
```

### 7.2 Plugin Endpoints

```
GET    /api/v1/plugins             → List all plugins with status
GET    /api/v1/plugins/:type       → List plugins by type (llm, tts, etc.)
POST   /api/v1/plugins/:type/:name/enable    → Enable plugin
POST   /api/v1/plugins/:type/:name/disable   → Disable plugin
POST   /api/v1/plugins/:type/:name/activate  → Set as active for type
GET    /api/v1/plugins/:type/:name/config    → Get plugin config schema
PUT    /api/v1/plugins/:type/:name/config    → Update plugin config
```

### 7.3 System Endpoints

```
GET    /api/v1/ping                → Health check (existing)
GET    /api/v1/system/info         → System info (version, platform, resources)
GET    /api/v1/system/voices       → List all available TTS voices
GET    /api/v1/system/fonts        → List available fonts
GET    /api/v1/system/songs        → List available BGM songs
```

### 7.4 Task Endpoints (Enhanced)

```
POST   /api/v1/videos              → Create video (existing)
GET    /api/v1/tasks/:id           → Get task status (existing)
DELETE /api/v1/tasks/:id           → Delete task (existing)
GET    /api/v1/tasks               → List all tasks (NEW - pagination)
POST   /api/v1/tasks/:id/cancel    → Cancel running task (NEW)
```

---

## 8. Auto-Update System

### 8.1 Update Flow

```
App starts → Check for updates (background)
    │
    ├── No update → Continue normally
    │
    └── Update available
        │
        ├── Show notification: "v1.2.0 available — [Update Now] [Later]"
        │
        └── User clicks "Update Now"
            │
            ├── Download update (delta if possible)
            ├── Show progress bar
            ├── Verify signature
            ├── Install update
            └── Restart app
```

### 8.2 Tauri Updater Configuration

```json
// tauri.conf.json (relevant section)
{
  "plugins": {
    "updater": {
      "active": true,
      "dialog": false,
      "pubkey": "YOUR_PUBLIC_KEY_HERE",
      "endpoints": [
        "https://releases.moneyprinterturbo.com/{{target}}/{{arch}}/{{current_version}}"
      ]
    }
  }
}
```

### 8.3 Update Server

For Phase 1, use **GitHub Releases** as the update server with a simple JSON endpoint:

```
GitHub Release → contains:
  - MoneyPrinterTurbo_1.2.0_x64-setup.exe
  - MoneyPrinterTurbo_1.2.0_x64.dmg
  - MoneyPrinterTurbo_1.2.0_amd64.AppImage
  - latest.json (update manifest)
```

A Vercel serverless function proxies GitHub Releases to the Tauri updater format:

```json
// Response format for Tauri updater
{
  "version": "1.2.0",
  "notes": "Bug fixes and performance improvements",
  "pub_date": "2026-06-15T00:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "signature": "...",
      "url": "https://github.com/.../releases/download/v1.2.0/MoneyPrinterTurbo_1.2.0_x64-setup.nsis.zip"
    },
    "darwin-x86_64": { ... },
    "darwin-aarch64": { ... },
    "linux-x86_64": { ... }
  }
}
```

---

## 9. Build & Distribution

### 9.1 Build Pipeline

```
┌─ Step 1: Build Python Sidecar ──────────────────────────┐
│                                                          │
│  PyInstaller --onefile main.py                           │
│  Output: python-backend.exe (Windows)                    │
│          python-backend (macOS/Linux)                    │
│                                                          │
│  Includes: app/, moviepy, ffmpeg, whisper models, etc.  │
│  Size: ~150-250MB (Python + deps + FFmpeg ~80MB)         │
└──────────────────────────────────────────────────────────┘
                    │
┌─ Step 2: Build React Frontend ──────────────────────────┐
│                                                          │
│  cd desktop && npm run build                             │
│  Output: desktop/dist/ (static HTML/JS/CSS)              │
│  Size: ~2-5MB                                            │
└──────────────────────────────────────────────────────────┘
                    │
┌─ Step 3: Build Tauri App ────────────────────────────────┐
│                                                          │
│  cd desktop && npm run tauri build                        │
│  Bundles: React dist + Rust binary + Python sidecar      │
│                                                          │
│  Output:                                                 │
│  Windows: .exe installer (NSIS) + .msi                   │
│  macOS:   .dmg + .app bundle                             │
│  Linux:   .AppImage + .deb                               │
│                                                          │
│  Total installer size: ~160-270MB                        │
└──────────────────────────────────────────────────────────┘
```

### 9.2 Development Setup

```bash
# Terminal 1: Python backend (hot-reload)
cd MoneyPrinterTurbo-v2
python main.py --port 18080 --mode desktop

# Terminal 2: Tauri + React (hot-reload)
cd MoneyPrinterTurbo-v2/desktop
npm run tauri dev
```

### 9.3 Tauri Configuration

```json
// desktop/src-tauri/tauri.conf.json
{
  "productName": "MoneyPrinterTurbo",
  "version": "1.0.0",
  "identifier": "com.moneyprinterturbo.app",
  "build": {
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "MoneyPrinterTurbo",
        "width": 1280,
        "height": 800,
        "minWidth": 960,
        "minHeight": 600,
        "center": true,
        "decorations": true
      }
    ],
    "security": {
      "csp": "default-src 'self'; connect-src 'self' http://127.0.0.1:18080; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'"
    }
  },
  "bundle": {
    "active": true,
    "targets": ["nsis", "dmg", "appimage", "deb"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "externalBin": ["binaries/python-backend"]
  }
}
```

---

## 10. State Management: SQLite Migration

### 10.1 Why SQLite

Current in-memory state is lost on restart. SQLite provides:
- Persistent task history
- Project management (list past videos)
- Plugin state
- No external server needed

### 10.2 Schema

```sql
-- Tasks table (replaces in-memory state)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    state INTEGER DEFAULT 0,      -- -1=failed, 0=pending, 1=complete, 4=processing
    progress REAL DEFAULT 0,
    params TEXT,                   -- JSON: VideoParams
    result TEXT,                   -- JSON: {videos, script, terms, ...}
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table (user-facing concept)
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    task_id TEXT REFERENCES tasks(id),
    thumbnail TEXT,               -- Path to thumbnail image
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plugin state
CREATE TABLE plugin_state (
    plugin_type TEXT NOT NULL,
    plugin_name TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    config TEXT,                   -- JSON: plugin-specific config
    PRIMARY KEY (plugin_type, plugin_name)
);
```

### 10.3 State Service (New Implementation)

```python
# app/services/state.py (add SQLiteState)

import sqlite3
from app.services.state import BaseState

class SQLiteState(BaseState):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript(SCHEMA_SQL)
        conn.close()

    def update_task(self, task_id, state, progress=0, **kwargs):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO tasks (id, state, progress, result, updated_at) "
            "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (task_id, state, progress, json.dumps(kwargs))
        )
        conn.commit()
        conn.close()

    # ... implement other BaseState methods
```

---

## 11. Phase 1 Deliverables Checklist

| # | Deliverable | Priority | Est. Days |
|---|-------------|----------|-----------|
| 1 | Tauri v2 project scaffolding + React + Vite + Tailwind + shadcn | Must | 2 |
| 2 | Sidecar integration (spawn FastAPI, health check, lifecycle) | Must | 3 |
| 3 | App shell (sidebar, routing, layout, theme) | Must | 2 |
| 4 | Dashboard page (recent projects, quick stats) | Must | 1 |
| 5 | Create page (video creation wizard, 5 steps) | Must | 4 |
| 6 | Projects page (task list, status, video preview) | Must | 2 |
| 7 | Settings page (config management UI) | Must | 2 |
| 8 | Plugin interfaces (ABC classes) | Must | 1 |
| 9 | Plugin manager + registry | Must | 2 |
| 10 | Migrate 3 providers to plugins (OpenAI, EdgeTTS, Pexels) | Must | 3 |
| 11 | Service layer plugin integration (with legacy fallback) | Must | 2 |
| 12 | Config v2 (TOML in app data dir) | Must | 1 |
| 13 | Config migration (v1 → v2) | Should | 1 |
| 14 | Keychain integration (Rust commands) | Should | 2 |
| 15 | Secrets flow (frontend → sidecar) | Should | 1 |
| 16 | New API endpoints (config, plugins, system) | Must | 2 |
| 17 | SQLite state (replace in-memory) | Must | 2 |
| 18 | i18n setup (react-i18next, migrate JSON files) | Must | 1 |
| 19 | Auto-updater setup (Tauri plugin + update server) | Should | 2 |
| 20 | PyInstaller sidecar build script | Must | 2 |
| 21 | Tauri build pipeline (Windows/macOS/Linux) | Must | 3 |
| 22 | Plugins page UI (list, enable/disable, config) | Should | 2 |
| 23 | System tray (minimize to tray) | Nice | 1 |
| **TOTAL** | | | **~40 days** |

### Priority Legend
- **Must**: Required for Phase 1 release
- **Should**: Important but can ship without
- **Nice**: Quality of life, do if time permits

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python sidecar bundle too large | Poor download experience | Use PyInstaller one-file mode, exclude unused deps, consider Nuitka later |
| FFmpeg bundling cross-platform | Build complexity | Start with Windows only, add macOS/Linux incrementally |
| MoviePy compatibility in bundled Python | Pipeline breaks | Test early, pin exact versions, include all transitive deps |
| Tauri v2 breaking changes | Dev delays | Pin Tauri version, follow stable releases only |
| Plugin system over-engineering | Time waste | Start minimal (3 plugins), expand based on actual need |
| Config migration edge cases | User data loss | Keep legacy config.toml as backup, never delete original |

---

## 13. Out of Scope (Phase 1)

These are explicitly NOT in Phase 1:

- License system (Keygen.sh integration) → Phase 1.5 / Business infrastructure
- Nuitka compilation (code protection) → Phase 1.5
- Template system → Phase 3
- New transitions/effects → Phase 3
- Auto-publishing → Phase 4
- Voice cloning → Phase 5
- AI video generation → Phase 5
- New API providers (Claude, ElevenLabs, etc.) → Phase 2
- Mobile support → Future

---

## 14. Backward Compatibility (CLI/API Mode)

The existing `python main.py` and `webui/Main.py` workflows MUST continue working unchanged.

### 14.1 Mode Detection

```python
# app/config/config.py (modified)

import os

def get_mode() -> str:
    """Detect running mode"""
    return os.environ.get("MPT_MODE", "api")  # "api" | "desktop"

def is_desktop_mode() -> bool:
    return get_mode() == "desktop"
```

### 14.2 Config System Selection by Mode

```
API/CLI mode (default):
  → Config: reads config.toml from project root (EXISTING behavior, unchanged)
  → State:  MemoryState or RedisState (EXISTING behavior, unchanged)
  → Secrets: read from config.toml plain text (EXISTING behavior)
  → Port: 8080 (existing default)

Desktop mode (--mode desktop):
  → Config: reads config.toml from OS app data dir (new ConfigManager)
  → State:  SQLiteState (persistent)
  → Secrets: received from frontend via /api/v1/config/secrets
  → Port: 18080 (avoids conflict with API mode)
```

```python
# app/services/state.py (modified)

def create_state():
    if is_desktop_mode():
        db_path = get_config_dir() / "moneyprinterturbo.db"
        return SQLiteState(str(db_path))
    elif config.app.get("enable_redis"):
        return RedisState(...)
    else:
        return MemoryState()

state = create_state()
```

### 14.3 Config Fallback for Secrets

```python
# app/config/config.py (modified)

def get_api_key(key_name: str) -> str:
    """Get API key with fallback chain:
    1. Environment variable (set by desktop frontend via secrets endpoint)
    2. config.toml value (existing behavior for CLI/API mode)
    """
    env_key = f"MPT_{key_name.upper()}"
    env_val = os.environ.get(env_key, "")
    if env_val:
        return env_val

    # Fallback to config.toml (existing behavior)
    return config.app.get(key_name, "")
```

All service code (`llm.py`, `voice.py`, `material.py`) will be updated to use `get_api_key()` instead of `config.app.get()` for API keys. This is backward-compatible: in API mode, env vars are empty, so it falls back to config.toml.

### 14.4 Secrets Endpoint Security

```python
# Only allow whitelisted secret keys
ALLOWED_SECRET_KEYS = {
    "openai_api_key", "openai_base_url",
    "pexels_api_keys", "pixabay_api_keys",
    "azure_speech_key", "azure_speech_region",
    "siliconflow_api_key",
    "moonshot_api_key", "deepseek_api_key",
    "gemini_api_key", "qwen_api_key",
    # ... all known API key fields
}

@router.put("/api/v1/config/secrets")
async def update_secrets(secrets: dict[str, str]):
    """Desktop frontend sends decrypted secrets at startup. Localhost only."""
    for key, value in secrets.items():
        if key not in ALLOWED_SECRET_KEYS:
            raise HTTPException(400, f"Unknown secret key: {key}")
        os.environ[f"MPT_{key.upper()}"] = value
    return {"status": "ok"}
```

---

## 15. Async/Sync Bridge for Plugins

### 15.1 Problem

The existing service layer is **synchronous** (task.py calls llm.generate_script synchronously in a thread). Plugin interfaces use **async** for future-proofing (network I/O benefits from async). We need a bridge.

### 15.2 Solution: Sync Wrapper

```python
# app/plugins/utils.py

import asyncio
from functools import wraps


def run_async(coro):
    """Run an async function from sync context (used in service layer)"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Already in async context (e.g., FastAPI endpoint)
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        # No event loop running (e.g., thread in task manager)
        return asyncio.run(coro)
```

### 15.3 Service Integration

```python
# app/services/llm.py (modified)

from app.plugins.utils import run_async

def _generate_response(prompt: str) -> str:
    """Sync function called by task.py"""
    llm_plugin = plugin_manager.get_active_plugin("llm")
    if llm_plugin and llm_plugin.is_available():
        # Bridge async plugin to sync caller
        return run_async(llm_plugin.generate_response(prompt))

    # Fallback to legacy code
    return _legacy_generate_response(prompt)
```

This keeps the service layer synchronous (no changes to task.py or the threading model) while allowing plugins to be async internally.

---

## 16. SQLite Thread Safety

### 16.1 Connection Pool

```python
# app/services/state.py

import sqlite3
import threading


class SQLiteState(BaseState):
    """Thread-safe SQLite state using thread-local connections"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local connection"""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )
            self._local.conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript(SCHEMA_SQL)
        conn.close()

    def update_task(self, task_id, state, progress=0, **kwargs):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO tasks (id, state, progress, result, updated_at) "
            "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(id) DO UPDATE SET state=?, progress=?, result=?, updated_at=CURRENT_TIMESTAMP",
            (task_id, state, progress, json.dumps(kwargs), state, progress, json.dumps(kwargs))
        )
        conn.commit()
```

---

## 17. Logging & Error Surfacing

### 17.1 Sidecar Log Capture

Tauri captures sidecar stdout/stderr via the shell plugin:

```rust
// src-tauri/src/sidecar.rs

let (mut rx, child) = sidecar.spawn().expect("failed to spawn");

// Forward sidecar output to frontend via events
tauri::async_runtime::spawn(async move {
    while let Some(event) = rx.recv().await {
        match event {
            CommandEvent::Stdout(line) => {
                app_handle.emit("sidecar-log", &line).ok();
            }
            CommandEvent::Stderr(line) => {
                app_handle.emit("sidecar-error", &line).ok();
            }
            _ => {}
        }
    }
});
```

### 17.2 Frontend Log Panel

```typescript
// desktop/src/hooks/useSidecarLogs.ts

import { listen } from "@tauri-apps/api/event";
import { useState, useEffect } from "react";

export function useSidecarLogs(maxLines = 500) {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const unlisten = listen<string>("sidecar-log", (event) => {
      setLogs(prev => [...prev.slice(-maxLines), event.payload]);
    });
    return () => { unlisten.then(fn => fn()); };
  }, []);

  return logs;
}
```

A collapsible log panel at the bottom of the Create page shows real-time pipeline progress. Users can toggle it via Settings (similar to existing `hide_log` setting).

---

## 18. Process Safety

### 18.1 Single Instance Enforcement

```rust
// src-tauri/src/lib.rs

fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            // Focus existing window if user tries to open second instance
            if let Some(window) = app.get_webview_window("main") {
                window.set_focus().ok();
            }
        }))
        // ... rest of setup
}
```

### 18.2 Port Conflict Handling

```rust
// src-tauri/src/sidecar.rs

fn find_available_port(preferred: u16) -> u16 {
    // Try preferred port first
    if std::net::TcpListener::bind(("127.0.0.1", preferred)).is_ok() {
        return preferred;
    }
    // Find next available port
    for port in (preferred + 1)..=(preferred + 100) {
        if std::net::TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    panic!("No available port found in range {}-{}", preferred, preferred + 100);
}
```

### 18.3 Orphaned Process Cleanup

```python
# main.py (desktop mode)

import os, signal, threading

def watchdog(parent_pid: int):
    """Kill self if parent (Tauri) process dies"""
    import psutil
    while True:
        if not psutil.pid_exists(parent_pid):
            logger.warning("Parent process died, shutting down sidecar")
            os.kill(os.getpid(), signal.SIGTERM)
            break
        threading.Event().wait(5)  # Check every 5 seconds

if args.mode == "desktop" and args.parent_pid:
    threading.Thread(target=watchdog, args=(args.parent_pid,), daemon=True).start()
```

Tauri passes its PID when launching the sidecar:
```rust
.args(["--port", &port.to_string(), "--mode", "desktop", "--parent-pid", &std::process::id().to_string()])
```

---

## 19. Testing Strategy

### 19.1 Test Scope for Phase 1

| Area | Test Type | Tool |
|------|-----------|------|
| Plugin manager/registry | Unit tests | pytest |
| SQLiteState parity with MemoryState | Integration tests | pytest |
| Config migration v1 → v2 | Unit tests | pytest |
| API endpoints (new) | Integration tests | pytest + httpx |
| Sidecar lifecycle | Manual + E2E | Tauri test driver |
| React components | Unit tests | Vitest + React Testing Library |
| Full pipeline (desktop mode) | E2E smoke test | Manual checklist |

### 19.2 Key Test Cases

**Plugin system:**
- Register/discover/enable/disable plugins
- Active plugin selection
- Legacy fallback when no plugin available
- Plugin with missing dependencies reports unavailable

**SQLiteState:**
- All BaseState methods produce identical results to MemoryState
- Concurrent writes from multiple threads
- Data persists across process restarts

**Config migration:**
- Standard config.toml migrates correctly
- Empty/missing fields use defaults
- API keys extracted to secrets dict
- Array values (pexels_api_keys) handled correctly
- Original config.toml preserved as backup

---

## 20. Config Migration Mapping

### 20.1 Full Key Mapping (v1 → v2)

```python
MIGRATION_MAP = {
    # [app] section
    "app.video_source":         ("app", "video_source"),
    "app.llm_provider":         ("plugins.active", "llm"),
    "app.max_concurrent_tasks": ("app", "max_concurrent_tasks"),

    # Video defaults
    "app.video_aspect":         ("video", "aspect"),
    "app.video_concat_mode":    ("video", "concat_mode"),
    "app.video_transition_mode":("video", "transition"),
    "app.video_clip_duration":  ("video", "clip_duration"),

    # [ui] section
    "ui.language":              ("app", "language"),
    "ui.hide_log":              ("app", "hide_log"),

    # [whisper] section
    "whisper.model_size":       ("whisper", "model_size"),
    "whisper.device":           ("whisper", "device"),
    "whisper.compute_type":     ("whisper", "compute_type"),
}

# These keys are SECRETS — extracted to keychain, NOT written to new config.toml
SECRET_KEYS = [
    "app.openai_api_key",
    "app.openai_base_url",
    "app.pexels_api_keys",      # array → join with comma or store first
    "app.pixabay_api_keys",     # array
    "app.moonshot_api_key",
    "app.ollama_api_key",
    "app.deepseek_api_key",
    "app.qwen_api_key",
    "app.gemini_api_key",
    "app.cloudflare_api_key",
    "app.ernie_api_key",
    "azure.speech_key",
    "azure.speech_region",
    "siliconflow.api_key",
]
```

### 20.2 Migration Process

```
1. Read old config.toml from project root
2. Create backup: config.toml.bak
3. Map settings to new structure using MIGRATION_MAP
4. Extract SECRET_KEYS → return separately (frontend stores in keychain)
5. Write new config.toml to app data dir
6. Log migration summary: X settings migrated, Y secrets extracted
7. NEVER delete original config.toml (CLI/API mode still uses it)
```

---

## 21. Revised Timeline (with buffer)

| # | Deliverable | Priority | Est. Days |
|---|-------------|----------|-----------|
| 1 | Tauri v2 scaffolding + React + Vite + Tailwind + shadcn | Must | 2 |
| 2 | Sidecar integration (spawn, health check, lifecycle, watchdog) | Must | 4 |
| 3 | Single-instance + port conflict handling | Must | 1 |
| 4 | App shell (sidebar, routing, layout, theme, log panel) | Must | 3 |
| 5 | Create page (video creation wizard, 5 steps + local materials) | Must | 5 |
| 6 | Dashboard page (recent projects, quick stats) | Must | 1 |
| 7 | Projects page (task list, status, video preview) | Must | 2 |
| 8 | Settings page (config management + API keys UI) | Must | 2 |
| 9 | Plugin interfaces (ABC classes) + async/sync bridge | Must | 2 |
| 10 | Plugin manager + registry | Must | 2 |
| 11 | Migrate 3 providers to plugins (OpenAI, EdgeTTS, Pexels) | Must | 3 |
| 12 | Service layer plugin integration (with legacy fallback) | Must | 2 |
| 13 | Config v2 (TOML in app data dir, mode detection) | Must | 2 |
| 14 | Config migration (v1 → v2, full mapping) | Must | 2 |
| 15 | Keychain integration (Rust commands) + secrets flow | Should | 2 |
| 16 | New API endpoints (config, plugins, system) | Must | 2 |
| 17 | SQLite state (thread-safe, replace in-memory) | Must | 3 |
| 18 | i18n setup (react-i18next, migrate JSON files) | Must | 1 |
| 19 | TypeScript types (full mirror of Pydantic models) | Must | 1 |
| 20 | PyInstaller sidecar build script | Must | 3 |
| 21 | Tauri build pipeline (Windows first, then macOS/Linux) | Must | 4 |
| 22 | Testing (plugins, SQLite, config migration, smoke) | Must | 3 |
| 23 | Auto-updater setup (Tauri plugin + GitHub Releases) | Should | 2 |
| 24 | Plugins page UI (list, enable/disable, config) | Should | 2 |
| 25 | System tray (minimize to tray) | Nice | 1 |
| | **Buffer (unexpected issues, build debugging)** | | **4** |
| **TOTAL** | | | **~54 days** |

### Critical Path

```
Scaffolding (1-2) → Sidecar (2-3) → App Shell (4) → Create Page (5)
                                                           ↓
                                          Plugin System (9-12) → Config (13-15)
                                                           ↓
                                          SQLite (17) → API Endpoints (16)
                                                           ↓
                                          Build Pipeline (20-21) → Testing (22)
```

Items 23-25 (auto-updater, plugins UI, system tray) can be deferred to Phase 1.5 if timeline is tight.
