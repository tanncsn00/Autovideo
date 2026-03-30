use keyring::Entry;

const SERVICE: &str = "MoneyPrinterTurbo";

#[tauri::command]
pub fn set_secret(key: &str, value: &str) -> Result<(), String> {
    let entry = Entry::new(SERVICE, key).map_err(|e| e.to_string())?;
    entry.set_password(value).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub fn get_secret(key: &str) -> Result<Option<String>, String> {
    let entry = Entry::new(SERVICE, key).map_err(|e| e.to_string())?;
    match entry.get_password() {
        Ok(password) => Ok(Some(password)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(keyring::Error::PlatformFailure(_)) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub fn delete_secret(key: &str) -> Result<(), String> {
    let entry = Entry::new(SERVICE, key).map_err(|e| e.to_string())?;
    match entry.delete_credential() {
        Ok(_) => Ok(()),
        Err(keyring::Error::NoEntry) => Ok(()),
        Err(keyring::Error::PlatformFailure(_)) => Ok(()),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub fn get_sidecar_port(state: tauri::State<'_, crate::SidecarPort>) -> u16 {
    state.0
}
