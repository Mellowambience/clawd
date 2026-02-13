import sys
import traceback

print("Testing Gateway Import...")
try:
    from moltbot.gateway import server
    print("✓ Import successful")
    
    print("\nTesting OpenClawEngine...")
    from moltbot.gateway.openclaw_engine import OpenClawEngine
    engine = OpenClawEngine()
    print(f"✓ Engine created: {engine.get_status_report()}")
    
    print("\nTesting MistGateway init...")
    gateway = server.MistGateway()
    print("✓ Gateway instance created")
    
    print("\nAll tests passed. Gateway should be able to start.")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nFull Traceback:")
    traceback.print_exc()
    sys.exit(1)
