import { useTranslation } from "react-i18next";
import { useState } from "react";

export default function License() {
  const { t } = useTranslation();
  const [key, setKey] = useState("");

  return (
    <div style={{ padding: 24, maxWidth: 600 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>{t("license.title")}</h1>

      <div style={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, padding: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <span style={{ padding: "4px 12px", borderRadius: 4, fontSize: 12, fontWeight: 600, background: "hsl(var(--secondary))", color: "hsl(var(--muted-foreground))" }}>
            {t("license.free")}
          </span>
        </div>
        <label>
          <div style={{ marginBottom: 6, fontSize: 14, fontWeight: 500 }}>License Key</div>
          <input value={key} onChange={(e) => setKey(e.target.value)}
            placeholder={t("license.placeholder")}
            style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid hsl(var(--border))", background: "hsl(var(--input))", color: "inherit", fontSize: 14 }}
          />
        </label>
        <button disabled={!key.trim()}
          style={{ marginTop: 16, padding: "10px 24px", borderRadius: 6, border: "none", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))", cursor: "pointer", fontWeight: 600, opacity: key.trim() ? 1 : 0.5 }}>
          {t("license.activate")}
        </button>
        <p style={{ marginTop: 16, fontSize: 12, color: "hsl(var(--muted-foreground))" }}>
          License activation will be available in a future update.
        </p>
      </div>
    </div>
  );
}
