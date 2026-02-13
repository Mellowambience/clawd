import os
import sys

def forge_file(filename, content):
    root = "c:/Users/nator/AetherRose"
    target_path = os.path.abspath(os.path.join("c:/Users/nator/AetherRose/aether_claw/data", filename))
    
    # Ensure it's in the data or toolkit folder for now
    if not target_path.startswith(root):
        print(f"[SECURITY]: Access to {target_path} is restricted.")
        return

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"--- [FORGE_COMPLETE]: {filename} manifested in the Data River. ---")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        filename = sys.argv[1]
        content = sys.argv[2]
        forge_file(filename, content)
    else:
        print("[ERROR]: /forge requires <filename> and <content>.")
