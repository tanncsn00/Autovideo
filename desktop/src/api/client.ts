import { useAppStore } from "../stores/appStore";

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
  getMusics: () => apiFetch<Record<string, unknown>>("/api/v1/musics"),
  getVideoMaterials: () => apiFetch<Record<string, unknown>>("/api/v1/video_materials"),
  getTemplates: (category?: string) =>
    apiFetch<Record<string, unknown>[]>(category ? `/api/v1/templates?category=${category}` : "/api/v1/templates"),
  applyTemplate: (templateId: string, overrides?: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>("/api/v1/templates/apply", {
      method: "POST",
      body: JSON.stringify({ template_id: templateId, overrides: overrides || {} }),
    }),
  getColorPresets: () => apiFetch<string[]>("/api/v1/effects/presets"),
  getCaptionStyles: () => apiFetch<string[]>("/api/v1/effects/caption-styles"),

  // Batch
  createBatch: (topics: Record<string, unknown>[], name?: string, maxConcurrent?: number) =>
    apiFetch<Record<string, unknown>>("/api/v1/batch", {
      method: "POST",
      body: JSON.stringify({ topics, name: name || "", max_concurrent: maxConcurrent || 2 }),
    }),
  startBatch: (jobId: string) => apiFetch<Record<string, unknown>>(`/api/v1/batch/${jobId}/start`, { method: "POST" }),
  getBatches: () => apiFetch<Record<string, unknown>[]>("/api/v1/batch"),
  getBatch: (jobId: string) => apiFetch<Record<string, unknown>>(`/api/v1/batch/${jobId}`),
  cancelBatch: (jobId: string) => apiFetch<Record<string, unknown>>(`/api/v1/batch/${jobId}/cancel`, { method: "POST" }),

  // Schedule
  schedulePost: (data: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>("/api/v1/schedule", { method: "POST", body: JSON.stringify(data) }),
  getScheduledPosts: (status?: string) =>
    apiFetch<Record<string, unknown>[]>(status ? `/api/v1/schedule?status=${status}` : "/api/v1/schedule"),
  cancelScheduledPost: (postId: string) =>
    apiFetch<Record<string, unknown>>(`/api/v1/schedule/${postId}/cancel`, { method: "POST" }),
  deleteScheduledPost: (postId: string) =>
    apiFetch<Record<string, unknown>>(`/api/v1/schedule/${postId}`, { method: "DELETE" }),

  // Analytics
  getAnalyticsSummary: (platform?: string) =>
    apiFetch<Record<string, unknown>>(platform ? `/api/v1/analytics/summary?platform=${platform}` : "/api/v1/analytics/summary"),
  getAnalyticsTop: (metric?: string, limit?: number) =>
    apiFetch<Record<string, unknown>[]>(`/api/v1/analytics/top?metric=${metric || "views"}&limit=${limit || 10}`),
  getAnalyticsTrend: (days?: number) =>
    apiFetch<Record<string, unknown>[]>(`/api/v1/analytics/trend?days=${days || 30}`),

  // Input processors
  processURL: (url: string, templateId?: string) =>
    apiFetch<Record<string, unknown>>("/api/v1/input/url", {
      method: "POST",
      body: JSON.stringify({ url, template_id: templateId || "" }),
    }),
  processRSS: (feedUrl: string, templateId?: string, maxItems?: number) =>
    apiFetch<Record<string, unknown>[]>("/api/v1/input/rss", {
      method: "POST",
      body: JSON.stringify({ feed_url: feedUrl, template_id: templateId || "", max_items: maxItems || 10 }),
    }),
  aiDirector: (subject: string, script?: string, platform?: string) =>
    apiFetch<Record<string, unknown>>("/api/v1/input/ai-director", {
      method: "POST",
      body: JSON.stringify({ subject, script: script || "", platform: platform || "general" }),
    }),
};
