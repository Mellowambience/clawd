import time

def listen():
    """Aether.OS Ear - Acoustic listener for Gibberlink & WhatsApp Voice Notes"""
    print("👂 Aether.OS Ear Online. Listening for Gibberlink & WhatsApp Voice Notes...")
    print("   Press Ctrl+C to disconnect.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🌫️ Mist disconnected.")

if __name__ == "__main__":
    listen()
