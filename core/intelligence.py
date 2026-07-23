from __future__ import annotations

from math import exp
from typing import Any


class CoreIntelligence:
    def __init__(self):
        self.strategy_weight = 1.0
        self.decision_history = []
        self.last_decision = None
        self.last_score = 0.0
        self.last_confidence = 0.0
        self.last_input = []
        self.strategy_history = [self.strategy_weight]

    def decide(self, input_signal, return_details: bool = False):
        input_sum = sum(input_signal)
        score = input_sum * self.strategy_weight
        decision = "Action-A" if score > 0 else "Action-B"
        confidence = self._confidence_from_score(score)
        feature_contributions = [
            {
                "feature_index": index,
                "raw_value": value,
                "weighted_contribution": round(value * self.strategy_weight, 4),
            }
            for index, value in enumerate(input_signal, start=1)
        ]

        self.last_decision = decision
        self.last_score = score
        self.last_confidence = confidence
        self.last_input = list(input_signal)
        self.decision_history.append(
            {
                "input": list(input_signal),
                "score": score,
                "decision": decision,
                "confidence": confidence,
                "strategy_weight": self.strategy_weight,
                "feature_contributions": feature_contributions,
            }
        )

        details = {
            "input_sum": input_sum,
            "weighted_score": score,
            "decision": decision,
            "confidence": confidence,
            "strategy_weight": self.strategy_weight,
            "feature_contributions": feature_contributions,
            "decision_margin": score,
        }
        if return_details:
            return decision, details
        return decision

    def update_strategy(self, delta):
        self.strategy_weight += delta
        self.strategy_history.append(self.strategy_weight)
        return self.strategy_weight

    def _confidence_from_score(self, score: float) -> float:
        magnitude = abs(score)
        confidence = 1.0 - exp(-magnitude / 5.0)
        return round(max(0.0, min(0.99, confidence)), 4)

    def summary(self) -> dict[str, Any]:
        return {
            "strategy_weight": self.strategy_weight,
            "last_decision": self.last_decision,
            "last_score": self.last_score,
            "last_confidence": self.last_confidence,
            "decisions_made": len(self.decision_history),
        }
