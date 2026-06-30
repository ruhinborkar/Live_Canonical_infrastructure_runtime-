"""Generic operator action recorder.

Captures human/operator interventions (submit work, acknowledge alert,
pause/resume, override) for the operator timeline and audit.
Inputs: operator action calls from APIs.
Outputs: chronological operator action log.
"""

from datetime import datetime, timezone
from typing import Any

from persistence.append_only_store import AppendOnlyStore
from services.event_loader import read_log_events

OPERATOR_LOG = "logging/logs/operator_actions.jsonl"


class OperatorActions:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def record(
        cls,
        action: str,
        *,
        operator: str = "operator",
        target: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "timestamp": cls._now(),
            "operator": operator,
            "action": action,
            "target": target,
            "details": details or {},
        }
        AppendOnlyStore.append_event(OPERATOR_LOG, entry)
        return entry

    @classmethod
    def tail(cls, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(read_log_events(OPERATOR_LOG)[-limit:]))
