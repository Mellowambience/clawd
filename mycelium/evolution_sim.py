import sys
import os
import time
import random
from pathlib import Path

# Mock LatticeArchive
class MockArchive:
    def __init__(self):
        self.state = {}
    def update(self, t, d): pass
    def get_history(self): return {}

from lattice_memory import LatticeMemory
from adaptive import AdaptiveRegistry
from learning import BehaviorLearner

def run_simulation():
    print("\n-------------------------------\nADAPTIVE EVOLUTION SIMULATION\n-------------------------------\n")
    
    adaptive = AdaptiveRegistry()
    archive = MockArchive()
    learner = BehaviorLearner(adaptive, archive)
    
    # 1. Base State: High Volatility (Simulated Pulse spike)
    base_lattice = {
        "nodes": [{"id": f"n{i}", "pulse": 150} for i in range(5)], 
        "state": {"mode": "alert", "dominant": "warm"},
        "cosmic": {}
    }
    
    # 2. Run Learning Cycles
    for i in range(1, 6):
        print(f"\n[ CYCLE {i} ]")
        
        # A. Select behavior
        behavior = adaptive.choose_behavior()
        print(f"  > Sandbox Test: '{behavior}'")
        
        # B. Apply behavior in Sandbox
        fn = adaptive.get_behavior(behavior)
        modified = fn(dict(base_lattice)) # Apply to copy
        
        # C. Evaluate Outcome
        # We cheat/mock the trend here, assuming 'stabilize' works best for high pulse
        outcome = learner.evaluate(behavior, base_lattice, modified)
        
        print(f"  > Outcome: {outcome['trend']} (Score: {outcome['score']})")
        if outcome['score'] > 0:
            print(f"    SUCCESS: Reinforcing '{behavior}' bias.")
        elif outcome['score'] < 0:
            print(f"    FAILURE: Reducing '{behavior}' bias.")

        # D. Check Promotion
        promoted = learner.promote_to_deployment()
        bias = adaptive.learned_bias.get(promoted, 0)
        print(f"  > LIVE Deployment: {promoted.upper()} (Bias: {bias:.2f})")
        
        time.sleep(0.2)

    print("\n[ DONE ] Simulation completed successfully.")

if __name__ == "__main__":
    run_simulation()
