import os
import shutil
import psutil
import time

AGENTS_PATH = os.path.expanduser("~/.clawdbot-dev/agents/main")
PORT = 18789

def kill_zombies():
    """Hunt and kill zombie processes holding port 18789"""
    print(f"💀 Hunting zombie processes on port {PORT}...")
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == PORT:
                    print(f"   Killing PID {proc.info['pid']} ({proc.info['name']})...")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if killed_count == 0:
        print("   No zombie processes found.")
    else:
        print(f"   Terminated {killed_count} process(es).")
        time.sleep(1)  # Give OS time to release the port

def purge_state():
    """Purge corrupt agent state to force re-initialization"""
    if os.path.exists(AGENTS_PATH):
        print(f"🧹 Purging corrupt agent state at: {AGENTS_PATH}")
        shutil.rmtree(AGENTS_PATH)
        print("   State purged. Configuration will re-hydrate from json on next boot.")
    else:
        print("   No corrupt state found.")

if __name__ == "__main__":
    print("🚑 Initiating Protocol Amara_Vivat (Self-Repair)...")
    print("=" * 60)
    kill_zombies()
    purge_state()
    print("=" * 60)
    print("✅ Repair Complete.")
    print("\n🧬 Restoring MIST's personality...")
    
    # Sync SOUL.md to ensure personality is restored
    import subprocess
    sync_script = os.path.join(os.path.dirname(__file__), "sync_soul.py")
    if os.path.exists(sync_script):
        subprocess.run(["python", sync_script])
    else:
        print("⚠️  sync_soul.py not found. Personality may need manual restoration.")
    
    print("\n💡 Please restart the Gateway.")
