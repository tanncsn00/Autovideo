import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { useSidecarStatus } from "../../hooks/useSidecarStatus";

export function AppShell() {
  const ready = useSidecarStatus();

  if (!ready) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          backgroundColor: "hsl(var(--background))",
          flexDirection: "column",
          gap: 16,
        }}
      >
        <div style={{ fontSize: 32, animation: "spin 1s linear infinite" }}>&#x27F3;</div>
        <p style={{ color: "hsl(var(--muted-foreground))" }}>Starting MoneyPrinterTurbo...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar />
      <main style={{ flex: 1, overflow: "auto" }}>
        <Outlet />
      </main>
    </div>
  );
}
