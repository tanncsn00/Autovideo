import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Batch() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [topicsText, setTopicsText] = useState("");
  const [jobName, setJobName] = useState("");

  const { data: batches } = useQuery({ queryKey: ["batches"], queryFn: api.getBatches, refetchInterval: 3000 });
  const createBatch = useMutation({
    mutationFn: () => {
      const topics = topicsText.split("\n").filter(l => l.trim()).map(line => {
        const parts = line.split(",").map(s => s.trim());
        return { topic: parts[0], template_id: parts[1] || "", platform: parts[2] || "general" };
      });
      return api.createBatch(topics, jobName);
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["batches"] }); setTopicsText(""); },
  });
  const startBatch = useMutation({ mutationFn: api.startBatch, onSuccess: () => qc.invalidateQueries({ queryKey: ["batches"] }) });

  const batchList = Array.isArray(batches) ? batches : [] as any[];

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Batch Production</h1>

      {/* Create batch */}
      <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 20, marginBottom: 24 }}>
        <h3 style={{ fontWeight: 600, marginBottom: 12 }}>Create Batch Job</h3>
        <input value={jobName} onChange={e => setJobName(e.target.value)} placeholder="Job name (optional)"
          style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", marginBottom: 12 }} />
        <textarea value={topicsText} onChange={e => setTopicsText(e.target.value)} rows={6}
          placeholder={"Enter topics (one per line):\nAI Trends 2026, tiktok-trending-facts, tiktok\nCooking Tips, , youtube\nStock Market Tips"}
          style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 13, fontFamily: "monospace", resize: "vertical" }} />
        <p style={{ fontSize: 11, color: "hsl(var(--muted-foreground))", margin: "6px 0 12px" }}>Format: topic, template_id (optional), platform (optional)</p>
        <button onClick={() => createBatch.mutate()} disabled={!topicsText.trim()}
          style={{ padding: "10px 24px", borderRadius: 6, border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))", cursor: "pointer", fontWeight: 600, opacity: topicsText.trim() ? 1 : 0.5 }}>
          Create Batch
        </button>
      </div>

      {/* Jobs list */}
      <h3 style={{ fontWeight: 600, marginBottom: 12 }}>Jobs</h3>
      {batchList.length === 0 ? (
        <p style={{ color: "hsl(var(--muted-foreground))" }}>No batch jobs yet</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {batchList.map((job: any) => (
            <div key={job.id} style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 16 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <div>
                  <span style={{ fontWeight: 600 }}>{job.name}</span>
                  <span style={{ marginLeft: 8, fontSize: 12, color: "hsl(var(--muted-foreground))" }}>{job.completed}/{job.total} videos</span>
                </div>
                <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600,
                  background: job.status === "completed" ? "#22c55e" : job.status === "processing" ? "#eab308" : job.status === "failed" ? "#ef4444" : "hsl(var(--secondary))",
                  color: "white" }}>{job.status}</span>
              </div>
              <div style={{ background: "hsl(var(--secondary))", borderRadius: 4, height: 6, overflow: "hidden" }}>
                <div style={{ width: `${job.progress || 0}%`, height: "100%", background: "hsl(var(--primary))", transition: "width 0.3s" }} />
              </div>
              {job.status === "pending" && (
                <button onClick={() => startBatch.mutate(job.id)}
                  style={{ marginTop: 8, padding: "6px 16px", borderRadius: 6, border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))", cursor: "pointer", fontSize: 12 }}>
                  Start
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
