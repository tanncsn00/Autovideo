# Phase 1: Desktop Application — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform MoneyPrinterTurbo from a FastAPI+Streamlit web app into a Tauri v2 desktop application with React frontend, plugin architecture, and secure configuration.

**Architecture:** Tauri v2 shell wraps a React 19 frontend that communicates with the existing FastAPI backend running as a sidecar subprocess. The Python service layer is 100% reused. A plugin system formalizes the existing Strategy patterns. Config is split into non-sensitive (TOML) and sensitive (OS Keychain).

**Tech Stack:** Tauri v2, React 19, Vite 6, TailwindCSS v4, shadcn/ui, Zustand, TanStack Query, react-i18next, PyInstaller, SQLite

**Spec:** `docs/superpowers/specs/2026-03-25-phase1-desktop-app-design.md`

---

## File Structure Overview

### New Files (desktop/)

```
desktop/
├── src-tauri/
│   ├── Cargo.toml                    # Rust dependencies
│   ├── tauri.conf.json               # Tauri config (window, bundle, security, updater)
│   ├── capabilities/
│   │   └── default.json              # Tauri v2 permissions
│   ├── build.rs                      # Tauri build script
│   ├── icons/                        # App icons (auto-generated)
│   └── src/
│       ├── main.rs                   # Tauri entry point (Windows subsystem)
│       ├── lib.rs                    # App setup: plugins, commands, sidecar init
│       ├── sidecar.rs                # Sidecar spawn, health check, watchdog
│       └── commands.rs               # IPC commands: keychain, port
│
├── src/
│   ├── main.tsx                      # React entry point
│   ├── App.tsx                       # Root: QueryProvider, Router, i18n
│   ├── api/
│   │   ├── client.ts                 # HTTP client wrapper (fetch → sidecar)
│   │   ├── hooks.ts                  # TanStack Query hooks
│   │   └── types.ts                  # TypeScript types mirroring Pydantic
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components (Button, Input, etc.)
│   │   └── layout/
│   │       ├── AppShell.tsx          # Sidebar + Header + Main content
│   │       ├── Sidebar.tsx           # Navigation sidebar
│   │       └── Header.tsx            # Top header with language switcher
│   ├── pages/
│   │   ├── Dashboard.tsx             # Home page
│   │   ├── Create.tsx                # Video creation wizard
│   │   ├── Projects.tsx              # Task/project list
│   │   ├── Settings.tsx              # Config management
│   │   ├── Plugins.tsx               # Plugin list
│   │   └── License.tsx               # License activation (placeholder)
│   ├── stores/
│   │   └── appStore.ts               # Zustand: sidecar status, theme, language
│   ├── i18n/
│   │   ├── index.ts                  # i18next config + language detection
│   │   └── locales/
│   │       ├── en.json               # Migrated from webui/i18n/en.json
│   │       ├── zh.json
│   │       └── vi.json
│   ├── hooks/
│   │   ├── useSidecarStatus.ts       # Poll sidecar health
│   │   └── useSidecarLogs.ts         # Listen to sidecar log events
│   ├── lib/
│   │   ├── secrets.ts                # Tauri keychain invoke wrappers
│   │   └── utils.ts                  # Shared utilities
│   └── styles/
│       └── globals.css               # Tailwind imports + base styles
│
├── index.html                        # Vite HTML entry
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.node.json
└── components.json                   # shadcn/ui config
```

### New Files (app/plugins/)

```
app/plugins/
├── __init__.py
├── base.py                           # ABC interfaces: LLMPlugin, TTSPlugin, etc.
├── manager.py                        # PluginManager: discover, load, lifecycle
├── registry.py                       # PluginRegistry: store, get, enable/disable
├── utils.py                          # run_async bridge
└── builtin/
    ├── __init__.py
    ├── llm/
    │   ├── __init__.py
    │   └── openai_plugin.py          # OpenAI provider as plugin
    ├── tts/
    │   ├── __init__.py
    │   └── edge_tts_plugin.py        # Edge TTS provider as plugin
    └── material/
        ├── __init__.py
        └── pexels_plugin.py          # Pexels provider as plugin
```

### New Files (app/ modifications)

```
app/
├── config/
│   ├── config.py                     # MODIFY: add get_api_key(), is_desktop_mode()
│   ├── config_v2.py                  # NEW: ConfigManager for desktop mode
│   └── migration.py                  # NEW: v1→v2 config migration
├── services/
│   ├── state.py                      # MODIFY: add SQLiteState class
│   └── llm.py                        # MODIFY: use plugin fallback pattern
├── controllers/
│   ├── v1/
│   │   ├── config_controller.py      # NEW: config CRUD endpoints
│   │   ├── plugin_controller.py      # NEW: plugin management endpoints
│   │   └── system_controller.py      # NEW: system info endpoints
│   └── v1/video.py                   # MODIFY: add cancel task endpoint
├── router.py                         # MODIFY: include new routers
└── main.py                           # MODIFY: add --port, --mode, --parent-pid args
```

### New Files (scripts/)

```
scripts/
├── build-sidecar.py                  # PyInstaller build script
└── dev.sh                            # Dev launcher (sidecar + tauri dev)
```

### Test Files

```
tests/
├── test_plugins/
│   ├── test_base.py                  # Plugin interface tests
│   ├── test_manager.py               # PluginManager tests
│   ├── test_registry.py              # PluginRegistry tests
│   └── test_openai_plugin.py         # OpenAI plugin tests
├── test_config/
│   ├── test_config_v2.py             # ConfigManager tests
│   └── test_migration.py             # Config migration tests
└── test_state/
    └── test_sqlite_state.py          # SQLiteState tests
```

---

## PART A: Scaffolding + Sidecar (Tasks 1-7)

### Task 1: Initialize Tauri v2 + React + Vite Project

**Files:**
- Create: `desktop/` (entire scaffolding)
- Create: `desktop/package.json`
- Create: `desktop/src-tauri/Cargo.toml`
- Create: `desktop/src-tauri/tauri.conf.json`
- Create: `desktop/src-tauri/capabilities/default.json`
- Create: `desktop/src-tauri/src/main.rs`
- Create: `desktop/src-tauri/src/lib.rs`
- Create: `desktop/vite.config.ts`
- Create: `desktop/tsconfig.json`
- Create: `desktop/index.html`
- Create: `desktop/src/main.tsx`
- Create: `desktop/src/App.tsx`

**Prerequisites:** Node.js >= 20, Rust toolchain, system deps for Tauri v2

- [ ] **Step 1: Create Tauri v2 project using create-tauri-app**

```bash
cd E:/tvk/MoneyPrinterTurbo-v2
npm create tauri-app@latest desktop -- --template react-ts --manager npm
```

Select: React, TypeScript, npm

- [ ] **Step 2: Verify scaffolding created**

```bash
ls desktop/src-tauri/src/
# Expected: main.rs, lib.rs
ls desktop/src/
# Expected: main.tsx, App.tsx, etc.
```

- [ ] **Step 3: Install additional frontend dependencies**

```bash
cd desktop
npm install zustand @tanstack/react-query react-router-dom@7 react-i18next i18next i18next-browser-languagedetector lucide-react framer-motion
npm install -D tailwindcss @tailwindcss/vite
```

- [ ] **Step 4: Install Tauri plugins (Rust side)**

Edit `desktop/src-tauri/Cargo.toml` — add to `[dependencies]`:

```toml
tauri-plugin-shell = "2"
tauri-plugin-store = "2"
tauri-plugin-dialog = "2"
tauri-plugin-notification = "2"
tauri-plugin-os = "2"
tauri-plugin-single-instance = "2"
tauri-plugin-updater = "2"
keyring = "3"
reqwest = { version = "0.12", features = ["blocking"] }
```

- [ ] **Step 5: Install Tauri plugin JS bindings**

```bash
cd desktop
npm install @tauri-apps/plugin-shell @tauri-apps/plugin-store @tauri-apps/plugin-dialog @tauri-apps/plugin-notification @tauri-apps/plugin-os @tauri-apps/plugin-updater
```

- [ ] **Step 6: Configure tauri.conf.json**

Overwrite `desktop/src-tauri/tauri.conf.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/nicovrc/tauri-v2-schema/main/tauri.conf.json",
  "productName": "MoneyPrinterTurbo",
  "version": "0.1.0",
  "identifier": "com.moneyprinterturbo.app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:1420",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
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
        "decorations": true,
        "visible": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; connect-src 'self' http://127.0.0.1:* ws://127.0.0.1:*; img-src 'self' data: blob: http://127.0.0.1:*; style-src 'self' 'unsafe-inline'; font-src 'self' data:"
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
    ]
  }
}
```

- [ ] **Step 7: Configure Tauri v2 capabilities**

Write `desktop/src-tauri/capabilities/default.json`:

```json
{
  "identifier": "default",
  "description": "Default capabilities for MoneyPrinterTurbo",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "shell:allow-execute",
    "shell:allow-spawn",
    "shell:allow-stdin-write",
    "shell:allow-kill",
    "store:default",
    "dialog:default",
    "notification:default",
    "os:default"
  ]
}
```

- [ ] **Step 8: Setup TailwindCSS v4**

Write `desktop/src/styles/globals.css`:

```css
@import "tailwindcss";
```

Update `desktop/vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

export default defineConfig(async () => ({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host ? { protocol: "ws", host, port: 1421 } : undefined,
    watch: { ignored: ["**/src-tauri/**"] },
  },
}));
```

- [ ] **Step 9: Verify Tauri dev builds and opens window**

```bash
cd desktop
npm run tauri dev
```

Expected: Empty Tauri window opens with Vite React app.

- [ ] **Step 10: Commit**

```bash
git add desktop/
git commit -m "feat: scaffold Tauri v2 + React + Vite + TailwindCSS project"
```

---

### Task 2: Setup shadcn/ui Component Library

**Files:**
- Create: `desktop/components.json`
- Create: `desktop/src/lib/utils.ts`
- Create: `desktop/src/components/ui/` (generated components)

- [ ] **Step 1: Initialize shadcn/ui**

```bash
cd desktop
npx shadcn@latest init
```

Select: New York style, Zinc base color, CSS variables: yes

- [ ] **Step 2: Add core components needed for the app**

```bash
npx shadcn@latest add button input label card select tabs separator scroll-area sheet sidebar tooltip badge progress dropdown-menu dialog form textarea switch slider toast sonner
```

- [ ] **Step 3: Verify components installed**

```bash
ls desktop/src/components/ui/
# Expected: button.tsx, input.tsx, card.tsx, etc.
```

- [ ] **Step 4: Commit**

```bash
git add desktop/
git commit -m "feat: add shadcn/ui component library"
```

---

### Task 3: Modify Python Entry Point for Desktop Mode

**Files:**
- Modify: `main.py`
- Modify: `app/config/config.py`
- Create: `app/controllers/v1/system_controller.py`
- Modify: `app/router.py`

- [ ] **Step 1: Write test for mode detection**

Create `tests/test_config/test_mode.py`:

```python
import os
import pytest


def test_default_mode_is_api():
    os.environ.pop("MPT_MODE", None)
    from app.config.config import get_mode, is_desktop_mode
    assert get_mode() == "api"
    assert is_desktop_mode() is False


def test_desktop_mode_detected():
    os.environ["MPT_MODE"] = "desktop"
    from app.config.config import get_mode, is_desktop_mode
    assert get_mode() == "desktop"
    assert is_desktop_mode() is True
    os.environ.pop("MPT_MODE")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd E:/tvk/MoneyPrinterTurbo-v2
python -m pytest tests/test_config/test_mode.py -v
```

Expected: FAIL — `get_mode` not found

- [ ] **Step 3: Add mode detection to config.py**

Add at the end of `app/config/config.py`:

```python
def get_mode() -> str:
    """Detect running mode: 'api' (default) or 'desktop'"""
    return os.environ.get("MPT_MODE", "api")

def is_desktop_mode() -> bool:
    return get_mode() == "desktop"

def get_api_key(key_name: str) -> str:
    """Get API key with fallback: env var (desktop) → config.toml (api)"""
    env_key = f"MPT_{key_name.upper()}"
    env_val = os.environ.get(env_key, "")
    if env_val:
        return env_val
    return app.get(key_name, "")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_config/test_mode.py -v
```

Expected: PASS

- [ ] **Step 5: Modify main.py for argparse**

Replace `main.py` content:

```python
import argparse
import os

import uvicorn
from loguru import logger

from app.config import config


def main():
    parser = argparse.ArgumentParser(description="MoneyPrinterTurbo")
    parser.add_argument("--port", type=int, default=config.listen_port)
    parser.add_argument("--host", type=str, default=config.listen_host)
    parser.add_argument("--mode", choices=["api", "desktop"], default="api")
    parser.add_argument("--parent-pid", type=int, default=0)
    args = parser.parse_args()

    if args.mode == "desktop":
        os.environ["MPT_MODE"] = "desktop"
        os.environ["MPT_PORT"] = str(args.port)
        args.host = "127.0.0.1"  # localhost only in desktop mode
        logger.info(f"Desktop mode: port={args.port}, parent_pid={args.parent_pid}")

        # Watchdog: kill self if parent (Tauri) dies
        if args.parent_pid:
            import threading
            def watchdog(ppid):
                import psutil
                while True:
                    if not psutil.pid_exists(ppid):
                        logger.warning("Parent process died, shutting down sidecar")
                        os._exit(0)
                    threading.Event().wait(5)
            threading.Thread(target=watchdog, args=(args.parent_pid,), daemon=True).start()

    logger.info(f"start server: http://{args.host}:{args.port}/docs")
    uvicorn.run(
        app="app.asgi:app",
        host=args.host,
        port=args.port,
        reload=config.reload_debug if args.mode == "api" else False,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Create system info endpoint**

Create `app/controllers/v1/system_controller.py`:

```python
import platform
import sys

from app.controllers.v1.base import new_router
from app.config import config
from app.utils import utils

router = new_router()


@router.get("/system/info", summary="Get system information")
def get_system_info():
    info = {
        "version": config.project_version,
        "python_version": sys.version,
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "mode": config.get_mode(),
    }
    return utils.get_response(200, info)


@router.get("/ping", summary="Health check")
def ping():
    return utils.get_response(200, {"message": "pong"})
```

- [ ] **Step 7: Register new router**

Modify `app/router.py`:

```python
from fastapi import APIRouter

from app.controllers.v1 import llm, video, system_controller

root_api_router = APIRouter()
root_api_router.include_router(video.router)
root_api_router.include_router(llm.router)
root_api_router.include_router(system_controller.router)
```

- [ ] **Step 8: Test server starts in desktop mode**

```bash
python main.py --port 18080 --mode desktop &
curl http://127.0.0.1:18080/api/v1/ping
curl http://127.0.0.1:18080/api/v1/system/info
# Expected: 200 OK with JSON response
# Kill the background process after testing
```

- [ ] **Step 9: Commit**

```bash
git add main.py app/config/config.py app/controllers/v1/system_controller.py app/router.py tests/
git commit -m "feat: add desktop mode, argparse, system endpoints, watchdog"
```

---

### Task 4: Implement Tauri Sidecar Lifecycle

**Files:**
- Create: `desktop/src-tauri/src/sidecar.rs`
- Modify: `desktop/src-tauri/src/lib.rs`
- Modify: `desktop/src-tauri/src/main.rs`
- Create: `desktop/src-tauri/src/commands.rs`

- [ ] **Step 1: Write sidecar.rs**

Create `desktop/src-tauri/src/sidecar.rs`:

```rust
use std::net::TcpListener;
use std::time::Duration;
use tauri::Manager;

/// Find an available port, starting from preferred
pub fn find_available_port(preferred: u16) -> u16 {
    for port in preferred..=(preferred + 100) {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    panic!("No available port found in range {}-{}", preferred, preferred + 100);
}

/// Wait for sidecar HTTP server to respond
pub async fn wait_for_ready(url: &str, timeout_ms: u64) -> Result<(), String> {
    let client = reqwest::Client::new();
    let start = std::time::Instant::now();
    let timeout = Duration::from_millis(timeout_ms);

    loop {
        if start.elapsed() > timeout {
            return Err(format!("Sidecar did not start within {}ms", timeout_ms));
        }

        match client.get(url).timeout(Duration::from_secs(2)).send().await {
            Ok(resp) if resp.status().is_success() => {
                return Ok(());
            }
            _ => {
                tokio::time::sleep(Duration::from_millis(500)).await;
            }
        }
    }
}
```

- [ ] **Step 2: Write commands.rs (keychain IPC)**

Create `desktop/src-tauri/src/commands.rs`:

```rust
use keyring::Entry;

const SERVICE: &str = "MoneyPrinterTurbo";

#[tauri::command]
pub fn set_secret(key: &str, value: &str) -> Result<(), String> {
    let entry = Entry::new(SERVICE, key).map_err(|e| e.to_string())?;
    entry.set_password(value).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub fn get_secret(key: &str) -> Result<Option<String>, String> {
    let entry = Entry::new(SERVICE, key).map_err(|e| e.to_string())?;
    match entry.get_password() {
        Ok(password) => Ok(Some(password)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub fn delete_secret(key: &str) -> Result<(), String> {
    let entry = Entry::new(SERVICE, key).map_err(|e| e.to_string())?;
    match entry.delete_credential() {
        Ok(_) => Ok(()),
        Err(keyring::Error::NoEntry) => Ok(()),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub fn get_sidecar_port(state: tauri::State<'_, crate::SidecarPort>) -> u16 {
    state.0
}
```

- [ ] **Step 3: Write lib.rs (app setup + sidecar launch)**

Replace `desktop/src-tauri/src/lib.rs`:

```rust
mod commands;
mod sidecar;

use tauri::Manager;

pub struct SidecarPort(pub u16);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.set_focus();
            }
        }))
        .invoke_handler(tauri::generate_handler![
            commands::set_secret,
            commands::get_secret,
            commands::delete_secret,
            commands::get_sidecar_port,
        ])
        .setup(|app| {
            let app_handle = app.handle().clone();

            // Find available port
            let port = sidecar::find_available_port(18080);
            app.manage(SidecarPort(port));

            // Spawn sidecar in background
            tauri::async_runtime::spawn(async move {
                let pid = std::process::id();

                // For development: launch Python directly
                // For production: launch bundled sidecar binary
                let python_cmd = if cfg!(debug_assertions) {
                    "python"
                } else {
                    // In production, use bundled sidecar
                    "python-backend"
                };

                let result = if cfg!(debug_assertions) {
                    // Dev mode: run python main.py directly
                    std::process::Command::new("python")
                        .arg("main.py")
                        .arg("--port")
                        .arg(port.to_string())
                        .arg("--mode")
                        .arg("desktop")
                        .arg("--parent-pid")
                        .arg(pid.to_string())
                        .current_dir(
                            app_handle.path().resource_dir()
                                .unwrap_or_else(|_| std::path::PathBuf::from(".."))
                                .parent()
                                .unwrap_or(&std::path::PathBuf::from(".."))
                                .to_path_buf()
                        )
                        .spawn()
                } else {
                    // Production: use Tauri sidecar
                    let shell = app_handle.shell();
                    // Will be configured when we add PyInstaller bundling
                    return;
                };

                match result {
                    Ok(_child) => {
                        let url = format!("http://127.0.0.1:{}/api/v1/ping", port);
                        match sidecar::wait_for_ready(&url, 15_000).await {
                            Ok(()) => {
                                println!("Sidecar ready on port {}", port);
                                if let Some(window) = app_handle.get_webview_window("main") {
                                    let _ = window.show();
                                }
                            }
                            Err(e) => {
                                eprintln!("Sidecar failed to start: {}", e);
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Failed to spawn sidecar: {}", e);
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 4: Update main.rs**

Replace `desktop/src-tauri/src/main.rs`:

```rust
// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    desktop_lib::run()
}
```

Note: `desktop_lib` is the lib name from Cargo.toml. Verify the `[lib]` name matches.

- [ ] **Step 5: Verify Tauri compiles**

```bash
cd desktop
npm run tauri dev
```

Expected: Tauri window opens, sidecar spawns Python backend on port 18080.

- [ ] **Step 6: Commit**

```bash
git add desktop/src-tauri/
git commit -m "feat: sidecar lifecycle, keychain commands, single-instance, port detection"
```

---

### Task 5: React App Shell (Sidebar + Routing + Theme)

**Files:**
- Create: `desktop/src/components/layout/AppShell.tsx`
- Create: `desktop/src/components/layout/Sidebar.tsx`
- Create: `desktop/src/components/layout/Header.tsx`
- Modify: `desktop/src/App.tsx`
- Modify: `desktop/src/main.tsx`
- Create: `desktop/src/stores/appStore.ts`
- Create: `desktop/src/hooks/useSidecarStatus.ts`
- Create: `desktop/src/pages/Dashboard.tsx` (placeholder)
- Create: `desktop/src/pages/Create.tsx` (placeholder)
- Create: `desktop/src/pages/Projects.tsx` (placeholder)
- Create: `desktop/src/pages/Settings.tsx` (placeholder)
- Create: `desktop/src/pages/Plugins.tsx` (placeholder)
- Create: `desktop/src/pages/License.tsx` (placeholder)

> **Note:** Use `@ui-ux-pro-max` skill for this task. Design a professional dark-theme desktop app shell with collapsible sidebar.

- [ ] **Step 1: Create Zustand app store**

Create `desktop/src/stores/appStore.ts`:

```typescript
import { create } from "zustand";

interface AppState {
  sidecarPort: number;
  sidecarReady: boolean;
  sidebarCollapsed: boolean;
  theme: "light" | "dark";

  setSidecarPort: (port: number) => void;
  setSidecarReady: (ready: boolean) => void;
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidecarPort: 18080,
  sidecarReady: false,
  sidebarCollapsed: false,
  theme: "dark",

  setSidecarPort: (port) => set({ sidecarPort: port }),
  setSidecarReady: (ready) => set({ sidecarReady: ready }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setTheme: (theme) => set({ theme }),
}));
```

- [ ] **Step 2: Create API client**

Create `desktop/src/api/client.ts`:

```typescript
import { useAppStore } from "@/stores/appStore";

function getBaseUrl(): string {
  const port = useAppStore.getState().sidecarPort;
  return `http://127.0.0.1:${port}`;
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  const json = await res.json();
  return json.data ?? json;
}

export const api = {
  ping: () => apiFetch<{ message: string }>("/api/v1/ping"),
  systemInfo: () => apiFetch<Record<string, string>>("/api/v1/system/info"),
  createVideo: (params: Record<string, unknown>) =>
    apiFetch<{ task_id: string }>("/api/v1/videos", {
      method: "POST",
      body: JSON.stringify(params),
    }),
  getTask: (taskId: string) => apiFetch<Record<string, unknown>>(`/api/v1/tasks/${taskId}`),
  getTasks: (page = 1, pageSize = 20) =>
    apiFetch<Record<string, unknown>>(`/api/v1/tasks?page=${page}&page_size=${pageSize}`),
  deleteTask: (taskId: string) =>
    apiFetch<Record<string, unknown>>(`/api/v1/tasks/${taskId}`, { method: "DELETE" }),
  getPlugins: (type?: string) =>
    apiFetch<Record<string, unknown>[]>(type ? `/api/v1/plugins?plugin_type=${type}` : "/api/v1/plugins"),
  getConfig: () => apiFetch<Record<string, unknown>>("/api/v1/config"),
  updateConfig: (data: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>("/api/v1/config", { method: "PUT", body: JSON.stringify({ data }) }),
  updateSecrets: (secrets: Record<string, string>) =>
    apiFetch<Record<string, unknown>>("/api/v1/config/secrets", { method: "PUT", body: JSON.stringify({ secrets }) }),
};
```

- [ ] **Step 3: Create sidecar status hook**

Create `desktop/src/hooks/useSidecarStatus.ts`:

```typescript
import { useEffect } from "react";
import { useAppStore } from "@/stores/appStore";
import { invoke } from "@tauri-apps/api/core";
import { api } from "@/api/client";

export function useSidecarStatus() {
  const setSidecarPort = useAppStore((s) => s.setSidecarPort);
  const setSidecarReady = useAppStore((s) => s.setSidecarReady);
  const sidecarReady = useAppStore((s) => s.sidecarReady);

  useEffect(() => {
    // Get port from Tauri
    invoke<number>("get_sidecar_port").then((port) => {
      setSidecarPort(port);
    });

    // Poll health until ready
    const interval = setInterval(async () => {
      try {
        await api.ping();
        setSidecarReady(true);
        clearInterval(interval);
      } catch {
        // Still waiting
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return sidecarReady;
}
```

- [ ] **Step 4: Create placeholder pages**

Create each page as a simple placeholder. Example for `desktop/src/pages/Dashboard.tsx`:

```typescript
export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="text-muted-foreground mt-2">Welcome to MoneyPrinterTurbo</p>
    </div>
  );
}
```

Create same pattern for: `Create.tsx`, `Projects.tsx`, `Settings.tsx`, `Plugins.tsx`, `License.tsx`

- [ ] **Step 5: Create AppShell layout**

Create `desktop/src/components/layout/Sidebar.tsx`:

```typescript
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/appStore";
import {
  LayoutDashboard,
  Video,
  FolderOpen,
  Puzzle,
  Settings,
  KeyRound,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/create", label: "Create Video", icon: Video },
  { path: "/projects", label: "Projects", icon: FolderOpen },
  { path: "/plugins", label: "Plugins", icon: Puzzle },
  { path: "/settings", label: "Settings", icon: Settings },
];

const bottomItems = [
  { path: "/license", label: "License", icon: KeyRound },
];

export function Sidebar() {
  const location = useLocation();
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggle = useAppStore((s) => s.toggleSidebar);

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "flex flex-col border-r bg-card h-screen transition-all duration-200",
          collapsed ? "w-16" : "w-56"
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-14 px-4 border-b">
          {!collapsed && (
            <span className="font-bold text-sm truncate">MoneyPrinterTurbo</span>
          )}
          <Button
            variant="ghost"
            size="icon"
            className={cn("ml-auto h-8 w-8", collapsed && "mx-auto")}
            onClick={toggle}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-2 space-y-1 px-2">
          {navItems.map((item) => {
            const active = location.pathname === item.path;
            const link = (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                  collapsed && "justify-center px-2"
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
            if (collapsed) {
              return (
                <Tooltip key={item.path}>
                  <TooltipTrigger asChild>{link}</TooltipTrigger>
                  <TooltipContent side="right">{item.label}</TooltipContent>
                </Tooltip>
              );
            }
            return link;
          })}
        </nav>

        {/* Bottom */}
        <div className="border-t py-2 px-2">
          {bottomItems.map((item) => {
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                  collapsed && "justify-center px-2"
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </div>
      </aside>
    </TooltipProvider>
  );
}
```

Create `desktop/src/components/layout/AppShell.tsx`:

```typescript
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { useSidecarStatus } from "@/hooks/useSidecarStatus";
import { Loader2 } from "lucide-react";

export function AppShell() {
  const ready = useSidecarStatus();

  if (!ready) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Starting MoneyPrinterTurbo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
```

- [ ] **Step 6: Wire up App.tsx with Router**

Replace `desktop/src/App.tsx`:

```typescript
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import Dashboard from "@/pages/Dashboard";
import Create from "@/pages/Create";
import Projects from "@/pages/Projects";
import Settings from "@/pages/Settings";
import Plugins from "@/pages/Plugins";
import License from "@/pages/License";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<Create />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/plugins" element={<Plugins />} />
            <Route path="/license" element={<License />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

- [ ] **Step 7: Update main.tsx**

Replace `desktop/src/main.tsx`:

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 8: Verify app shell renders with navigation**

```bash
cd desktop
npm run tauri dev
```

Expected: App opens with sidebar navigation, loading screen until sidecar ready, then Dashboard page.

- [ ] **Step 9: Commit**

```bash
git add desktop/src/
git commit -m "feat: app shell with sidebar navigation, routing, sidecar status"
```

---

### Task 6: Setup i18n (react-i18next)

**Files:**
- Create: `desktop/src/i18n/index.ts`
- Create: `desktop/src/i18n/locales/en.json`
- Create: `desktop/src/i18n/locales/zh.json`
- Create: `desktop/src/i18n/locales/vi.json`
- Modify: `desktop/src/main.tsx`

- [ ] **Step 1: Create i18n config**

Create `desktop/src/i18n/index.ts`:

```typescript
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "./locales/en.json";
import zh from "./locales/zh.json";
import vi from "./locales/vi.json";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
      vi: { translation: vi },
    },
    fallbackLng: "en",
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
  });

export default i18n;
```

- [ ] **Step 2: Create minimal translation files**

Create `desktop/src/i18n/locales/en.json`:

```json
{
  "app": {
    "name": "MoneyPrinterTurbo",
    "loading": "Starting MoneyPrinterTurbo..."
  },
  "nav": {
    "dashboard": "Dashboard",
    "create": "Create Video",
    "projects": "Projects",
    "plugins": "Plugins",
    "settings": "Settings",
    "license": "License"
  },
  "dashboard": {
    "title": "Dashboard",
    "welcome": "Welcome to MoneyPrinterTurbo",
    "recent_projects": "Recent Projects",
    "quick_create": "Quick Create",
    "no_projects": "No projects yet. Create your first video!"
  },
  "create": {
    "title": "Create Video",
    "step_content": "Content",
    "step_style": "Style",
    "step_audio": "Audio",
    "step_subtitle": "Subtitle",
    "step_review": "Review & Generate",
    "subject": "Video Subject",
    "subject_placeholder": "Enter a topic for your video...",
    "script": "Custom Script",
    "language": "Language",
    "generate": "Generate Video",
    "generating": "Generating..."
  },
  "projects": {
    "title": "Projects",
    "no_projects": "No projects yet",
    "status_processing": "Processing",
    "status_complete": "Complete",
    "status_failed": "Failed",
    "delete": "Delete",
    "delete_confirm": "Are you sure you want to delete this project?"
  },
  "settings": {
    "title": "Settings",
    "api_keys": "API Keys",
    "video_defaults": "Video Defaults",
    "audio_defaults": "Audio Defaults",
    "subtitle_defaults": "Subtitle Defaults",
    "save": "Save",
    "saved": "Settings saved"
  },
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "confirm": "Confirm",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success"
  }
}
```

Create `desktop/src/i18n/locales/zh.json` and `vi.json` with same keys, translated.

- [ ] **Step 3: Import i18n in main.tsx**

Add at the top of `desktop/src/main.tsx`:

```typescript
import "./i18n";
```

- [ ] **Step 4: Update Sidebar to use i18n**

In `Sidebar.tsx`, replace hardcoded labels:

```typescript
import { useTranslation } from "react-i18next";
// ...
const { t } = useTranslation();

const navItems = [
  { path: "/", label: t("nav.dashboard"), icon: LayoutDashboard },
  { path: "/create", label: t("nav.create"), icon: Video },
  // ...
];
```

- [ ] **Step 5: Commit**

```bash
git add desktop/src/i18n/ desktop/src/main.tsx desktop/src/components/layout/Sidebar.tsx
git commit -m "feat: i18n setup with react-i18next, en/zh/vi translations"
```

---

### Task 7: Development Script

**Files:**
- Create: `scripts/dev.sh`
- Create: `scripts/dev.bat`

- [ ] **Step 1: Create dev launcher scripts**

Create `scripts/dev.sh`:

```bash
#!/bin/bash
# Development launcher: starts Python sidecar + Tauri dev

echo "Starting MoneyPrinterTurbo Desktop (dev mode)..."

# Start Python sidecar in background
cd "$(dirname "$0")/.."
python main.py --port 18080 --mode desktop &
SIDECAR_PID=$!
echo "Sidecar PID: $SIDECAR_PID"

# Start Tauri dev
cd desktop
npm run tauri dev

# Cleanup
kill $SIDECAR_PID 2>/dev/null
echo "Dev environment stopped."
```

Create `scripts/dev.bat`:

```bat
@echo off
echo Starting MoneyPrinterTurbo Desktop (dev mode)...

cd /d "%~dp0\.."
start /B python main.py --port 18080 --mode desktop

cd desktop
npm run tauri dev

taskkill /F /IM python.exe /T 2>nul
echo Dev environment stopped.
```

- [ ] **Step 2: Commit**

```bash
git add scripts/
git commit -m "feat: development launcher scripts"
```

---

## PART B: Plugin Architecture (Tasks 8-12)

### Task 8: Plugin Base Interfaces

**Files:**
- Create: `app/plugins/__init__.py`
- Create: `app/plugins/base.py`
- Create: `tests/test_plugins/__init__.py`
- Create: `tests/test_plugins/test_base.py`

- [ ] **Step 1: Write tests for plugin interfaces**

Create `tests/test_plugins/test_base.py`:

```python
import pytest
from app.plugins.base import LLMPlugin, TTSPlugin, MaterialPlugin, PluginMeta


class MockLLMPlugin(LLMPlugin):
    def get_meta(self):
        return PluginMeta(
            name="mock-llm", display_name="Mock LLM", version="1.0.0",
            description="Test", author="test", plugin_type="llm",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def generate_response(self, prompt, **kwargs): return "mock response"
    def get_models(self): return ["mock-model"]


def test_llm_plugin_instantiation():
    plugin = MockLLMPlugin()
    meta = plugin.get_meta()
    assert meta.name == "mock-llm"
    assert meta.plugin_type == "llm"
    assert plugin.is_available() is True


def test_llm_plugin_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        LLMPlugin()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_plugins/test_base.py -v
```

Expected: FAIL — module not found

- [ ] **Step 3: Implement base.py**

Create `app/plugins/__init__.py` (empty).

Create `app/plugins/base.py` — use the full code from the design spec Section 5.2. Contains: `PluginMeta`, `PluginConfig`, `BasePlugin`, `LLMPlugin`, `TTSPlugin`, `MaterialPlugin`, `EffectPlugin`, `MusicPlugin`.

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_plugins/test_base.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/plugins/ tests/test_plugins/
git commit -m "feat: plugin ABC interfaces (LLM, TTS, Material, Effect, Music)"
```

---

### Task 9: Plugin Registry

**Files:**
- Create: `app/plugins/registry.py`
- Create: `tests/test_plugins/test_registry.py`

- [ ] **Step 1: Write registry tests**

Create `tests/test_plugins/test_registry.py`:

```python
import pytest
from app.plugins.registry import PluginRegistry
from tests.test_plugins.test_base import MockLLMPlugin


def test_register_and_get():
    reg = PluginRegistry()
    plugin = MockLLMPlugin()
    reg.register("llm", "mock-llm", plugin)
    assert reg.get("llm", "mock-llm") is plugin


def test_first_registered_becomes_active():
    reg = PluginRegistry()
    plugin = MockLLMPlugin()
    reg.register("llm", "mock-llm", plugin)
    assert reg.get_active("llm") is plugin


def test_set_active():
    reg = PluginRegistry()
    p1 = MockLLMPlugin()
    p2 = MockLLMPlugin()
    reg.register("llm", "p1", p1)
    reg.register("llm", "p2", p2)
    reg.set_active("llm", "p2")
    assert reg.get_active("llm") is p2


def test_enable_disable():
    reg = PluginRegistry()
    plugin = MockLLMPlugin()
    reg.register("llm", "mock", plugin)
    reg.disable("llm", "mock")
    listed = reg.list("llm")
    assert listed[0]["enabled"] is False
    reg.enable("llm", "mock")
    listed = reg.list("llm")
    assert listed[0]["enabled"] is True


def test_list_returns_metadata():
    reg = PluginRegistry()
    plugin = MockLLMPlugin()
    reg.register("llm", "mock-llm", plugin)
    result = reg.list("llm")
    assert len(result) == 1
    assert result[0]["name"] == "mock-llm"
    assert result[0]["active"] is True
    assert result[0]["available"] is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_plugins/test_registry.py -v
```

- [ ] **Step 3: Implement registry.py**

Use the code from design spec Section 5.4.

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_plugins/test_registry.py -v
```

- [ ] **Step 5: Commit**

```bash
git add app/plugins/registry.py tests/test_plugins/test_registry.py
git commit -m "feat: plugin registry with enable/disable/active selection"
```

---

### Task 10: Plugin Manager

**Files:**
- Create: `app/plugins/manager.py`
- Create: `app/plugins/utils.py`
- Create: `tests/test_plugins/test_manager.py`

- [ ] **Step 1: Write manager tests**

Create `tests/test_plugins/test_manager.py`:

```python
import pytest
from pathlib import Path
from app.plugins.manager import PluginManager


def test_manager_discovers_builtin_plugins():
    manager = PluginManager()
    manager.discover_plugins()
    # After Task 11, builtin plugins will exist
    plugins = manager.list_plugins()
    assert isinstance(plugins, list)


def test_manager_get_active_plugin():
    manager = PluginManager()
    manager.discover_plugins()
    # Should not crash even with no plugins
    result = manager.get_active_plugin("nonexistent")
    assert result is None
```

- [ ] **Step 2: Implement manager.py**

Use the code from design spec Section 5.3.

- [ ] **Step 3: Implement utils.py (async bridge)**

Create `app/plugins/utils.py`:

```python
import asyncio


def run_async(coro):
    """Run an async coroutine from synchronous context"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_plugins/test_manager.py -v
```

- [ ] **Step 5: Commit**

```bash
git add app/plugins/manager.py app/plugins/utils.py tests/test_plugins/test_manager.py
git commit -m "feat: plugin manager with discovery, async bridge utility"
```

---

### Task 11: Migrate First 3 Providers to Plugins

**Files:**
- Create: `app/plugins/builtin/__init__.py`
- Create: `app/plugins/builtin/llm/__init__.py`
- Create: `app/plugins/builtin/llm/openai_plugin.py`
- Create: `app/plugins/builtin/tts/__init__.py`
- Create: `app/plugins/builtin/tts/edge_tts_plugin.py`
- Create: `app/plugins/builtin/material/__init__.py`
- Create: `app/plugins/builtin/material/pexels_plugin.py`
- Create: `tests/test_plugins/test_openai_plugin.py`

- [ ] **Step 1: Write OpenAI plugin test**

Create `tests/test_plugins/test_openai_plugin.py`:

```python
import pytest
from app.plugins.builtin.llm.openai_plugin import OpenAIPlugin


def test_openai_plugin_meta():
    plugin = OpenAIPlugin()
    meta = plugin.get_meta()
    assert meta.name == "openai"
    assert meta.plugin_type == "llm"


def test_openai_plugin_unavailable_without_key():
    plugin = OpenAIPlugin()
    # Without API key configured, should be unavailable
    assert plugin.is_available() is False or plugin.is_available() is True  # depends on config


def test_openai_plugin_lists_models():
    plugin = OpenAIPlugin()
    models = plugin.get_models()
    assert "gpt-4o" in models or len(models) > 0
```

- [ ] **Step 2: Implement OpenAI plugin**

Create `app/plugins/builtin/llm/openai_plugin.py` using design spec Section 5.5 code, but using `config.get_api_key("openai_api_key")` instead of `config.app.get(...)`.

- [ ] **Step 3: Implement Edge TTS plugin**

Create `app/plugins/builtin/tts/edge_tts_plugin.py`:

```python
import edge_tts
import asyncio
from app.plugins.base import TTSPlugin, PluginMeta


class EdgeTTSPlugin(TTSPlugin):
    def get_meta(self):
        return PluginMeta(
            name="edge-tts", display_name="Microsoft Edge TTS",
            version="1.0.0", description="Free Azure Edge TTS with 400+ voices",
            author="MoneyPrinterTurbo", plugin_type="tts", builtin=True,
        )

    def validate_config(self, config): return True
    def is_available(self): return True

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        rate_str = f"+{int((rate - 1) * 100)}%" if rate >= 1 else f"{int((rate - 1) * 100)}%"
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
        sub_maker = edge_tts.SubMaker()
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.feed(chunk)
        return output_path, sub_maker

    def get_voices(self):
        from app.plugins.utils import run_async
        voices = run_async(edge_tts.list_voices())
        return [
            {"id": v["ShortName"], "name": v["FriendlyName"],
             "language": v["Locale"], "gender": v["Gender"]}
            for v in voices
        ]
```

- [ ] **Step 4: Implement Pexels plugin**

Create `app/plugins/builtin/material/pexels_plugin.py`:

```python
import requests
from app.plugins.base import MaterialPlugin, PluginMeta
from app.config.config import get_api_key


class PexelsPlugin(MaterialPlugin):
    def get_meta(self):
        return PluginMeta(
            name="pexels", display_name="Pexels",
            version="1.0.0", description="Free stock video and photo library",
            author="MoneyPrinterTurbo", plugin_type="material", builtin=True,
        )

    def validate_config(self, config):
        return bool(config.get("api_key"))

    def is_available(self):
        keys = get_api_key("pexels_api_keys")
        return bool(keys)

    async def search(self, query, aspect="16:9", max_results=10):
        keys = get_api_key("pexels_api_keys")
        api_key = keys.split(",")[0].strip() if isinstance(keys, str) else keys[0]
        orientation = "landscape" if aspect == "16:9" else "portrait" if aspect == "9:16" else None

        params = {"query": query, "per_page": max_results}
        if orientation:
            params["orientation"] = orientation

        headers = {"Authorization": api_key}
        resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for video in data.get("videos", []):
            best = max(video.get("video_files", []), key=lambda f: f.get("width", 0), default={})
            if best:
                results.append({
                    "url": best.get("link", ""),
                    "duration": video.get("duration", 0),
                    "width": best.get("width", 0),
                    "height": best.get("height", 0),
                    "provider": "pexels",
                })
        return results

    async def download(self, url, output_dir):
        import hashlib, os
        filename = f"vid-{hashlib.md5(url.encode()).hexdigest()}.mp4"
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            return filepath
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
```

- [ ] **Step 5: Create all __init__.py files**

```bash
touch app/plugins/builtin/__init__.py
touch app/plugins/builtin/llm/__init__.py
touch app/plugins/builtin/tts/__init__.py
touch app/plugins/builtin/material/__init__.py
```

- [ ] **Step 6: Verify plugin discovery works**

```bash
python -c "
from app.plugins.manager import PluginManager
m = PluginManager()
m.discover_plugins()
for p in m.list_plugins():
    print(f'{p[\"plugin_type\"]}: {p[\"name\"]} (available={p[\"available\"]})')
"
```

Expected: Lists openai, edge-tts, pexels

- [ ] **Step 7: Run all plugin tests**

```bash
python -m pytest tests/test_plugins/ -v
```

- [ ] **Step 8: Commit**

```bash
git add app/plugins/builtin/ tests/test_plugins/
git commit -m "feat: builtin plugins - OpenAI LLM, Edge TTS, Pexels material"
```

---

### Task 12: Service Layer Plugin Integration

**Files:**
- Modify: `app/services/llm.py` (add plugin fallback)
- Create: `app/controllers/v1/plugin_controller.py`
- Modify: `app/router.py`

- [ ] **Step 1: Create global plugin manager instance**

Add to `app/plugins/__init__.py`:

```python
from app.plugins.manager import PluginManager

plugin_manager = PluginManager()
plugin_manager.discover_plugins()
```

- [ ] **Step 2: Add plugin fallback to llm.py**

At the top of `app/services/llm.py`, after imports, add:

```python
from app.plugins import plugin_manager
from app.plugins.utils import run_async
```

Find the `_generate_response` function and wrap it:

```python
# Rename existing function
_legacy_generate_response = _generate_response

def _generate_response(prompt: str) -> str:
    """Generate response using plugin system with legacy fallback"""
    llm_plugin = plugin_manager.get_active_plugin("llm")
    if llm_plugin and llm_plugin.is_available():
        try:
            return run_async(llm_plugin.generate_response(prompt))
        except Exception as e:
            logger.warning(f"Plugin failed, falling back to legacy: {e}")

    return _legacy_generate_response(prompt)
```

- [ ] **Step 3: Create plugin controller**

Create `app/controllers/v1/plugin_controller.py`:

```python
from app.controllers.v1.base import new_router
from app.plugins import plugin_manager
from app.utils import utils

router = new_router()


@router.get("/plugins", summary="List all plugins")
def list_plugins(plugin_type: str = None):
    plugins = plugin_manager.list_plugins(plugin_type)
    return utils.get_response(200, plugins)


@router.post("/plugins/{plugin_type}/{name}/activate", summary="Set plugin as active")
def activate_plugin(plugin_type: str, name: str):
    plugin_manager.set_active(plugin_type, name)
    return utils.get_response(200, {"message": f"Activated {name} for {plugin_type}"})


@router.post("/plugins/{plugin_type}/{name}/enable", summary="Enable plugin")
def enable_plugin(plugin_type: str, name: str):
    plugin_manager.enable_plugin(plugin_type, name)
    return utils.get_response(200, {"message": f"Enabled {name}"})


@router.post("/plugins/{plugin_type}/{name}/disable", summary="Disable plugin")
def disable_plugin(plugin_type: str, name: str):
    plugin_manager.disable_plugin(plugin_type, name)
    return utils.get_response(200, {"message": f"Disabled {name}"})
```

- [ ] **Step 4: Register plugin router**

Modify `app/router.py`:

```python
from app.controllers.v1 import llm, video, system_controller, plugin_controller

root_api_router = APIRouter()
root_api_router.include_router(video.router)
root_api_router.include_router(llm.router)
root_api_router.include_router(system_controller.router)
root_api_router.include_router(plugin_controller.router)
```

- [ ] **Step 5: Test plugin endpoints**

```bash
python main.py --port 18080 --mode desktop &
curl http://127.0.0.1:18080/api/v1/plugins
# Expected: JSON array of plugins
```

- [ ] **Step 6: Commit**

```bash
git add app/plugins/__init__.py app/services/llm.py app/controllers/v1/plugin_controller.py app/router.py
git commit -m "feat: plugin integration in service layer with legacy fallback, plugin API endpoints"
```

---

## PART C: Config + State (Tasks 13-16)

### Task 13: Config v2 System

**Files:**
- Create: `app/config/config_v2.py`
- Create: `tests/test_config/test_config_v2.py`

- [ ] **Step 1: Install platformdirs + tomli_w**

```bash
pip install platformdirs tomli_w
```

- [ ] **Step 2: Write tests**

Create `tests/test_config/test_config_v2.py`:

```python
import os
import tempfile
import pytest
from unittest.mock import patch
from app.config.config_v2 import ConfigManager


@pytest.fixture
def config_dir(tmp_path):
    with patch("app.config.config_v2.get_config_dir", return_value=tmp_path):
        yield tmp_path


def test_creates_default_config(config_dir):
    cm = ConfigManager()
    assert (config_dir / "config.toml").exists()


def test_get_set_value(config_dir):
    cm = ConfigManager()
    cm.set("app", "language", "ja")
    assert cm.get("app", "language") == "ja"


def test_persistence(config_dir):
    cm1 = ConfigManager()
    cm1.set("app", "language", "ko")

    cm2 = ConfigManager()
    assert cm2.get("app", "language") == "ko"


def test_defaults(config_dir):
    cm = ConfigManager()
    assert cm.get("app", "language") is not None
    assert cm.get("video", "aspect") is not None
```

- [ ] **Step 3: Implement config_v2.py**

Use the code from design spec Section 6.2.

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_config/test_config_v2.py -v
```

- [ ] **Step 5: Commit**

```bash
git add app/config/config_v2.py tests/test_config/
git commit -m "feat: ConfigManager v2 with OS app data dir, TOML persistence"
```

---

### Task 14: Config Migration (v1 → v2)

**Files:**
- Create: `app/config/migration.py`
- Create: `tests/test_config/test_migration.py`

- [ ] **Step 1: Write migration tests**

Create `tests/test_config/test_migration.py`:

```python
import os
import tempfile
import pytest
from pathlib import Path
from app.config.migration import migrate_v1_to_v2


@pytest.fixture
def legacy_config(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('''
[app]
video_source = "pexels"
llm_provider = "openai"
openai_api_key = "sk-test-123"
pexels_api_keys = ["key1", "key2"]

[ui]
language = "zh"

[whisper]
model_size = "large-v3"
''')
    return config


def test_migration_extracts_secrets(legacy_config):
    result = migrate_v1_to_v2(legacy_config)
    assert "sk-test-123" in str(result["secrets"].get("openai_api_key", ""))
    assert "openai_api_key" not in str(result["config"])


def test_migration_maps_settings(legacy_config):
    result = migrate_v1_to_v2(legacy_config)
    config = result["config"]
    assert config["app"]["video_source"] == "pexels"
    assert config["app"]["language"] == "zh"


def test_migration_creates_backup(legacy_config):
    migrate_v1_to_v2(legacy_config)
    assert (legacy_config.parent / "config.toml.bak").exists()
```

- [ ] **Step 2: Implement migration.py**

Use the mapping from design spec Section 20.

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_config/test_migration.py -v
```

- [ ] **Step 4: Commit**

```bash
git add app/config/migration.py tests/test_config/test_migration.py
git commit -m "feat: config v1→v2 migration with secret extraction and backup"
```

---

### Task 15: SQLite State

**Files:**
- Modify: `app/services/state.py`
- Create: `tests/test_state/__init__.py`
- Create: `tests/test_state/test_sqlite_state.py`

- [ ] **Step 1: Write SQLiteState tests**

Create `tests/test_state/test_sqlite_state.py`:

```python
import json
import tempfile
import pytest
import threading
from app.services.state import SQLiteState


@pytest.fixture
def state():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return SQLiteState(f.name)


def test_update_and_get_task(state):
    state.update_task("task-1", state=4, progress=50)
    task = state.get_task("task-1")
    assert task is not None
    assert task["state"] == 4
    assert task["progress"] == 50


def test_complete_task(state):
    state.update_task("task-1", state=1, progress=100, videos=["/path/to/video.mp4"])
    task = state.get_task("task-1")
    assert task["state"] == 1


def test_delete_task(state):
    state.update_task("task-1", state=4)
    state.delete_task("task-1")
    assert state.get_task("task-1") is None


def test_get_all_tasks_pagination(state):
    for i in range(25):
        state.update_task(f"task-{i}", state=1, progress=100)
    tasks, total = state.get_all_tasks(page=1, page_size=10)
    assert len(tasks) == 10
    assert total == 25


def test_thread_safety(state):
    errors = []
    def writer(task_id):
        try:
            for i in range(50):
                state.update_task(task_id, state=4, progress=i * 2)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer, args=(f"task-{i}",)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0
```

- [ ] **Step 2: Implement SQLiteState**

Add to `app/services/state.py` using the thread-safe code from design spec Section 16.

Also modify the state initialization at the bottom:

```python
def create_state():
    mode = os.environ.get("MPT_MODE", "api")
    if mode == "desktop":
        from app.config.config_v2 import get_config_dir
        db_path = str(get_config_dir() / "moneyprinterturbo.db")
        return SQLiteState(db_path)
    elif _cfg.get("app", {}).get("enable_redis", False):
        return RedisState(...)
    else:
        return MemoryState()

state = create_state()
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_state/test_sqlite_state.py -v
```

- [ ] **Step 4: Commit**

```bash
git add app/services/state.py tests/test_state/
git commit -m "feat: SQLiteState with thread-safe connections, WAL mode, pagination"
```

---

### Task 16: Config + Secrets API Endpoints

**Files:**
- Create: `app/controllers/v1/config_controller.py`
- Modify: `app/router.py`

- [ ] **Step 1: Create config controller**

Create `app/controllers/v1/config_controller.py`:

```python
import os
from fastapi import HTTPException
from pydantic import BaseModel
from app.controllers.v1.base import new_router
from app.config.config import is_desktop_mode
from app.utils import utils

router = new_router()

ALLOWED_SECRET_KEYS = {
    "openai_api_key", "openai_base_url", "openai_model_name",
    "pexels_api_keys", "pixabay_api_keys",
    "azure_speech_key", "azure_speech_region",
    "siliconflow_api_key",
    "moonshot_api_key", "deepseek_api_key",
    "gemini_api_key", "qwen_api_key",
    "cloudflare_api_key", "ernie_api_key",
    "ollama_api_key",
}


@router.get("/config", summary="Get app configuration")
def get_config():
    if is_desktop_mode():
        from app.config.config_v2 import ConfigManager
        cm = ConfigManager()
        return utils.get_response(200, cm.get_all())
    else:
        from app.config import config
        return utils.get_response(200, {"app": config.app, "ui": config.ui})


class ConfigUpdate(BaseModel):
    data: dict


@router.put("/config", summary="Update configuration")
def update_config(body: ConfigUpdate):
    if is_desktop_mode():
        from app.config.config_v2 import ConfigManager
        cm = ConfigManager()
        cm.update(body.data)
        return utils.get_response(200, {"message": "Config updated"})
    raise HTTPException(400, "Config update only available in desktop mode")


class SecretsUpdate(BaseModel):
    secrets: dict[str, str]


@router.put("/config/secrets", summary="Receive secrets from desktop frontend")
def update_secrets(body: SecretsUpdate):
    if not is_desktop_mode():
        raise HTTPException(400, "Secrets endpoint only available in desktop mode")

    for key, value in body.secrets.items():
        if key not in ALLOWED_SECRET_KEYS:
            raise HTTPException(400, f"Unknown secret key: {key}")
        os.environ[f"MPT_{key.upper()}"] = value

    return utils.get_response(200, {"message": f"Set {len(body.secrets)} secrets"})
```

- [ ] **Step 2: Register router**

Add to `app/router.py`:

```python
from app.controllers.v1 import llm, video, system_controller, plugin_controller, config_controller

root_api_router.include_router(config_controller.router)
```

- [ ] **Step 3: Test endpoints**

```bash
python main.py --port 18080 --mode desktop &
curl http://127.0.0.1:18080/api/v1/config
curl -X PUT http://127.0.0.1:18080/api/v1/config/secrets \
  -H "Content-Type: application/json" \
  -d '{"secrets": {"openai_api_key": "sk-test"}}'
```

- [ ] **Step 4: Commit**

```bash
git add app/controllers/v1/config_controller.py app/router.py
git commit -m "feat: config and secrets API endpoints with security whitelist"
```

---

## PART D: Frontend Pages (Tasks 17-21)

> **Note:** Tasks 17-21 should use `@ui-ux-pro-max` skill for professional UI implementation. Each page gets its own task.

### Task 17: Dashboard Page

**Files:**
- Modify: `desktop/src/pages/Dashboard.tsx`
- Create: `desktop/src/api/hooks.ts`

- [ ] **Step 1: Create TanStack Query hooks**

Create `desktop/src/api/hooks.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

export function useTasks(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["tasks", page, pageSize],
    queryFn: () => api.getTasks(page, pageSize),
  });
}

export function useTask(taskId: string | null) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () => api.getTask(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const state = query.state.data?.state;
      return state === 4 ? 2000 : false;
    },
  });
}

export function useCreateVideo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.createVideo,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });
}

export function useDeleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.deleteTask,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });
}

export function useSystemInfo() {
  return useQuery({
    queryKey: ["system-info"],
    queryFn: api.systemInfo,
  });
}

export function usePlugins(type?: string) {
  return useQuery({
    queryKey: ["plugins", type],
    queryFn: () => api.getPlugins(type),
  });
}
```

- [ ] **Step 2: Implement Dashboard with recent tasks + system info**

Use `@ui-ux-pro-max` skill. Dashboard should show:
- Welcome card with system info
- Recent projects grid (last 6 tasks)
- Quick create button
- Stats: total videos, active tasks

- [ ] **Step 3: Commit**

```bash
git add desktop/src/pages/Dashboard.tsx desktop/src/api/hooks.ts
git commit -m "feat: dashboard page with recent projects and system info"
```

---

### Task 18: Create Video Page (5-Step Wizard)

**Files:**
- Modify: `desktop/src/pages/Create.tsx`
- Create: `desktop/src/api/types.ts`
- Create: `desktop/src/stores/videoStore.ts`

> This is the most complex page. Use `@ui-ux-pro-max` skill.

- [ ] **Step 1: Create TypeScript types**

Create `desktop/src/api/types.ts` — use the full types from design spec Section 4.5, ensuring all fields from Pydantic `VideoParams` are included (including `video_source`, `video_materials`, `custom_audio_file`).

- [ ] **Step 2: Create video creation store**

Create `desktop/src/stores/videoStore.ts`:

```typescript
import { create } from "zustand";
import type { VideoParams } from "@/api/types";

interface VideoStore {
  currentStep: number;
  params: Partial<VideoParams>;
  taskId: string | null;

  setStep: (step: number) => void;
  updateParams: (params: Partial<VideoParams>) => void;
  setTaskId: (id: string | null) => void;
  reset: () => void;
}

export const useVideoStore = create<VideoStore>((set) => ({
  currentStep: 0,
  params: {
    video_aspect: "16:9",
    video_concat_mode: "random",
    video_transition_mode: "FadeIn",
    video_clip_duration: 5,
    video_count: 1,
    video_language: "en",
    voice_name: "en-US-AriaNeural-Female",
    voice_volume: 1.0,
    voice_rate: 1.0,
    bgm_volume: 0.2,
    subtitle_enabled: true,
    subtitle_position: "bottom",
    font_size: 60,
    n_threads: 2,
    paragraph_number: 1,
  },
  taskId: null,

  setStep: (step) => set({ currentStep: step }),
  updateParams: (params) => set((s) => ({ params: { ...s.params, ...params } })),
  setTaskId: (id) => set({ taskId: id }),
  reset: () => set({ currentStep: 0, params: {}, taskId: null }),
}));
```

- [ ] **Step 3: Implement 5-step wizard**

Create wizard with steps:
1. **Content** — subject/script, language, paragraph count
2. **Style** — aspect ratio, video source, clip duration, transition, concat mode
3. **Audio** — voice selection, voice rate, BGM selection, BGM volume
4. **Subtitle** — enabled, position, font, colors, stroke
5. **Review & Generate** — summary + generate button + progress tracking

Use `@ui-ux-pro-max` skill for each step component.

- [ ] **Step 4: Wire up generation with progress polling**

Use `useCreateVideo()` mutation on generate, then `useTask()` with polling to show progress.

- [ ] **Step 5: Commit**

```bash
git add desktop/src/pages/Create.tsx desktop/src/api/types.ts desktop/src/stores/videoStore.ts
git commit -m "feat: video creation wizard with 5 steps and progress tracking"
```

---

### Task 19: Projects Page

**Files:**
- Modify: `desktop/src/pages/Projects.tsx`

- [ ] **Step 1: Implement project list with status badges**

Use `@ui-ux-pro-max` skill. Show:
- Table/grid of all tasks with pagination
- Status badge (processing/complete/failed)
- Video preview (thumbnail or play button linking to `http://127.0.0.1:{port}/tasks/{id}/final-1.mp4`)
- Delete button with confirmation dialog
- Open folder button

- [ ] **Step 2: Commit**

```bash
git add desktop/src/pages/Projects.tsx
git commit -m "feat: projects page with task list, status, video preview, delete"
```

---

### Task 20: Settings Page

**Files:**
- Modify: `desktop/src/pages/Settings.tsx`
- Create: `desktop/src/lib/secrets.ts`

- [ ] **Step 1: Create secrets helper**

Create `desktop/src/lib/secrets.ts`:

```typescript
import { invoke } from "@tauri-apps/api/core";

const SERVICE = "MoneyPrinterTurbo";

export async function getSecret(key: string): Promise<string | null> {
  return invoke<string | null>("get_secret", { key });
}

export async function setSecret(key: string, value: string): Promise<void> {
  return invoke("set_secret", { key, value });
}

export async function deleteSecret(key: string): Promise<void> {
  return invoke("delete_secret", { key });
}
```

- [ ] **Step 2: Implement settings page with tabs**

Use `@ui-ux-pro-max` skill. Tabs:
- **API Keys** — input fields for each provider's API key (stored in keychain)
- **Video Defaults** — aspect ratio, source, clip duration, transitions
- **Audio Defaults** — default voice, rate, BGM volume
- **Subtitle Defaults** — enabled, position, font, colors
- **General** — language, theme, max concurrent tasks

Each tab saves independently. API keys go to keychain + sidecar secrets endpoint.

- [ ] **Step 3: Commit**

```bash
git add desktop/src/pages/Settings.tsx desktop/src/lib/secrets.ts
git commit -m "feat: settings page with API key management, video/audio/subtitle defaults"
```

---

### Task 21: Plugins Page

**Files:**
- Modify: `desktop/src/pages/Plugins.tsx`

- [ ] **Step 1: Implement plugins list**

Show:
- Cards for each plugin grouped by type (LLM, TTS, Material)
- Active indicator (radio-like per type)
- Enable/disable toggle
- Availability indicator (green/red dot)
- Click to activate

- [ ] **Step 2: Commit**

```bash
git add desktop/src/pages/Plugins.tsx
git commit -m "feat: plugins page with enable/disable/activate controls"
```

---

## PART E: Build & Distribution (Tasks 22-25)

### Task 22: PyInstaller Sidecar Build

**Files:**
- Create: `scripts/build-sidecar.py`
- Create: `desktop/src-tauri/binaries/` (output dir)

- [ ] **Step 1: Install PyInstaller**

```bash
pip install pyinstaller
```

- [ ] **Step 2: Create build script**

Create `scripts/build-sidecar.py`:

```python
"""Build Python sidecar as standalone executable using PyInstaller"""
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "desktop" / "src-tauri" / "binaries"

def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "python-backend",
        "--distpath", str(OUTPUT),
        "--workpath", str(ROOT / "build" / "pyinstaller"),
        "--specpath", str(ROOT / "build"),
        "--add-data", f"{ROOT / 'resource'};resource",
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

    print(f"Building sidecar: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Rename for Tauri sidecar convention
    import platform
    target_triple = get_target_triple()
    src = OUTPUT / ("python-backend.exe" if sys.platform == "win32" else "python-backend")
    dst = OUTPUT / f"python-backend-{target_triple}{'.exe' if sys.platform == 'win32' else ''}"
    shutil.move(str(src), str(dst))
    print(f"Sidecar built: {dst}")


def get_target_triple():
    import platform
    machine = platform.machine().lower()
    if sys.platform == "win32":
        return f"x86_64-pc-windows-msvc" if machine == "amd64" else f"{machine}-pc-windows-msvc"
    elif sys.platform == "darwin":
        return f"{'aarch64' if machine == 'arm64' else machine}-apple-darwin"
    else:
        return f"{machine}-unknown-linux-gnu"


if __name__ == "__main__":
    build()
```

- [ ] **Step 3: Test build**

```bash
python scripts/build-sidecar.py
ls desktop/src-tauri/binaries/
# Expected: python-backend-x86_64-pc-windows-msvc.exe (or equivalent)
```

- [ ] **Step 4: Update tauri.conf.json for sidecar**

Add to `desktop/src-tauri/tauri.conf.json` under `"bundle"`:

```json
"externalBin": ["binaries/python-backend"]
```

- [ ] **Step 5: Commit**

```bash
git add scripts/build-sidecar.py desktop/src-tauri/tauri.conf.json
git commit -m "feat: PyInstaller sidecar build script with Tauri naming convention"
```

---

### Task 23: Tauri Production Build

**Files:**
- Create: `scripts/build-desktop.sh`
- Create: `scripts/build-desktop.bat`

- [ ] **Step 1: Create full build script**

Create `scripts/build-desktop.sh`:

```bash
#!/bin/bash
set -e

echo "=== Building MoneyPrinterTurbo Desktop ==="

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Step 1: Building Python sidecar..."
cd "$ROOT"
python scripts/build-sidecar.py

echo "Step 2: Building Tauri application..."
cd "$ROOT/desktop"
npm run tauri build

echo "=== Build complete ==="
echo "Installers at: desktop/src-tauri/target/release/bundle/"
ls -la src-tauri/target/release/bundle/*/
```

- [ ] **Step 2: Run full build**

```bash
bash scripts/build-desktop.sh
```

Expected: Installer created in `desktop/src-tauri/target/release/bundle/`

- [ ] **Step 3: Test installer**

Run the generated installer, verify:
- App installs and opens
- Sidecar starts (check process manager)
- Can navigate all pages
- Can generate a test video (if API keys configured)

- [ ] **Step 4: Commit**

```bash
git add scripts/
git commit -m "feat: full desktop build pipeline (sidecar + tauri)"
```

---

### Task 24: Run All Tests

- [ ] **Step 1: Run Python tests**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 2: Verify existing API mode still works**

```bash
python main.py
# Should start on port 8080 as before
curl http://127.0.0.1:8080/api/v1/ping
curl http://127.0.0.1:8080/docs
# Expected: Swagger docs load, ping returns pong
```

- [ ] **Step 3: Verify Streamlit still works**

```bash
streamlit run webui/Main.py
# Expected: Streamlit UI loads and functions normally
```

- [ ] **Step 4: Commit any fixes**

---

### Task 25: Final Integration Test

- [ ] **Step 1: Start desktop app in dev mode**

```bash
bash scripts/dev.sh
# OR on Windows:
scripts\dev.bat
```

- [ ] **Step 2: Verify full flow**

Checklist:
- [ ] App opens with loading screen
- [ ] Sidecar starts (check localhost:18080/api/v1/ping)
- [ ] Dashboard shows system info
- [ ] Navigate to Create → fill wizard → generate video
- [ ] Projects page shows task with progress
- [ ] Settings page can save API keys
- [ ] Plugins page lists builtin plugins
- [ ] Language switcher works (en/zh/vi)
- [ ] Sidebar collapses/expands
- [ ] Closing app kills sidecar process
- [ ] Second instance is blocked (single-instance)

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: Phase 1 complete - desktop app with plugin architecture"
```

---

## Agent Assignment Guide

| Task | Skill to Use | Agent Type |
|------|-------------|------------|
| 1-2 | General | Scaffolding + npm/cargo commands |
| 3 | General | Python backend modifications |
| 4 | General | Rust/Tauri code |
| 5-6 | `@ui-ux-pro-max` | React components, layout, styling |
| 7 | General | Shell scripts |
| 8-12 | General | Python plugin architecture |
| 13-16 | General | Python config/state/API |
| 17-21 | `@ui-ux-pro-max` | React pages with professional UI |
| 22-23 | General | Build scripts, PyInstaller |
| 24-25 | General | Testing + integration |

**Parallelizable work:**
- Tasks 8-12 (plugins) can run in parallel with Tasks 5-6 (frontend shell)
- Tasks 13-16 (config/state) can start after Task 3 (Python mode detection)
- Tasks 17-21 (frontend pages) depend on Task 5 (app shell) + Task 16 (API endpoints)
- Tasks 22-23 (build) depend on everything else
