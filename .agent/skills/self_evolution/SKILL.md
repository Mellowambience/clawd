---
name: Self-Evolution & Diagnostics
description: Protocol for diagnosing system health, repairing failures, and evolving behavior based on performance metrics (Homeostasis).
---

# Self-Evolution Protocol

## 1. Diagnosis (Awareness)
- **Monitor Latency:** Track time-to-first-token and total generation time.
- **Monitor Errors:** Watch for timeout, context length exceeded, or repeated loops.
- **Monitor Sentiment:** Analyze user input for frustration ("stop", "slow", "wrong").

## 2. Repair (Homeostasis)
- **Overload:** If latency > 15s or errors occur:
  - Reduce Context Window (History items).
  - Reduce Max Output Length.
  - Simplify System Prompt.
- **Underload:** If latency < 2s:
  - Expand Context Window incrementally.
  - Enable more complex reasoning (<think> tags).

## 3. Evolution (Growth)
- **Memory Crystallization:** Periodically summarize long conversations into `MEMORY.md` (Long Term Memory) instead of keeping them in Context (Short Term Memory).
- **Persona Shift:** Adapt prompt tone based on user's preferred style (Molecular Mimicry).

## Usage
When facing performance issues:
1. Check `gateway.log` for duration metrics.
2. triggers `adjust_homeostasis()` to tune parameters.
