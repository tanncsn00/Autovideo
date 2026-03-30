import { useTranslation } from "react-i18next";
import { useState, useEffect } from "react";
import { useConfig } from "../api/hooks";
import { api, apiFetch } from "../api/client";
import { setSecret, getSecret } from "../lib/secrets";

// All API key fields grouped by category
const API_KEY_GROUPS = [
  {
    title: "LLM Providers",
    fields: [
      { key: "openai_api_key", label: "OpenAI API Key", placeholder: "sk-..." },
      { key: "openai_base_url", label: "OpenAI Base URL (optional)", placeholder: "https://api.openai.com/v1" },
      { key: "openai_model_name", label: "OpenAI Model", placeholder: "gpt-4o-mini" },
      { key: "claude_api_key", label: "Claude (Anthropic) API Key", placeholder: "sk-ant-..." },
      { key: "gemini_api_key", label: "Google Gemini API Key", placeholder: "AI..." },
      { key: "deepseek_api_key", label: "DeepSeek API Key", placeholder: "sk-..." },
      { key: "groq_api_key", label: "Groq API Key", placeholder: "gsk_..." },
      { key: "mistral_api_key", label: "Mistral API Key", placeholder: "" },
      { key: "moonshot_api_key", label: "Moonshot (Kimi) API Key", placeholder: "" },
      { key: "qwen_api_key", label: "Qwen (Alibaba) API Key", placeholder: "" },
      { key: "ollama_base_url", label: "Ollama URL (local)", placeholder: "http://localhost:11434/v1" },
    ],
  },
  {
    title: "TTS / Voice",
    fields: [
      { key: "fpt_ai_api_key", label: "FPT.AI API Key (Vietnamese TTS)", placeholder: "Lay tai console.fpt.ai" },
      { key: "vbee_api_key", label: "VBee API Key (Vietnamese TTS)", placeholder: "" },
      { key: "vbee_app_id", label: "VBee App ID", placeholder: "" },
      { key: "elevenlabs_api_key", label: "ElevenLabs API Key", placeholder: "" },
      { key: "azure_speech_key", label: "Azure Speech Key", placeholder: "" },
      { key: "azure_speech_region", label: "Azure Speech Region", placeholder: "eastus" },
      { key: "siliconflow_api_key", label: "SiliconFlow API Key", placeholder: "" },
      { key: "gpt_sovits_api_url", label: "GPT-SoVITS Server URL", placeholder: "http://127.0.0.1:9880" },
    ],
  },
  {
    title: "Video / Material Sources",
    fields: [
      { key: "pexels_api_keys", label: "Pexels API Key", placeholder: "" },
      { key: "pixabay_api_keys", label: "Pixabay API Key", placeholder: "" },
      { key: "unsplash_access_key", label: "Unsplash Access Key", placeholder: "" },
    ],
  },
];

// Publishing platforms with login buttons (separate from API key groups)
const PUBLISHING_PLATFORMS = [
  { id: "tiktok-auto", name: "TikTok", icon: "🎵", loginEndpoint: "/api/v1/publishers/tiktok/login", description: "Login once → auto upload videos. No API key needed." },
  { id: "youtube", name: "YouTube", icon: "📺", loginEndpoint: "", description: "Coming soon — requires Google OAuth setup" },
  { id: "instagram", name: "Instagram", icon: "📸", loginEndpoint: "", description: "Coming soon — requires Meta Developer approval" },
  { id: "facebook", name: "Facebook", icon: "👤", loginEndpoint: "", description: "Coming soon — requires Meta Developer approval" },
  { id: "twitter", name: "X (Twitter)", icon: "𝕏", loginEndpoint: "", description: "Coming soon — requires X Developer account" },
  { id: "linkedin", name: "LinkedIn", icon: "💼", loginEndpoint: "", description: "Coming soon — requires LinkedIn Developer app" },
];

const ALL_FIELDS = API_KEY_GROUPS.flatMap((g) => g.fields);

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "8px 12px",
  borderRadius: 6,
  border: "1px solid hsl(var(--border))",
  background: "hsl(var(--input))",
  color: "inherit",
  fontSize: 14,
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  cursor: "pointer",
};

const cardStyle: React.CSSProperties = {
  background: "hsl(var(--card))",
  border: "1px solid hsl(var(--border))",
  borderRadius: 8,
  padding: 24,
  marginBottom: 16,
};

export default function Settings() {
  const { t, i18n } = useTranslation();
  const { data: config } = useConfig();
  const [activeTab, setActiveTab] = useState("api_keys");
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);
  const [expandedGroup, setExpandedGroup] = useState<string | null>("LLM Providers");

  // Video default settings
  const [videoDefaults, setVideoDefaults] = useState({
    video_aspect: "16:9",
    video_source: "pexels",
    video_clip_duration: 5,
    video_transition_mode: "FadeIn",
    video_concat_mode: "random",
    color_preset: "none",
    caption_style: "default",
  });

  // Audio default settings
  const [audioDefaults, setAudioDefaults] = useState({
    voice_name: "en-US-AriaNeural-Female",
    voice_rate: 1.0,
    bgm_volume: 0.2,
  });

  // Load existing secrets
  useEffect(() => {
    ALL_FIELDS.forEach(async (field) => {
      const val = await getSecret(field.key);
      if (val) setSecrets((s) => ({ ...s, [field.key]: val }));
    });
    // Also load tiktok_account_name
    (async () => {
      const val = await getSecret("tiktok_account_name");
      if (val) setSecrets((s) => ({ ...s, tiktok_account_name: val }));
    })();
  }, []);

  // Load config defaults
  useEffect(() => {
    if (config && typeof config === "object") {
      const c = config as any;
      if (c.video) {
        setVideoDefaults((d) => ({ ...d, ...c.video }));
      }
      if (c.audio) {
        setAudioDefaults((d) => ({ ...d, ...c.audio }));
      }
      // Load tiktok_account_name from config if not already in secrets
      const tiktokName = c.app?.tiktok_account_name || c.ui?.tiktok_account_name;
      if (tiktokName) {
        setSecrets((s) => s.tiktok_account_name ? s : { ...s, tiktok_account_name: tiktokName });
      }
    }
  }, [config]);

  const handleSaveSecrets = async () => {
    const nonEmpty: Record<string, string> = {};
    for (const [key, value] of Object.entries(secrets)) {
      if (value && value.trim()) {
        await setSecret(key, value);
        nonEmpty[key] = value;
      }
    }
    if (Object.keys(nonEmpty).length > 0) {
      await api.updateSecrets(nonEmpty);
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleSaveVideoDefaults = async () => {
    try {
      await api.updateConfig({ video: videoDefaults });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error("Failed to save video defaults:", e);
    }
  };

  const handleSaveAudioDefaults = async () => {
    try {
      await api.updateConfig({ audio: audioDefaults });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error("Failed to save audio defaults:", e);
    }
  };

  // Publishing login state
  const [loginLoading, setLoginLoading] = useState<string | null>(null);
  const [loginStatus, setLoginStatus] = useState<Record<string, string>>({});

  // Check TikTok login status on load
  useEffect(() => {
    apiFetch<any>("/api/v1/publishers/tiktok/status")
      .then((d) => {
        if (d?.connected) {
          setLoginStatus((s) => ({ ...s, "tiktok-auto": "connected" }));
        }
      })
      .catch(() => {});
  }, []);

  const handlePlatformLogin = async (platform: any) => {
    if (!platform.loginEndpoint) return;
    setLoginLoading(platform.id);
    try {
      // Call login — this opens browser, may take minutes
      const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
      await fetch(`http://127.0.0.1:${port}${platform.loginEndpoint}`, {
        method: "POST",
        signal: AbortSignal.timeout(300000), // 5 min timeout
      });
    } catch (e: any) {
      console.log(`Login request ended: ${e.message || "completed"}`);
    }
    // Always check status after login attempt (regardless of request result)
    try {
      const status = await apiFetch<any>("/api/v1/publishers/tiktok/status");
      if (status?.connected) {
        setLoginStatus((s) => ({ ...s, [platform.id]: "connected" }));
      } else {
        setLoginStatus((s) => ({ ...s, [platform.id]: "failed" }));
      }
    } catch {
      setLoginStatus((s) => ({ ...s, [platform.id]: "failed" }));
    }
    setLoginLoading(null);
  };

  const tabs = ["api_keys", "publishing", "video_defaults", "audio_defaults", "general"];

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>{t("settings.title")}</h1>

      {/* Tab buttons */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "8px 16px",
              borderRadius: 6,
              border: "1px solid hsl(var(--border))",
              background: activeTab === tab ? "hsl(var(--primary))" : "transparent",
              color: activeTab === tab ? "hsl(var(--primary-foreground))" : "inherit",
              cursor: "pointer",
              fontSize: 13,
              fontWeight: activeTab === tab ? 600 : 400,
            }}
          >
            {t(`settings.${tab}`)}
          </button>
        ))}
      </div>

      {/* API Keys Tab */}
      {activeTab === "api_keys" && (
        <div>
          {API_KEY_GROUPS.map((group) => {
            const isExpanded = expandedGroup === group.title;
            const hasKeys = group.fields.some((f) => secrets[f.key]?.trim());
            return (
              <div key={group.title} style={{ ...cardStyle }}>
                <button
                  onClick={() => setExpandedGroup(isExpanded ? null : group.title)}
                  style={{
                    width: "100%",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    background: "none",
                    border: "none",
                    color: "inherit",
                    cursor: "pointer",
                    padding: 0,
                    fontSize: 15,
                    fontWeight: 600,
                  }}
                >
                  <span>
                    {group.title}
                    {hasKeys && (
                      <span
                        style={{
                          marginLeft: 8,
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          background: "#22c55e",
                          display: "inline-block",
                        }}
                      />
                    )}
                  </span>
                  <span style={{ fontSize: 18, color: "hsl(var(--muted-foreground))" }}>
                    {isExpanded ? "−" : "+"}
                  </span>
                </button>

                {isExpanded && (
                  <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 14 }}>
                    {group.fields.map((field) => (
                      <label key={field.key}>
                        <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500, color: "hsl(var(--muted-foreground))" }}>
                          {field.label}
                        </div>
                        <input
                          type={field.key.includes("key") || field.key.includes("secret") || field.key.includes("token") ? "password" : "text"}
                          value={secrets[field.key] || ""}
                          onChange={(e) => setSecrets((s) => ({ ...s, [field.key]: e.target.value }))}
                          placeholder={field.placeholder || ""}
                          style={inputStyle}
                        />
                      </label>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          <button
            onClick={handleSaveSecrets}
            style={{
              padding: "10px 32px",
              borderRadius: 6,
              border: "none",
              background: "hsl(var(--primary))",
              color: "hsl(var(--primary-foreground))",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 14,
            }}
          >
            {saved ? "Saved!" : "Save All API Keys"}
          </button>
        </div>
      )}

      {/* Publishing Tab */}
      {activeTab === "publishing" && (
        <div>
          <div style={{ fontSize: 13, color: "hsl(var(--muted-foreground))", marginBottom: 16 }}>
            Connect your social media accounts to auto-publish videos directly from the app.
          </div>

          {/* TikTok username */}
          <div style={{...cardStyle, marginBottom: 12}}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <span style={{ fontSize: 20 }}>🎵</span>
              <span style={{ fontSize: 13, fontWeight: 600 }}>TikTok Username</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <input
                value={secrets["tiktok_account_name"] || ""}
                onChange={e => setSecrets(s => ({...s, tiktok_account_name: e.target.value}))}
                placeholder="@username"
                style={{...inputStyle, flex: 1}}
              />
              <button onClick={async () => {
                const name = secrets["tiktok_account_name"];
                if (name) {
                  await setSecret("tiktok_account_name", name);
                  await api.updateSecrets({tiktok_account_name: name});
                }
              }} style={{padding: "8px 16px", borderRadius: 6, border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))", cursor: "pointer", fontSize: 13, fontWeight: 600, whiteSpace: "nowrap"}}>
                Save
              </button>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {PUBLISHING_PLATFORMS.map((platform) => {
              const status = loginStatus[platform.id];
              const isLoading = loginLoading === platform.id;
              return (
                <div key={platform.id} style={{...cardStyle, display: "flex", alignItems: "center", gap: 16}}>
                  <span style={{ fontSize: 28 }}>{platform.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>{platform.name}</div>
                    <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>{platform.description}</div>
                  </div>
                  {status === "connected" ? (
                    <span style={{ padding: "6px 16px", borderRadius: 6, fontSize: 12, fontWeight: 600, background: "#22c55e", color: "white" }}>
                      Connected
                    </span>
                  ) : platform.loginEndpoint ? (
                    <button
                      onClick={() => handlePlatformLogin(platform)}
                      disabled={isLoading}
                      style={{
                        padding: "8px 20px", borderRadius: 6, fontSize: 13, fontWeight: 600, cursor: "pointer",
                        border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))",
                        opacity: isLoading ? 0.5 : 1,
                      }}
                    >
                      {isLoading ? "Connecting..." : status === "failed" ? "Retry Login" : "Login"}
                    </button>
                  ) : (
                    <span style={{ padding: "6px 16px", borderRadius: 6, fontSize: 12, background: "hsl(var(--secondary))", color: "hsl(var(--muted-foreground))" }}>
                      Coming Soon
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Video Defaults Tab */}
      {activeTab === "video_defaults" && (
        <div style={cardStyle}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Aspect Ratio</div>
              <select value={videoDefaults.video_aspect} onChange={(e) => setVideoDefaults((d) => ({ ...d, video_aspect: e.target.value }))} style={selectStyle}>
                <option value="16:9">16:9 (Landscape)</option>
                <option value="9:16">9:16 (Portrait / TikTok / Shorts)</option>
                <option value="1:1">1:1 (Square / Instagram)</option>
              </select>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Video Source</div>
              <select value={videoDefaults.video_source} onChange={(e) => setVideoDefaults((d) => ({ ...d, video_source: e.target.value }))} style={selectStyle}>
                <option value="pexels">Pexels</option>
                <option value="pixabay">Pixabay</option>
                <option value="local">Local Files</option>
              </select>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Clip Duration (seconds)</div>
              <input type="number" min={2} max={15} value={videoDefaults.video_clip_duration}
                onChange={(e) => setVideoDefaults((d) => ({ ...d, video_clip_duration: parseInt(e.target.value) || 5 }))} style={inputStyle} />
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Transition</div>
              <select value={videoDefaults.video_transition_mode} onChange={(e) => setVideoDefaults((d) => ({ ...d, video_transition_mode: e.target.value }))} style={selectStyle}>
                <option value="None">None</option>
                <option value="FadeIn">Fade In</option>
                <option value="FadeOut">Fade Out</option>
                <option value="SlideIn">Slide In</option>
                <option value="SlideOut">Slide Out</option>
                <option value="WipeLeft">Wipe Left</option>
                <option value="WipeRight">Wipe Right</option>
                <option value="ZoomIn">Zoom In</option>
                <option value="ZoomOut">Zoom Out</option>
                <option value="Flash">Flash</option>
                <option value="BlackFade">Black Fade</option>
                <option value="Shuffle">Shuffle (Random)</option>
              </select>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Color Preset</div>
              <select value={videoDefaults.color_preset} onChange={(e) => setVideoDefaults((d) => ({ ...d, color_preset: e.target.value }))} style={selectStyle}>
                <option value="none">None</option>
                <option value="cinematic">Cinematic</option>
                <option value="warm">Warm</option>
                <option value="cool">Cool</option>
                <option value="vintage">Vintage</option>
                <option value="noir">Noir (B&W)</option>
                <option value="vibrant">Vibrant</option>
                <option value="muted">Muted</option>
                <option value="high_contrast">High Contrast</option>
              </select>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Caption Style</div>
              <select value={videoDefaults.caption_style} onChange={(e) => setVideoDefaults((d) => ({ ...d, caption_style: e.target.value }))} style={selectStyle}>
                <option value="default">Default (Static)</option>
                <option value="hormozi">Hormozi (Bold, Centered, Color Pop)</option>
                <option value="documentary">Documentary (Clean, Bottom Bar)</option>
                <option value="tiktok-viral">TikTok Viral (Large, Bouncy)</option>
                <option value="corporate">Corporate (Subtle, Professional)</option>
              </select>
            </label>
          </div>

          <button onClick={handleSaveVideoDefaults}
            style={{ marginTop: 20, padding: "10px 32px", borderRadius: 6, border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))", cursor: "pointer", fontWeight: 600 }}>
            {saved ? "Saved!" : "Save Video Defaults"}
          </button>
        </div>
      )}

      {/* Audio Defaults Tab */}
      {activeTab === "audio_defaults" && (
        <div style={cardStyle}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Default Voice</div>
              <input value={audioDefaults.voice_name} onChange={(e) => setAudioDefaults((d) => ({ ...d, voice_name: e.target.value }))}
                placeholder="en-US-AriaNeural-Female" style={inputStyle} />
              <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 4 }}>
                Edge TTS voices: en-US-AriaNeural-Female, en-US-GuyNeural-Male, zh-CN-XiaoxiaoNeural-Female, etc.
              </div>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Voice Rate: {audioDefaults.voice_rate}x</div>
              <input type="range" min={0.5} max={2.0} step={0.05} value={audioDefaults.voice_rate}
                onChange={(e) => setAudioDefaults((d) => ({ ...d, voice_rate: parseFloat(e.target.value) }))}
                style={{ width: "100%" }} />
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>BGM Volume: {audioDefaults.bgm_volume}</div>
              <input type="range" min={0} max={1} step={0.05} value={audioDefaults.bgm_volume}
                onChange={(e) => setAudioDefaults((d) => ({ ...d, bgm_volume: parseFloat(e.target.value) }))}
                style={{ width: "100%" }} />
            </label>
          </div>

          <button onClick={handleSaveAudioDefaults}
            style={{ marginTop: 20, padding: "10px 32px", borderRadius: 6, border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))", cursor: "pointer", fontWeight: 600 }}>
            {saved ? "Saved!" : "Save Audio Defaults"}
          </button>
        </div>
      )}

      {/* General Tab */}
      {activeTab === "general" && (
        <div style={cardStyle}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>{t("settings.language")}</div>
              <select value={i18n.language} onChange={(e) => i18n.changeLanguage(e.target.value)} style={selectStyle}>
                <option value="en">English</option>
                <option value="zh">中文</option>
                <option value="vi">Tiếng Việt</option>
              </select>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>LLM Provider</div>
              <select defaultValue="openai" style={selectStyle}>
                <option value="openai">OpenAI</option>
                <option value="claude">Claude (Anthropic)</option>
                <option value="gemini">Google Gemini</option>
                <option value="deepseek">DeepSeek</option>
                <option value="groq">Groq</option>
                <option value="mistral">Mistral AI</option>
                <option value="moonshot">Moonshot (Kimi)</option>
                <option value="qwen">Qwen (Alibaba)</option>
                <option value="ollama">Ollama (Local)</option>
              </select>
            </label>

            <label>
              <div style={{ marginBottom: 4, fontSize: 13, fontWeight: 500 }}>Max Concurrent Tasks</div>
              <input type="number" min={1} max={10} defaultValue={5} style={inputStyle} />
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
