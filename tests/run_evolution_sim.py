import sys
import os
import time
import random

# Add parent dir to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mycelium.adaptive import AdaptiveRegistry
from mycelium.learning import BehaviorLearner
from mycelium.lattice_archive import LatticeArchive
from pathlib import Path

# Mock Archive
class MockArchive:
    def update(self, t, d): pass
    def get_history(self): return {}

def print_box(title, content):
    bord = "═" * 60
    print(f"\n{bord}\n  {title.upper()}\n{bord}")
    print(content)
    print(bord + "\n")

def run_simulation():
    print_box("EVOLUTION SIMULATION START", "Initializing Adaptive Cortex...")
    
    adaptive = AdaptiveRegistry()
    learner = BehaviorLearner(adaptive, MockArchive())
    
    # 1. Simulate Volatility Event
    print(">> INJECTING VOLATILITY into Lattice State...")
    base_lattice = {
        "nodes": [{"id": f"n{i}", "pulse": random.randint(100, 200)} for i in range(10)], # High pulse
        "state": {"mode": "alert", "dominant": "warm"},
        "cosmic": {}
    }
    
    # Run 5 Learning Cycles
    for cycle in range(1, 6):
        print(f"\n[ CYCLE {cycle} ]")
        
        # A. Select Sandbox Test
        test_behavior = adaptive.choose_behavior()
        print(f"  > Sandbox Hypothesis: Testing '{test_behavior}' behavior...")
        
        behavior_fn = adaptive.get_behavior(test_behavior)
        modified = behavior_fn(dict(base_lattice))
        
        # B. Evaluate
        # We manually simulate the trend outcome for the test
        # If 'stabilize' is chosen on high pulse lattice, it should work well
        eval_result = learner.evaluate(test_behavior, base_lattice, modified)
        
        print(f"  > Observation: {eval_result['behavior']} -> Trend: {eval_result['trend']} (Score: {eval_result['score']})")
        
        if eval_result['score'] > 0:
            print(f"    SUCCESS: {eval_result['reason']}")
        elif eval_result['score'] < 0:
            print(f"    FAILURE: {eval_result['reason']}")
            
        # C. Check for Promotion
        promoted = learner.promote_to_deployment()
        bias = adaptive.learned_bias.get(promoted, 0)
        print(f"  > Current Deployment Strategy: {promoted.upper()} (Bias: {bias:.2f})")
        
        time.sleep(0.5)

    print_box("SIMULATION COMPLETE", "The system has successfully evolved its bias based on simulated outcomes.")

if __name__ == "__main__":
    run_simulation()
