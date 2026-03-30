import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Analytics() {
  const { t } = useTranslation();
  const { data: summary } = useQuery({ queryKey: ["analytics-summary"], queryFn: () => api.getAnalyticsSummary() });
  const { data: topVideos } = useQuery({ queryKey: ["analytics-top"], queryFn: () => api.getAnalyticsTop("views", 5) });
  const { data: trend } = useQuery({ queryKey: ["analytics-trend"], queryFn: () => api.getAnalyticsTrend(14) });

  const stats = (summary && typeof summary === "object" && !Array.isArray(summary) ? summary : {}) as any;
  const top = Array.isArray(topVideos) ? topVideos : [] as any[];
  const trendData = Array.isArray(trend) ? trend : [] as any[];

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Analytics</h1>

      {/* Summary cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 32 }}>
        {[
          { label: "Total Videos", value: stats.total_videos || 0 },
          { label: "Total Views", value: (stats.total_views || 0).toLocaleString() },
          { label: "Total Likes", value: (stats.total_likes || 0).toLocaleString() },
          { label: "Watch Hours", value: (stats.total_watch_hours || 0).toFixed(1) },
        ].map(card => (
          <div key={card.label} style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 16 }}>
            <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))" }}>{card.label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>{card.value}</div>
          </div>
        ))}
      </div>

      {/* Top performing */}
      <h3 style={{ fontWeight: 600, marginBottom: 12 }}>Top Performing Videos</h3>
      {top.length === 0 ? (
        <p style={{ color: "hsl(var(--muted-foreground))", marginBottom: 32 }}>No analytics data yet. Publish some videos first!</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 32 }}>
          {top.map((v: any, i: number) => (
            <div key={i} style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 12, display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ fontWeight: 700, fontSize: 18, width: 30, textAlign: "center", color: "hsl(var(--muted-foreground))" }}>#{i + 1}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{v.task_id?.slice(0, 12)}...</div>
                <div style={{ fontSize: 11, color: "hsl(var(--muted-foreground))" }}>{v.platform}</div>
              </div>
              <div style={{ fontWeight: 700 }}>{(v.views || 0).toLocaleString()} views</div>
            </div>
          ))}
        </div>
      )}

      {/* Trend */}
      {trendData.length > 0 && (
        <>
          <h3 style={{ fontWeight: 600, marginBottom: 12 }}>Daily Trend (14 days)</h3>
          <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 16 }}>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 120 }}>
              {trendData.map((d: any, i: number) => {
                const maxViews = Math.max(...trendData.map((x: any) => x.views || 1));
                const height = Math.max(4, ((d.views || 0) / maxViews) * 100);
                return (
                  <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                    <div style={{ width: "100%", height: `${height}%`, background: "hsl(var(--primary))", borderRadius: "4px 4px 0 0", minHeight: 4 }} />
                    <span style={{ fontSize: 9, color: "hsl(var(--muted-foreground))", transform: "rotate(-45deg)", whiteSpace: "nowrap" }}>
                      {d.snapshot_date?.slice(5)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
