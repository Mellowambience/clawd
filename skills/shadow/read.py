import os
import sys

def read_file(target):
    root = "c:/Users/nator/AetherRose"
    target_path = os.path.abspath(target)
    
    if not target_path.startswith(root):
        print(f"[SECURITY]: Access to {target_path} is restricted.")
        return

    if not os.path.exists(target_path):
        print(f"[ERROR]: File '{target}' not found.")
        return

    if os.path.getsize(target_path) > 1024 * 50: # 50KB limit
        print("[LIMIT]: File too large for direct read. Use /summarize.")
        return

    print(f"--- [DATA_STREAM]: {target} ---")
    with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
        print(f.read())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        read_file(sys.argv[1])
    else:
        print("[ERROR]: No file target specified.")
