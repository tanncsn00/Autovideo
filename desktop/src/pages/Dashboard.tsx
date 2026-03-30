import { useTranslation } from "react-i18next";
import { useSystemInfo } from "../api/hooks";
import { useTasks } from "../api/hooks";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const { t } = useTranslation();
  const { data: sysInfo } = useSystemInfo();
  const { data: tasksData } = useTasks(1, 6);

  const tasks = (tasksData as any)?.tasks || [];
  const totalVideos = (tasksData as any)?.total || 0;

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>{t("dashboard.title")}</h1>
      <p style={{ color: "hsl(var(--muted-foreground))", marginBottom: 24 }}>{t("dashboard.welcome")}</p>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 32 }}>
        <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 20 }}>
          <div style={{ color: "hsl(var(--muted-foreground))", fontSize: 14 }}>{t("dashboard.total_videos")}</div>
          <div style={{ fontSize: 32, fontWeight: 700, marginTop: 4 }}>{totalVideos}</div>
        </div>
        <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 20 }}>
          <div style={{ color: "hsl(var(--muted-foreground))", fontSize: 14 }}>Version</div>
          <div style={{ fontSize: 18, fontWeight: 600, marginTop: 8 }}>{(sysInfo as any)?.version || "..."}</div>
        </div>
        <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 20 }}>
          <Link to="/create" style={{ textDecoration: "none", color: "inherit" }}>
            <div style={{ fontSize: 14, color: "hsl(var(--muted-foreground))" }}>{t("dashboard.quick_create")}</div>
            <div style={{ fontSize: 24, marginTop: 8 }}>{"\u{1F3AC}"} +</div>
          </Link>
        </div>
      </div>

      {/* Recent Projects */}
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>{t("dashboard.recent")}</h2>
      {tasks.length === 0 ? (
        <p style={{ color: "hsl(var(--muted-foreground))" }}>{t("dashboard.no_projects")}</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: 12 }}>
          {tasks.map((task: any) => (
            <div
              key={task.id}
              style={{
                background: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: 8,
                padding: 16,
              }}
            >
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{task.id?.slice(0, 8)}...</div>
              <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))" }}>
                {task.state === 1 ? "\u2705 Complete" : task.state === 4 ? "\u23F3 Processing" : task.state === -1 ? "\u274C Failed" : "\u23F8 Pending"}
              </div>
              {task.state === 4 && (
                <div style={{ marginTop: 8, background: "hsl(var(--secondary))", borderRadius: 4, height: 4, overflow: "hidden" }}>
                  <div style={{ width: `${task.progress || 0}%`, height: "100%", background: "hsl(var(--primary))", transition: "width 0.3s" }} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
