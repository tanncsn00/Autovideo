import { useTranslation } from "react-i18next";
import { useTasks, useDeleteTask } from "../api/hooks";
import { useState, useRef, useEffect } from "react";
import { apiFetch } from "../api/client";
import { useAppStore } from "../stores/appStore";

const btnPrimary: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 6, border: "none", fontSize: 12, fontWeight: 600, cursor: "pointer",
  background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))",
};
const btnOutline: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 6, fontSize: 12, cursor: "pointer",
  border: "1px solid hsl(var(--border))", background: "transparent", color: "inherit",
};
const btnDanger: React.CSSProperties = {
  ...btnOutline, border: "1px solid hsl(var(--destructive))", color: "hsl(var(--destructive))",
};

export default function Projects() {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useTasks(page, 20);
  const deleteTask = useDeleteTask();
  const port = useAppStore((s) => s.sidecarPort);

  // Modal states
  const [selectedTask, setSelectedTask] = useState<any | null>(null);
  const [publishModal, setPublishModal] = useState<any | null>(null);
  const [scheduleModal, setScheduleModal] = useState<any | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState<any>(null);

  // Schedule form
  const [scheduleForm, setScheduleForm] = useState({
    platform: "tiktok-auto",
    title: "",
    description: "",
    tags: "",
    scheduled_time: "",
  });

  // Track which tasks are scheduled
  const [scheduledTasks, setScheduledTasks] = useState<Record<string, any>>({});

  // Load scheduled posts on mount
  useEffect(() => {
    apiFetch<any[]>("/api/v1/schedule").then(posts => {
      const arr = Array.isArray(posts) ? posts : [];
      const map: Record<string, any> = {};
      arr.forEach((p: any) => { map[p.task_id] = p; });
      setScheduledTasks(map);
    }).catch(() => {});
  }, []);

  const tasks = Array.isArray(data) ? data : (data as any)?.tasks || [];
  const total = (data as any)?.total || (Array.isArray(data) ? data.length : 0);
  const totalPages = Math.ceil(total / 20) || 1;

  const getStatusBadge = (state: number) => {
    if (state === 1) return { text: "Complete", color: "#22c55e", icon: "✅" };
    if (state === 4) return { text: "Processing", color: "#eab308", icon: "⏳" };
    if (state === -1) return { text: "Failed", color: "#ef4444", icon: "❌" };
    return { text: "Pending", color: "#6b7280", icon: "⏸" };
  };

  const getVideoUrl = (task: any) => {
    if (task.videos && task.videos.length > 0) {
      return task.videos[0];
    }
    return null;
  };

  const handlePublish = async (task: any, platforms: string[]) => {
    setPublishing(true);
    setPublishResult(null);
    try {
      const result = await apiFetch<any>("/api/v1/publish", {
        method: "POST",
        body: JSON.stringify({
          task_id: task.id,
          platforms,
          title: scheduleForm.title || task.script?.slice(0, 100) || "Video",
          description: scheduleForm.description || "",
          tags: scheduleForm.tags ? scheduleForm.tags.split(",").map((t: string) => t.trim()) : [],
        }),
      });
      setPublishResult(result);
    } catch (e: any) {
      setPublishResult({ error: e.message || "Publish failed" });
    }
    setPublishing(false);
  };

  const handleSchedule = async (task: any) => {
    try {
      await apiFetch("/api/v1/schedule", {
        method: "POST",
        body: JSON.stringify({
          task_id: task.id,
          platform: scheduleForm.platform,
          title: scheduleForm.title || "Scheduled Video",
          description: scheduleForm.description,
          tags: scheduleForm.tags ? scheduleForm.tags.split(",").map((t: string) => t.trim()) : [],
          scheduled_time: scheduleForm.scheduled_time,
        }),
      });
      setScheduledTasks(s => ({ ...s, [task.id]: { platform: scheduleForm.platform, scheduled_time: scheduleForm.scheduled_time, status: "pending" } }));
      setScheduleModal(null);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1000 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Projects</h1>

      {isLoading ? (
        <p style={{ color: "hsl(var(--muted-foreground))" }}>Loading...</p>
      ) : tasks.length === 0 ? (
        <div style={{ textAlign: "center", padding: 60, color: "hsl(var(--muted-foreground))" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🎬</div>
          <div style={{ fontSize: 16 }}>No videos yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>Go to Create Video to make your first video</div>
        </div>
      ) : (
        <>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {tasks.map((task: any) => {
              const badge = getStatusBadge(task.state);
              const videoUrl = getVideoUrl(task);
              const hasVideo = task.state === 1 && videoUrl;

              return (
                <div key={task.id}
                  style={{
                    background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8,
                    padding: 16, cursor: hasVideo ? "pointer" : "default",
                    transition: "border 0.15s",
                  }}
                  onClick={() => hasVideo && setSelectedTask(task)}
                  onMouseEnter={e => hasVideo && (e.currentTarget.style.borderColor = "hsl(var(--primary))")}
                  onMouseLeave={e => (e.currentTarget.style.borderColor = "hsl(var(--border))")}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                    {/* Video thumbnail / icon */}
                    <div style={{
                      width: 80, height: 56, borderRadius: 6, background: "hsl(var(--secondary))",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 24, flexShrink: 0,
                    }}>
                      {hasVideo ? "▶" : badge.icon}
                    </div>

                    {/* Info */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: 14, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {task.script ? task.script.slice(0, 80) + "..." : task.id.slice(0, 12)}
                      </div>
                      <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>
                        ID: {task.id.slice(0, 8)} · {task.terms ? task.terms.slice(0, 3).join(", ") : ""}
                      </div>
                      {task.state === 4 && (
                        <div style={{ marginTop: 4, background: "hsl(var(--secondary))", borderRadius: 4, height: 4, width: 200, overflow: "hidden" }}>
                          <div style={{ width: `${task.progress || 0}%`, height: "100%", background: badge.color, transition: "width 0.3s" }} />
                        </div>
                      )}
                    </div>

                    {/* Status badges */}
                    <div style={{ display: "flex", flexDirection: "column", gap: 4, alignItems: "flex-end" }}>
                      <span style={{ padding: "4px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600, color: "white", background: badge.color, whiteSpace: "nowrap" }}>
                        {badge.text}
                      </span>
                      {scheduledTasks[task.id] && (
                        <span style={{ padding: "3px 8px", borderRadius: 4, fontSize: 10, fontWeight: 600, color: "white", background: "#3b82f6", whiteSpace: "nowrap" }}>
                          📅 {scheduledTasks[task.id].platform === "tiktok-auto" ? "TikTok" : scheduledTasks[task.id].platform}
                          {scheduledTasks[task.id].scheduled_time && ` · ${new Date(scheduledTasks[task.id].scheduled_time).toLocaleDateString()}`}
                        </span>
                      )}
                    </div>

                    {/* Actions */}
                    <div style={{ display: "flex", gap: 4 }} onClick={e => e.stopPropagation()}>
                      {hasVideo && (
                        <>
                          <button onClick={() => setPublishModal(task)} style={btnPrimary}>Publish</button>
                          <button onClick={() => { setScheduleForm({ ...scheduleForm, title: task.script?.slice(0, 100) || "" }); setScheduleModal(task); }} style={btnOutline}>Schedule</button>
                        </>
                      )}
                      <button onClick={() => deleteTask.mutate(task.id)} style={btnDanger}>Delete</button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "center" }}>
              {Array.from({ length: totalPages }, (_, i) => (
                <button key={i} onClick={() => setPage(i + 1)}
                  style={{ ...btnOutline, background: page === i + 1 ? "hsl(var(--primary))" : "transparent", color: page === i + 1 ? "hsl(var(--primary-foreground))" : "inherit" }}>
                  {i + 1}
                </button>
              ))}
            </div>
          )}
        </>
      )}

      {/* ═══ VIDEO PREVIEW MODAL ═══ */}
      {selectedTask && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
          onClick={() => setSelectedTask(null)}>
          <div style={{ background: "hsl(var(--card))", borderRadius: 12, padding: 24, width: "90%", maxWidth: 700, maxHeight: "90vh", overflowY: "auto" }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontWeight: 700, fontSize: 18, margin: 0 }}>Video Preview</h3>
              <button onClick={() => setSelectedTask(null)} style={{ ...btnOutline, fontSize: 16, padding: "4px 12px" }}>×</button>
            </div>

            {/* Video player */}
            {selectedTask.videos && selectedTask.videos[0] && (
              <video
                controls
                autoPlay
                style={{ width: "100%", borderRadius: 8, background: "#000", maxHeight: 400 }}
                src={`http://127.0.0.1:${port}/tasks/${selectedTask.id}/final-1.mp4`}
              />
            )}

            {/* Script */}
            {selectedTask.script && (
              <details style={{ marginTop: 16 }}>
                <summary style={{ cursor: "pointer", fontSize: 13, fontWeight: 600 }}>Script</summary>
                <pre style={{ background: "hsl(var(--secondary))", padding: 12, borderRadius: 6, fontSize: 12, whiteSpace: "pre-wrap", marginTop: 8, maxHeight: 150, overflowY: "auto" }}>
                  {selectedTask.script}
                </pre>
              </details>
            )}

            {/* Terms */}
            {selectedTask.terms && (
              <div style={{ marginTop: 8, fontSize: 12, color: "hsl(var(--muted-foreground))" }}>
                Keywords: {Array.isArray(selectedTask.terms) ? selectedTask.terms.join(", ") : selectedTask.terms}
              </div>
            )}

            {/* Actions */}
            <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
              <button onClick={() => { setSelectedTask(null); setPublishModal(selectedTask); }} style={btnPrimary}>
                Publish Now
              </button>
              <button onClick={() => { setSelectedTask(null); setScheduleForm({ ...scheduleForm, title: selectedTask.script?.slice(0, 100) || "" }); setScheduleModal(selectedTask); }} style={btnOutline}>
                Schedule
              </button>
              {selectedTask.videos && selectedTask.videos[0] && (
                <a href={`http://127.0.0.1:${port}/api/v1/download/${selectedTask.id}/final-1.mp4`}
                  download style={{ ...btnOutline, textDecoration: "none", display: "inline-flex", alignItems: "center" }}>
                  Download
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ═══ PUBLISH MODAL ═══ */}
      {publishModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1001 }}
          onClick={() => { setPublishModal(null); setPublishResult(null); }}>
          <div style={{ background: "hsl(var(--card))", borderRadius: 12, padding: 24, width: "90%", maxWidth: 500 }}
            onClick={e => e.stopPropagation()}>
            <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 16 }}>Publish Video</h3>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Title</div>
                <input value={scheduleForm.title} onChange={e => setScheduleForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="Video title..."
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14 }} />
              </label>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Description</div>
                <textarea value={scheduleForm.description} onChange={e => setScheduleForm(f => ({ ...f, description: e.target.value }))}
                  rows={3} placeholder="Video description..."
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14, resize: "vertical" }} />
              </label>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Tags (comma separated)</div>
                <input value={scheduleForm.tags} onChange={e => setScheduleForm(f => ({ ...f, tags: e.target.value }))}
                  placeholder="viral, trending, ai"
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14 }} />
              </label>

              {/* Platform buttons */}
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Select Platform</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {[
                  { id: "tiktok-auto", name: "TikTok", icon: "🎵" },
                  { id: "youtube", name: "YouTube", icon: "📺" },
                  { id: "instagram", name: "Instagram", icon: "📸" },
                  { id: "facebook", name: "Facebook", icon: "👤" },
                ].map(p => (
                  <button key={p.id}
                    onClick={() => handlePublish(publishModal, [p.id])}
                    disabled={publishing}
                    style={{ ...btnPrimary, opacity: publishing ? 0.5 : 1, display: "flex", alignItems: "center", gap: 6 }}>
                    <span>{p.icon}</span> {p.name}
                  </button>
                ))}
              </div>

              {/* Result */}
              {publishResult && (
                <div style={{ padding: 12, borderRadius: 6, fontSize: 12, marginTop: 8,
                  background: publishResult.error ? "hsl(var(--destructive) / 0.1)" : "hsl(120 50% 20% / 0.3)",
                  color: publishResult.error ? "hsl(var(--destructive))" : "#22c55e" }}>
                  {publishResult.error ? `Error: ${publishResult.error}` : "Published successfully!"}
                  <pre style={{ marginTop: 4, fontSize: 11, whiteSpace: "pre-wrap" }}>{JSON.stringify(publishResult, null, 2)}</pre>
                </div>
              )}
            </div>

            <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
              <button onClick={() => { setPublishModal(null); setPublishResult(null); }} style={btnOutline}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ═══ SCHEDULE MODAL ═══ */}
      {scheduleModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1001 }}
          onClick={() => setScheduleModal(null)}>
          <div style={{ background: "hsl(var(--card))", borderRadius: 12, padding: 24, width: "90%", maxWidth: 500 }}
            onClick={e => e.stopPropagation()}>
            <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 16 }}>Schedule Video</h3>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Platform</div>
                <select value={scheduleForm.platform} onChange={e => setScheduleForm(f => ({ ...f, platform: e.target.value }))}
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit" }}>
                  <option value="tiktok-auto">🎵 TikTok</option>
                  <option value="youtube">📺 YouTube</option>
                  <option value="instagram">📸 Instagram</option>
                  <option value="facebook">👤 Facebook</option>
                </select>
              </label>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Title</div>
                <input value={scheduleForm.title} onChange={e => setScheduleForm(f => ({ ...f, title: e.target.value }))}
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14 }} />
              </label>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Tags</div>
                <input value={scheduleForm.tags} onChange={e => setScheduleForm(f => ({ ...f, tags: e.target.value }))}
                  placeholder="viral, trending"
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14 }} />
              </label>
              <label>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Schedule Time</div>
                <input type="datetime-local" value={scheduleForm.scheduled_time}
                  onChange={e => setScheduleForm(f => ({ ...f, scheduled_time: e.target.value }))}
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14 }} />
              </label>
            </div>

            <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
              <button onClick={() => handleSchedule(scheduleModal)}
                disabled={!scheduleForm.scheduled_time}
                style={{ ...btnPrimary, opacity: scheduleForm.scheduled_time ? 1 : 0.5 }}>
                Schedule
              </button>
              <button onClick={() => setScheduleModal(null)} style={btnOutline}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
