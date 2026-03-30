// Tauri keychain integration - will use invoke() when Tauri is available
const isTauri = typeof window !== "undefined" && "__TAURI__" in window;

export async function getSecret(key: string): Promise<string | null> {
  if (isTauri) {
    const { invoke } = await import("@tauri-apps/api/core");
    return invoke<string | null>("get_secret", { key });
  }
  // Fallback for browser dev: use localStorage
  return localStorage.getItem(`mpt_secret_${key}`);
}

export async function setSecret(key: string, value: string): Promise<void> {
  if (isTauri) {
    const { invoke } = await import("@tauri-apps/api/core");
    return invoke("set_secret", { key, value });
  }
  localStorage.setItem(`mpt_secret_${key}`, value);
}

export async function deleteSecret(key: string): Promise<void> {
  if (isTauri) {
    const { invoke } = await import("@tauri-apps/api/core");
    return invoke("delete_secret", { key });
  }
  localStorage.removeItem(`mpt_secret_${key}`);
}
