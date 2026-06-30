"""State transition engine.

Defines the legal operational lifecycle transitions and validates/records
transitions. Generic finite-state-machine guard reused by the runtime engine
and exposed for audit of the operational state history.
"""

from datetime import datetime, timezone
from typing import Any

LEGAL_TRANSITIONS = {
    "STOPPED": {"STARTING"},
    "STARTING": {"RUNNING", "STOPPING", "STOPPED"},
    "RUNNING": {"DEGRADED", "STOPPING"},
    "DEGRADED": {"RUNNING", "STOPPING"},
    "STOPPING": {"STOPPED"},
}


class StateTransitionEngine:
    _history: list[dict[str, Any]] = []

    @classmethod
    def is_legal(cls, current: str, target: str) -> bool:
        return target in LEGAL_TRANSITIONS.get(current, set())

    @classmethod
    def record(cls, current: str, target: str) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from": current,
            "to": target,
            "legal": cls.is_legal(current, target),
        }
        cls._history.append(entry)
        cls._history = cls._history[-200:]
        return entry

    @classmethod
    def history(cls, limit: int = 50) -> list[dict[str, Any]]:
        return list(reversed(cls._history[-limit:]))

    @classmethod
    def legal_map(cls) -> dict[str, list[str]]:
        return {state: sorted(targets) for state, targets in LEGAL_TRANSITIONS.items()}
