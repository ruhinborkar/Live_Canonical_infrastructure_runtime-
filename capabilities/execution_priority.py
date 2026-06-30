"""Execution prioritisation capability.

Generic, rule-based scoring that maps an event to a priority value
(1 = most urgent, 9 = lowest). Rules are domain-agnostic signals only.
Inputs: a runtime event.
Outputs: integer priority.
"""

from typing import Any

DEFAULT_PRIORITY = 5


class ExecutionPriority:
    @classmethod
    def score(cls, event: dict[str, Any]) -> int:
        priority = DEFAULT_PRIORITY
        event_type = event.get("event_type")
        payload = event.get("payload", {}) or {}

        if event_type in {"INTERRUPTED_EVENT", "CORRUPTED_EVENT"}:
            priority -= 3
        if str(payload.get("severity", "")).upper() in {"HIGH", "CRITICAL"}:
            priority -= 2
        if payload.get("urgent") is True:
            priority -= 1
        if event.get("runtime_state") == "DEGRADED":
            priority -= 1

        explicit = event.get("priority")
        if isinstance(explicit, int):
            priority = explicit

        return max(1, min(9, priority))
