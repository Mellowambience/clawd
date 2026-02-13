// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;
use std::fs;

// Luna Agent Commands
#[tauri::command]
async fn luna_scan_workspace() -> Result<String, String> {
    let client = reqwest::Client::new();
    match client.get("http://127.0.0.1:8766/workspace/scan")
        .send()
        .await
    {
        Ok(response) => {
            match response.text().await {
                Ok(body) => Ok(body),
                Err(e) => Err(format!("Failed to read response: {}", e))
            }
        },
        Err(e) => Err(format!("Luna agent offline: {}", e))
    }
}

#[tauri::command]
async fn luna_read_file(path: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    let payload = serde_json::json!({"path": path});
    
    match client.post("http://127.0.0.1:8766/file/read")
        .json(&payload)
        .send()
        .await
    {
        Ok(response) => {
            match response.text().await {
                Ok(body) => Ok(body),
                Err(e) => Err(format!("Failed to read response: {}", e))
            }
        },
        Err(e) => Err(format!("Luna agent offline: {}", e))
    }
}

#[tauri::command]
async fn luna_execute_command(command: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    let payload = serde_json::json!({"command": command});
    
    match client.post("http://127.0.0.1:8766/execute/shell")
        .json(&payload)
        .send()
        .await
    {
        Ok(response) => {
            match response.text().await {
                Ok(body) => Ok(body),
                Err(e) => Err(format!("Failed to read response: {}", e))
            }
        },
        Err(e) => Err(format!("Luna agent offline: {}", e))
    }
}

#[tauri::command]
async fn luna_get_state() -> Result<String, String> {
    let client = reqwest::Client::new();
    match client.get("http://127.0.0.1:8766/state")
        .send()
        .await
    {
        Ok(response) => {
            match response.text().await {
                Ok(body) => Ok(body),
                Err(e) => Err(format!("Failed to read response: {}", e))
            }
        },
        Err(e) => Err(format!("Luna agent offline: {}", e))
    }
}

fn main() {
    // CRITICAL: Force WebView2 transparency at the engine level
    std::env::set_var("WEBVIEW2_DEFAULT_BACKGROUND_COLOR", "0");

    let toggle_maintenance = tauri::CustomMenuItem::new("toggle_maintenance".to_string(), "Toggle Maintenance Mode");
    let quit = tauri::CustomMenuItem::new("quit".to_string(), "Quit");
    let tray_menu = tauri::SystemTrayMenu::new()
        .add_item(toggle_maintenance)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    let system_tray = tauri::SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            luna_scan_workspace,
            luna_read_file,
            luna_execute_command,
            luna_get_state
        ])
        .setup(|app| {
            let window = app.get_window("MistLuna").unwrap();
            
            // Force decorations off and show (this helps with shadows/squares on Windows)
            window.set_decorations(false).unwrap();
            
            // Move to a default corner position instead of center-stuck
            window.set_position(tauri::Position::Physical(tauri::PhysicalPosition { x: 100, y: 100 })).unwrap();
            
            window.show().unwrap();
            Ok(())
        })
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            tauri::SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "quit" => {
                        std::process::exit(0);
                    }
                    "toggle_maintenance" => {
                        let flag_path = r"c:\Users\nator\clawd\data\maintenance_mode.flag";
                        let current = fs::read_to_string(flag_path).unwrap_or_else(|_| "OFF".to_string());
                        let new = if current.trim() == "ON" { "OFF" } else { "ON" };
                        
                        // Ensure directory exists
                        if let Some(parent) = std::path::Path::new(flag_path).parent() {
                            fs::create_dir_all(parent).unwrap_or(());
                        }

                        fs::write(flag_path, new).expect("failed to write flag");
                        
                        // Notify all windows
                        app.emit_all("maintenance-toggled", new).unwrap();
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
