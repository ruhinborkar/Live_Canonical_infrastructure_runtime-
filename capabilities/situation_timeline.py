"""Generic situation timeline.

Append-only, time-ordered record of operationally significant events so the
command center can answer "what is happening / what just happened".
Inputs: timeline entries from engine, capabilities, operators.
Outputs: chronological tail for dashboards and audits.
"""

from datetime import datetime, timezone
from typing import Any

from persistence.append_only_store import AppendOnlyStore
from services.event_loader import read_log_events

TIMELINE_LOG = "logging/logs/situation_timeline.jsonl"


class SituationTimeline:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def record(
        cls,
        category: str,
        summary: str,
        *,
        severity: str = "INFO",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "timestamp": cls._now(),
            "category": category,
            "summary": summary,
            "severity": severity,
            "details": details or {},
        }
        AppendOnlyStore.append_event(TIMELINE_LOG, entry)
        return entry

    @classmethod
    def tail(cls, limit: int = 100) -> list[dict[str, Any]]:
        entries = read_log_events(TIMELINE_LOG)
        return list(reversed(entries[-limit:]))

    @classmethod
    def clear(cls) -> None:
        AppendOnlyStore.clear_log(TIMELINE_LOG)
