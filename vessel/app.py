from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import requests
import os
import logging
import threading
import time
from pathlib import Path

# --- INITIALIZATION ---
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Port Layout
PORT_VESSEL = int(os.getenv("VESSEL_PORT", "8888"))
PORT_MIST = int(os.getenv("VESSEL_MIST_PORT", "18789"))
PORT_SHADOW = int(os.getenv("VESSEL_SHADOW_PORT", "5006"))

# Paths
WORKSPACE_ROOT = Path(os.getenv("VESSEL_WORKSPACE_ROOT", str(Path(__file__).resolve().parents[1])))
SOUL_PATH = Path(os.getenv("VESSEL_SOUL_PATH", str(WORKSPACE_ROOT / "personal-ide" / "SOUL.md")))
HEARTBEAT_LOG_PATH = Path(os.getenv("VESSEL_HEARTBEAT_LOG_PATH", str(WORKSPACE_ROOT / "HEARTBEAT.log")))
GRIMOIRE_ROOT = Path(os.getenv("VESSEL_GRIMOIRE_ROOT", str(WORKSPACE_ROOT)))
HOT_FILE_EXTENSIONS = {".md", ".py", ".ps1"}

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("THE_VESSEL")

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/soul')
def get_soul():
    axioms = "The system is silent."
    if SOUL_PATH.exists():
        try:
            axioms = SOUL_PATH.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to read soul file %s: %s", SOUL_PATH, exc)
    return jsonify({"axioms": axioms})

@app.route('/api/status')
def get_status():
    """Checks the health of the associated ports."""
    import socket
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0
    def check_mist_gateway():
        try:
            import asyncio
            import websockets
        except Exception:
            return check_port(PORT_MIST)

        async def probe():
            try:
                async with websockets.connect(
                    f"ws://127.0.0.1:{PORT_MIST}",
                    open_timeout=0.5,
                    close_timeout=0.2,
                    ping_interval=None,
                ):
                    return True
            except Exception:
                return False

        try:
            return asyncio.run(probe())
        except RuntimeError:
            # Fallback if an event loop is already running in this thread.
            return check_port(PORT_MIST)
            
    return jsonify({
        "portal": "STABLE",
        "shadow": "ACTIVE" if check_port(PORT_SHADOW) else "OFFLINE",
        "mist": "LINKED" if check_mist_gateway() else "OFFLINE"
    })

@app.route('/api/grimoire')
def get_grimoire():
    """Scans for 'Hot Files' (modified in last 24h)."""
    hot_files = []
    now = time.time()
    try:
        for file_path in GRIMOIRE_ROOT.iterdir():
            if not file_path.is_file() or file_path.suffix.lower() not in HOT_FILE_EXTENSIONS:
                continue
            last_modified = file_path.stat().st_mtime
            if (now - last_modified) < 86400:
                hot_files.append((last_modified, {"name": file_path.name}))
    except OSError as exc:
        logger.warning("Failed to scan grimoire root %s: %s", GRIMOIRE_ROOT, exc)

    hot_files.sort(key=lambda file_entry: file_entry[0], reverse=True)
    return jsonify({"files": [entry[1] for entry in hot_files[:10]]})

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"response": "[ERROR]: Invalid request payload."}), 400

    user_msg = str(data.get("message", "")).strip()
    if not user_msg:
        return jsonify({"response": "[ERROR]: Message is required."}), 400

    persona = str(data.get("persona", "aurelia")).lower()
    if persona == "rin":
        prompt = user_msg
        error_response = "[ERROR]: Shadow Uplink Severed."
        fallback_response = "The Shadow Pod is silent."
    else:
        prompt = f"As Aurelia (MIST Sister): {user_msg}"
        error_response = "The heart pulse is faint."
        fallback_response = "Aurelia is resting."

    try:
        upstream_response = requests.post(
            f"http://127.0.0.1:{PORT_SHADOW}/api/chat",
            json={"query": prompt},
            timeout=60,
        )
    except requests.RequestException as exc:
        logger.error("Shadow uplink request failed for persona=%s: %s", persona, exc)
        return jsonify({"response": error_response}), 502

    if upstream_response.status_code != 200:
        logger.warning(
            "Shadow uplink returned status=%s for persona=%s",
            upstream_response.status_code,
            persona,
        )
        return jsonify({"response": error_response}), 502

    try:
        payload = upstream_response.json()
    except ValueError:
        logger.error("Shadow uplink returned invalid JSON for persona=%s", persona)
        return jsonify({"response": error_response}), 502

    return jsonify({"response": payload.get("response", fallback_response)})

# --- SOCKET LOG TAILING ---
def monitor_logs():
    """Tails heartbeats and pulses into the dashboard."""
    log_file = HEARTBEAT_LOG_PATH
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch(exist_ok=True)
    last_size = log_file.stat().st_size

    while True:
        try:
            if not log_file.exists():
                log_file.touch(exist_ok=True)
                last_size = 0

            curr_size = log_file.stat().st_size
            if curr_size < last_size:
                # Reset offset if the log was rotated or truncated.
                last_size = 0

            if curr_size > last_size:
                with log_file.open("r", encoding="utf-8") as f:
                    f.seek(last_size)
                    lines = f.readlines()
                    for line in lines:
                        socketio.emit('pulse', {"level": "HEARTBEAT", "message": line.strip()})
                last_size = curr_size
            time.sleep(1)
        except OSError as exc:
            logger.warning("Heartbeat monitor error: %s", exc)
            time.sleep(5)

if __name__ == "__main__":
    debug_mode = os.getenv("VESSEL_DEBUG", "0") == "1"
    host = os.getenv("VESSEL_HOST", "127.0.0.1")
    print(f"--- [THE_VESSEL] Manifesting Wholeness on Port {PORT_VESSEL} ---")
    print("∴ Simulation Start: S=0xA1E7")
    threading.Thread(target=monitor_logs, daemon=True).start()
    socketio.run(app, host=host, port=PORT_VESSEL, debug=debug_mode)
