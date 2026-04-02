import { Link, useLocation } from "react-router-dom";
import { useAppStore } from "../../stores/appStore";
import { useTranslation } from "react-i18next";

const navItems = [
  { path: "/", icon: "\u{1F4CA}", labelKey: "nav.dashboard" },
  { path: "/create", icon: "\u{1F3AC}", labelKey: "nav.create" },
  { path: "/projects", icon: "\u{1F4C1}", labelKey: "nav.projects" },
  { path: "/plugins", icon: "\u{1F9E9}", labelKey: "nav.plugins" },
  { path: "/settings", icon: "\u2699\uFE0F", labelKey: "nav.settings" },
  { path: "/batch", icon: "\uD83D\uDCE6", labelKey: "nav.batch" },
  { path: "/schedule", icon: "\uD83D\uDCC5", labelKey: "nav.schedule" },
  { path: "/analytics", icon: "\uD83D\uDCC8", labelKey: "nav.analytics" },
  { path: "/manager", icon: "\uD83D\uDDC2\uFE0F", labelKey: "nav.manager" },
];

const bottomItems = [
  { path: "/license", icon: "\u{1F511}", labelKey: "nav.license" },
];

export function Sidebar() {
  const location = useLocation();
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggle = useAppStore((s) => s.toggleSidebar);
  const { t } = useTranslation();

  return (
    <aside
      style={{
        width: collapsed ? 60 : 220,
        borderRight: "1px solid hsl(var(--border))",
        backgroundColor: "hsl(var(--card))",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        transition: "width 0.2s",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          height: 56,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          borderBottom: "1px solid hsl(var(--border))",
          justifyContent: collapsed ? "center" : "space-between",
        }}
      >
        {!collapsed && (
          <span style={{ fontWeight: 700, fontSize: 14, whiteSpace: "nowrap" }}>
            AutoVideo
          </span>
        )}
        <button
          onClick={toggle}
          style={{
            background: "none",
            border: "none",
            color: "hsl(var(--muted-foreground))",
            cursor: "pointer",
            fontSize: 16,
            padding: 4,
          }}
        >
          {collapsed ? "\u2192" : "\u2190"}
        </button>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "8px" }}>
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "8px 12px",
                borderRadius: 6,
                textDecoration: "none",
                color: active ? "hsl(var(--primary-foreground))" : "hsl(var(--muted-foreground))",
                backgroundColor: active ? "hsl(var(--primary))" : "transparent",
                marginBottom: 2,
                fontSize: 14,
                transition: "all 0.15s",
              }}
            >
              <span style={{ fontSize: 16 }}>{item.icon}</span>
              {!collapsed && <span>{t(item.labelKey)}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div style={{ borderTop: "1px solid hsl(var(--border))", padding: "8px" }}>
        {bottomItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "8px 12px",
                borderRadius: 6,
                textDecoration: "none",
                color: active ? "hsl(var(--primary-foreground))" : "hsl(var(--muted-foreground))",
                backgroundColor: active ? "hsl(var(--primary))" : "transparent",
                fontSize: 14,
              }}
            >
              <span style={{ fontSize: 16 }}>{item.icon}</span>
              {!collapsed && <span>{t(item.labelKey)}</span>}
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
