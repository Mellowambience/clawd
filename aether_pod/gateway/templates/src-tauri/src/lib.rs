#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  use tauri::image::Image;
  use tauri::menu::{Menu, MenuItem};
  use tauri::path::BaseDirectory;
  use tauri::tray::TrayIconBuilder;
  use tauri::{AppHandle, Manager, State};
  use tauri_plugin_global_shortcut::{Code, Modifiers, ShortcutState};
  use tauri_plugin_notification::NotificationExt;
  use std::fs;
  use std::path::PathBuf;
  use std::sync::Mutex;

  #[derive(Clone)]
  struct TrayIcons {
    normal: Image<'static>,
    cyan: Image<'static>,
    red: Image<'static>,
    idle: Image<'static>,
  }

  struct SilenceState {
    enabled: bool,
  }

  const SILENCE_FLAG_PATH: &str = "C:\\Users\\nator\\clawd\\data\\silence.flag";

  fn load_icon(app: &AppHandle, rel_path: &str) -> tauri::Result<Image<'static>> {
    let path = app.path().resolve(rel_path, BaseDirectory::Resource)?;
    Ok(Image::from_path(path)?.to_owned())
  }

  fn apply_silence(app: &AppHandle, enabled: bool) -> Result<(), String> {
    let path = PathBuf::from(SILENCE_FLAG_PATH);
    if enabled {
      if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
      }
      fs::write(&path, b"silence").map_err(|e| e.to_string())?;
      let _ = app
        .notification()
        .builder()
        .title("MistLuna")
        .body("silence enabled")
        .show();
    } else {
      let _ = fs::remove_file(&path);
      let _ = app
        .notification()
        .builder()
        .title("MistLuna")
        .body("silence disabled")
        .show();
    }
    Ok(())
  }

  #[tauri::command]
  fn set_tray_state(
    app: AppHandle,
    state: String,
    icons: State<TrayIcons>,
  ) -> Result<(), String> {
    let icon = match state.as_str() {
      "cyan" => &icons.cyan,
      "red" => &icons.red,
      "idle" => &icons.idle,
      _ => &icons.normal,
    };
    if let Some(tray) = app.tray_by_id("mist_tray") {
      tray.set_icon(Some(icon.clone())).map_err(|e| e.to_string())?;
    }
    Ok(())
  }

  #[tauri::command]
  fn notify(app: AppHandle, title: String, body: String) -> Result<(), String> {
    app
      .notification()
      .builder()
      .title(title)
      .body(body)
      .show()
      .map_err(|e| e.to_string())
  }

  tauri::Builder::default()
    .plugin(tauri_plugin_notification::init())
    .plugin(
      tauri_plugin_global_shortcut::Builder::new()
        .with_shortcuts(["super+shift+KeyL", "super+alt+KeyQ"])? // Win+Shift+L, Win+Alt+Q
        .with_handler(|app, shortcut, event| {
          if event.state != ShortcutState::Pressed {
            return;
          }
          if shortcut.matches(Modifiers::SUPER | Modifiers::SHIFT, Code::KeyL) {
            if let Some(window) = app.get_webview_window("main") {
              let is_visible = window.is_visible().unwrap_or(true);
              if is_visible {
                let _ = window.hide();
              } else {
                let _ = window.show();
                let _ = window.set_focus();
              }
            }
          }
          if shortcut.matches(Modifiers::SUPER | Modifiers::ALT, Code::KeyQ) {
            let state = app.state::<Mutex<SilenceState>>();
            let mut guard = state.lock().unwrap();
            guard.enabled = !guard.enabled;
            let _ = apply_silence(app, guard.enabled);
          }
        })
        .build(),
    )
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      let icons = TrayIcons {
        normal: load_icon(app, "icons/32x32.png")?,
        cyan: load_icon(app, "icons/tray_cyan.png")?,
        red: load_icon(app, "icons/tray_red.png")?,
        idle: load_icon(app, "icons/tray_idle.png")?,
      };
      app.manage(icons);

      app.manage(Mutex::new(SilenceState { enabled: false }));

      // Tray menu (right-click pulsing icon)
      let show = MenuItem::with_id(app, "show", "Show", true, None::<&str>)?;
      let silence = MenuItem::with_id(app, "silence", "Enter Silence", true, None::<&str>)?;
      let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
      let menu = Menu::with_items(app, &[&show, &silence, &quit])?;

      TrayIconBuilder::with_id("mist_tray")
        .menu(&menu)
        .icon(load_icon(app, "icons/32x32.png")?)
        .on_menu_event(|app, event| match event.id().as_ref() {
          "show" => {
            if let Some(window) = app.get_webview_window("main") {
              let _ = window.show();
              let _ = window.set_focus();
            }
          }
          "silence" => {
            let state = app.state::<Mutex<SilenceState>>();
            let mut guard = state.lock().unwrap();
            guard.enabled = !guard.enabled;
            let _ = apply_silence(app, guard.enabled);
          }
          "quit" => {
            app.exit(0);
          }
          _ => {}
        })
        .build(app)?;

      Ok(())
    })
    .invoke_handler(tauri::generate_handler![set_tray_state, notify])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
