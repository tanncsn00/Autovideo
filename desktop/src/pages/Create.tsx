import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { useVideoStore } from "../stores/videoStore";
import { useCreateVideo, useTask, useTemplates } from "../api/hooks";
import { api, apiFetch } from "../api/client";

const STEPS = [
  { key: "content", label: "Content" },
  { key: "script", label: "Script" },
  { key: "style", label: "Style" },
  { key: "audio", label: "Audio" },
  { key: "subtitle", label: "Subtitle" },
  { key: "materials", label: "Materials" },
  { key: "review", label: "Review" },
];

const inputStyle: React.CSSProperties = {
  width: "100%", padding: "8px 12px", borderRadius: 6, fontSize: 14,
  border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit",
};
const selectStyle: React.CSSProperties = { ...inputStyle, cursor: "pointer" };
const btnPrimary: React.CSSProperties = {
  padding: "10px 24px", borderRadius: 6, border: "none", fontWeight: 600, fontSize: 14, cursor: "pointer",
  background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))",
};
const btnOutline: React.CSSProperties = {
  padding: "8px 20px", borderRadius: 6, fontSize: 13, cursor: "pointer",
  border: "1px solid hsl(var(--border))", background: "transparent", color: "inherit",
};
const labelStyle: React.CSSProperties = { fontSize: 13, fontWeight: 500, marginBottom: 4, display: "block" };

const AVAILABLE_FONTS = [
  "STHeitiMedium.ttc", "STHeitiLight.ttc", "MicrosoftYaHeiBold.ttc",
  "MicrosoftYaHeiNormal.ttc", "Charm-Bold.ttf", "Charm-Regular.ttf", "UTM Kabel KT.ttf",
];

export default function Create() {
  const { t } = useTranslation();
  const { currentStep, params, taskId, setStep, updateParams, setTaskId, reset } = useVideoStore();
  const createVideo = useCreateVideo();
  const { data: taskData } = useTask(taskId);
  const { data: templates } = useTemplates();
  const templateList = Array.isArray(templates) ? templates : [];

  // Script generation state
  const [scriptLoading, setScriptLoading] = useState(false);
  const [scriptTaskId, setScriptTaskId] = useState<string | null>(null);

  // Voice state
  const [langFilter, setLangFilter] = useState("en");
  const [genderFilter, setGenderFilter] = useState("");
  const [voicePreviewLoading, setVoicePreviewLoading] = useState<string | null>(null);
  const voiceAudioRef = useRef<HTMLAudioElement>(null);

  // BGM state
  const [bgmList, setBgmList] = useState<any[]>([]);
  const [playingBgm, setPlayingBgm] = useState("");
  const [bgmUploading, setBgmUploading] = useState(false);
  const bgmAudioRef = useRef<HTMLAudioElement>(null);
  const bgmFileRef = useRef<HTMLInputElement>(null);

  // Materials state
  const [materialList, setMaterialList] = useState<any[]>([]);
  const [matUploading, setMatUploading] = useState(false);
  const matFileRef = useRef<HTMLInputElement>(null);

  // Prompt templates
  const [promptTemplates, setPromptTemplates] = useState<any[]>([]);
  const [promptCat, setPromptCat] = useState("");

  // Voices
  const { data: voicesData } = useQuery({
    queryKey: ["voices", langFilter],
    queryFn: () => apiFetch<any[]>(langFilter ? `/api/v1/voices?language=${langFilter}` : "/api/v1/voices"),
  });
  const voices = Array.isArray(voicesData) ? voicesData : [];
  const filteredVoices = genderFilter ? voices.filter((v: any) => v.gender === genderFilter) : voices;

  // Script task polling
  const { data: scriptTaskData } = useTask(scriptTaskId);

  useEffect(() => {
    if (scriptTaskData && (scriptTaskData as any).state === 1 && (scriptTaskData as any).script) {
      updateParams({ video_script: (scriptTaskData as any).script });
      setScriptLoading(false);
      setScriptTaskId(null);
    } else if (scriptTaskData && (scriptTaskData as any).state === -1) {
      setScriptLoading(false);
      setScriptTaskId(null);
    }
  }, [scriptTaskData]);

  // Load BGM list
  useEffect(() => {
    apiFetch<any>("/api/v1/musics").then(d => setBgmList(Array.isArray(d) ? d : d?.files || [])).catch(() => {});
  }, []);

  // Load materials
  useEffect(() => {
    apiFetch<any>("/api/v1/video_materials").then(d => setMaterialList(Array.isArray(d) ? d : d?.files || [])).catch(() => {});
  }, []);

  // Load prompt templates
  useEffect(() => {
    apiFetch<any[]>("/api/v1/prompt-templates").then(d => setPromptTemplates(Array.isArray(d) ? d : [])).catch(() => {});
  }, []);

  // Handlers
  const handleSelectTemplate = async (templateId: string) => {
    try {
      const p = await api.applyTemplate(templateId);
      updateParams({ ...p, template_id: templateId } as any);
    } catch (e) { console.error(e); }
  };

  const handleGenerateScript = async () => {
    if (!params.video_subject) return;
    setScriptLoading(true);
    try {
      const result = await apiFetch<any>("/api/v1/scripts", {
        method: "POST",
        body: JSON.stringify({
          video_subject: params.video_subject,
          video_language: params.video_language || "en",
          paragraph_number: params.paragraph_number || 1,
        }),
      });
      if (result?.video_script) {
        updateParams({ video_script: result.video_script });
      }
    } catch (e) {
      console.error(e);
    }
    setScriptLoading(false);
  };

  const handlePreviewVoice = async (voiceName: string) => {
    setVoicePreviewLoading(voiceName);
    try {
      const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
      const resp = await fetch(`http://127.0.0.1:${port}/api/v1/voices/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ voice: voiceName }),
      });
      const blob = await resp.blob();
      if (voiceAudioRef.current) {
        voiceAudioRef.current.src = URL.createObjectURL(blob);
        voiceAudioRef.current.play();
      }
    } catch (e) { console.error(e); }
    setVoicePreviewLoading(null);
  };

  const handlePlayBgm = async (bgm: any) => {
    if (playingBgm === bgm.name) {
      bgmAudioRef.current?.pause();
      setPlayingBgm("");
      return;
    }
    try {
      const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
      bgmAudioRef.current!.src = `http://127.0.0.1:${port}/api/v1/musics/play/${encodeURIComponent(bgm.name)}`;
      bgmAudioRef.current!.play().catch(() => {});
      setPlayingBgm(bgm.name);
    } catch(e) { console.error(e); }
  };

  const handleUploadBgm = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBgmUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
      await fetch(`http://127.0.0.1:${port}/api/v1/musics`, { method: "POST", body: formData });
      const d = await apiFetch<any>("/api/v1/musics");
      setBgmList(Array.isArray(d) ? d : d?.files || []);
    } catch (e) { console.error(e); }
    setBgmUploading(false);
  };

  const handleUploadMaterial = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    setMatUploading(true);
    try {
      const port = (await import("../stores/appStore")).useAppStore.getState().sidecarPort;
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append("file", file);
        await fetch(`http://127.0.0.1:${port}/api/v1/video_materials`, { method: "POST", body: formData });
      }
      const d = await apiFetch<any>("/api/v1/video_materials");
      setMaterialList(Array.isArray(d) ? d : d?.files || []);
    } catch (e) { console.error(e); }
    setMatUploading(false);
  };

  const handleGenerate = async () => {
    if (!params.video_subject && !params.video_script) return;
    try {
      const result = await createVideo.mutateAsync(params as Record<string, unknown>);
      setTaskId((result as any).task_id);
      setStep(6); // Go to review step to show progress
    } catch (e) { console.error(e); }
  };

  const promptCategories = [...new Set(promptTemplates.map((t: any) => t.category))];
  const filteredPrompts = promptCat ? promptTemplates.filter((t: any) => t.category === promptCat) : promptTemplates;

  return (
    <div style={{ padding: 24, maxWidth: 850, margin: "0 auto" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Create Video</h1>

      {/* Hidden audio elements */}
      <audio ref={voiceAudioRef} style={{ display: "none" }} />
      <audio ref={bgmAudioRef} style={{ display: "none" }} onEnded={() => setPlayingBgm("")} />
      <input ref={bgmFileRef} type="file" accept=".mp3" style={{ display: "none" }} onChange={handleUploadBgm} />
      <input ref={matFileRef} type="file" accept=".mp4,.mov,.avi,.jpg,.jpeg,.png" multiple style={{ display: "none" }} onChange={handleUploadMaterial} />

      {/* Quick template select */}
      {templateList.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))", marginBottom: 8 }}>Quick Start Template (optional)</div>
          <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 4 }}>
            {templateList.slice(0, 8).map((t: any) => (
              <button key={t.id} onClick={() => handleSelectTemplate(t.id)}
                style={{ minWidth: 120, padding: "8px 12px", borderRadius: 6, textAlign: "left" as const, cursor: "pointer", fontSize: 12,
                  border: (params as any).template_id === t.id ? "2px solid hsl(var(--primary))" : "1px solid hsl(var(--border))",
                  background: "hsl(var(--card))", color: "inherit" }}>
                <div style={{ fontWeight: 600 }}>{t.name}</div>
                <div style={{ fontSize: 10, color: "hsl(var(--muted-foreground))" }}>{t.category}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step indicators */}
      <div style={{ display: "flex", gap: 4, marginBottom: 24 }}>
        {STEPS.map((step, i) => (
          <button key={step.key} onClick={() => setStep(i)}
            style={{ flex: 1, padding: "6px 4px", borderRadius: 6, fontSize: 11, cursor: "pointer", fontWeight: i === currentStep ? 700 : 400,
              border: "none", background: i === currentStep ? "hsl(var(--primary))" : i < currentStep ? "hsl(var(--primary) / 0.3)" : "hsl(var(--secondary))",
              color: i === currentStep ? "hsl(var(--primary-foreground))" : "hsl(var(--muted-foreground))" }}>
            {i + 1}. {step.label}
          </button>
        ))}
      </div>

      {/* Step content */}
      <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 24, minHeight: 300 }}>

        {/* STEP 1: CONTENT */}
        {currentStep === 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Prompt template selector */}
            <div>
              <div style={labelStyle}>Script Style (optional)</div>
              <div style={{ display: "flex", gap: 4, marginBottom: 8, flexWrap: "wrap" }}>
                <button onClick={() => setPromptCat("")} style={{ ...btnOutline, fontSize: 10, padding: "3px 8px", border: !promptCat ? "2px solid hsl(var(--primary))" : btnOutline.border }}>All</button>
                {promptCategories.map(c => (
                  <button key={c} onClick={() => setPromptCat(c)} style={{ ...btnOutline, fontSize: 10, padding: "3px 8px", textTransform: "capitalize", border: promptCat === c ? "2px solid hsl(var(--primary))" : btnOutline.border }}>{c}</button>
                ))}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 6, maxHeight: 150, overflowY: "auto" }}>
                {filteredPrompts.slice(0, 12).map((pt: any) => (
                  <button key={pt.id} onClick={() => updateParams({ prompt_template: pt.id } as any)}
                    style={{ padding: "6px 10px", borderRadius: 6, textAlign: "left" as const, cursor: "pointer", fontSize: 11,
                      border: (params as any).prompt_template === pt.id ? "2px solid hsl(var(--primary))" : "1px solid hsl(var(--border))",
                      background: "hsl(var(--card))", color: "inherit" }}>
                    <div style={{ fontWeight: 600 }}>{pt.name}</div>
                    <div style={{ fontSize: 9, color: "hsl(var(--muted-foreground))", marginTop: 1 }}>{pt.description?.slice(0, 50)}</div>
                  </button>
                ))}
              </div>
            </div>

            <label><div style={labelStyle}>Video Subject *</div>
              <input value={params.video_subject || ""} onChange={e => updateParams({ video_subject: e.target.value })} placeholder="Enter your video topic..." style={inputStyle} /></label>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <label><div style={labelStyle}>Language</div>
                <select value={params.video_language || "en"} onChange={e => updateParams({ video_language: e.target.value })} style={selectStyle}>
                  <option value="en">English</option><option value="vi">Vietnamese</option><option value="zh">Chinese</option>
                  <option value="ja">Japanese</option><option value="ko">Korean</option><option value="es">Spanish</option>
                  <option value="fr">French</option><option value="de">German</option>
                </select></label>
              <label><div style={labelStyle}>Paragraphs</div>
                <input type="number" min={1} max={5} value={params.paragraph_number || 1} onChange={e => updateParams({ paragraph_number: parseInt(e.target.value) })} style={inputStyle} /></label>
            </div>

            {/* URL import */}
            <div style={{ borderTop: "1px solid hsl(var(--border))", paddingTop: 12 }}>
              <div style={{ ...labelStyle, color: "hsl(var(--muted-foreground))" }}>Or import from URL / YouTube</div>
              <div style={{ display: "flex", gap: 8 }}>
                <input id="url-input" placeholder="Paste URL or YouTube link..." style={{ ...inputStyle, flex: 1 }} />
                <button onClick={async () => {
                  const el = document.getElementById("url-input") as HTMLInputElement;
                  if (!el?.value) return;
                  try { const r = await api.processURL(el.value); updateParams(r as any); } catch(e) { console.error(e); }
                }} style={{ ...btnPrimary, fontSize: 12, padding: "8px 16px", whiteSpace: "nowrap" }}>Import</button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: SCRIPT PREVIEW */}
        {currentStep === 1 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontSize: 16, fontWeight: 600 }}>Video Script</div>
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={handleGenerateScript} disabled={scriptLoading || !params.video_subject}
                  style={{ ...btnPrimary, fontSize: 12, padding: "6px 16px", opacity: (scriptLoading || !params.video_subject) ? 0.5 : 1 }}>
                  {scriptLoading ? "Generating..." : params.video_script ? "Regenerate" : "Generate Script"}
                </button>
              </div>
            </div>

            {scriptLoading && (
              <div style={{ padding: 20, textAlign: "center", color: "hsl(var(--muted-foreground))" }}>
                <div style={{ fontSize: 24, marginBottom: 8, animation: "spin 1s linear infinite" }}>&#x27F3;</div>
                AI is writing your script...
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
              </div>
            )}

            <textarea value={params.video_script || ""} onChange={e => updateParams({ video_script: e.target.value })}
              placeholder={params.video_subject ? "Click 'Generate Script' above, or paste your own script here..." : "Go back to Step 1 and enter a topic first"}
              rows={12} style={{ ...inputStyle, resize: "vertical", fontSize: 14, lineHeight: 1.6 }} />

            {params.video_script && (
              <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))" }}>
                {params.video_script.length} characters · ~{Math.ceil(params.video_script.split(/\s+/).length / 150)} min read
                <br />Edit the script above if needed, then proceed to next step.
              </div>
            )}
          </div>
        )}

        {/* STEP 3: STYLE */}
        {currentStep === 2 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <label><div style={labelStyle}>Aspect Ratio</div>
              <select value={params.video_aspect || "16:9"} onChange={e => updateParams({ video_aspect: e.target.value as any })} style={selectStyle}>
                <option value="16:9">16:9 Landscape (YouTube)</option>
                <option value="9:16">9:16 Portrait (TikTok/Shorts)</option>
                <option value="1:1">1:1 Square (Instagram)</option>
              </select></label>
            <label><div style={labelStyle}>Transition</div>
              <select value={params.video_transition_mode || "FadeIn"} onChange={e => updateParams({ video_transition_mode: e.target.value as any })} style={selectStyle}>
                <option value="None">None</option><option value="FadeIn">Fade In</option><option value="FadeOut">Fade Out</option>
                <option value="SlideIn">Slide In</option><option value="SlideOut">Slide Out</option>
                <option value="WipeLeft">Wipe Left</option><option value="WipeRight">Wipe Right</option>
                <option value="ZoomIn">Zoom In</option><option value="ZoomOut">Zoom Out</option>
                <option value="Flash">Flash</option><option value="BlackFade">Black Fade</option><option value="Shuffle">Shuffle (Random)</option>
              </select></label>
            <label><div style={labelStyle}>Color Preset</div>
              <select value={(params as any).color_preset || "none"} onChange={e => updateParams({ color_preset: e.target.value } as any)} style={selectStyle}>
                <option value="none">None</option><option value="cinematic">Cinematic</option><option value="warm">Warm</option>
                <option value="cool">Cool</option><option value="vintage">Vintage</option><option value="noir">Noir (B&W)</option>
                <option value="vibrant">Vibrant</option><option value="muted">Muted</option><option value="high_contrast">High Contrast</option>
                <option value="dark_motivation">Dark Motivation</option><option value="dark_cinematic">Dark Cinematic</option>
              </select></label>
            <label><div style={labelStyle}>Caption Style</div>
              <select value={(params as any).caption_style || "default"} onChange={e => updateParams({ caption_style: e.target.value } as any)} style={selectStyle}>
                <option value="default">Default (Static)</option><option value="hormozi">Hormozi (Bold Centered)</option>
                <option value="documentary">Documentary (Clean Bottom)</option><option value="tiktok-viral">TikTok Viral (Large Bouncy)</option>
                <option value="corporate">Corporate (Subtle)</option>
              </select></label>
            <label><div style={labelStyle}>Clip Duration (sec)</div>
              <input type="number" min={2} max={15} value={params.video_clip_duration || 5} onChange={e => updateParams({ video_clip_duration: parseInt(e.target.value) })} style={inputStyle} /></label>
            <label><div style={labelStyle}>Video Count</div>
              <input type="number" min={1} max={5} value={params.video_count || 1} onChange={e => updateParams({ video_count: parseInt(e.target.value) })} style={inputStyle} /></label>
          </div>
        )}

        {/* STEP 4: AUDIO */}
        {currentStep === 3 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Voice selection */}
            <div>
              <div style={{ ...labelStyle, fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Voice</div>
              <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
                <select value={langFilter} onChange={e => setLangFilter(e.target.value)} style={{ ...selectStyle, width: "auto" }}>
                  <option value="">All Languages</option><option value="en">English</option><option value="vi">Vietnamese</option>
                  <option value="zh">Chinese</option><option value="ja">Japanese</option><option value="ko">Korean</option>
                  <option value="es">Spanish</option><option value="fr">French</option><option value="de">German</option>
                </select>
                <select value={genderFilter} onChange={e => setGenderFilter(e.target.value)} style={{ ...selectStyle, width: "auto" }}>
                  <option value="">All</option><option value="Female">Female</option><option value="Male">Male</option>
                </select>
              </div>
              <div style={{ padding: 8, background: "hsl(var(--secondary))", borderRadius: 6, fontSize: 12, marginBottom: 8 }}>
                Selected: <strong>{params.voice_name || "None"}</strong>
              </div>
              <div style={{ maxHeight: 200, overflowY: "auto", display: "flex", flexDirection: "column", gap: 3 }}>
                {filteredVoices.slice(0, 50).map((v: any) => {
                  const vid = `${v.name}-${v.gender}`;
                  return (
                    <div key={v.name} onClick={() => updateParams({ voice_name: vid })}
                      style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", borderRadius: 6, cursor: "pointer",
                        border: params.voice_name === vid ? "2px solid hsl(var(--primary))" : "1px solid hsl(var(--border))",
                        background: params.voice_name === vid ? "hsl(var(--primary) / 0.1)" : "transparent" }}>
                      <span style={{ fontSize: 14 }}>{v.gender === "Female" ? "\👩" : "\👨"}</span>
                      <div style={{ flex: 1, fontSize: 12 }}>
                        <div style={{ fontWeight: 500 }}>{v.display_name}</div>
                        <div style={{ fontSize: 10, color: "hsl(var(--muted-foreground))" }}>{v.locale}</div>
                      </div>
                      <button onClick={e => { e.stopPropagation(); handlePreviewVoice(v.name); }}
                        disabled={voicePreviewLoading === v.name}
                        style={{ ...btnOutline, fontSize: 10, padding: "3px 10px" }}>
                        {voicePreviewLoading === v.name ? "..." : "\u25B6 Preview"}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Voice rate */}
            <label><div style={labelStyle}>Voice Speed: {params.voice_rate || 1.0}x</div>
              <input type="range" min={0.5} max={2.0} step={0.05} value={params.voice_rate || 1.0}
                onChange={e => updateParams({ voice_rate: parseFloat(e.target.value) })} style={{ width: "100%" }} /></label>

            {/* BGM */}
            <div style={{ borderTop: "1px solid hsl(var(--border))", paddingTop: 16 }}>
              <div style={{ ...labelStyle, fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Background Music</div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
                <button onClick={() => updateParams({ bgm_type: "random", bgm_file: "" })}
                  style={{ ...btnOutline, fontSize: 11, border: (!params.bgm_type || params.bgm_type === "random") ? "2px solid hsl(var(--primary))" : btnOutline.border }}>\🎲 Random</button>
                <button onClick={() => updateParams({ bgm_type: "no", bgm_file: "" })}
                  style={{ ...btnOutline, fontSize: 11, border: params.bgm_type === "no" ? "2px solid hsl(var(--primary))" : btnOutline.border }}>\🔇 No BGM</button>
                <button onClick={() => bgmFileRef.current?.click()} disabled={bgmUploading}
                  style={{ ...btnOutline, fontSize: 11, borderStyle: "dashed" }}>{bgmUploading ? "Uploading..." : "+ Upload MP3"}</button>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {bgmList.map((bgm: any) => (
                  <div key={bgm.name} onClick={() => updateParams({ bgm_type: "custom", bgm_file: bgm.file })}
                    style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", borderRadius: 6, cursor: "pointer",
                      border: params.bgm_file === bgm.file ? "2px solid hsl(var(--primary))" : "1px solid hsl(var(--border))" }}>
                    <button onClick={e => { e.stopPropagation(); handlePlayBgm(bgm); }}
                      style={{ ...btnOutline, fontSize: 10, padding: "3px 10px", minWidth: 55 }}>
                      {playingBgm === bgm.name ? "\u23F8 Stop" : "\u25B6 Play"}
                    </button>
                    <span style={{ fontSize: 12 }}>\🎵 {bgm.name}</span>
                    <span style={{ fontSize: 10, color: "hsl(var(--muted-foreground))", marginLeft: "auto" }}>{(bgm.size / 1024 / 1024).toFixed(1)}MB</span>
                  </div>
                ))}
              </div>
              <label style={{ marginTop: 8, display: "block" }}><div style={labelStyle}>BGM Volume: {params.bgm_volume || 0.2}</div>
                <input type="range" min={0} max={1} step={0.05} value={params.bgm_volume || 0.2}
                  onChange={e => updateParams({ bgm_volume: parseFloat(e.target.value) })} style={{ width: "100%" }} /></label>
            </div>
          </div>
        )}

        {/* STEP 5: SUBTITLE */}
        {currentStep === 4 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
              <input type="checkbox" checked={params.subtitle_enabled ?? true} onChange={e => updateParams({ subtitle_enabled: e.target.checked })} />
              <span style={{ fontWeight: 600 }}>Enable Subtitles</span>
            </label>

            {params.subtitle_enabled !== false && (
              <>
                {/* LIVE PREVIEW */}
                <div style={{ background: "#000", borderRadius: 8, height: 180, display: "flex",
                  alignItems: params.subtitle_position === "top" ? "flex-start" : params.subtitle_position === "center" ? "center" : "flex-end",
                  justifyContent: "center", padding: 20, position: "relative", overflow: "hidden" }}>
                  <div style={{ position: "absolute", top: 8, right: 8, fontSize: 10, color: "#666" }}>PREVIEW</div>
                  <div style={{
                    fontSize: Math.min(params.font_size || 60, 40),
                    color: params.text_fore_color || "#FFFFFF",
                    WebkitTextStroke: `${Math.min(params.stroke_width || 1.5, 2)}px ${params.stroke_color || "#000000"}`,
                    backgroundColor: params.text_background_color === "transparent" ? "transparent" : (params.text_background_color || "transparent"),
                    padding: "4px 12px", textAlign: "center", maxWidth: "90%", lineHeight: 1.3,
                    fontFamily: (params.font_name || "").includes("Charm") ? "cursive" : (params.font_name || "").includes("Kabel") ? "fantasy" : "sans-serif",
                  }}>
                    The quick brown fox jumps
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <label><div style={labelStyle}>Position</div>
                    <select value={params.subtitle_position || "bottom"} onChange={e => updateParams({ subtitle_position: e.target.value })} style={selectStyle}>
                      <option value="top">Top</option><option value="center">Center</option><option value="bottom">Bottom</option>
                    </select></label>
                  <label><div style={labelStyle}>Font</div>
                    <select value={params.font_name || ""} onChange={e => updateParams({ font_name: e.target.value })} style={selectStyle}>
                      <option value="">Default (System)</option>
                      {AVAILABLE_FONTS.map(f => <option key={f} value={f}>{f.replace(/\.(ttf|ttc)$/, "")}</option>)}
                    </select></label>
                  <label><div style={labelStyle}>Font Size: {params.font_size || 60}px</div>
                    <input type="range" min={20} max={120} value={params.font_size || 60}
                      onChange={e => updateParams({ font_size: parseInt(e.target.value) })} style={{ width: "100%" }} /></label>
                  <label><div style={labelStyle}>Stroke Width: {params.stroke_width || 1.5}px</div>
                    <input type="range" min={0} max={5} step={0.5} value={params.stroke_width || 1.5}
                      onChange={e => updateParams({ stroke_width: parseFloat(e.target.value) })} style={{ width: "100%" }} /></label>
                  <label><div style={labelStyle}>Text Color</div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <input type="color" value={params.text_fore_color || "#FFFFFF"}
                        onChange={e => updateParams({ text_fore_color: e.target.value })} style={{ width: 40, height: 32, border: "none", cursor: "pointer" }} />
                      <input value={params.text_fore_color || "#FFFFFF"} onChange={e => updateParams({ text_fore_color: e.target.value })} style={{ ...inputStyle, width: 100 }} />
                    </div></label>
                  <label><div style={labelStyle}>Stroke Color</div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <input type="color" value={params.stroke_color || "#000000"}
                        onChange={e => updateParams({ stroke_color: e.target.value })} style={{ width: 40, height: 32, border: "none", cursor: "pointer" }} />
                      <input value={params.stroke_color || "#000000"} onChange={e => updateParams({ stroke_color: e.target.value })} style={{ ...inputStyle, width: 100 }} />
                    </div></label>
                  <label><div style={labelStyle}>Background Color</div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <input type="color" value={params.text_background_color === "transparent" ? "#000000" : (params.text_background_color || "#000000")}
                        onChange={e => updateParams({ text_background_color: e.target.value })} style={{ width: 40, height: 32, border: "none", cursor: "pointer" }} />
                      <button onClick={() => updateParams({ text_background_color: "transparent" })}
                        style={{ ...btnOutline, fontSize: 10, padding: "4px 8px" }}>Transparent</button>
                    </div></label>
                </div>
              </>
            )}
          </div>
        )}

        {/* STEP 6: MATERIALS */}
        {currentStep === 5 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <div style={labelStyle}>Video Source</div>
              <div style={{ display: "flex", gap: 8 }}>
                {["pexels", "pixabay", "local"].map(src => (
                  <button key={src} onClick={() => updateParams({ video_source: src } as any)}
                    style={{ ...btnOutline, flex: 1, textTransform: "capitalize",
                      border: (params.video_source || "pexels") === src ? "2px solid hsl(var(--primary))" : btnOutline.border }}>
                    {src === "pexels" ? "\🌐 Pexels (Stock)" : src === "pixabay" ? "\🌐 Pixabay (Stock)" : "\📁 Local Files"}
                  </button>
                ))}
              </div>
            </div>

            {(params.video_source || "pexels") !== "local" && (
              <div style={{ padding: 16, background: "hsl(var(--secondary))", borderRadius: 8, fontSize: 13 }}>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>Stock Video Mode</div>
                <div style={{ color: "hsl(var(--muted-foreground))", fontSize: 12 }}>
                  Videos will be automatically searched and downloaded based on your script content.
                  Make sure you have a {params.video_source === "pixabay" ? "Pixabay" : "Pexels"} API key configured in Settings.
                </div>
              </div>
            )}

            {params.video_source === "local" && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>Local Materials ({materialList.length} files)</div>
                  <button onClick={() => matFileRef.current?.click()} disabled={matUploading}
                    style={btnPrimary}>{matUploading ? "Uploading..." : "+ Upload Video/Image"}</button>
                </div>
                {materialList.length === 0 && (
                  <div style={{ padding: 30, textAlign: "center", color: "hsl(var(--muted-foreground))", border: "2px dashed hsl(var(--border))", borderRadius: 8 }}>
                    No local files yet. Upload videos (.mp4, .mov) or images (.jpg, .png) to use as materials.
                  </div>
                )}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 8 }}>
                  {materialList.map((m: any) => (
                    <div key={m.name} style={{ background: "hsl(var(--secondary))", borderRadius: 8, padding: 12 }}>
                      <div style={{ fontSize: 24, textAlign: "center", marginBottom: 4 }}>
                        {m.name.match(/\.(mp4|mov|avi)$/i) ? "\🎬" : "\🖼"}
                      </div>
                      <div style={{ fontSize: 11, fontWeight: 500, textAlign: "center", wordBreak: "break-all" }}>{m.name}</div>
                      <div style={{ fontSize: 10, color: "hsl(var(--muted-foreground))", textAlign: "center" }}>{(m.size / 1024 / 1024).toFixed(1)} MB</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 7: REVIEW & GENERATE */}
        {currentStep === 6 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ fontSize: 16, fontWeight: 600 }}>Review & Generate</div>

            {/* Summary */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 13 }}>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Subject:</span> {params.video_subject || "(custom script)"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Aspect:</span> {params.video_aspect || "16:9"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Voice:</span> {params.voice_name || "Default"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Transition:</span> {params.video_transition_mode || "FadeIn"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Color:</span> {(params as any).color_preset || "none"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Captions:</span> {(params as any).caption_style || "default"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Source:</span> {params.video_source || "pexels"}</div>
              <div><span style={{ color: "hsl(var(--muted-foreground))" }}>Script:</span> {params.video_script ? `${params.video_script.length} chars` : "Will generate"}</div>
            </div>

            {/* Script preview */}
            {params.video_script && (
              <details>
                <summary style={{ cursor: "pointer", fontSize: 13, color: "hsl(var(--muted-foreground))" }}>View Script</summary>
                <pre style={{ background: "hsl(var(--secondary))", padding: 12, borderRadius: 6, fontSize: 12, whiteSpace: "pre-wrap", maxHeight: 200, overflowY: "auto", marginTop: 8 }}>
                  {params.video_script}
                </pre>
              </details>
            )}

            {/* Progress */}
            {taskId && taskData && (
              <div style={{ padding: 16, background: "hsl(var(--secondary))", borderRadius: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <span>{(taskData as any).state === 1 ? "\u2705 Complete!" : (taskData as any).state === 4 ? "\u23F3 Processing..." : (taskData as any).state === -1 ? "\u274C Failed" : "Pending"}</span>
                  <span>{(taskData as any).progress || 0}%</span>
                </div>
                <div style={{ background: "hsl(var(--border))", borderRadius: 4, height: 8, overflow: "hidden" }}>
                  <div style={{ width: `${(taskData as any).progress || 0}%`, height: "100%", background: "hsl(var(--primary))", transition: "width 0.5s" }} />
                </div>
              </div>
            )}

            {/* Actions */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button onClick={async () => {
                try {
                  const s = await api.aiDirector(params.video_subject || "", params.video_script || "");
                  updateParams(s as any);
                } catch(e) { console.error(e); }
              }} style={{ ...btnOutline, borderColor: "hsl(var(--primary))", color: "hsl(var(--primary))" }}>
                \🤖 AI Director
              </button>
              <button onClick={handleGenerate} disabled={createVideo.isPending || (!!taskId && (taskData as any)?.state === 4)}
                style={{ ...btnPrimary, opacity: createVideo.isPending ? 0.5 : 1 }}>
                {createVideo.isPending ? "Starting..." : "\🚀 Generate Video"}
              </button>
              <button onClick={reset} style={btnOutline}>Reset All</button>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
        <button onClick={() => setStep(Math.max(0, currentStep - 1))} disabled={currentStep === 0}
          style={{ ...btnOutline, opacity: currentStep === 0 ? 0.3 : 1 }}>{"← Back"}</button>
        <button onClick={() => setStep(Math.min(STEPS.length - 1, currentStep + 1))} disabled={currentStep === STEPS.length - 1}
          style={{ ...btnPrimary, opacity: currentStep === STEPS.length - 1 ? 0.3 : 1 }}>{"Next →"}</button>
      </div>
    </div>
  );
}
