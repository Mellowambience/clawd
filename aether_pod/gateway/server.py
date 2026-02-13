from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import os
import threading
import time
import datetime
from pod.core import AetherPod

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

pod = AetherPod()
LOG_FILE = "c:/Users/nator/clawd/aether_pod/data/operation.log"

def log_to_pulse(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | **{level}** | {message} |\n")
    socketio.emit('new_pulse', {
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
        'level': level,
        'message': message
    })

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        query = data.get("query", "")
        log_to_pulse(f"Query: {query}", "USER")
        
        response = pod.ask(query)
        log_to_pulse("Response Generated", "RIN")
        
        return jsonify({"response": response})
    except Exception as e:
        err_msg = f"FATAL_RES_ERROR: {e}"
        log_to_pulse(err_msg, "CRITICAL")
        return jsonify({"response": f"The Shadow Core has encountered a fatal resonance: {e}"}), 500

def watch_logs():
    """Tails the system logs (optional hook for sub-commands)"""
    pass # Expandable for real-time subprocess logging

if __name__ == "__main__":
    print("--- [SHADOW_CLAW] Engaging Fused Gateway ---")
    socketio.run(app, port=5006, debug=True)
