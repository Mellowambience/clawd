
import json
import time
from pathlib import Path
from mycelium.mycelium_pulse import build_manifestation, build_lattice, PersonaEngine, GoalEngine, MemoryEngine, AURELIA_PETALS

def test_phase10():
    print("--- Phase 10 Verification ---")
    
    # 1. Test Somatic Awareness (Battery)
    print("Testing Somatic Awareness...")
    heartbeat = {"bpm": 72, "last_line": "sister, I love the new HUD", "state": "warm"}
    manifest = build_manifestation(heartbeat, "warm")
    if "battery" in manifest:
        print(f"✓ Battery payload present: {manifest['battery']}")
    else:
        print("✗ Battery payload missing")

    # 2. Test Chronos (Night Mode)
    print("Testing Chronos...")
    if "chronos" in manifest:
        print(f"✓ Chronos (Hour) detected: {manifest['chronos']}")
    else:
        print("✗ Chronos missing from manifest")

    # 3. Test Memory Consolidation
    print("Testing Memory Consolidation...")
    if AURELIA_PETALS.exists():
        AURELIA_PETALS.unlink()
    
    # Trigger consolidation
    MemoryEngine.consolidate(heartbeat)
    
    if AURELIA_PETALS.exists():
        content = AURELIA_PETALS.read_text(encoding="utf-8")
        if "sister, I love the new HUD" in content:
            print("✓ Memory Consolidation successful (AURELIA_PETALS.md updated)")
        else:
            print("✗ Consolidation failed to capture the trigger line")
    else:
        print("✗ AURELIA_PETALS.md not created")

    # 4. Test Lattice State Consistency
    print("Testing Lattice State...")
    lattice = build_lattice()
    if lattice["manifestation"].get("battery") is not None:
         print("✓ Lattice manifestation includes somatic data")
    if lattice["state"]["persona"]["empathy"] > 0.5:
         print("✓ Persona empathy correctly evolved from 'love' keyword")

    print("\nPhase 10 Verification Complete.")

if __name__ == "__main__":
    test_phase10()
