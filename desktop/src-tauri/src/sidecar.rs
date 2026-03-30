use std::net::TcpListener;
use std::time::Duration;

/// Find an available port, starting from preferred
pub fn find_available_port(preferred: u16) -> u16 {
    for port in preferred..=(preferred + 100) {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    panic!(
        "No available port found in range {}-{}",
        preferred,
        preferred + 100
    );
}

/// Wait for sidecar HTTP server to respond
pub async fn wait_for_ready(url: &str, timeout_ms: u64) -> Result<(), String> {
    let start = std::time::Instant::now();
    let timeout = Duration::from_millis(timeout_ms);
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build()
        .map_err(|e| e.to_string())?;

    loop {
        if start.elapsed() > timeout {
            return Err(format!("Sidecar did not start within {}ms", timeout_ms));
        }

        match client.get(url).send().await {
            Ok(resp) if resp.status().is_success() => {
                return Ok(());
            }
            _ => {
                tokio::time::sleep(Duration::from_millis(500)).await;
            }
        }
    }
}
