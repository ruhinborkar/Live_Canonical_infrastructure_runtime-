"""Event ingestion capability.

Normalises arbitrary inbound payloads into runtime events and submits them to
the engine. The single entry point for all external work intake.
Inputs: raw payload dicts (any shape) + optional priority/source.
Outputs: accepted task descriptors.
Dependencies: background runtime engine, execution_priority.
"""

from typing import Any

from capabilities.execution_priority import ExecutionPriority
from runtime.background_runtime_engine import get_engine


class EventIngestion:
    @classmethod
    def ingest(
        cls,
        payload: dict[str, Any],
        *,
        priority: int | None = None,
        source: str = "ingestion",
    ) -> dict[str, Any]:
        event = cls._normalise(payload)
        resolved_priority = priority if priority is not None else ExecutionPriority.score(event)
        return get_engine().submit(event, priority=resolved_priority, source=source)

    @classmethod
    def ingest_batch(cls, payloads: list[dict[str, Any]], *, source: str = "ingestion") -> dict[str, Any]:
        accepted = [cls.ingest(p, source=source) for p in payloads]
        return {"accepted": len(accepted), "task_ids": [t["task_id"] for t in accepted]}

    @staticmethod
    def _normalise(payload: dict[str, Any]) -> dict[str, Any]:
        if "payload" in payload and isinstance(payload["payload"], dict):
            event = dict(payload)
        else:
            event = {"payload": dict(payload)}
        event.setdefault("event_type", "NORMAL_EVENT")
        event.setdefault("runtime_state", "OPERATIONAL")
        return event
