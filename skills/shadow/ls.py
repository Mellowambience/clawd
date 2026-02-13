import os
import sys

def list_files(target="."):
    # Restrict to AetherRose root for security
    root = "c:/Users/nator/AetherRose"
    target_path = os.path.abspath(os.path.join(os.getcwd(), target))
    
    if not target_path.startswith(root):
        print(f"[SECURITY]: Access to {target_path} is restricted.")
        return

    if not os.path.exists(target_path):
        print(f"[ERROR]: Path '{target}' not found.")
        return

    print(f"--- [DIRECTORY_SCAN]: {target} ---")
    for item in os.listdir(target_path):
        is_dir = "[DIR]" if os.path.isdir(os.path.join(target_path, item)) else "     "
        print(f"{is_dir} {item}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    list_files(path)
