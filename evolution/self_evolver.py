from __future__ import annotations

from typing import Any


class SelfEvolver:
    def __init__(self, memory):
        self.memory = memory
        self.evolution_history = []
        self.last_update = None

    def evolve(self, core, window_size: int = 5):
        experiences = self.memory.recent(window_size)

        if not experiences:
            self.last_update = {
                "avg_reward": 0.0,
                "delta": 0.0,
                "reason": "No experiences available",
                "window_size": window_size,
            }
            return self.last_update

        avg_reward = sum(e["reward"] for e in experiences) / len(experiences)

        if avg_reward < 0:
            delta = -0.1
            reason = "Recent feedback is negative, so strategy is reduced."
        else:
            delta = 0.05
            reason = "Recent feedback is positive, so strategy is reinforced."

        previous_weight = core.strategy_weight
        updated_weight = core.update_strategy(delta)

        self.last_update = {
            "avg_reward": avg_reward,
            "delta": delta,
            "previous_weight": previous_weight,
            "updated_weight": updated_weight,
            "window_size": window_size,
            "reason": reason,
            "recent_count": len(experiences),
            "adaptation_score": round(max(0.0, min(1.0, (avg_reward + 1.0) / 2.0)), 4),
        }
        self.evolution_history.append(self.last_update)
        return self.last_update

    def summary(self) -> dict[str, Any]:
        latest = self.last_update or {}
        return {
            "evolution_steps": len(self.evolution_history),
            "last_update": latest,
        }
