import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";

type Tab = "templates" | "prompts" | "bgm" | "fonts" | "materials";

const tabStyle = (active: boolean): React.CSSProperties => ({
  padding: "8px 16px", borderRadius: 6, fontSize: 13, cursor: "pointer", fontWeight: active ? 600 : 400,
  border: "1px solid hsl(var(--border))",
  background: active ? "hsl(var(--primary))" : "transparent",
  color: active ? "hsl(var(--primary-foreground))" : "inherit",
});

const cardStyle: React.CSSProperties = {
  background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 16,
};

const inputStyle: React.CSSProperties = {
  width: "100%", padding: "8px 12px", borderRadius: 6, fontSize: 14,
  border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit",
};

const btnPrimary: React.CSSProperties = {
  padding: "8px 20px", borderRadius: 6, border: "none", fontSize: 13, fontWeight: 600, cursor: "pointer",
  background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))",
};

const btnOutline: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 6, fontSize: 12, cursor: "pointer",
  border: "1px solid hsl(var(--border))", background: "transparent", color: "inherit",
};

const btnDanger: React.CSSProperties = {
  ...btnOutline, border: "1px solid hsl(var(--destructive))", color: "hsl(var(--destructive))",
};

// ═══════════════════════════════════════
// VIDEO TEMPLATES
// ═══════════════════════════════════════
function TemplateManager() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [viewing, setViewing] = useState<any | null>(null);
  const [editing, setEditing] = useState<any | null>(null);
  const emptyForm = {
    id: "", name: "", description: "", category: "custom", platform: "general",
    video_aspect: "9:16", video_transition_mode: "FadeIn", video_clip_duration: 5,
    voice_name: "en-US-AriaNeural-Female", voice_rate: 1.0, bgm_volume: 0.2,
    subtitle_enabled: true, subtitle_position: "bottom", font_size: 60,
    text_fore_color: "#FFFFFF", stroke_color: "#000000",
    caption_style: "default", color_preset: "none",
    paragraph_number: 1, video_language: "en",
  };
  const [form, setForm] = useState(emptyForm);

  const loadTemplates = () => {
    apiFetch<any[]>("/api/v1/templates").then(d => setTemplates(Array.isArray(d) ? d : [])).catch(() => {});
  };
  useEffect(loadTemplates, []);

  const handleSave = async () => {
    const id = form.id || `custom-${Date.now()}`;
    await apiFetch("/api/v1/templates", {
      method: "POST",
      body: JSON.stringify({ ...form, id }),
    });
    setEditing(null);
    setForm(emptyForm);
    loadTemplates();
  };

  const handleNew = () => {
    setForm(emptyForm);
    setEditing({});
    setViewing(null);
  };

  const handleEdit = (t: any) => {
    setForm(t);
    setEditing(t);
    setViewing(null);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ fontWeight: 600 }}>Video Templates ({templates.length})</h3>
        <button onClick={handleNew} style={btnPrimary}>+ New Template</button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: 12 }}>
        {templates.map((t: any) => (
          <div key={t.id} style={{ ...cardStyle, cursor: "pointer", transition: "border 0.15s" }}
            onClick={() => setViewing(t)}
            onMouseEnter={e => (e.currentTarget.style.borderColor = "hsl(var(--primary))")}
            onMouseLeave={e => (e.currentTarget.style.borderColor = "hsl(var(--border))")}>
            <div style={{ fontWeight: 600, fontSize: 14 }}>{t.name}</div>
            <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>
              {t.category} · {t.video_aspect} · {t.caption_style || "default"}
            </div>
            <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 4 }}>{t.description}</div>
          </div>
        ))}
      </div>

      {/* VIEW DETAIL MODAL */}
      {viewing && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }} onClick={() => setViewing(null)}>
        <div style={{ ...cardStyle, padding: 24, width: "90%", maxWidth: 550, maxHeight: "85vh", overflowY: "auto" }} onClick={e => e.stopPropagation()}>
          <h4 style={{ fontWeight: 600, fontSize: 18, marginBottom: 16 }}>{viewing.name}</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, fontSize: 13 }}>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Category:</span> {viewing.category}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Platform:</span> {viewing.platform || "general"}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Aspect:</span> {viewing.video_aspect}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Transition:</span> {viewing.video_transition_mode}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Color:</span> {viewing.color_preset || "none"}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Captions:</span> {viewing.caption_style || "default"}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Voice:</span> {viewing.voice_name}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Rate:</span> {viewing.voice_rate}x</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Clip:</span> {viewing.video_clip_duration}s</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>BGM Vol:</span> {viewing.bgm_volume}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Font Size:</span> {viewing.font_size}</div>
            <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Language:</span> {viewing.video_language || "en"}</div>
          </div>
          {viewing.description && (
            <div style={{ marginTop: 12, fontSize: 12, color: "hsl(var(--muted-foreground))" }}>{viewing.description}</div>
          )}
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={() => handleEdit(viewing)} style={btnPrimary}>Edit / Duplicate</button>
            <button onClick={() => setViewing(null)} style={btnOutline}>Close</button>
          </div>
        </div>
        </div>
      )}

      {/* EDIT/CREATE MODAL */}
      {editing !== null && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1001 }} onClick={() => setEditing(null)}>
        <div style={{ ...cardStyle, padding: 24, width: "90%", maxWidth: 600, maxHeight: "85vh", overflowY: "auto" }} onClick={e => e.stopPropagation()}>
          <h4 style={{ fontWeight: 600, marginBottom: 16 }}>{editing?.id ? "Edit Template" : "New Template"}</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Name</div>
              <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} style={inputStyle} placeholder="My Template" /></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Category</div>
              <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} style={inputStyle}>
                <option value="custom">Custom</option><option value="tiktok">TikTok</option><option value="youtube-shorts">YouTube Shorts</option>
                <option value="instagram-reels">Instagram Reels</option><option value="corporate">Corporate</option><option value="education">Education</option>
              </select></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Aspect Ratio</div>
              <select value={form.video_aspect} onChange={e => setForm({ ...form, video_aspect: e.target.value })} style={inputStyle}>
                <option value="9:16">9:16 (Portrait)</option><option value="16:9">16:9 (Landscape)</option><option value="1:1">1:1 (Square)</option>
              </select></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Transition</div>
              <select value={form.video_transition_mode} onChange={e => setForm({ ...form, video_transition_mode: e.target.value })} style={inputStyle}>
                <option value="FadeIn">Fade In</option><option value="FadeOut">Fade Out</option><option value="SlideIn">Slide In</option>
                <option value="ZoomIn">Zoom In</option><option value="Flash">Flash</option><option value="Shuffle">Shuffle</option>
              </select></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Color Preset</div>
              <select value={form.color_preset} onChange={e => setForm({ ...form, color_preset: e.target.value })} style={inputStyle}>
                <option value="none">None</option><option value="cinematic">Cinematic</option><option value="warm">Warm</option>
                <option value="cool">Cool</option><option value="vintage">Vintage</option><option value="noir">Noir</option>
              </select></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Caption Style</div>
              <select value={form.caption_style} onChange={e => setForm({ ...form, caption_style: e.target.value })} style={inputStyle}>
                <option value="default">Default</option><option value="hormozi">Hormozi</option><option value="documentary">Documentary</option>
                <option value="tiktok-viral">TikTok Viral</option><option value="corporate">Corporate</option>
              </select></label>
            <label style={{ gridColumn: "1 / -1" }}><div style={{ fontSize: 12, marginBottom: 4 }}>Description</div>
              <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} style={{ ...inputStyle, resize: "vertical" }} /></label>
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={handleSave} style={btnPrimary}>Save Template</button>
            <button onClick={() => setEditing(null)} style={btnOutline}>Cancel</button>
          </div>
        </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════
// PROMPT TEMPLATES
// ═══════════════════════════════════════
function PromptManager() {
  const [prompts, setPrompts] = useState<any[]>([]);
  const [editing, setEditing] = useState<any | null>(null);
  const [viewing, setViewing] = useState<any | null>(null);
  const [filterCat, setFilterCat] = useState("");
  const [form, setForm] = useState({
    id: "", name: "", description: "", category: "custom",
    prompt_prefix: "", prompt_suffix: "", language: "any", example: "",
  });

  const loadPrompts = () => {
    apiFetch<any[]>("/api/v1/prompt-templates").then(d => setPrompts(Array.isArray(d) ? d : [])).catch(() => {});
  };
  useEffect(loadPrompts, []);

  const handleSave = async () => {
    const id = form.id || `custom-${Date.now()}`;
    await apiFetch("/api/v1/prompt-templates", {
      method: "POST",
      body: JSON.stringify({ ...form, id }),
    });
    setEditing(null);
    setForm({ id: "", name: "", description: "", category: "custom", prompt_prefix: "", prompt_suffix: "", language: "any", example: "" });
    loadPrompts();
  };

  const handleDelete = async (id: string) => {
    // Delete directly (no confirm dialog — Tauri WebView may not support it)
    await apiFetch(`/api/v1/prompt-templates/${id}`, { method: "DELETE" });
    loadPrompts();
  };

  const handleEdit = (p: any) => {
    setForm({
      id: p.id, name: p.name, description: p.description || "",
      category: p.category, prompt_prefix: p.prompt_prefix || "",
      prompt_suffix: p.prompt_suffix || "", language: p.language || "any",
      example: p.example || "",
    });
    setEditing(p);
  };

  const handleDuplicate = (p: any) => {
    setForm({
      id: `${p.id}-copy-${Date.now()}`,
      name: `${p.name} (Copy)`,
      description: p.description || "",
      category: "custom",
      prompt_prefix: p.prompt_prefix || "",
      prompt_suffix: p.prompt_suffix || "",
      language: p.language || "any",
      example: p.example || "",
    });
    setEditing({});
  };

  const categories = [...new Set(prompts.map((p: any) => p.category))];
  const filtered = filterCat ? prompts.filter((p: any) => p.category === filterCat) : prompts;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ fontWeight: 600 }}>Prompt Templates ({prompts.length})</h3>
        <button onClick={() => { setForm({ id: "", name: "", description: "", category: "custom", prompt_prefix: "", prompt_suffix: "", language: "any", example: "" }); setEditing({}); }} style={btnPrimary}>
          + New Prompt
        </button>
      </div>

      {/* Category filter */}
      <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
        <button onClick={() => setFilterCat("")} style={{ ...btnOutline, fontSize: 11, padding: "4px 10px", border: !filterCat ? "2px solid hsl(var(--primary))" : btnOutline.border }}>All</button>
        {categories.map(cat => (
          <button key={cat} onClick={() => setFilterCat(cat)} style={{ ...btnOutline, fontSize: 11, padding: "4px 10px", textTransform: "capitalize", border: filterCat === cat ? "2px solid hsl(var(--primary))" : btnOutline.border }}>{cat}</button>
        ))}
      </div>

      {/* Prompt list */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {filtered.map((p: any) => (
          <div key={p.id} style={{ ...cardStyle, display: "flex", alignItems: "flex-start", gap: 16, cursor: "pointer", transition: "border 0.15s" }}
            onClick={() => setViewing(p)}
            onMouseEnter={e => (e.currentTarget.style.borderColor = "hsl(var(--primary))")}
            onMouseLeave={e => (e.currentTarget.style.borderColor = "hsl(var(--border))")}>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontWeight: 600, fontSize: 14 }}>{p.name}</span>
                {p.builtin && <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, background: "hsl(var(--secondary))", color: "hsl(var(--muted-foreground))" }}>built-in</span>}
              </div>
              <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>{p.description}</div>
              {p.example && (
                <div style={{ fontSize: 11, fontStyle: "italic", color: "hsl(var(--muted-foreground))", marginTop: 4, opacity: 0.7 }}>
                  "{p.example.slice(0, 100)}..."
                </div>
              )}
            </div>
            <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 600, background: "hsl(var(--secondary))", color: "hsl(var(--muted-foreground))", textTransform: "capitalize", whiteSpace: "nowrap" }}>{p.category}</span>
          </div>
        ))}
      </div>

      {/* VIEW DETAIL MODAL */}
      {viewing && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }} onClick={() => setViewing(null)}>
        <div style={{ ...cardStyle, padding: 24, width: "90%", maxWidth: 650, maxHeight: "85vh", overflowY: "auto" }} onClick={e => e.stopPropagation()}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <h4 style={{ fontWeight: 600, fontSize: 18, margin: 0 }}>{viewing.name}</h4>
            {viewing.builtin && <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 3, background: "hsl(var(--secondary))", color: "hsl(var(--muted-foreground))" }}>built-in</span>}
            <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 600, background: "hsl(var(--secondary))", color: "hsl(var(--muted-foreground))", textTransform: "capitalize" }}>{viewing.category}</span>
            <span style={{ fontSize: 11, color: "hsl(var(--muted-foreground))" }}>{viewing.language}</span>
          </div>
          <div style={{ fontSize: 13, color: "hsl(var(--muted-foreground))", marginBottom: 16 }}>{viewing.description}</div>

          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4, color: "hsl(var(--primary))" }}>Prompt Prefix (Instructions before topic)</div>
            <pre style={{ background: "hsl(var(--secondary))", padding: 12, borderRadius: 6, fontSize: 12, whiteSpace: "pre-wrap", lineHeight: 1.5, maxHeight: 200, overflowY: "auto" }}>
              {viewing.prompt_prefix || "(no prefix)"}
            </pre>
          </div>

          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4, color: "hsl(var(--primary))" }}>Prompt Suffix (Instructions after topic)</div>
            <pre style={{ background: "hsl(var(--secondary))", padding: 12, borderRadius: 6, fontSize: 12, whiteSpace: "pre-wrap", lineHeight: 1.5 }}>
              {viewing.prompt_suffix || "(no suffix)"}
            </pre>
          </div>

          {viewing.example && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>Example Output</div>
              <div style={{ fontSize: 12, fontStyle: "italic", color: "hsl(var(--muted-foreground))", padding: 12, background: "hsl(var(--secondary))", borderRadius: 6 }}>
                "{viewing.example}"
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => { handleDuplicate(viewing); setViewing(null); }} style={btnPrimary}>Duplicate & Edit</button>
            {!viewing.builtin && <button onClick={() => { handleEdit(viewing); setViewing(null); }} style={btnOutline}>Edit</button>}
            {!viewing.builtin && <button onClick={() => { handleDelete(viewing.id); setViewing(null); }} style={btnDanger}>Delete</button>}
            <button onClick={() => setViewing(null)} style={btnOutline}>Close</button>
          </div>
        </div>
        </div>
      )}

      {/* Create/Edit form — MODAL */}
      {editing !== null && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }} onClick={() => setEditing(null)}>
        <div style={{ ...cardStyle, padding: 24, width: "90%", maxWidth: 700, maxHeight: "85vh", overflowY: "auto" }} onClick={e => e.stopPropagation()}>
          <h4 style={{ fontWeight: 600, marginBottom: 16 }}>{form.id && editing?.id ? "Edit Prompt" : "New Prompt Template"}</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              <label><div style={{ fontSize: 12, marginBottom: 4 }}>Name</div>
                <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} style={inputStyle} placeholder="My Hook Style" /></label>
              <label><div style={{ fontSize: 12, marginBottom: 4 }}>Category</div>
                <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} style={inputStyle}>
                  <option value="custom">Custom</option><option value="hook">Hook</option><option value="storytelling">Storytelling</option>
                  <option value="educational">Educational</option><option value="marketing">Marketing</option><option value="viral">Viral</option>
                </select></label>
              <label><div style={{ fontSize: 12, marginBottom: 4 }}>Language</div>
                <select value={form.language} onChange={e => setForm({ ...form, language: e.target.value })} style={inputStyle}>
                  <option value="any">Any Language</option><option value="en">English</option><option value="vi">Vietnamese</option>
                  <option value="zh">Chinese</option><option value="ja">Japanese</option><option value="ko">Korean</option>
                </select></label>
            </div>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Description</div>
              <input value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} style={inputStyle} placeholder="Short description of this style" /></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Prompt Prefix <span style={{ color: "hsl(var(--muted-foreground))", fontWeight: 400 }}>(instructions BEFORE the topic)</span></div>
              <textarea value={form.prompt_prefix} onChange={e => setForm({ ...form, prompt_prefix: e.target.value })} rows={5}
                style={{ ...inputStyle, resize: "vertical", fontFamily: "monospace", fontSize: 12 }}
                placeholder={"Write a video script that...\nStructure: [Hook] → [Body] → [CTA]\nUse short, punchy sentences."} /></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Prompt Suffix <span style={{ color: "hsl(var(--muted-foreground))", fontWeight: 400 }}>(instructions AFTER the topic)</span></div>
              <textarea value={form.prompt_suffix} onChange={e => setForm({ ...form, prompt_suffix: e.target.value })} rows={2}
                style={{ ...inputStyle, resize: "vertical", fontFamily: "monospace", fontSize: 12 }}
                placeholder="Make it engaging and shareable." /></label>
            <label><div style={{ fontSize: 12, marginBottom: 4 }}>Example Output <span style={{ color: "hsl(var(--muted-foreground))", fontWeight: 400 }}>(preview for users)</span></div>
              <input value={form.example} onChange={e => setForm({ ...form, example: e.target.value })} style={inputStyle}
                placeholder="Most people think X. They're wrong..." /></label>
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={handleSave} disabled={!form.name || !form.prompt_prefix} style={{ ...btnPrimary, opacity: (!form.name || !form.prompt_prefix) ? 0.5 : 1 }}>Save Prompt Template</button>
            <button onClick={() => setEditing(null)} style={btnOutline}>Cancel</button>
          </div>
        </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════
// BGM / MUSIC MANAGER
// ═══════════════════════════════════════
function BgmManager() {
  const [bgmList, setBgmList] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState("");

  const loadBgm = () => {
    apiFetch<any>("/api/v1/musics").then(data => {
      setBgmList(Array.isArray(data) ? data : data?.files || []);
    }).catch(() => {});
  };
  useEffect(loadBgm, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
      await fetch(`http://127.0.0.1:${port}/api/v1/musics`, { method: "POST", body: formData });
      loadBgm();
    } catch (err) { console.error("Upload failed:", err); }
    setUploading(false);
  };

  const handlePlay = (name: string) => {
    if (playing === name) {
      audioRef.current?.pause();
      setPlaying("");
    } else {
      if (audioRef.current) {
        const port = 18080;
        audioRef.current.src = `http://127.0.0.1:${port}/api/v1/musics/play/${encodeURIComponent(name)}`;
        audioRef.current.play().catch(() => {});
        setPlaying(name);
      }
    }
  };

  return (
    <div>
      <audio ref={audioRef} onEnded={() => setPlaying("")} style={{ display: "none" }} />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ fontWeight: 600 }}>Background Music ({bgmList.length} tracks)</h3>
        <div>
          <input ref={fileRef} type="file" accept=".mp3" style={{ display: "none" }} onChange={handleUpload} />
          <button onClick={() => fileRef.current?.click()} disabled={uploading} style={btnPrimary}>
            {uploading ? "Uploading..." : "+ Upload MP3"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {bgmList.length === 0 && (
          <div style={{ color: "hsl(var(--muted-foreground))", padding: 20, textAlign: "center" }}>
            No music files. Upload MP3 files to use as background music.
          </div>
        )}
        {bgmList.map((bgm: any) => (
          <div key={bgm.name} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: 12 }}>
            <button onClick={() => handlePlay(bgm.name)} style={{ ...btnOutline, minWidth: 60 }}>
              {playing === bgm.name ? "⏸ Stop" : "▶ Play"}
            </button>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: 500 }}>🎵 {bgm.name}</div>
              <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))" }}>
                {(bgm.size / 1024 / 1024).toFixed(1)} MB
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════
// FONTS MANAGER
// ═══════════════════════════════════════
function FontManager() {
  const [fonts, setFonts] = useState<string[]>([]);

  useEffect(() => {
    // Fonts are in resource/fonts/
    apiFetch<any>("/api/v1/system/info").then(() => {
      // For now, hardcode known fonts
      setFonts([
        "Charm-Bold.ttf", "Charm-Regular.ttf",
        "MicrosoftYaHeiBold.ttc", "MicrosoftYaHeiNormal.ttc",
        "STHeitiLight.ttc", "STHeitiMedium.ttc",
        "UTM Kabel KT.ttf",
      ]);
    }).catch(() => {});
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ fontWeight: 600 }}>Fonts ({fonts.length})</h3>
        <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))" }}>
          Add fonts to <code>resource/fonts/</code> folder
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 8 }}>
        {fonts.map(f => (
          <div key={f} style={cardStyle}>
            <div style={{ fontSize: 14, fontWeight: 500 }}>🔤 {f}</div>
            <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>
              {f.endsWith(".ttf") ? "TrueType" : "TrueType Collection"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════
// LOCAL MATERIALS MANAGER
// ═══════════════════════════════════════
function MaterialManager() {
  const [materials, setMaterials] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement | null>(null);

  const loadMaterials = () => {
    apiFetch<any>("/api/v1/video_materials").then(data => {
      setMaterials(Array.isArray(data) ? data : data?.files || []);
    }).catch(() => {});
  };
  useEffect(loadMaterials, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append("file", file);
        const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
        await fetch(`http://127.0.0.1:${port}/api/v1/video_materials`, { method: "POST", body: formData });
      }
      loadMaterials();
    } catch (err) { console.error("Upload failed:", err); }
    setUploading(false);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ fontWeight: 600 }}>Local Materials ({materials.length})</h3>
        <div>
          <input ref={fileRef} type="file" accept=".mp4,.mov,.avi,.jpg,.jpeg,.png" multiple style={{ display: "none" }} onChange={handleUpload} />
          <button onClick={() => fileRef.current?.click()} disabled={uploading} style={btnPrimary}>
            {uploading ? "Uploading..." : "+ Upload Video/Image"}
          </button>
        </div>
      </div>

      <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))", marginBottom: 12 }}>
        Upload your own videos/images to use instead of stock footage. Select "Local" as video source when creating videos.
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 8 }}>
        {materials.length === 0 && (
          <div style={{ color: "hsl(var(--muted-foreground))", padding: 20 }}>
            No local materials. Upload videos or images.
          </div>
        )}
        {materials.map((m: any) => (
          <div key={m.name} style={cardStyle}>
            <div style={{ fontSize: 14, fontWeight: 500 }}>
              {m.name.match(/\.(mp4|mov|avi)$/i) ? "🎬" : "🖼"} {m.name}
            </div>
            <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>
              {(m.size / 1024 / 1024).toFixed(1)} MB
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════
// MAIN MANAGER PAGE
// ═══════════════════════════════════════
export default function Manager() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>("templates");

  return (
    <div style={{ padding: 24, maxWidth: 1000 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Resource Manager</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        {([
          { id: "templates", label: "Video Templates", icon: "🎬" },
          { id: "prompts", label: "Prompt Templates", icon: "✍️" },
          { id: "bgm", label: "Background Music", icon: "🎵" },
          { id: "fonts", label: "Fonts", icon: "🔤" },
          { id: "materials", label: "Local Materials", icon: "📁" },
        ] as { id: Tab; label: string; icon: string }[]).map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={tabStyle(activeTab === tab.id)}>
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "templates" && <TemplateManager />}
      {activeTab === "prompts" && <PromptManager />}
      {activeTab === "bgm" && <BgmManager />}
      {activeTab === "fonts" && <FontManager />}
      {activeTab === "materials" && <MaterialManager />}
    </div>
  );
}
