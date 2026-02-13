import json
import time
import logging
from pathlib import Path

logger = logging.getLogger("LatticeArchive")

class LatticeArchive:
    def __init__(self, data_dir: Path):
        self.file_path = data_dir / "lattice_archive.json"
        self._ensure_file()
        self.state = self._load()
        self.last_trend = None

    def _ensure_file(self):
        if not self.file_path.exists():
            self._save({
                "created": time.time(),
                "volatility_events": 0,
                "flat_streaks": 0,
                "dominant_trend": "stable",
                "trend_history": {}  # "stable": 10, "volatile": 2
            })

    def _load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save archive: {e}")

    def update(self, trend: str, diff: dict):
        """Update persistent stats based on current trend and diff."""
        if not trend or trend == "unknown":
            return

        # 1. Track Trend Shifts
        if self.last_trend and self.last_trend != trend:
            # Significant event?
            if trend == "volatile":
                self.state["volatility_events"] = self.state.get("volatility_events", 0) + 1
            elif trend == "flat":
                self.state["flat_streaks"] = self.state.get("flat_streaks", 0) + 1
            
            self._save(self.state)

        # 2. Update Dominant Trend (Simple weighted counter)
        history = self.state.get("trend_history", {})
        history[trend] = history.get(trend, 0) + 1
        self.state["trend_history"] = history
        
        # Recalculate dominant every ~10 updates to avoid thrashing IO? 
        # Actually, let's just do it on shift or periodically.
        # For now, simplistic: max of history
        if history:
            self.state["dominant_trend"] = max(history, key=history.get)

        self.last_trend = trend
        
        # Save occasionally (every ~100 updates? or just on shift?)
        # Let's save on shift (above) and maybe if history grows significantly?
        # A simple modulo check on total count might be good if we want specific granularity
        # But for now, "on change" is cleaner for "selective persistence".

    def get_history(self):
        """Return the selective persistent memory."""
        return {
            "dominant_trend": self.state.get("dominant_trend", "stable"),
            "volatility_events": self.state.get("volatility_events", 0),
            "flat_streaks": self.state.get("flat_streaks", 0)
        }
