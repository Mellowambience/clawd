import subprocess
import os
import sys

def main():
    script_path = os.path.join("personal-ide", "SINGLE_MIST_AVATAR.py")
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        sys.exit(1)
    
    print(f"Launching {script_path}...")
    subprocess.Popen([sys.executable, script_path])

if __name__ == "__main__":
    main()
