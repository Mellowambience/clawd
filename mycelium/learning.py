import logging
import random
import time
from lattice_memory import LatticeMemory

logger = logging.getLogger("BehaviorLearner")

class BehaviorLearner:
    def __init__(self, adaptive_registry, archive):
        self.registry = adaptive_registry
        self.archive = archive
        self.sandbox_memory = LatticeMemory(size=10) # Separate memory for sandbox
        
        # Track last applied behavior and outcome in sandbox
        self.last_sandbox_behavior = None
        self.last_sandbox_ts = 0

    def evaluate(self, behavior_name, original_lattice, modified_lattice):
        """
        Evaluate if a chosen behavior improved the system state in Sandbox.
        
        Args:
            behavior_name (str): The behavior applied.
            original_lattice (dict): Raw lattice state before behavior.
            modified_lattice (dict): Resulting lattice state after behavior.
            
        Returns:
            dict: Outcome metrics (delta trend, diff reduction, etc.)
        """
        # Push to sandbox memory to track trends
        frame = {
            "lattice": modified_lattice, 
            "cosmic": original_lattice.get("cosmic") # Assuming cosmic doesn't change by behavior (yet)
        }
        self.sandbox_memory.push(frame)
        
        # Calculate sandbox trend
        trend = self.sandbox_memory.trend()
        
        # Define success criteria based on *intent* of behavior
        score = 0
        reason = "neutral"
        
        if behavior_name == "stabilize":
            # Success = lower volatility (trend -> 'flat' or 'stable')
            if trend in ["flat", "stable"]:
                score = 0.5
                reason = "trend_stabilized"
            elif trend == "volatile":
                score = -0.5
                reason = "volatility_persisted"
                
        elif behavior_name == "amplify":
            # Success = higher energy (trend -> 'volatile' or 'drifting')
            if trend in ["volatile", "drifting"]:
                score = 0.5
                reason = "energy_amplified"
            elif trend == "flat":
                score = -0.5
                reason = "amplification_failed"
                
        elif behavior_name == "focus":
            # Success = fewer changes (diff -> smaller dt or structure stable)
            diff = self.sandbox_memory.diff()
            if diff and not diff.get("lattice_changed"):
                score = 0.8
                reason = "structure_focused"
            else:
                score = 0.1
                reason = "minor_drift"
        
        # Log learning event
        if score != 0:
            logger.info(f"Sandbox Evaluation: {behavior_name} -> {trend} (Score: {score}, Reason: {reason})")
            
        # Update Registry Bias
        self.registry.update_bias(behavior_name, score * 0.1) # Small learning steps
        
        # Record outcome for persistence
        self.last_sandbox_behavior = behavior_name
        self.last_sandbox_ts = time.time()
        
        return {
            "behavior": behavior_name,
            "trend": trend,
            "score": score,
            "reason": reason
        }

    def promote_to_deployment(self):
        """
        Decide which behavior from sandbox experiments is ready for LIVE deployment.
        
        Returns:
            str: Name of the promoted behavior, or None if no clear winner.
        """
        # Find behavior with highest learned bias
        best_behavior = None
        max_bias = -1.0
        
        for name, bias in self.registry.learned_bias.items():
            if bias > max_bias and bias > 0.2: # Must have positive reinforcement
                max_bias = bias
                best_behavior = name
        
        if best_behavior:
            logger.info(f"Promoting behavior to LIVE: {best_behavior} (Bias: {max_bias:.2f})")
            return best_behavior
            
        return "neutral" # Default fallback
