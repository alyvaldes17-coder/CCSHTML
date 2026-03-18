// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn get_hwid() -> String {
    let hostname = hostname::get()
        .unwrap_or_default()
        .to_string_lossy()
        .to_string();
    let cleaned: String = hostname
        .chars()
        .filter(|c| c.is_alphanumeric())
        .take(12)
        .collect();
    format!("AODA-{}", cleaned.to_uppercase())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .invoke_handler(tauri::generate_handler![greet, get_hwid])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
