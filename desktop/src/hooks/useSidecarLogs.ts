import { useState, useEffect } from "react";

const isTauri = typeof window !== "undefined" && "__TAURI__" in window;

export function useSidecarLogs(maxLines = 500) {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    if (!isTauri) return;

    let unlisten: (() => void) | null = null;

    import("@tauri-apps/api/event").then(({ listen }) => {
      listen<string>("sidecar-log", (event) => {
        setLogs((prev) => [...prev.slice(-(maxLines - 1)), event.payload]);
      }).then((fn) => {
        unlisten = fn;
      });
    });

    return () => {
      unlisten?.();
    };
  }, [maxLines]);

  return logs;
}
