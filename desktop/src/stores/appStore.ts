import { create } from "zustand";

interface AppState {
  sidecarPort: number;
  sidecarReady: boolean;
  sidebarCollapsed: boolean;
  theme: "light" | "dark";
  setSidecarPort: (port: number) => void;
  setSidecarReady: (ready: boolean) => void;
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidecarPort: 18080,
  sidecarReady: false,
  sidebarCollapsed: false,
  theme: "dark",
  setSidecarPort: (port) => set({ sidecarPort: port }),
  setSidecarReady: (ready) => set({ sidecarReady: ready }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setTheme: (theme) => set({ theme }),
}));
