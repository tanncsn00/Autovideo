import { useEffect } from "react";
import { useAppStore } from "../stores/appStore";
import { api } from "../api/client";

export function useSidecarStatus() {
  const setSidecarReady = useAppStore((s) => s.setSidecarReady);
  const sidecarReady = useAppStore((s) => s.sidecarReady);

  useEffect(() => {
    if (sidecarReady) return;

    const interval = setInterval(async () => {
      try {
        await api.ping();
        setSidecarReady(true);
        clearInterval(interval);
      } catch {
        // Still waiting
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [sidecarReady, setSidecarReady]);

  return sidecarReady;
}
