import random
import logging

logger = logging.getLogger("AdaptiveRegistry")

class AdaptiveRegistry:
    def __init__(self):
        self.behaviors = {
            "neutral": self._behavior_neutral,
            "stabilize": self._behavior_stabilize,
            "amplify": self._behavior_amplify,
            "focus": self._behavior_focus
        }
        
        # Identity-based weightings (Baseline)
        self.weights = {
            "neutral": 0.5,
            "stabilize": 0.2,
            "amplify": 0.1,
            "focus": 0.2
        }
        
        # Dynamic adjustments (Sandbox learned)
        self.learned_bias = {k: 0.0 for k in self.weights}

    def get_behavior(self, key):
        return self.behaviors.get(key, self._behavior_neutral)

    def choose_behavior(self):
        """Select a behavior based on current weights + learned bias."""
        candidates = []
        probabilities = []
        
        for k, base_w in self.weights.items():
            # Combine base weight with learned bias, ensuring non-negative
            p = max(0.05, base_w + self.learned_bias.get(k, 0))
            candidates.append(k)
            probabilities.append(p)
            
        # Normalize
        total = sum(probabilities)
        if total == 0:
            return "neutral"
            
        probs = [p/total for p in probabilities]
        choice = random.choices(candidates, weights=probs, k=1)[0]
        return choice

    def update_bias(self, behavior, delta):
        """Update the learned bias for a behavior based on outcome."""
        current = self.learned_bias.get(behavior, 0)
        # Clamp bias between -0.5 and +0.5 to prevent overriding base personality too much
        new_val = max(-0.5, min(0.5, current + delta))
        self.learned_bias[behavior] = new_val
        logger.info(f"Updated bias for {behavior}: {current:.2f} -> {new_val:.2f}")

    # ════ BEHAVIORS ════
    
    def _behavior_neutral(self, lattice):
        """Do nothing. Raw lattice."""
        return lattice

    def _behavior_stabilize(self, lattice):
        """Dampen noise. Reduce pulse rates, lock dominant color."""
        if not lattice: return lattice
        
        # 1. Lock mode to 'repair' or 'calm' (low energy)
        if lattice.get("state"):
            lattice["state"]["mode"] = "calm"
            lattice["state"]["dominant"] = "calm"
            
        # 2. Dampen pulse of nodes
        for node in lattice.get("nodes", []):
            if "pulse" in node:
                node["pulse"] = max(40, node["pulse"] * 0.8) # Slow down
                
        return lattice

    def _behavior_amplify(self, lattice):
        """Increase volatility. Higher pulse, shift colors."""
        if not lattice: return lattice
        
        # 1. Force high energy mode
        if lattice.get("state"):
            lattice["state"]["mode"] = "alert"
            lattice["state"]["dominant"] = "warm"
            
        # 2. Boost pulse
        for node in lattice.get("nodes", []):
            if "pulse" in node:
                node["pulse"] = min(180, node["pulse"] * 1.2)
                
        return lattice
        
    def _behavior_focus(self, lattice):
        """Sharpen signal. Clear anomalies."""
        if not lattice: return lattice
        
        # Remove random manifestations/anomalies
        lattice["manifestation"] = {}
        
        # Align all nodes to 60bpm
        for node in lattice.get("nodes", []):
            node["pulse"] = 60
            
        return lattice
