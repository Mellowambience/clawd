from collections import deque
import time

class LatticeMemory:
    def __init__(self, size=5):
        self.frames = deque(maxlen=size)

    def push(self, frame: dict):
        snapshot = {
            "ts": time.time(),
            "lattice": frame.get("lattice"),
            "cosmic": frame.get("cosmic"),
        }
        self.frames.append(snapshot)

    def diff(self):
        if len(self.frames) < 2:
            return None

        a, b = self.frames[-2], self.frames[-1]
        
        # Safe compare for cosmic/lattice which might be dicts or None
        cosmic_changed = a["cosmic"] != b["cosmic"]
        lattice_changed = a["lattice"] != b["lattice"]
        
        return {
            "dt": b["ts"] - a["ts"],
            "cosmic_changed": cosmic_changed,
            "lattice_changed": lattice_changed,
        }

    def trend(self):
        if len(self.frames) < 3:
            return "stable"

        changes = 0
        for i in range(1, len(self.frames)):
            if self.frames[i]["lattice"] != self.frames[i-1]["lattice"]:
                changes += 1

        if changes >= len(self.frames) - 1:
            return "volatile"
        if changes == 0:
            return "flat"
        return "drifting"
