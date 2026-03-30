import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Schedule() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const { data: posts } = useQuery({ queryKey: ["schedule"], queryFn: () => api.getScheduledPosts() });
  const cancelPost = useMutation({ mutationFn: api.cancelScheduledPost, onSuccess: () => qc.invalidateQueries({ queryKey: ["schedule"] }) });
  const deletePost = useMutation({ mutationFn: api.deleteScheduledPost, onSuccess: () => qc.invalidateQueries({ queryKey: ["schedule"] }) });

  const postList = Array.isArray(posts) ? posts : [] as any[];

  const statusColor = (s: string) => s === "published" ? "#22c55e" : s === "pending" ? "#eab308" : s === "publishing" ? "#3b82f6" : "#ef4444";

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Content Schedule</h1>
      {postList.length === 0 ? (
        <p style={{ color: "hsl(var(--muted-foreground))" }}>No scheduled posts. Schedule videos from the Create or Projects page.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {postList.map((post: any) => (
            <div key={post.id} style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 16, display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{post.title}</div>
                <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))", marginTop: 2 }}>
                  {post.platform} · {new Date(post.scheduled_time).toLocaleString()}
                </div>
              </div>
              <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600, color: "white", background: statusColor(post.status) }}>
                {post.status}
              </span>
              {post.status === "pending" && (
                <button onClick={() => cancelPost.mutate(post.id)}
                  style={{ padding: "4px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "transparent", color: "inherit", cursor: "pointer", fontSize: 12 }}>
                  Cancel
                </button>
              )}
              <button onClick={() => deletePost.mutate(post.id)}
                style={{ padding: "4px 12px", borderRadius: 6, border: "1px solid hsl(var(--destructive))", background: "transparent", color: "hsl(var(--destructive))", cursor: "pointer", fontSize: 12 }}>
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
