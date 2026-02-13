import socket
import sys

def check_port(host, port, name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"[OK] {name} is listening on {host}:{port}")
        else:
            print(f"[FAIL] {name} is NOT listening on {host}:{port} (Code: {result})")
        s.close()
    except Exception as e:
        print(f"[ERROR] Could not check {name}: {e}")

print("--- DIAGNOSTIC: PORT CHECK ---")
check_port("127.0.0.1", 8765, "PULSE Server (SocketIO)")
check_port("127.0.0.1", 18789, "GATEWAY Server (WebSocket)")
print("------------------------------")
