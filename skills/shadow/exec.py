import os
import sys
import subprocess

def exec_command(cmd):
    # Restricted execution
    # Blacklist dangerous commands
    blacklist = ["rm", "del", "format", "taskkill", "shutdown"]
    if any(b in cmd.lower() for b in blacklist):
        print(f"[SECURITY]: Command '{cmd}' contains restricted operations.")
        return

    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=30)
        print(f"--- [SYSTEM_OUTPUT] ---\n{result.decode('utf-8')}")
    except Exception as e:
        print(f"[ERROR]: Execution failed. {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        exec_command(" ".join(sys.argv[1:]))
    else:
        print("[ERROR]: No command specified.")
