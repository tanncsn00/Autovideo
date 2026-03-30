mod commands;
mod sidecar;

use tauri::Manager;

pub struct SidecarPort(pub u16);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.set_focus();
            }
        }))
        .invoke_handler(tauri::generate_handler![
            commands::set_secret,
            commands::get_secret,
            commands::delete_secret,
            commands::get_sidecar_port,
        ])
        .setup(|app| {
            // In dev mode: use fixed port 18080 (sidecar started manually)
            // In prod mode: find available port and launch sidecar
            let port: u16 = if cfg!(debug_assertions) { 18080 } else { sidecar::find_available_port(18080) };
            app.manage(SidecarPort(port));

            // Show window immediately — React handles loading state
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
            }

            if !cfg!(debug_assertions) {
                let app_handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    let pid = std::process::id();
                    let sidecar_result = std::process::Command::new("python-backend")
                        .arg("--port")
                        .arg(port.to_string())
                        .arg("--mode")
                        .arg("desktop")
                        .arg("--parent-pid")
                        .arg(pid.to_string())
                        .spawn();

                    match sidecar_result {
                        Ok(_) => println!("Sidecar spawned on port {}", port),
                        Err(e) => eprintln!("Failed to spawn sidecar: {}", e),
                    }
                });
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
