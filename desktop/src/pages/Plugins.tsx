import { useTranslation } from "react-i18next";
import { usePlugins } from "../api/hooks";
import { apiFetch } from "../api/client";
import type { PluginInfo } from "../api/types";

export default function Plugins() {
  const { t } = useTranslation();
  const { data: plugins, refetch } = usePlugins();

  const pluginList = (Array.isArray(plugins) ? plugins : []) as unknown as PluginInfo[];
  const groups: Record<string, PluginInfo[]> = {};
  pluginList.forEach((p) => {
    if (!groups[p.plugin_type]) groups[p.plugin_type] = [];
    groups[p.plugin_type].push(p);
  });

  const handleActivate = async (type: string, name: string) => {
    await apiFetch(`/api/v1/plugins/${type}/${name}/activate`, { method: "POST" });
    refetch();
  };

  const typeLabels: Record<string, string> = {
    llm: t("plugins.llm"),
    tts: t("plugins.tts"),
    material: t("plugins.material"),
  };

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>{t("plugins.title")}</h1>

      {Object.entries(groups).map(([type, items]) => (
        <div key={type} style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12, color: "hsl(var(--muted-foreground))" }}>
            {typeLabels[type] || type.toUpperCase()}
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
            {items.map((plugin) => (
              <div key={plugin.name}
                style={{
                  background: "hsl(var(--card))",
                  border: `1px solid ${plugin.active ? "hsl(var(--primary))" : "hsl(var(--border))"}`,
                  borderRadius: 8,
                  padding: 16,
                  position: "relative",
                }}>
                {plugin.active && (
                  <span style={{ position: "absolute", top: 8, right: 8, padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600, background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))" }}>
                    {t("plugins.active")}
                  </span>
                )}
                <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>{plugin.display_name}</div>
                <div style={{ fontSize: 12, color: "hsl(var(--muted-foreground))", marginBottom: 8 }}>{plugin.description}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: plugin.available ? "#22c55e" : "#ef4444" }} />
                  <span>{plugin.available ? t("plugins.available") : t("plugins.unavailable")}</span>
                  <span style={{ color: "hsl(var(--muted-foreground))" }}>v{plugin.version}</span>
                </div>
                {!plugin.active && (
                  <button onClick={() => handleActivate(plugin.plugin_type, plugin.name)}
                    style={{ marginTop: 12, padding: "6px 16px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "transparent", color: "inherit", cursor: "pointer", fontSize: 12 }}>
                    {t("plugins.activate")}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      {pluginList.length === 0 && (
        <p style={{ color: "hsl(var(--muted-foreground))" }}>{t("plugins.no_plugins")}</p>
      )}
    </div>
  );
}
