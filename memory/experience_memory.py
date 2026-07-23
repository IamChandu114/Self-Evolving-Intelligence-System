from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ExperienceMemory:
    """Session and disk-backed experience store for the adaptive system."""

    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path else self._default_storage_path()
        self.experiences: list[dict[str, Any]] = []
        self.retrieval_count = 0
        self.load()

    def _default_storage_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "storage" / "experience_memory.json"

    def _ensure_storage_dir(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if not self.storage_path.exists():
            self.experiences = []
            self.retrieval_count = 0
            return

        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.experiences = payload.get("experiences", [])
            self.retrieval_count = int(payload.get("retrieval_count", 0))
        except Exception:
            self.experiences = []
            self.retrieval_count = 0

    def save(self) -> None:
        self._ensure_storage_dir()
        payload = {
            "experiences": self.experiences,
            "retrieval_count": self.retrieval_count,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def store(self, input_signal, decision, reward, metadata: dict[str, Any] | None = None):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "input": list(input_signal),
            "decision": decision,
            "reward": reward,
            "confidence": None if metadata is None else metadata.get("confidence"),
            "strategy_weight": None if metadata is None else metadata.get("strategy_weight"),
            "notes": None if metadata is None else metadata.get("notes"),
        }
        if metadata:
            entry.update({k: v for k, v in metadata.items() if k not in entry})

        self.experiences.append(entry)
        self.save()
        return entry

    def recent(self, n: int = 5):
        self.retrieval_count += 1
        self.save()
        return self.experiences[-n:]

    def latest(self):
        return self.experiences[-1] if self.experiences else None

    def search(self, query: str):
        if not query:
            return list(self.experiences)

        needle = query.lower().strip()
        results = []
        for experience in self.experiences:
            haystack = " ".join(
                [
                    str(experience.get("timestamp", "")),
                    str(experience.get("input", "")),
                    str(experience.get("decision", "")),
                    str(experience.get("reward", "")),
                    str(experience.get("confidence", "")),
                    str(experience.get("strategy_weight", "")),
                    str(experience.get("notes", "")),
                ]
            ).lower()
            if needle in haystack:
                results.append(experience)
        return results

    def filter_entries(
        self,
        decision: str | None = None,
        reward: int | None = None,
        minimum_confidence: float | None = None,
    ):
        filtered = list(self.experiences)
        if decision and decision != "All":
            filtered = [item for item in filtered if item.get("decision") == decision]
        if reward is not None:
            filtered = [item for item in filtered if item.get("reward") == reward]
        if minimum_confidence is not None:
            filtered = [
                item
                for item in filtered
                if item.get("confidence") is not None and float(item.get("confidence")) >= minimum_confidence
            ]
        return filtered

    def export_json(self) -> str:
        payload = {
            "experiences": self.experiences,
            "retrieval_count": self.retrieval_count,
        }
        return json.dumps(payload, indent=2)

    def reset(self, persist: bool = True):
        self.experiences = []
        self.retrieval_count = 0
        if persist and self.storage_path.exists():
            self.storage_path.unlink()

    def summary(self) -> dict[str, Any]:
        rewards = [item.get("reward", 0) for item in self.experiences]
        average_reward = sum(rewards) / len(rewards) if rewards else 0.0
        confidence_values = [item.get("confidence") for item in self.experiences if item.get("confidence") is not None]
        return {
            "size": len(self.experiences),
            "retrieval_count": self.retrieval_count,
            "average_reward": average_reward,
            "positive_feedback": sum(1 for reward in rewards if reward > 0),
            "negative_feedback": sum(1 for reward in rewards if reward < 0),
            "average_confidence": sum(confidence_values) / len(confidence_values) if confidence_values else 0.0,
            "storage_path": str(self.storage_path),
        }
